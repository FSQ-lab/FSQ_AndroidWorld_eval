# Editing-domain offline queries

Campaign: `amkernel-0.1.4-r15-current-stack-full-20261109T154403Z`.

## Offline probes

The following exact Python code was executed read-only in a host Eval cell. It streams raw files to the cited physical line, parses structured PythonResponse, compiles **only** named pure AST functions, and performs collection/string comparisons. It does not import AndroidWorld modules with device side effects or use MCP/Appium/ADB. It writes no files and leaves no temporary script.

The empty `before` and constructed candidate objects isolate the reference-match mechanism; they are not historical DB contents or a substitute score replay. Amount/category candidates come from actual task parameters solely to hold those dimensions constant; actual persisted values remain unproven. Logging is replaced only for the isolated function's warning sink, not its decision logic.

```python
import ast, collections, contextlib, csv, difflib, io, json, pathlib, types
C = pathlib.Path("campaigns/amkernel-0.1.4-r15-current-stack-full-20261109T154403Z")
D = {i: next((C / "episodes").glob(f"{i:03d}-*")) / "attempt-1" for i in (14, 23, 24)}
R = {i: json.loads((d / "result.json").read_text()) for i, d in D.items()}
def response_at(index, physical_line):
    with (D[index] / "raw-private/agent-events.jsonl").open() as f:
        for n, line in enumerate(f, 1):
            if n == physical_line:
                event = json.loads(line)
                assert event["type"] == "tool_execution_end"
                texts = [b["text"] for b in event["result"]["content"] if b["type"] == "text"]
                return json.loads("".join(texts))
    raise ValueError("Missing physical line")
note = response_at(14, 1189)["result"][0]["text"]
rows = list(csv.DictReader(io.StringIO(note), delimiter="|"))
params = R[14]["task"]["params"]
category = {1:"Others",2:"Income",3:"Food",4:"Housing",5:"Social",6:"Entertainment",7:"Transportation",8:"Clothes",9:"Health Care",10:"Education",11:"Donation"}
expected = [(r["name"], f"${r['amount']/100}", category[r["category"]], r["note"] + (". Reimbursable." if target else "")) for target, group in ((True, params["row_objects"]), (False, params["noise_row_objects"])) for r in group]
actual = [(r["name"], r["amount_dollars"], r["category_name"], r["note"]) for r in rows]
print(json.dumps({"dataRows":len(rows),"lineCount":len(note.splitlines()),"terminalNewline":note.endswith("\n"),"completeMultiset":collections.Counter(actual)==collections.Counter(expected),"missing":list((collections.Counter(expected)-collections.Counter(actual)).elements()),"unexpected":list((collections.Counter(actual)-collections.Counter(expected)).elements()),"targets":[dict(noteDataLine=n+2,**r) for n,r in enumerate(rows) if "reimbursable" in r["note"].lower()]}, indent=2))
# Compile only the named pure functions; never execute source imports/device classes.
fpath = pathlib.Path("android_world/android_world/utils/fuzzy_match_lib.py")
fnodes = [n for n in ast.parse(fpath.read_text()).body if isinstance(n, ast.FunctionDef) and n.name == "fuzzy_match"]
fns = {"difflib":difflib,"_MIN_DIFF_SIMILARITY":0.9}
exec(compile(ast.Module(body=fnodes,type_ignores=[]),str(fpath),"exec"), fns)
fuzzy = fns["fuzzy_match"]
vpath = pathlib.Path("android_world/android_world/task_evals/common_validators/sqlite_validators.py")
vnodes = [n for n in ast.parse(vpath.read_text()).body if isinstance(n, ast.FunctionDef) and n.name == "validate_rows_addition_integrity"]
vns = {"sqlite_schema_utils":types.SimpleNamespace(RowType=object),"fuzzy_match_lib":types.SimpleNamespace(fuzzy_match=fuzzy),"logging":types.SimpleNamespace(warning=lambda *a, **k:None)}
exec(compile(ast.Module(body=vnodes,type_ignores=[]),str(vpath),"exec"), vns)
references = params["row_objects"]
# These candidates are constructed from actual parameters + actually typed/reopened notes.
# Full historical DB/category/cents persistence is NOT represented by these synthetic objects.
candidates = [dict(r,note=r["note"]+". Reimbursable.") for r in references]
convert = lambda group: [types.SimpleNamespace(**r) for r in group]
compare = lambda group: vns["validate_rows_addition_integrity"]([],convert(group),convert(references),["name","amount","category","note"],["name","note"])
print(json.dumps({"notes":[{"name":ref["name"],"reference":ref["note"],"observed":cand["note"],"ratio":difflib.SequenceMatcher(None,ref["note"].lower(),cand["note"].lower()).ratio(),"match":fuzzy(ref["note"],cand["note"])} for ref,cand in zip(references,candidates)],"withMarkers":compare(candidates),"withoutMarkers":compare(references)},indent=2))
h = R[23]["task"]["params"]
expected_header = h["header"] + "\n\n" + h["original_content"] + "\n"
observed_header = response_at(23,1887)["result"]["savedField"]
updated = R[24]["task"]["params"]["updated_content"]
observed_updated = response_at(24,2874)["result"]["text"]
print(json.dumps({"expectedHeader":expected_header,"observedHeader":observed_header,"exactHeaderEquality":observed_header==expected_header,"updatedRequested":updated,"observedUpdatedAfterSave":observed_updated,"updatedEquality":observed_updated==updated,"updatedFuzzy":fuzzy(observed_updated.strip(),updated)},indent=2))
for i in (14,23,24):
    budget = R[i]["stepBudget"]
    print(json.dumps({"index":i,"accepted":budget["executedActionCount"],"allocated":budget["maxSteps"],"kinds":dict(collections.Counter(a["kind"] for a in budget["actions"])),"rejectedActionCount":budget["rejectedActionCount"],"exhausted":budget["exhausted"],"closure":budget["closureReason"]},sort_keys=True))
```

### Actual output

```text
{
  "dataRows": 102,
  "lineCount": 103,
  "terminalNewline": false,
  "completeMultiset": true,
  "missing": [],
  "unexpected": [],
  "targets": [
    {
      "noteDataLine": 59,
      "name": "Laundry",
      "amount_dollars": "$96.3",
      "category_name": "Clothes",
      "note": "Urgent. Reimbursable."
    },
    {
      "noteDataLine": 72,
      "name": "Car Insurance",
      "amount_dollars": "$303.01",
      "category_name": "Transportation",
      "note": "I may repeat this. Reimbursable."
    }
  ]
}
{
  "notes": [
    {
      "name": "Laundry",
      "reference": "Urgent",
      "observed": "Urgent. Reimbursable.",
      "ratio": 0.4444444444444444,
      "match": false
    },
    {
      "name": "Car Insurance",
      "reference": "I may repeat this",
      "observed": "I may repeat this. Reimbursable.",
      "ratio": 0.6938775510204082,
      "match": false
    }
  ],
  "withMarkers": false,
  "withoutMarkers": true
}
{
  "expectedHeader": "RnI8sP34yDzJQbvkfplR\n\nWeekend plans: Hiking trip to Blue Mountain.\n",
  "observedHeader": "RnI8sP34yDzJQbvkfplR\n\nWeekend plans: Hiking trip to Blue Mountain.\n",
  "exactHeaderEquality": true,
  "updatedRequested": "inNqu8UNNtyXBHCZpYp7",
  "observedUpdatedAfterSave": "inNqu8UNNtyXBHCZpYp7",
  "updatedEquality": true,
  "updatedFuzzy": true
}
{"accepted": 33, "allocated": 60, "closure": "agent_finished", "exhausted": false, "index": 14, "kinds": {"actions": 4, "back": 2, "click": 18, "input": 6, "mobile: hideKeyboard": 2, "mobile: pressKey": 1}, "rejectedActionCount": 0}
{"accepted": 12, "allocated": 12, "closure": "step_budget", "exhausted": true, "index": 23, "kinds": {"actions": 1, "back": 2, "clear": 1, "click": 6, "input": 1, "mobile: longClickGesture": 1}, "rejectedActionCount": 0}
{"accepted": 11, "allocated": 12, "closure": "agent_finished", "exhausted": false, "index": 24, "kinds": {"back": 1, "clear": 1, "click": 7, "input": 2}, "rejectedActionCount": 0}
```

## Retrieval contract

For every cell quoted in the JSON record, read raw line `timeline.toolCells[].startLine` as `tool_execution_start`, parse `args.content` JSON and use `code` exactly. Read matching `endLine` as `tool_execution_end`, concatenate text blocks under result.content and parse PythonResponse. Full `toolCallId` must match, not only the shortened `call_...` prefix in Markdown. Do not use partial streaming message_update as a terminal result. The JSON report preserves the complete request code and actual bounded structured result/error payload for every Python cell in these three cases.

Initial prompt: physical line9, `message_end` role=user. First business final:014 line6014,023 line3558,024 line3927. Later cleanup finals are intentionally ignored by receipt contract. All initial task/reference-clock/string-contract facts are already independently checked in parent-owned `shared-offline-checks.json`.

## Historical persistence limitations

- 014 reopened both Expense Detail records. This supports app-level stored-record evidence but not category/cents/full-database invariants or post-quit state. `run-full.log:279` directly records the historical missing-Laundry reference, without after rows.
- 023 exact edited string equals source oracle expected including the two LF separator and terminal LF. No post-navigation reopened-content or filesystem read exists; last selected original filename is visible and no rename is attempted.
- 024 replacement exact equality is editor evidence, not filesystem proof. Requested filename is never entered, no rename is attempted, and voluntary stop occurs at11/12 rather than exhaustion.
- Runtime's kernelState stays alive throughout these probes' source event records. No inference from wrong outcome to Runtime failure is justified.
- Current pure source hashes are in `domain-editing.json`; frozen/current19-file harness digest agreement is parent evidence, not an asserted frozen oracle-source equivalence check.
