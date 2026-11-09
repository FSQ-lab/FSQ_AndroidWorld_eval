"""Exercise RPC process boundaries, not just final-log extraction."""

from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
from queue import Queue
import sys

import pytest

from fsq_androidworld_eval.action_budget import ActionGate, StepBudgetExceeded
from fsq_androidworld_eval.lifecycle import EpisodeDeadlines
from fsq_androidworld_eval import omp_supervisor as supervisor
from fsq_androidworld_eval.runner import _normalize_agent_events


# A deterministic RPC peer supplies business and cleanup messages over the real
# process pipes. No Android execution or successful evaluator result is simulated.
PEER = r'''
import json,sys
mode = MODE

def emit(event):
    print(json.dumps(event),flush=True)

def final(text):
    emit({'type':'message_end','message':{'role':'assistant','stopReason':'stop',
         'content':[{'type':'text','text':text}]}})

def end():
    emit({'type':'agent_end','isTerminal':True})

def tool_start(identity):
    emit({'type':'tool_execution_start','toolCallId':identity,'toolName':'write',
          'args':{'path':'xd://mcp__amkernel_python_exec','content':json.dumps({'code':'retained_driver'})}})

for line in sys.stdin:
    command=json.loads(line)
    if command.get('id')=='episode':
        tool_start('observe')
        if mode not in ('wait_for_finalization','no_answer'):
            final('{"taskOutcome":"first answer"}')
            if mode=='duplicate': final('{"taskOutcome":"wrong replacement"}')
            end()
    elif command.get('id')=='answer-finalization' and mode=='wait_for_finalization':
        final('{"taskOutcome":"last legal action result"}')
        end()
    elif command.get('id')=='cleanup':
        emit({'type':'message_end','message':{'role':'user','content':[{'type':'text','text':command['message']}]}})
        tool_start('quit')
        emit({'type':'tool_execution_end','toolCallId':'quit','result':{'content':[{'type':'text','text':json.dumps({
          'status':'completed','kernelState':'alive','executionCount':2,'durationMs':1,
          'result':{'ownedSessionId':'owned-test-driver','quitReturned':True}})}]}})
        final('{"taskOutcome":"cleanup must never become the answer","sessionCleanup":"closed"}')
        end()
'''


def _gate_with_last_legal_action() -> ActionGate:
    gate = ActionGate()
    with ThreadPoolExecutor(max_workers=1) as pool:
        def action():
            permit = gate.submit({'kind': 'click', 'path': '/session/:sessionId/click'})
            permit.complete(200)
        work = pool.submit(action)
        assert gate.advance_step()['status'] == 200
        work.result(timeout=2)
    return gate


def _run(tmp_path: Path, gate: ActionGate, mode: str, *, business: float = 5):
    peer = tmp_path / 'peer'
    peer.write_text(f'#!{sys.executable}\n' + PEER.replace('MODE', repr(mode), 1))
    peer.chmod(0o700)
    profile = tmp_path / 'sandbox.sb'
    profile.write_text('(version 1) (allow default)')
    output = tmp_path / 'episode'
    output.mkdir()
    result = supervisor.run_omp(
        project=tmp_path, sandbox_profile=profile, output_dir=output,
        prompt='business request', omp=str(peer), model='fixture/model',
        deadlines=EpisodeDeadlines(business, cleanup_seconds=2, termination_grace_seconds=1),
        action_gate=gate, normalize=_normalize_agent_events, skills=(),
    )
    private = json.loads((output / 'raw-private/business-submission.json').read_text())
    return result, private


def test_last_legal_action_can_deliver_answer_without_another_mutation(tmp_path):
    gate = _gate_with_last_legal_action()
    gate.close_budget()
    result, private = _run(tmp_path, gate, 'wait_for_finalization')
    assert private['answer'] == 'last legal action result'
    assert result['answerSubmission']['receipt']['phase'] == 'finalization'
    assert json.loads(result['normalized']['finalText']) == {'taskOutcome': 'last legal action result'}
    assert result['termination']['reason'] == 'step_budget'
    assert result['agentCompleted'] is False
    assert len([c for c in result['normalized']['toolCalls'] if 'sessionCleanup' in c]) == 1
    assert gate.snapshot()['executedActionCount'] == 1
    with pytest.raises(StepBudgetExceeded):
        gate.submit({'kind': 'click', 'path': '/session/:sessionId/click'})
    assert gate.snapshot()['executedActionCount'] == 1


@pytest.mark.parametrize('close_before_read', [False, True])
def test_receipt_and_gate_close_order_does_not_drop_business_answer(tmp_path, monkeypatch, close_before_read):
    gate = _gate_with_last_legal_action()
    if close_before_read:
        gate.close_budget()
    else:
        class DelayedConsumer(Queue):
            def get(self, *args, **kwargs):
                event = super().get(*args, **kwargs)
                gate.close_budget()
                return event
        monkeypatch.setattr(supervisor, 'Queue', DelayedConsumer)
    result, private = _run(tmp_path, gate, 'immediate')
    assert private['answer'] == 'first answer'
    assert result['answerSubmission']['receipt']['receivedAtSeconds'] <= result['answerSubmission']['cutoffSeconds']
    assert json.loads(result['normalized']['finalText'])['taskOutcome'] == 'first answer'


def test_first_submission_cannot_be_replaced_by_later_business_or_cleanup_final(tmp_path):
    result, private = _run(tmp_path, _gate_with_last_legal_action(), 'duplicate')
    assert private['answer'] == 'first answer'
    assert result['answerSubmission']['ignoredFinalMessages'] == 2
    assert result['termination']['reason'] == 'completed'


@pytest.mark.parametrize('business_limited', [False, True])
def test_finalization_is_bounded_and_cleanup_cannot_supply_missing_answer(tmp_path, monkeypatch, business_limited):
    maximum = 0.02 if not business_limited else 120
    monkeypatch.setitem(supervisor.ANSWER_SUBMISSION_PROTOCOL, 'maximumFinalizationSeconds', maximum)
    gate = _gate_with_last_legal_action()
    gate.close_budget()
    result, private = _run(tmp_path, gate, 'no_answer', business=0.05 if business_limited else 5)
    assert private['reason'] == 'no_submission'
    assert private['rawText'] is None
    assert result['normalized']['finalText'] is None
    evidence = result['answerSubmission']
    assert evidence['finalizationDeadlineSeconds'] <= evidence['businessDeadlineSeconds']
    assert evidence['cleanupRequestedAtSeconds'] >= evidence['finalizationDeadlineSeconds']
    assert len([c for c in result['normalized']['toolCalls'] if 'sessionCleanup' in c]) == 1
    assert result['termination']['reason'] == ('business_deadline' if business_limited else 'step_budget')
