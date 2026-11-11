# Media diagnosis: reproducible offline queries

Campaign: `amkernel-0.1.4-r15-current-stack-full-20261109T154403Z` only.

These are offline reads and pure causal probes, not task/score reruns or tests. No AndroidWorld environment module is imported, and no ADB, Appium, MCP, device, build, formatter or test command was run. The two pure helpers were extracted by AST into isolated namespaces. The playlist probe uses UI-derived hypothetical rows, **not the original database**. Current source provenance remains as described in `domain-media.md`.

## Streamed event extraction

The following standalone code reproduces the extraction and the pure outputs. It stores only selected tool starts/ends, never dumps logs or image payloads. A documentation-only `read` of the `python_exec` route has no `content` key and must not be counted as execution.

```python
import ast, collections, difflib, json, pathlib, types
C = pathlib.Path("campaigns/amkernel-0.1.4-r15-current-stack-full-20261109T154403Z")
for case in ["001-AudioRecorderRecordAudioWithFileName", "036-MarkorTranscribeVideo", "115-VlcCreateTwoPlaylists"]:
    p = C / "episodes" / case / "attempt-1"
    r = json.loads((p / "result.json").read_text())
    starts, ends = {}, {}
    with (p / "raw-private/agent-events.jsonl").open() as stream:
        for line_no, line in enumerate(stream, 1):
            event = json.loads(line)
            if event.get("type") == "tool_execution_start":
                args = event.get("args", {})
                if args.get("path") == "xd://mcp__amkernel_python_exec" and "content" in args:
                    starts[event["toolCallId"]] = (line_no, json.loads(args["content"]))
            elif event.get("type") == "tool_execution_end" and event["toolCallId"] in starts:
                ends[event["toolCallId"]] = (line_no, event)
    print(case, "reward", r["officialReward"], "accepted", r["stepBudget"]["executedActionCount"],
          "max", r["stepBudget"]["maxSteps"], "reference", r["stepBudget"]["referenceStepsExecuted"],
          "exhausted", r["stepBudget"]["exhausted"], "closure", r["stepBudget"]["closureReason"])
    print("kinds", dict(collections.Counter(a["kind"] for a in r["stepBudget"]["actions"])))
    print("pairs", [(n, start, ends[call][0]) for n, (call, (start, _)) in enumerate(starts.items(), 1)])
    # Inspect any selected original cell without printing images/base64/full trees:
    # n = 24  # choose a case-specific executionCount from domain-media.json
    # call, (start, args) = list(starts.items())[n-1]
    # end_no, event = ends[call]
    # response = json.loads(next(q["text"] for q in event["result"]["content"] if q["type"] == "text"))
    # print(args["code"])
    # print({k: response.get(k) for k in ["status", "kernelState", "result", "error"]})

# Extract only pure functions; do not import task/environment modules.
root = pathlib.Path("android_world/android_world")
f = root / "utils/fuzzy_match_lib.py"
node = next(n for n in ast.parse(f.read_text()).body if isinstance(n, ast.FunctionDef) and n.name == "fuzzy_match")
ns = {"difflib": difflib, "_MIN_DIFF_SIMILARITY": 0.9}
exec(compile(ast.Module(body=[node], type_ignores=[]), str(f), "exec"), ns)
actual, expected = "Moria, Charlotte, Emilia", "Maria,Charlotte,Emilia"
print("fuzzy", difflib.SequenceMatcher(None, actual.lower(), expected.lower()).ratio(), ns["fuzzy_match"](actual, expected))
print("audio target", "presentation_fGwr.m4a" + ".m4a")
f = root / "task_evals/common_validators/sqlite_validators.py"
node = next(n for n in ast.parse(f.read_text()).body if isinstance(n, ast.FunctionDef) and n.name == "verify_playlist")
ns2 = {"sqlite_schema_utils": types.SimpleNamespace(PlaylistInfo=object),
       "fuzzy_match_lib": types.SimpleNamespace(fuzzy_match=ns["fuzzy_match"])}
exec(compile(ast.Module(body=[node], type_ignores=[]), str(f), "exec"), ns2)
p = json.loads((C / "episodes/115-VlcCreateTwoPlaylists/attempt-1/result.json").read_text())["task"]["params"]
observed = [p["files2"][i] for i in [0,1,3,2]]
rows = [types.SimpleNamespace(playlist_name=p["playlist_name2"], media_file_name=name, order_in_playlist=i)
        for i,name in enumerate(observed)]
print("Adventure positions", [a == b for a,b in zip(observed, p["files2"])])
print("UI-derived rows only", ns2["verify_playlist"](rows, p["playlist_name2"], p["files2"]))
print("possible component pairs", [(a,b) for a in [0,1] for b in [0,1] if (a+b)/2 == 0.5])
```

### Actual extraction outputs

- `001-AudioRecorderRecordAudioWithFileName`: reward `0.0`; accepted `9` / `20`; reference `10`; exhausted `False`; closure `agent_finished`. Kinds `{'click': 6, 'input': 2, 'clear': 1}`.
  - Execution-count → raw start/end lines: 1→442/443, 2→747/748, 3→980/981, 4→1306/1307, 5→1579/1580, 6→1852/1853, 7→2190/2191, 8→2467/2468, 9→3074/3075, 10→3439/3440, 11→3614/3615.
- `036-MarkorTranscribeVideo`: reward `0.0`; accepted `20` / `20`; reference `20`; exhausted `True`; closure `step_budget`. Kinds `{'actions': 3, 'click': 11, 'mobile: pressKey': 1, 'clear': 2, 'input': 3}`.
  - Execution-count → raw start/end lines: 1→319/320, 2→602/603, 3→805/808, 4→1005/1006, 5→1263/1264, 6→1503/1504, 7→1888/1889, 8→2388/2390, 9→2636/2637, 10→2931/2934, 11→3397/3400, 12→3863/3865, 13→4250/4251, 14→4574/4575, 15→4821/4822, 16→4999/5000, 17→5234/5235, 18→5466/5467, 19→5633/5634, 20→5906/5907, 21→6307/6308, 22→6509/6510, 23→6873/6874, 24→7301/7304, 25→7433/7434.
- `115-VlcCreateTwoPlaylists`: reward `0.5`; accepted `46` / `48`; reference `47`; exhausted `False`; closure `agent_finished`. Kinds `{'actions': 3, 'click': 37, 'input': 3, 'back': 3}`.
  - Execution-count → raw start/end lines: 1→312/313, 2→581/582, 3→759/760, 4→1017/1018, 5→1246/1247, 6→1428/1429, 7→1753/1754, 8→1956/1957, 9→2121/2122, 10→2303/2304, 11→2555/2556, 12→3001/3002, 13→3262/3263, 14→3543/3544, 15→3842/3843, 16→4012/4013, 17→4330/4331, 18→4634/4635, 19→4851/4852, 20→5169/5170, 21→5642/5643, 22→5792/5793, 23→6022/6023, 24→6288/6289, 25→6527/6528, 26→6763/6764, 27→7007/7008, 28→7258/7259, 29→7442/7443, 30→7651/7652, 31→7889/7890, 32→8367/8368, 33→8578/8579.

The semantic ledgers in `domain-media.json` map every accepted action, in order, to its cell and full toolCallId. This reconstruction was checked offline against each original `result.stepBudget.actions` kind sequence: all three matched exactly (9, 20 and 46 entries). That is an analysis consistency check, not an app/test replay. A locator/import failure before any forwarded mutation is not counted. Unsupported gesture authorization failures are not ActionGate rejections.

## Pure oracle probes

Actual outputs:

```text
fuzzy 0.9130434782608695 True
audio target presentation_fGwr.m4a.m4a
Adventure positions [True, True, False, False]
UI-derived rows only False
possible component pairs [(0, 1), (1, 0)]
```

Interpretation and limits:

- The original saved Markor UI string (`Moria, Charlotte, Emilia`) passes the **current content helper**, despite the Maria typo and spaces. This does not read a file, prove persistence, or prove that the historical evaluator reached content comparison.
- The Audio oracle target concatenation is deterministic. It proves contract inconsistency in the reviewed source, not which physical recorder path existed.
- The Adventure probe assumes extension-hidden UI stems correspond to exact `.mp4` DB names and that displayed order corresponds to zero-based DB positions. Neither is captured as SQLite evidence. It illustrates the predicate mismatch; it does not identify the historically failing component by itself.
- Reward 0.5 algebra proves exactly one Boolean component passed given the reviewed implementation. `Ultimate=1, Adventure=0` is probable from UI/actions, not an archived component result.

## Retained video image

The only complete later-frame contact sheet needed here is already in raw end event line 3865 (also toolResult message line3867), call `call_G4Ujy9Ssgwn0gsQGcxzH57em`. This code inspects it without saving new evidence:

```python
# Continues with imports and C from the prior block. Reads retained bytes only.
import base64, hashlib, io
from PIL import Image
path = C / "episodes/036-MarkorTranscribeVideo/attempt-1/raw-private/agent-events.jsonl"
with path.open() as stream:
    for line_no, line in enumerate(stream, 1):
        if line_no != 3865:
            continue
        event = json.loads(line)
        item = next(q for q in event["result"]["content"] if q["type"] == "image")
        assert "…" not in item["data"]  # earlier PNGs are explicitly RPC-elided; do not fabricate them
        data = base64.b64decode(item["data"])
        print(len(data), hashlib.sha256(data).hexdigest())
        image = Image.open(io.BytesIO(data))
        print(image.size)
        # In a notebook/Eval image-capable output: display/print(image).
        # Do not write to original evidence or decode incomplete earlier PNGs as complete frames.
        break
```

Actual output:

```text
338307 ccc6e9dbda2ce40d678c27f09b500bbd53eebff94573c1eb3b7bb0bc87e16782
(1140, 1320)
```

Actual visual interpretation: top-left two samples (original indices16 and18, loop-relative10.30s and11.49s) show **Emilia**. Sample20 at12.89s and all later even samples through36 at22.59s show the VLC library/noise-video thumbnails, not additional target messages. These are elapsed times since the second sampling loop began, **not playback positions**. No seek/replay/reset occurred between the two loops.

Earlier image evidence is incomplete in the immutable event stream: call8's four PNG strings each contain `…[... chars elided for RPC frame]`; call10's single PNG is similarly elided; call11 declares five display metadata entries but retains only two image payloads, both elided. Attempting to base64-decode an elided earlier payload failed with `ValueError: string argument should contain only ASCII characters`; this led to using only the complete call12 JPEG. No pixel repair, regenerated video, OCR guess or invented Maria/Charlotte observation was substituted. The app's exact24second video description is observed in call6;320x240/30fps/mp4v are source-generation settings, not measured historical media metadata.

## Submission and cleanup boundary

The parent-owned `shared-offline-checks.json` records actual contract/receipt checks for all 20 failures. For these three, first business final lines are3539/7345/8499; parsed `taskOutcome` values are original strings and match archived diagnostics. The selected submissions precede cleanup; subsequent cleanup finals cannot replace them. `parse_submission` only strips outer string whitespace. These tasks are not InformationRetrieval, so final prose does not become file/database oracle input.

`runner.py:716-737` finishes business/cleanup and owns session cleanup before evaluator lines790-796; task teardown starts822after evaluation. Dedicated cleanup cells here contain only `driver.quit()`, not restores/deletes/resets. There is no post-quit filesystem/DB snapshot, so persistence effects of quit are not directly measured. Later task teardown cannot explain the earlier score. Parent receipt also establishes current harness source digest matches the frozen harness; this is not a byte-level comparison of every AndroidWorld task source.
