# Retro offline queries and actual outputs

Scope: only current campaign cases 058 and 060. These are archival read-only queries and minimal pure causal probes, not a task/score replay, a test suite, or device/Runtime execution. No external modules with device side effects were imported. No original artifacts changed; no temporary scripts created.

## Q1 — bounded stream extraction

Exact code executed (paths relative to repository root). It omits incremental messages, thinking payloads, and screenshots; source event line numbers preserve original receipt identity.

```python
import json
from collections import Counter
from pathlib import Path
C = Path("campaigns/amkernel-0.1.4-r15-current-stack-full-20261109T154403Z")
for episode in ["058-RetroCreatePlaylist", "060-RetroPlaylistDuration"]:
    p = C / "episodes" / episode / "attempt-1"
    result = json.loads((p / "result.json").read_text())
    starts = {}
    states = Counter()
    observations = []
    finals = []
    # Stream one event at a time; do not dump message_update/thinking/base64 content.
    with (p / "raw-private/agent-events.jsonl").open() as stream:
        for line_number, line in enumerate(stream, 1):
            event = json.loads(line)
            if event.get("type") == "tool_execution_start":
                starts[event["toolCallId"]] = (line_number, event.get("args", {}))
            if event.get("type") == "tool_execution_end":
                start_line, args = starts.get(event["toolCallId"], (None, {}))
                if args.get("path") != "xd://mcp__amkernel_python_exec" or not args.get("content"):
                    continue  # Excludes tool-route documentation reads.
                text = next((x["text"] for x in event.get("result", {}).get("content", []) if x.get("type") == "text"), None)
                response = json.loads(text)
                states[(response.get("status"), response.get("kernelState"))] += 1
                value = response.get("result")
                if isinstance(value, dict):
                    for key in ["subtitles", "subtitle", "selection", "options", "titleTexts"]:
                        if key in value:
                            observations.append({"execution": response["executionCount"], "rawLines": [start_line, line_number], "key": key, "value": value[key]})
                    for fact in value.get("facts", []):
                        if str(fact.get("id", "")).endswith("/subtitle"):
                            observations.append({"execution": response["executionCount"], "rawLines": [start_line, line_number], "key": "subtitle", "value": fact.get("t", fact.get("text"))})
            if event.get("type") == "message_end":
                message = event.get("message", {})
                if message.get("role") == "assistant" and message.get("stopReason") == "stop":
                    finals.append({"line": line_number, "text": "".join(x.get("text", "") for x in message.get("content", []) if x.get("type") == "text")})
    print(json.dumps({"episode": episode, "states": {str(k): v for k, v in states.items()}, "actions": dict(Counter(x["kind"] for x in result["stepBudget"]["actions"])), "accepted": result["stepBudget"]["executedActionCount"], "allocated": result["stepBudget"]["maxSteps"], "observations": observations, "firstFinal": finals[0], "cleanupFinalLine": finals[-1]["line"]}, ensure_ascii=False))
```

Actual output:

```jsonl
{"episode": "058-RetroCreatePlaylist", "states": {"('completed', 'alive')": 22, "('failed', 'alive')": 3}, "actions": {"actions": 1, "click": 20, "input": 2}, "accepted": 23, "allocated": 24, "observations": [{"execution": 23, "rawLines": [6249, 6250], "key": "subtitle", "value": "1 Song  •  03:50"}], "firstFinal": {"line": 6630, "text": "{\"taskOutcome\":\"Incomplete: playlist Hip Hop Bangers 270 contains only Dreamer's Awake; the requested three-song order was not established.\"}"}, "cleanupFinalLine": 6723}
{"episode": "060-RetroPlaylistDuration", "states": {"('completed', 'alive')": 28, "('failed', 'alive')": 3}, "actions": {"click": 23, "input": 2, "back": 3, "actions": 2}, "accepted": 30, "allocated": 30, "observations": [{"execution": 18, "rawLines": [5213, 5214], "key": "titleTexts", "value": ["Beyond the Horizon", "City of Stars", "Eternal Flame", "Falling Feathers", "Forever Young", "Golden Days", "Heartbeat Away", "Hidden Paths", "Moonlight Sonata", "Orbiting Stars", "Return to Paradise", "Silent Dreams"]}, {"execution": 22, "rawLines": [6659, 6660], "key": "selection", "value": ["14 selected"]}, {"execution": 25, "rawLines": [7669, 7670], "key": "subtitles", "value": ["14 Songs  •  01:08:25"]}, {"execution": 26, "rawLines": [8559, 8560], "key": "subtitle", "value": ["14 Songs  •  01:08:25"]}, {"execution": 27, "rawLines": [8890, 8891], "key": "selection", "value": ["1 selected"]}, {"execution": 29, "rawLines": [9578, 9579], "key": "selection", "value": ["4 selected"]}, {"execution": 30, "rawLines": [9791, 9794], "key": "options", "value": ["Add to playlist", "Remove from playlist", "Delete from device", "Select all"]}], "firstFinal": {"line": 9855, "text": "{\"taskOutcome\":\"Incomplete: playlist \\\"Reggae Rhythms 51\\\" exists with 14 songs totaling 01:08:25; the 45–50 minute requirement was not reached before the UI action budget was exhausted.\"}"}, "cleanupFinalLine": 9948}
```

Limits: returned top-level summaries, not a complete actual music corpus. Only structured `tool_execution_end` results count as Python execution evidence. A start code computing a value is not proof the value was returned. `titleTexts` has twelve visible rows, not fourteen complete song records. The cleanup final is not the selected business final.

## Q2 — current-source AST and arithmetic

Exact pure code executed:

```python
import ast
from pathlib import Path
m = ast.parse(Path('android_world/android_world/task_evals/single/retro_music.py').read_text())
c = next(n for n in m.body if isinstance(n, ast.ClassDef) and n.name == 'RetroPlaylistDuration')
f = next(n for n in c.body if isinstance(n, ast.FunctionDef) and n.name == 'initialize_task')
print({'direct_calls':[ast.unparse(n.func) for n in ast.walk(f) if isinstance(n,ast.Call)],'contains_super':any(isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id == 'super' for n in ast.walk(f))})
print({'oracle_min_ms':45*60*1000,'oracle_max_ms':50*60*1000,'seeded_target_ms':int(47.5*60*1000),'ui_total_seconds':1*3600+8*60+25,'ui_excess_seconds_over_upper':1*3600+8*60+25-50*60,'ui_over_upper_factor':(1*3600+8*60+25)/(50*60)})
```

Actual output:

```text
{'direct_calls': ['_clear_playlist_dbs', '_generate_list_with_sum', 'zip', '_scan_music_directory', 'int', 'len', 'user_data_generation.write_mp3_file_to_device', 'user_data_generation.write_mp3_file_to_device', 'file_utils.convert_to_posix_path', 'file_utils.convert_to_posix_path', 'random.choice', 'random.choice', 'random.randint', 'file.split', 'file.split'], 'contains_super': False}
{'oracle_min_ms': 2700000, 'oracle_max_ms': 3000000, 'seeded_target_ms': 2850000, 'ui_total_seconds': 4105, 'ui_excess_seconds_over_upper': 1105, 'ui_over_upper_factor': 1.3683333333333334}
```

`seeded_target_ms` is only the source's intended target-partition total, not reconstructed seeded per-song metadata. The duration subclass omits base initialization, which normally resets the PRNG from params.seed. Do not generate benchmark answers from that seed. No actual song durations were reconstructed by this probe.

## Q3 — synthetic locator-shape counterexample

The analysis interpreter had no `lxml` installed (`lxml_available False`); no package was installed. This standard-library fixture implements the broad ancestor/descendant candidate relation and document-order selection. It is **not Appium XPath execution or the missing historical full DOM**.

Exact code executed:

```python
import ast
import xml.etree.ElementTree as ET
from pathlib import Path
# Synthetic two-level container, preserving the historical observed title order.
r = ET.fromstring('''<android.view.ViewGroup id="screen"><android.view.ViewGroup id="list"><android.view.ViewGroup id="dream-row"><title text="Dreamer&apos;s Awake"/><menu id="dream-menu"/></android.view.ViewGroup><android.view.ViewGroup id="golden-row"><title text="Golden Days"/><menu id="golden-menu"/></android.view.ViewGroup><android.view.ViewGroup id="hidden-row"><title text="Hidden Paths"/><menu id="hidden-menu"/></android.view.ViewGroup></android.view.ViewGroup></android.view.ViewGroup>''')
for title in ['Golden Days', "Dreamer's Awake", 'Hidden Paths']:
 candidates = {id(menu):menu for group in r.iter('android.view.ViewGroup') if any(t.get('text')==title for t in group.iter('title')) for menu in group.iter('menu')}
 matches=[e.get('id') for e in r.iter('menu') if id(e) in candidates]
 print({'target':title,'broad_descendant_matches_in_document_order':matches,'first_match':matches[0]})
```

Actual output:

```text
{'target': 'Golden Days', 'broad_descendant_matches_in_document_order': ['dream-menu', 'golden-menu', 'hidden-menu'], 'first_match': 'dream-menu'}
{'target': "Dreamer's Awake", 'broad_descendant_matches_in_document_order': ['dream-menu', 'golden-menu', 'hidden-menu'], 'first_match': 'dream-menu'}
{'target': 'Hidden Paths', 'broad_descendant_matches_in_document_order': ['dream-menu', 'golden-menu', 'hidden-menu'], 'first_match': 'dream-menu'}
```

This falsifies uniqueness of the **selector shape** on a nested repeated-row layout. It does not prove which historical element Appium returned. Historical supporting facts are first-row Dreamer's Awake, three broad selectors, final one-song Dreamer's Awake; full clicked element IDs are absent. Root confidence is probable, not confirmed.

## Q4 — captured malformed verification code

Using `CALLS` extracted from the original start/end events in the analysis kernel:

```python
try:
    compile(CALLS[58][20]['args']['code'], 'captured-cell-21', 'exec')
except SyntaxError as e:
    print({'captured_cell_21_compile': type(e).__name__, 'line': e.lineno, 'message': e.msg})
```

Actual output:

```text
{'captured_cell_21_compile': 'SyntaxError', 'line': 6, 'message': 'unterminated string literal (detected at line 6)'}
```

The archived response already records this failure at raw58 lines5653–5654; this pure compilation establishes that no statements in that cell could run. It is not a rerun of an observed UI failure. The corrected cell22 executes navigation and later times out waiting for all three titles. All accepted-action attribution uses cell22, not the malformed cell21.

## Q5 — action-kind alignment and collection boundary

The structured report's 23/30 action descriptions were aligned in order to the immutable result.stepBudget.actions, then this pure check was executed in the analysis kernel (does not call device or evaluator):

```python
for n, rows in ledger_spec.items():
    print(n, 'action mapping kinds match',
          all(k == a['kind'] for (_, k, _), a in zip(rows, R[n]['stepBudget']['actions'])),
          'count', len(ledgers[n]))
```

Actual output:

```text
58 action mapping kinds match True count 23
60 action mapping kinds match True count 30
```

Action targets remain interpretation from submitted code because sanitized ledger records have kind/path/status only. JSON stores full original toolCall IDs and raw start/end lines. The pure set difference `declared15 - visible12` gave:

```text
['Endless Summer', 'Through the Storm', 'Whispering Wind']
```

The selected-count14 does **not** identify which two of those three are actual offscreen songs, or whether stale music exists. No actual per-song duration observation exists. A zero-length generated segment/media-scan omission is an alternative, not a proven finding.

## Shared checks and provenance

Parent-owned `shared-offline-checks.json` records that both original goals and the initialization-reference clock were present, valid string envelopes parsed exactly to their saved archive, submission hashes matched, and Harness source identity matches the frozen 19-file digest. It does not certify initialized song metadata or final database rows. AndroidWorld oracle byte identity has not independently been proven here beyond result-declared revision. No historical r12 case is used.
