# Notes domain: reproducible offline queries

Campaign: `amkernel-0.1.4-r15-current-stack-full-20261109T154403Z`.

## Method and safety

The query below was executed with host Python through `functions.eval`, not the AMKernel/device tool. It streams the two original raw JSONL logs once per execution, joins `tool_execution_start` and `tool_execution_end` by **full** toolCallId, decodes only the structured PythonResponse text for `write` calls whose args.path is `xd://mcp__amkernel_python_exec`, and prints bounded selected business facts. The short ID printed is only a display anchor; `domain-notes.json` retains full IDs and original source code. Target-document `read` calls are deliberately excluded from execution counts. No base64/image bytes, full page source, logs, or unrelated private data are emitted.

This is evidence decoding and a minimal pure-string causal probe, not a task, score, or test rerun. No Appium, ADB, MCP, AndroidWorld environment modules, device APIs, or evaluator are invoked. No temporary script file is needed. The official original evidence is not changed. `len(encode())` and shape/fuzzy comparisons below apply to **captured editor readback**, not to uncaptured filesystem bytes at evaluation.

## Exact executed query

```python
import collections, difflib, json, pathlib
C = pathlib.Path("campaigns/amkernel-0.1.4-r15-current-stack-full-20261109T154403Z")
for index, name in [(30, "MarkorDeleteNewestNote"), (33, "MarkorMergeNotes")]:
    p = C / "episodes" / f"{index:03}-{name}" / "attempt-1"
    result = json.loads((p / "result.json").read_text())
    starts, calls = {}, []
    with (p / "raw-private/agent-events.jsonl").open() as stream:
        for line_number, line in enumerate(stream, 1):
            event = json.loads(line)
            if event.get("type") == "tool_execution_start":
                starts[event["toolCallId"]] = (line_number, event)
            elif event.get("type") == "tool_execution_end":
                start_line, start = starts.pop(event["toolCallId"])
                if start.get("toolName") != "write" or start.get("args", {}).get("path") != "xd://mcp__amkernel_python_exec":
                    continue
                args = json.loads(start["args"]["content"])
                # Only the structured PythonResponse text; never print images/base64.
                text = next(item["text"] for item in event["result"]["content"] if item.get("type") == "text")
                response = json.loads(text)
                calls.append({"startLine": start_line, "endLine": line_number,
                              "toolCallId": event["toolCallId"].split("|")[0],
                              "code": args["code"], "response": response})
    budget = result["stepBudget"]
    record = {"index": index, "reward": result["officialReward"],
              "termination": result["agent"]["termination"]["reason"],
              "allocated": budget["maxSteps"], "consumed": budget["executedActionCount"],
              "referenceSteps": budget["referenceStepsExecuted"],
              "actionKinds": dict(collections.Counter(a["kind"] for a in budget["actions"])),
              "pythonStatuses": dict(collections.Counter(c["response"]["status"] for c in calls)),
              "kernelStates": dict(collections.Counter(c["response"]["kernelState"] for c in calls)),
              "proxyDenied": result["appiumSessionAudit"]["deniedCommandCount"],
              "gateRejected": budget["rejectedActionCount"],
              "businessReceiptLine": result["agent"]["answerSubmission"]["receipt"]["eventSequence"]}
    if index == 30:
        elements = calls[4]["response"]["result"]["elements"]
        rows = []
        for i, element in enumerate(elements):
            if element.get("desc", "").startswith("File "):
                rows.append({"filename": elements[i+1]["text"], "displayedTime": elements[i+2]["text"]})
        record["initialVisibleNoteRows"] = rows
        record["failedCells"] = [{"call": i+1, "endLine": c["endLine"], "type": c["response"]["error"]["type"], "message": c["response"]["error"]["message"]} for i, c in enumerate(calls) if c["response"]["status"] == "failed"]
        record["lastMutation"] = {"endLine": calls[14]["endLine"], "result": calls[14]["response"]["result"]}
        record["postMutationObservation"] = {"endLine": calls[15]["endLine"], "result": calls[15]["response"]["result"]}
    else:
        source = calls[5]["response"]["result"]["texts"]
        readback = calls[9]["response"]["result"]
        params = result["task"]["params"]
        expected = "\n\n".join(params[f"file{i}_content"] for i in [1,2,3]) + "\n"
        actual = readback["readback"]
        lines = actual.replace("\r", "").strip().split("\n")
        ratio = difflib.SequenceMatcher(None, actual.replace("\r", "").strip().lower(), expected.lower()).ratio()
        record["sourceResponseLine"] = calls[5]["endLine"]
        record["sourceTexts"] = source
        record["persistedResponseLine"] = calls[9]["endLine"]
        record["persistedResult"] = readback
        record["purePredicateProbe"] = {"oracleExactName": params["new_file_name"],
            "observedListedName": readback["listedAs"],
            "actualBytes": len(actual.encode()), "oracleExpectedBytes": len(expected.encode()),
            "oracleExpectedText": expected, "constructMatchesReadback": actual == "".join(source),
            "exactContentMatch": actual == expected, "postStripLines": lines,
            "strictBlankLinePredicate": len(lines) == 5 and not lines[1] and not lines[3],
            "fuzzyRatio": ratio, "fuzzyPassAt0_9": ratio >= 0.9}
    print(json.dumps(record, indent=2))
```

## Actual output

```json
{
  "index": 30,
  "reward": 0.0,
  "termination": "step_budget",
  "allocated": 10,
  "consumed": 10,
  "referenceSteps": 10,
  "actionKinds": {
    "mobile: activateApp": 1,
    "click": 5,
    "back": 3,
    "actions": 1
  },
  "pythonStatuses": {
    "completed": 13,
    "failed": 4
  },
  "kernelStates": {
    "alive": 17
  },
  "proxyDenied": 1,
  "gateRejected": 0,
  "businessReceiptLine": 3678,
  "initialVisibleNoteRows": [
    {
      "filename": "final_friendly_king.md",
      "displayedTime": "10/15/2023, 15:34"
    },
    {
      "filename": "fine_jelly_final.md",
      "displayedTime": "10/15/2023, 15:17"
    }
  ],
  "failedCells": [
    {
      "call": 2,
      "endLine": 604,
      "type": "ModuleNotFoundError",
      "message": "No module named 'lxml'"
    },
    {
      "call": 7,
      "endLine": 1620,
      "type": "selenium.common.exceptions.TimeoutException",
      "message": ""
    },
    {
      "call": 12,
      "endLine": 2844,
      "type": "selenium.common.exceptions.UnknownMethodException",
      "message": "Only a single native touch pointer is supported"
    },
    {
      "call": 14,
      "endLine": 3250,
      "type": "TypeError",
      "message": "PointerActions.move_to_location() got an unexpected keyword argument 'duration'"
    }
  ],
  "lastMutation": {
    "endLine": 3419,
    "result": {
      "admitted": true
    }
  },
  "postMutationObservation": {
    "endLine": 3554,
    "result": {
      "activity": ".activity.MainActivity",
      "deleted": true,
      "remainingNewestPresent": false,
      "visibleTexts": []
    }
  }
}
{
  "index": 33,
  "reward": 0.0,
  "termination": "completed",
  "allocated": 78,
  "consumed": 17,
  "referenceSteps": 18,
  "actionKinds": {
    "mobile: activateApp": 1,
    "click": 8,
    "back": 5,
    "clear": 1,
    "input": 2
  },
  "pythonStatuses": {
    "completed": 11
  },
  "kernelStates": {
    "alive": 11
  },
  "proxyDenied": 0,
  "gateRejected": 0,
  "businessReceiptLine": 2543,
  "sourceResponseLine": 1233,
  "sourceTexts": [
    "m4kMyOGWaENoPj6FqLjd\n",
    "fxHXZsqrmnwYjXvte9pg\n",
    "f42GOjFWb2aKHogAFQSY\n"
  ],
  "persistedResponseLine": 2502,
  "persistedResult": {
    "listedAs": "mIObBbo4.md",
    "title": "mIObBbo4",
    "readback": "m4kMyOGWaENoPj6FqLjd\nfxHXZsqrmnwYjXvte9pg\nf42GOjFWb2aKHogAFQSY\n",
    "expected": "m4kMyOGWaENoPj6FqLjd\nfxHXZsqrmnwYjXvte9pg\nf42GOjFWb2aKHogAFQSY\n",
    "persistedMatch": true
  },
  "purePredicateProbe": {
    "oracleExactName": "mIObBbo4",
    "observedListedName": "mIObBbo4.md",
    "actualBytes": 63,
    "oracleExpectedBytes": 65,
    "oracleExpectedText": "m4kMyOGWaENoPj6FqLjd\n\nfxHXZsqrmnwYjXvte9pg\n\nf42GOjFWb2aKHogAFQSY\n",
    "constructMatchesReadback": true,
    "exactContentMatch": false,
    "postStripLines": [
      "m4kMyOGWaENoPj6FqLjd",
      "fxHXZsqrmnwYjXvte9pg",
      "f42GOjFWb2aKHogAFQSY"
    ],
    "strictBlankLinePredicate": false,
    "fuzzyRatio": 0.9763779527559056,
    "fuzzyPassAt0_9": true
  }
}
```

## Pure merge predicate probe

The final `purePredicateProbe` above is the bounded helper-equivalent probe. Current source predicates:

- `android_world/android_world/task_evals/common_validators/file_validators.py:199-226`: exact filename presence first, then `fuzzy_match`.
- `android_world/android_world/utils/fuzzy_match_lib.py:20-51`: case-insensitive `difflib.SequenceMatcher(...).ratio() >= 0.9`.
- `android_world/android_world/task_evals/single/markor.py:603-638`: only after CreateFile passes, remove CR, strip, split LF, require exactly five lines with empty indices 1 and 3.

Result: the reopened text has 63 UTF-8 bytes versus the constructed oracle target's 65 bytes; fuzzy similarity would pass (0.9763779527559056), but the strict blank-line condition fails. This does **not** show that the strict gate ran in the actual official evaluation: the observed `.md` filename probably failed the earlier exact-path gate. No unobserved `cat`/`find` output is inferred.

## Current source provenance

The campaign records AndroidWorld revision `55ddaf5edc6f6c25673aed343907d5b9dca66f84`, package version `0.1.0`, Harness revision 15. The inspected current task/helper hashes were computed read-only:

- `android_world/android_world/task_evals/single/markor.py`: `183d3763e34ede196c0df795235ab3aa79d434d744da54aefb82bfd753a93340`
- `android_world/android_world/utils/file_utils.py`: `5bd04ccdafba65f4b909c8bb9fca166e5eba92dc2e64c83f80729941dfab2d1d`
- `android_world/android_world/task_evals/common_validators/file_validators.py`: `ce7137e22fe94d25a6ebdf1fdd8bf0cf327ed20907af48a2f2ee34ca6b13bf20`
- `android_world/android_world/task_evals/utils/user_data_generation.py`: `7dd456f18429668d0dfd48f3ddcdc4134b1a26f66cbe84ad0d85bbc902cb9c7b`
- `android_world/android_world/utils/datetime_utils.py`: `32594fcd09e038467166678c7894b649f32c3a815f054b5d85c0fdb69b9d6e81`
- `android_world/android_world/utils/fuzzy_match_lib.py`: `e7376554fd9a413ff00d71656e09609c9070d0b384028b89fd931e32fcfb2969`

No separately recovered frozen AndroidWorld per-file digest was compared here. The parent's `shared-offline-checks.json` records its independent current/frozen **Harness** source digest comparison and first-final/answer-parser checks; do not extend that to unverified AndroidWorld source files.

## Metadata semantics source

Current `file_utils.py:60-74` describes `change_time` as ctime, but `get_file_list_with_metadata:519-520` asks for `ls ... -ll -au`. Upstream Toybox source/help explicitly identifies `-u` as atime and says long output uses `-cu` for display:

<https://raw.githubusercontent.com/landley/toybox/master/toys/posix/ls.c>

This external source was read statically; it is not an emulator binary check. An Android13 googlesource fetch timed out before the upstream read succeeded. No device shell was used. Exact emulator `ls` version, mount atime behavior, and original per-file initial/final timestamps remain unknown; the episode's reward cannot be attributed to this source-level mismatch alone.

## Missing-evidence search boundary

The formal attempt directories contain only `result.json`, `normalized-agent-events.json`, `raw-private/business-submission.json`, `raw-private/agent-events.jsonl` and empty stderr. Their original Python code returns UI facts, not file metadata/inventories. The same campaign's per-task rehearsal records (`harness-rehearsal/tasks/030-MarkorDeleteNewestNote/result.json:1-18,65-68` and case033 equivalent) contain an initial-state probe 0.0 and matching params hashes, but no file list/timestamps and no Agent execution. They are separate initializations, not missing formal-attempt persistence snapshots. Recovery receipts are service/session attestations; the case030 pre-recovery receipt confirms Markor2.10.9/API33/UTC, not note files.

No initialization RNG replay was used to manufacture missing file timestamps or final content. No historical failure was re-executed to confirm it. Final filesystem, source-file mtimes, and any final Markor DB remain unknown.
