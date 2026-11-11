# Retrieval offline query receipt

Scope: only campaign `amkernel-0.1.4-r15-current-stack-full-20261109T154403Z`, cases 076/091/106/107. These are isolated read-only queries and pure causal probes, **not device calls, formal task replay, initialized-score reruns, or seed replay**. Original evidence and source files were not mutated. No throwaway scripts were created. Historical screenshot 091 raw line 3606 was decoded in memory and viewed; no new screenshot was captured or stored.

## Evidence indexing

The stream query below is a readable composition of the actual indexing/decoding cells. Line numbers are physical JSONL line numbers; tool IDs in `domain-retrieval.json` retain full originals. Raw starts contain code in `args.content`; raw ends contain actual structured `PythonResponse`. Outer tool completion is never treated as proof of inner success. Image/base64 and thinking payloads are never printed.

Actual raw lengths: 076=1889, 091=3885, 106=5630, 107=4376 events/lines. Actual Python responses: 7/24/19/15 respectively, total65; 9failed inner responses; all65`kernelState=alive`. Skill/schema reads are not Python executions. Actual accepted UI actions3/12/10/8, total33.

```python
import json
from pathlib import Path
C = Path("campaigns/amkernel-0.1.4-r15-current-stack-full-20261109T154403Z")
names = {76:"SimpleCalendarFirstEventAfterStartTime",91:"SportsTrackerTotalDistanceForCategoryOverInterval",
         106:"TasksCompletedTasksForDate",107:"TasksDueNextWeek"}
# Stream one line at a time; never print raw text/image payloads or thinking fields.
raw_events = {}
for i, name in names.items():
    selected = []
    with (C / f"episodes/{i:03d}-{name}/attempt-1/raw-private/agent-events.jsonl").open() as f:
        for line_no, line in enumerate(f, 1):
            e = json.loads(line)
            if e.get("type") in ("tool_execution_start", "tool_execution_end", "message_end"):
                selected.append((line_no, e))
    raw_events[i] = selected

def dec_result(e):
    for item in e.get("result",{}).get("content",[]):
        if item.get("type") != "text": continue
        try: value = json.loads(item.get("text", ""))
        except ValueError: continue
        if isinstance(value,dict) and "status" in value: return value
    return None
calls = {}
for i, events in raw_events.items():
    ends = {e["toolCallId"]:(ln,e) for ln,e in events if e["type"] == "tool_execution_end"}
    calls[i] = []
    for ln,e in events:
        if e["type"] == "tool_execution_start" and e.get("toolName") == "write" and e.get("args",{}).get("path") == "xd://mcp__amkernel_python_exec":
            args = json.loads(e["args"]["content"])
            endln,ee = ends[e["toolCallId"]]
            calls[i].append({"startLine":ln,"endLine":endln,"toolCallId":e["toolCallId"],
                             "code":args["code"],"response":dec_result(ee)})
```

## Pure helper extraction

The executed setup used protobuf5.29.5. Generated descriptor byte literals were obtained via AST; no AndroidWorld module with device imports was imported. Only listed functions were compiled from current source into an isolated namespace with postponed annotations. The fuzzy matcher dependency was represented by the same case-insensitive difflib threshold expression, not a device/mock outcome. This source is current checkout, not independently byte-verified against a frozen AndroidWorld per-file snapshot in this slice.

```python
import ast, types, datetime, difflib, typing
from pathlib import Path
from google.protobuf import descriptor_pool, text_format, message
from google.protobuf.internal import builder
IR = Path("android_world/android_world/task_evals/information_retrieval")
def source_fn(path, name, namespace):
    tree = ast.parse(path.read_text())
    node = next(x for x in tree.body
                if isinstance(x, (ast.FunctionDef, ast.AsyncFunctionDef)) and x.name == name)
    exec(compile(ast.Module(body=[node], type_ignores=[]), str(path), "exec",
                 dont_inherit=True,
                 flags=__import__("__future__").annotations.compiler_flag), namespace)
    return namespace[name]
mods = {}
for kind in ["state", "task"]:
    p = IR / "proto" / f"{kind}_pb2.py"
    tree = ast.parse(p.read_text())
    assignment = next(x for x in tree.body if isinstance(x, ast.Assign)
                      and any(isinstance(t, ast.Name) and t.id == "DESCRIPTOR" for t in x.targets))
    serialized = ast.literal_eval(assignment.value.args[0])
    mod = types.ModuleType(f"offline_{kind}_pb2")
    mod.DESCRIPTOR = descriptor_pool.Default().AddSerializedFile(serialized)
    builder.BuildMessageAndEnumDescriptors(mod.DESCRIPTOR, mod.__dict__)
    builder.BuildTopDescriptorsAndMessages(mod.DESCRIPTOR, mod.__name__, mod.__dict__)
    mods[kind] = mod
pb = mods["task"]
tasksproto = pb.Tasks()
text_format.Merge((IR / "proto/tasks.textproto").read_text(), tasksproto)
templates = {t.name: t for t in tasksproto.tasks}
ns = {"task_pb2": pb, "state_pb2": mods["state"], "message": message,
      "datetime": datetime, "ExpectedAnswer": typing.Any, "Any": typing.Any,
      "Iterator": typing.Iterator,
      "fuzzy_match_lib": types.SimpleNamespace(fuzzy_match=lambda a,b:
          difflib.SequenceMatcher(None, str(a).lower(), str(b).lower()).ratio() >= .9)}
for fn in ["_check_match_types", "_cast_answers_to_type", "_get_field_values",
           "get_expected_answer", "check_agent_answer", "compare"]:
    source_fn(IR / "proto_utils.py", fn, ns)
```

## Pure causal probes

These input facts are either captured UI values, direct nonrandom template binding, structural counts, or an explicitly synthetic comparator fixture. They do not reconstruct an unknown seed sequence. The following readable composition contains the helper calls actually exercised; individual returned values are recorded in the complete receipt below.

```python
# P1: directly bound relevant title; not random initialization or live scoring.
cal = pb.Task()
cal.CopyFrom(templates["SimpleCalendarFirstEventAfterStartTime"])
event = cal.relevant_state.state.calendar.events[0]
event.title = "Grocery Shopping"
event.start_date = "October 29 2023"
event.start_time = "5:20pm"
t = datetime.datetime(2023,10,29,17,20,tzinfo=datetime.timezone.utc)
print({"strictAfter": t > t, "inclusiveAfter": t >= t,
       "oracleExpectedTitles": ns["get_expected_answer"](cal)})

# P2: literal count independent of every substitution, seed, title and due date.
nextweek = templates["TasksDueNextWeek"]
print(ns["get_expected_answer"](nextweek))

# P3: AST-only distance helper and literal name domain.
asrc = ast.parse((IR / "activity_app_utils.py").read_text())
name_map = ast.literal_eval(next(x.value for x in asrc.body if isinstance(x, ast.Assign)
    and any(isinstance(t, ast.Name) and t.id == "_CATEGORY_TO_ACTIVITY_NAMES" for t in x.targets)))
random_names = {name for values in name_map.values() for name in values}
convert = source_fn(IR / "activity_app_utils.py", "_distance_rounding_error_conversion",
                    {"_MILES_TO_METERS": 1609.34})
domain = [float(x) for p in templates["SportsTrackerTotalDistanceForCategoryOverInterval"].task_params
          if p.name == "distance" for x in p.possible_values]
for title, miles in [("Need more strength and conditioning",1.24),("Mindful Movement",2.80)]:
    print(title, title in random_names,
          [(d, convert(d)) for d in domain if round(convert(d)/1609.34,2) == miles])
print({"4000ConvertsTo":convert(4000), "reconstructedSum":convert(2000)+convert(4500)})

# P4: structural missing member; deliberately do not invent the third title.
print({"expectedLength":len(templates["TasksCompletedTasksForDate"].relevant_state.state.tasks_app.tasks_app_tasks),
       "submittedLength":2, "lengthGuardPasses":2 == 3})

# P5: synthetic comparator counterexample, NOT a score rerun of an episode.
mini = pb.Task()
mini.success_criteria.expectations.add(match_type=pb.Expectation.STRING_MATCH,
    field_transformation=pb.FieldTransformation(field_name="title", operation=pb.FieldTransformation.IDENTITY))
for title in ["Plan family reunion","Participate in brainstorming session"]:
    mini.relevant_state.state.tasks_app.tasks_app_tasks.add(title=title)
print(ns["get_expected_answer"](mini))
print(ns["check_agent_answer"]("Plan family reunion, Plan family reunion", mini))
```

## Complete next-week inventory

Captured windows are raw ends L2437/L3055/L3320/L3581 (first window is taken from cell7 before-scroll result). Longest overlaps5,3,6; total26. The original implementation includes `Mon` in its label set. An intermediate analyst calculation accidentally omitted `Mon` and gave19/13; this was corrected to the exact captured predicate before reporting20/14. This is a query-composition correction, not new device evidence or reward repricing.

```python
# Four actual captured windows; this recomputes collection stitching, not a task/score.
r107 = calls[107]
windows = [r107[6]["response"]["result"]["before"],
           r107[9]["response"]["result"]["after"],
           r107[10]["response"]["result"]["after"],
           r107[11]["response"]["result"]["after"]]
def rowkey(r): return (r["title"],r["description"],r["due"])
def joinwindows(a,b):
    overlaps = [n for n in range(1,min(len(a),len(b))+1)
                if [rowkey(r) for r in a[-n:]] == [rowkey(r) for r in b[:n]]]
    n = max(overlaps, default=0)
    return a+b[n:], n
rows = windows[0]
overlaps = []
for w in windows[1:]: rows,ov = joinwindows(rows,w); overlaps.append(ov)
tsrc = ast.parse((IR / "task_app_utils.py").read_text())
noise = ast.literal_eval(next(x.value for x in tsrc.body if isinstance(x,ast.Assign)
    and any(isinstance(t,ast.Name) and t.id == "_TASKS" for t in x.targets)))
seed_titles = set(next(p.possible_values for p in templates["TasksDueNextWeek"].task_params if p.name == "title"))
labels = {"Tmrw","Mon","Tue","Wed","Thu","Fri","Sat","Oct 22"}  # EXACT Agent code predicate
members = [r for r in rows if r["title"] in seed_titles]
print({"mergedRows":len(rows),"overlaps":overlaps,
       "corpusIntersection":sorted(seed_titles.intersection(noise)),
       "agentCount":sum(r["due"] in labels for r in rows),"correctCount":len(members),
       "falsePositives":sum(r["due"] in labels and r["title"] not in seed_titles for r in rows)})
```

## Pure probe results

The final exact executed receipt-print code, operating on the probe outputs above, was:

```python
print(json.dumps(probes, ensure_ascii=False, indent=2))
```

Actual output:

```json
{
  "calendarBoundary": {
    "capturedTitle": "Grocery Shopping",
    "eventStart": "2023-10-29T17:20:00+00:00",
    "strictAfter": false,
    "inclusiveAfter": true,
    "oracleExpectedTitles": [
      "Grocery Shopping"
    ],
    "capturedNextDay": "Appointment for Budget Planning @ 2023-10-30 08:35",
    "limitation": "Not an inventory of 75 random events or a recomputed strict-after first event."
  },
  "tasksNextWeekCount": {
    "relevantRows": 6,
    "expectedCountFromUninstantiatedStructure": [
      6
    ],
    "referenceWeekday": "Sunday",
    "start": "2023-10-16",
    "end": "2023-10-22",
    "limitation": "Count only; no seeded membership replay."
  },
  "sportsConversion": {
    "observedSeededNameCandidates": [
      {
        "name": "Need more strength and conditioning",
        "inRandomNameCorpus": false,
        "displayMiles": 1.24,
        "matchingInputMeters": [
          2000.0
        ],
        "convertedMeters": [
          1996
        ]
      },
      {
        "name": "Mindful Movement",
        "inRandomNameCorpus": false,
        "displayMiles": 2.8,
        "matchingInputMeters": [
          4500.0
        ],
        "convertedMeters": [
          4506
        ]
      }
    ],
    "capturedInputParameter4000ConvertsTo": 4007,
    "reconstructedSum": 6502,
    "distanceFromSubmitted1996": 4506,
    "strictTolerance": 10,
    "limitation": "Seeded-row identification is source/captured-title inference, not raw database dump; category and exact 06:15 second-row date shown as Monday only."
  },
  "completedListCardinality": {
    "templateRelevantRows": 3,
    "submittedTitles": [
      "Participate in brainstorming session",
      "Plan family reunion"
    ],
    "submittedCount": 2,
    "oracleLengthGuardPasses": false,
    "missingTitlesCount": 1,
    "thirdTitle": "uncaptured"
  },
  "listComparatorDuplicateProbe": {
    "syntheticExpected": [
      "Plan family reunion",
      "Participate in brainstorming session"
    ],
    "syntheticSubmitted": "Plan family reunion, Plan family reunion",
    "actualCheckAgentAnswerReturn": true,
    "relationToCampaignFailure": "Latent false-positive comparator weakness, NOT cause of a 2-vs-3 rejection."
  },
  "nextWeekMembershipReconstruction": {
    "mergedRows": 26,
    "overlaps": [
      5,
      3,
      6
    ],
    "seedRandomCorpusIntersection": [],
    "correctMembers": [
      {
        "ordinal": 12,
        "title": "Follow up on support tickets",
        "due": "Tmrw",
        "normalizedDueDateInferred": "2023-10-16"
      },
      {
        "ordinal": 13,
        "title": "Plan family reunion",
        "due": "Tue",
        "normalizedDueDateInferred": "2023-10-17"
      },
      {
        "ordinal": 14,
        "title": "Book flights for conference",
        "due": "Wed",
        "normalizedDueDateInferred": "2023-10-18"
      },
      {
        "ordinal": 15,
        "title": "Research market trends",
        "due": "Fri",
        "normalizedDueDateInferred": "2023-10-20"
      },
      {
        "ordinal": 16,
        "title": "Send report to manager",
        "due": "Sat",
        "normalizedDueDateInferred": "2023-10-21"
      },
      {
        "ordinal": 17,
        "title": "Organize files and folders",
        "due": "Oct 22",
        "normalizedDueDateInferred": "2023-10-22"
      }
    ],
    "agentLabelCount": 20,
    "sourceAndCapturedFactCount": 6,
    "wronglyIncludedDistractors": 14,
    "limitations": "Absolute random due dates use default 14-day generator bounds Oct8 15:34 through Oct22 15:33 UTC and exclusions Oct16–22; exact due times and DB row IDs uncaptured."
  }
}
```

## Limits

- 076 oracle target at the equality boundary is computable without replay; strict-after complete answer and date scope are not established by a next-day candidate.
- 091 6502 m is a **probable source/display reconstruction** using both template-only names and unique distance-domain mapping. No initialized sports proto/DB snapshot or second detail/category read is archived. The primary symptom—single observed contribution submitted as total—is directly captured.
- 106 expected cardinality3 is computable; exact third title is uncaptured. Params title is explicitly not a replacement for it.
- 107 literal expected count6 is computable; full26-row membership/date reconstruction uses captured windows plus disjoint generator corpora, bounded random time window and exclusions. Absolute random due times/DB row IDs are missing.
- The synthetic duplicate-list acceptance is a latent false-positive comparator defect, not the cause of the observed two-versus-three failure.
- No reward has been recomputed or repriced. Parent `shared-offline-checks.json` holds independent first-final/parse/receipt/hash checks and the frozen Harness source digest comparison.
