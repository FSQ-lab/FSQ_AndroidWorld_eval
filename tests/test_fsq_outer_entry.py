"""Public CLI watchdog exercised with a real, owned offline child process."""
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import textwrap


def test_public_standalone_bounds_initialization_and_reports_forced_unknown(tmp_path):
    script = textwrap.dedent("""
        import json, os, runpy, subprocess, sys
        from pathlib import Path
        import pytest
        from fsq_androidworld_eval import fsq_runner as runner, fsq_campaign as campaign
        root = Path(sys.argv[1]).resolve()
        fixture = runpy.run_path('tests/test_fsq_runner.py')['offline_episode'].__wrapped__
        patch = pytest.MonkeyPatch()
        execute, _, _ = fixture(root / 'front', patch)
        context = execute.fixture
        context.spec['timeBudget']['episodeSeconds'] = 2.0
        patch.setattr(runner, 'episode_time_budget', lambda _: dict(context.spec['timeBudget']))
        original_spawn = campaign._spawn
        original_popen = subprocess.Popen
        def observe_owned_spawn(*args, **kwargs):
            child = original_popen(*args, **kwargs)
            if kwargs.get('start_new_session'):
                (root / 'owned-child.json').write_text(json.dumps({'pid': child.pid, 'pgid': child.pid}))
            return child
        patch.setattr(subprocess, 'Popen', observe_owned_spawn)
        inner = r'''
        import json, os, runpy, sys, time
        from pathlib import Path
        import pytest
        from fsq_androidworld_eval import fsq_runner as runner, fsq_campaign as campaign
        root = Path(sys.argv[1]).resolve()
        patch = pytest.MonkeyPatch()
        fixture = runpy.run_path('tests/test_fsq_runner.py')['offline_episode'].__wrapped__
        execute, _, _ = fixture(root, patch)
        context = execute.fixture
        context.spec['timeBudget']['episodeSeconds'] = 2.0
        patch.setattr(runner, 'episode_time_budget', lambda _: dict(context.spec['timeBudget']))
        def blocked_initialization(self, env):
            (root.parent / 'initialization-entered.json').write_text(json.dumps({'pid': os.getpid(), 'pgid': os.getpgrp()}))
            time.sleep(60)
        patch.setattr(context.task_type, 'initialize_task', blocked_initialization)
        auth = runner.load_authorization(context.manifest_path, context.manifest, 'smoke', context.authorization)
        auth['resource'].update(exclusive=True, disposable=True, mutationsAllowed=True)
        patch.setattr(runner, 'load_authorization', lambda *args: auth)
        patch.setattr(campaign, '_load_candidate', lambda *args: context.manifest)
        patch.setattr(campaign, 'validate_readiness', lambda *args, **kwargs: {})
        patch.setattr(campaign, 'attest_readiness', lambda *args: None)
        args = campaign.build_parser().parse_args(sys.argv[2:])
        raise SystemExit(campaign._episode(args))
        '''
        def controlled_spawn(command, output, timeout):
            # Bootstrap only fixture admission/environment in the real child,
            # then execute the actual internal operation and outer supervisor.
            return original_spawn([sys.executable, '-B', '-c', inner, str(root / 'inside'), *command[4:]], output, timeout)
        patch.setattr(campaign, '_spawn', controlled_spawn)
        runner.main(['--project', str(root / 'front'), '--manifest', str(context.manifest_path),
            '--task-index', '0', '--output-dir', str(root / 'front' / 'episode'),
            '--authorization', str(context.authorization), '--readiness', str(context.readiness)])
    """)
    root = tmp_path.resolve()
    driver = subprocess.Popen([sys.executable, "-B", "-c", script, str(root)],
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              text=True, start_new_session=True)
    try:
        stdout, stderr = driver.communicate(timeout=15)
        assert driver.returncode == 1, stderr
        assert (root / "initialization-entered.json").exists(), stderr + stdout
        marker = json.loads((root / "initialization-entered.json").read_text())
        terminal = json.loads(stdout.splitlines()[-1])
        assert terminal["classification"] == "invalid_outer_process"
        assert terminal["outerProcess"]["forced"] is True
        assert terminal["outerProcess"]["timeoutSeconds"] == 2.0
        assert terminal["outerProcess"]["termination"]["outerExitObserved"] is True
        assert terminal["cleanupFailure"] is True and terminal["cleanup"] == "unknown"
        state = subprocess.run(["/bin/ps", "-p", str(marker["pid"]), "-o", "stat="],
                               capture_output=True, text=True, check=False).stdout.strip()
        assert not state or state.startswith("Z")
        assert not (root / "front" / "episode" / "raw-private" / "worker-process.json").exists()
    finally:
        # Never use process names or historical device/service PIDs.
        owned = root / "owned-child.json"
        if owned.exists():
            group = json.loads(owned.read_text())["pgid"]
            try:
                os.killpg(group, signal.SIGKILL)
            except ProcessLookupError:
                pass
        if driver.poll() is None:
            os.killpg(driver.pid, signal.SIGKILL)
        driver.wait(timeout=5)
