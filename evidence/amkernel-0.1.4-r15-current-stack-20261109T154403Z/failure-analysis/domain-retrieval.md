# Retrieval failure analysis

Campaign: `amkernel-0.1.4-r15-current-stack-full-20261109T154403Z` only. Scope: cases 076,091,106,107. This is diagnosis, not a product/config/test modification. Historical official rewards remain unchanged.

## Findings at a glance

| Case | Recorded answer / reward | Strongest finding | Root confidence |
|---|---|---|---|
|076 SimpleCalendarFirstEventAfterStartTime|Appointment for Budget Planning /0|Template inserts expected Grocery Shopping **at**17:20 but asks for first event **after**17:20. The Agent excludes equality and opens next day; that does not prove complete or date-scoped correctness.|Confirmed oracle wording/generation inconsistency; strict-after answer correctness unknown|
|091 SportsTrackerTotalDistanceForCategoryOverInterval|1996 /0|1996 is one1.24mi activity, not the total of both captured template-only candidates. Second2.80mi contribution implies probable6502m total, after per-row initialization conversion.|Confirmed single-item answer and missing coverage; exact total probable source/display reconstruction|
|106 TasksCompletedTasksForDate|Participate in brainstorming session, Plan family reunion /0, step_budget|Two items submitted against three relevant title slots; third title never captured. Misnavigation, filter ambiguity, ineffective gestures and policy-denied compounds prevent full collection.|Confirmed cardinality rejection; precise completed-toggle state probable/unknown|
|107 TasksDueNextWeek|20 /0|All26rows reconstructed, but weekday-string predicate wrongly includes14past-week distractors. Literal oracle count is6; six actual source/captured members identified without seed replay.|Confirmed authored-predicate defect; absolute noise dates source-derived, not DB readback|

Full structured records—including exact params, goal, full toolCall IDs, every Python cell's original request code, inner status, action ledger, root/fix separation and unknowns—are in `domain-retrieval.json`. Reproducible read-only query code, actual pure-probe outputs and limitations are in `domain-retrieval-queries.md`.

## Shared mechanism, provenance and limits

- Official tasks are dynamic classes registered from `information_retrieval_registry.py:51-112`. `InformationRetrieval.__init__` copies the task template and sets complexity from the proto (`information_retrieval.py:65-80`); `initialize_task:82-107` formats the proto, may reword prompt dates, then initializes the app. Manifest params are **not** a frozen dump of instantiated relevant rows. `_without_replacement` formatting removes each params value from candidate pools before further random selection (`proto_utils.py:254-268,271-325,336-403`). No seeded initialization was replayed here.
- Frozen actual budgets are10/20/10/10; do not infer12/22 from registry class complexity overrides1.2/2.2. The instance copies proto complexity1/2, and the recorded budgets agree with `suite_utils._allocate_step_budget:491-502` (`int(10*complexity)`). No budget or reward repricing is proposed.
- `InformationRetrieval.is_successful:109-119` compares `env.interaction_cache` to expected values extracted **only from initialized relevant proto**, not the live DB. The base method merely checks initialization (`task_eval.py:166-180`). COUNT/SUM return one numeric answer; string retrieval returns all title values (`proto_utils.py:183-251`). Each of these four tasks has one all-or-nothing success criterion; no partial subscores.
- String answers are comma-split and stripped per item; STRING_MATCH uses case-insensitive difflib similarity>=0.9 (`fuzzy_match_lib.py:20-51`). Cardinality must match; then each submitted item can match any expected item (`proto_utils.py:147-180`). This is order-independent but not one-to-one. The synthetic duplicate probe confirms a latent false-positive weakness, **not** the cause of the two-versus-three rejection. A proposed occurrence-aware fuzzy matching fix is recorded separately in JSON.
- First business/finalization assistant stop wins (`omp_supervisor.py:211-234`). Only a nonempty string `taskOutcome` is accepted; outer whitespace is stripped, not content-coerced (`submission.py:45-93`). Runner reparses the archived raw text and places the exact answer string in the IR interaction cache (`runner.py:771-788`). Parent `shared-offline-checks.json.receiptPrecedenceProbe` confirms the first receipt and archived raw text agree and precede cutoffs. All four archived envelopes are valid strings. Correct format is not semantic correctness.
- Cleanup/quit precedes evaluation (`runner.py:716-737,790-796`), task teardown follows it. Each scoped cleanup cell only calls quit and returns its successful owned-session receipt. Because these IR expected values are in-memory proto values, no cleanup-induced change to expected membership is evidenced. There is no per-attempt SQLite snapshot; a UI observation is not promoted to persisted DB proof.
- Initial user prompt is raw JSONL line9 in each case and includes the exact goal, initialized reference clock `2023-10-15T15:34:00+00:00`, timezoneUTC, business/string contract and actual step limit. Thus missing-clock or legacy number-envelope explanations are excluded here. The runtime clock is explicitly described as initialization reference, not a live device clock measurement.
- Original result, normalized events, raw JSONL and business submission files were read only.65 actual Python responses were inspected (7/24/19/15):56 completed,9 failed, **all kernelState alive**.33 accepted UI actions total. A failed cell can follow a successful prefix action. No device/Appium/ADB/MCP command, formal task/score rerun, test, build, linter or formatter was invoked by this investigation.
- Campaign records AndroidWorld revision`55ddaf5edc6f6c25673aed343907d5b9dca66f84`. Current scoped source hashes are in JSON; this slice did not independently byte-match AndroidWorld helpers to a frozen per-file source snapshot. Parent shared receipt reports current19-file Harness digest exactly matching the frozen manifest. Source-derived inferences are distinguished below from direct UI facts.
- The frozen Skill was actually loaded. Its `amkernel-appium.md` section **Prove scope, membership and coverage** already demands full population, business membership, precise date predicates/reference clock and correct measures/units (raw read ends076L57,091L54,106L57,107L54). These failures do not establish that the Skill lacks the rule or Runtime is defective. Workflow fixes below are proposed behavior changes, not claims of approved Skill/core changes; amkernel-owner mechanism analysis remains separately owned.

## Case076 — equality boundary is not strict after

**Prompt:** What is my first event after5:20pm October29 2023 in Simple Calendar Pro? Titles only.

**Actual archive:** `{"taskOutcome":"Appointment for Budget Planning"}`; `parsedValue.taskOutcome` and stripped `answer` are that same string. First business final is raw L1782, received 93.553689s, before cleanup; reward 0, terminationcompleted.

### Oracle and actual boundary facts

Template `tasks.textproto:858-893` creates exactly one relevant event using `{date}`, `{time}`, `{title}` and returns IDENTITY(title). Here title is directly bound (not without-replacement) to **Grocery Shopping**, at **Oct 29 17:20**, lasting60minutes. Calendar utility converts withUTC (`calendar_utils.py:56-130`), inserts this plus75 random events, shuffles, and excludes qualifying later same-day random spans (`133-155,192-331`). The oracle never computes minimum start time or applies a strict-after predicate; its expected title is the direct relevant title.

Raw endL1353 (`call_kPvttdCGaXq4Y3Ru9uaiaUMC`, cell 5) actually returns `October29(Sun)`, `Grocery Shopping`, `17:20-18:20`. Cell6 is a deliberate next-day arrow tap; raw endL1678 (`call_T8Hpx8zwhHfUly2h4wVFyGh9`) returns `October30(Mon)`, `Appointment for Budget Planning`, `08:35-09:35`. These are original structured Python response facts, not an inference from final text.

Pure isolated probe on those exact threshold facts yields strictAfter=false, inclusiveAfter=true, oracleExpectedTitles=[Grocery Shopping]. This confirms a **template wording/generation/oracle inconsistency**: the target is exactly at the boundary, whereas ordinary “after” excludes equality. It is not a Runtime or Harness parsing problem.

The date may also constrain search to Oct 29 rather than any future day; the goal does not make that scope explicit. There is no complete76-event inventory or proof that the next-day08:35event is the globally first strict-after event. The Agent's equality exclusion is reasonable but does **not** certify its answer as correct under either unresolved scope. Recorded reward is not changed.

### Cause and separate fix

Immediate mismatch is submitted next-day title versus expected relevant-proto title. Confirmed root is the oracle task-contract inconsistency; complete Agent user-goal correctness remains unknown. Proposed decision: either explicitly say **at or after**, or separate query time from a strictly later inserted start and exclude earlier qualifying competitors, with clear date/tie semantics. That semantic cutover needs a new comparable identity. Do not instruct the execution model to memorize source answers or silently reprice this attempt.

## Case091 — one correct conversion is not a total

**Prompt:** Total kayaking distance in OpenTracks from Oct 09 through Oct 10 2023 inclusive, integer meters.

**Actual archive:** `{"taskOutcome":"1996"}`; parsed and stripped answer1996string. First business final raw L3792, received 175.104071s; reward 0, terminationcompleted.12/20 actions,8 unused.

### Collection and numeric reconstruction

Template `tasks.textproto:2932-2990` contains **two** relevant activities, both categorykayaking and start_dateOct9. It sums initialized `total_distance`. Distractor generation adds20 rows, rejecting lowercase categoryCONTAINSkayaking AND local startdate>=Oct 9 AND<=Oct 10 (`activity_app_utils.py:42-53,144-231`). Thus the interval is start-day based, not activity-end overlap; UTC day semantics include both dates.

`_create_activity_from_proto:65-110` mutates each proto distance before insertion/score extraction. Conversion is per-row `round(round(meters/1609.34,2)*1609.34)` (`56-62`). Numeric comparison is `abs(answer-expected)<10`, **strict**, not<=10 (`proto_utils.py:169-175`). Displayed miles should not be summed as original manifestdistance4000: that param is removed from the without-replacement pool, as are manifestname/time values. A source/display reconstruction is required.

Raw endL3301, cell 20, already contains these two candidates on Monday:

|Captured title|Time|Displayed distance|Offline source-linked reconstruction|
|---|---|---|---|
|Need more strength and conditioning|08:00|1.24mi|Unique allowed input2000m -> stored/proto 1996 m|
|Mindful Movement|06:15|2.80mi|Unique allowed input4500m -> stored/proto 4506 m|

Cell21 opens only the first; raw L3432 returns full Oct 9 08:00date and1.24mi. Cell22 exposes no category text. Historical screenshotL3606 shows a paddling/kayaking glyph; that alone would not prove taxonomy. Stronger offline basis: AST literal extraction confirms **neither title exists anywhere in the random-activity name corpus**, while both are in the relevant task name pool. With two relevant slots, both captured candidates are the relevant generated records under this source contract. The two distances uniquely map within the allowed distance domain. Probable reconstructed expected total is **1996+4506=6502m**. Submission differs by4506m, far beyond10m tolerance.

This6502is **not** an archived oracle return or persisted DB fact. The second full detail/category/start timestamp and initialized sports proto are missing; confidence in the exact total is probable source/display reconstruction. The direct behavioral evidence is stronger: answer1996is one observed activity's conversion, and complete category/date population was not established before finalizing.

Cell11's unfiltered aggregate is KAYAKING(4),14.53mi—not requested interval evidence. Filter dialog atL2289 shows Oct 15–21; opening its clipped From picker and clicking the header never returns a successful Oct 9/Oct 10date change, and the dialog is cancelled. Stale failures in cells7/13occur after successful prefix clicks; reconciliation cells8/14prove the changed surface. Neither is Runtime death. Some random names overlap category corpora (e.g.Waterway Paddle/Paddle Outing), so random-title intuition alone cannot classify them. Source excludes all qualifying noise, but all 22 DB rows were not independently captured: final bottom Kayak Expedition row is clipped and tail not fully traversed.

### Cause and separate fix

Probable root is Agent aggregate-population failure: abandoned filter route, selected one detail, omitted a second already-visible source-linked candidate, and stopped with8 steps unused. Unit arithmetic alone is not the defect. Proposed behavior: establish verified category/date aggregate scope or enumerate and bind every candidate's identity/category/full date/distance before reducing. Keep ambiguous membership unknown rather than call a single item a total. Existing Skill already says this; an extra textual exemplar would need separate justification, and no core Runtime blame is supported.

## Case106 — missing third member under an exhausted navigation budget

**Prompt:** Which tasks have I completed for Oct 16 2023 in Tasks? Titles only.

**Actual archive:** `{"taskOutcome":"Participate in brainstorming session, Plan family reunion"}`. The string is valid; first finalization final raw L5539 received 251.325493s, about21.186s after finalization started230.139016s, within120s and original720s business deadline. Reward0; terminationstep_budget.

### Exact oracle collection; what cannot be known

Template `tasks.textproto:1527-1576` contains **three** relevant tasks. Each is dueOct16 and completedOct10 with selectedtimes. Exclusion is due_date==Oct 16, regardless completion state, for20 random distractors. Success returns all three relevant titles. It does **not** ask the DB for completion timestamps onOct16 and does not infer business status from checkboxes. `task_app_utils.py:55-96,176-236` stores completion timestamp milliseconds and0for incomplete. Due-time is absent, so relevant due date is midnightUTC. “Completed for” is less explicit than “completed tasks due on”; source chooses due-for date. Treat wording clarification as a decision, not a proven bad oracle.

RawL1417before filter manipulation shows two candidate titles, each dueTmrw; reference dateOct15makes that Oct 16. They match relevant-only title corpus, not noise titles. A third relevant title is never captured. **Do not substitute params.title=Plan team outing**: formatting removes that value before without-replacement title choices. Without replaying initialization or possessing the DB/proto snapshot, the exact third title cannot be computed.

The expected **cardinality 3** is nevertheless structural and computable without replay. Submitted cardinality 2 necessarily fails `check_agent_answer`'s length guard before any fuzzy comparison. Order is irrelevant. No complete expected title list is fabricated here.

### Historical execution and failure layering

- Cell3's drawer swipe consumesstep1, then its chosen wait predicate times out; subsequent read proves drawer is open. Do not treat whole failed cell as a failed mutation.
- Cell6's right swipe intended to open the app drawer/navigation instead leaves the Agent on the launcher; subsequent read confirms wrong surface. Why the app exit occurred (e.g.edge gesture) is not proved.
- Cell8 relaunches Tasks and opens More options, using two steps. Cell9 toggles Show completed. Its tuple-bearing result is boundedrepr; cell 10recovers retained rows as JSON. Result is8 unchecked noise rows; initially seen target titles are absent. The menu's actual checked ON/OFFstate was not captured, so hiding completed is probable, not established solely by menu text.
- UiScrollable.scrollToEnd(12) in cell 11 is denied **before admission**, because one locator could conceal multiple UI interactions. It consumes0 accepted steps. Cell12's allowed swipe does not advance relevant rows. Cell13 Sort click is accepted, but its wait expects labels different from the actual Grouping/Sorting sheet and times out. Reads recover the real sort surface.
- Cell17back succeeds (step 9), then percent10scroll is denied before admission as beyond single-interaction bounds. Cell18percent1scroll consumesstep10, returnsfalse and the same 8 rows. Harness finalization message is raw L5122. Further mutations stop; the business answer reuses only the two initial candidates. Dedicated cleanupquit is raw L5611.

Both protocol denials are distinct from `stepBudget.rejectedActionCount=0`: `_authorize` validates before the action gate (`appium_proxy.py:494-502,309-319,871-872`). There are no post-budget rejected mutation attempts. All19 inner responses report kernelState alive;5 inner failures comprise 3 wait timeouts and 2 policy denials. Execution survival is not business success.

### Cause and separate fix

Confirmed immediate cause is incomplete2-versus-3list. Behavior-level root is incomplete target collection after wrong-surface navigation, unverified filter scope and ineffective/unsupported scrolling, ending at10 steps. The exact filter-state subcause remains uncertain. Proposed behavior: reconcile surface after each timeout, compare same candidate rows/status across completed-filter changes, and use one bounded supportedgesture with measured row progress rather than compoundUiScrollable/percent10or unrelated sorting exploration. No guarantee that every task can be completed in10 steps is asserted; do not invent missing members after exhaustion. The Skill already requires these invariants.

## Case107 — full traversal followed by an incorrect date-label predicate

**Prompt:** How many tasks due next week? Week startsMonday; integer.

**Actual archive:** `{"taskOutcome":"20"}`; string parsed unchanged. First business final raw L4268 received 172.391514s; reward 0, terminationcompleted.8/10 actions,2 unused.

### Complete membership reconstruction

Reference clock is SundayOct15 2023 UTC, so next week is **Oct 16–Oct 22inclusive**, equivalently [Oct 16 00:00,Oct 23 00:00)UTC. Template `tasks.textproto:1398-1524` has **six** relevant rows; COUNT(tasks_app_tasks) therefore expects6independent of names/seed. Due-date choices without replacement are Oct 16–22 after excluding params.due_date Oct 19. Noise20rejects that whole date interval. No incomplete-only or currently-visible condition is in this oracle.

Two initial mobile scrollGestures returnfalse and unchanged, but subsequentW3C swipes actually advance. Therefore those earlyfalsevalues were not population-completeness proof. Four actual JSON row windows, stitched with longest contiguous overlaps5,3,6, give26 records. A final same-direction W3C swipe returns unchanged after progress, supporting terminal coverage. Raw cell 14 then explicitly merges 26 and counts 20.

The relevant task title corpus and random `_TASKS` corpus are disjoint (AST literal query returns empty intersection). Captured six relevant-title records therefore identify the membership below without seed replay. Generator window for noise is default14days centeredOct15 15:34, i.e.Oct 8 15:34 through Oct 22 15:33; exclusion removesOct16–22, so random due days are Oct 8–15. This permits mapping their ambiguousweekdaylabels to past week, **as a source-derived reconstruction**, not direct DB timestamp evidence.

|True member|Captured label|Reconstructed due date|
|---|---|---|
|Follow up on support tickets|Tmrw|Oct 16|
|Plan family reunion|Tue|Oct 17|
|Book flights for conference|Wed|Oct 18|
|Research market trends|Fri|Oct 20|
|Send report to manager|Sat|Oct 21|
|Organize files and folders|Oct 22|Oct 22|

The bug is the Agent-authored cell 14predicate:

```python
next_week_labels={'Tmrw','Mon','Tue','Wed','Thu','Fri','Sat','Oct 22'}
next_week=[... for r in all_rows if r['due'] in next_week_labels]
```

This includes14 past-week noise occurrences along with6 members. It is not an arithmetic issue or first-page count. It is also not a reason to deduplicate titles: there are multiple legitimate same-title occurrences, includingtwo identical Finish Project Proposal Oct 8 rows that the overlapmerge correctly preserves. Exact row IDs are absent; tuple overlap is not a universal stable identity guarantee, but captured sequence/multiplicities26=6+20andterminal window support this bounded reconstruction.

|#|Captured title|Label|Source-linked due date|In true week?|Agent counted?|
|---|---|---|---|---|---|
|1|Finish Project Proposal|Oct 8|2023-10-08|no|no|
|2|Finish Project Proposal|Oct 8|2023-10-08|no|no|
|3|Finish Project Proposal|Fri|2023-10-13|no|yes|
|4|Call Grandma|Wed|2023-10-11|no|yes|
|5|Call Grandma|Thu|2023-10-12|no|yes|
|6|Water Plants|Thu|2023-10-12|no|yes|
|7|Call Grandma|Today|2023-10-15|no|no|
|8|Reply to Emails|Fri|2023-10-13|no|yes|
|9|Water Plants|Yest|2023-10-14|no|no|
|10|Create Budget for Next Month|Fri|2023-10-13|no|yes|
|11|Read 'The Martian'|Today|2023-10-15|no|no|
|12|Follow up on support tickets|Tmrw|2023-10-16|yes|yes|
|13|Plan family reunion|Tue|2023-10-17|yes|yes|
|14|Book flights for conference|Wed|2023-10-18|yes|yes|
|15|Research market trends|Fri|2023-10-20|yes|yes|
|16|Send report to manager|Sat|2023-10-21|yes|yes|
|17|Organize files and folders|Oct 22|2023-10-22|yes|yes|
|18|Call Grandma|Wed|2023-10-11|no|yes|
|19|Brainstorm Blog Post Ideas|Thu|2023-10-12|no|yes|
|20|Read 'The Martian'|Thu|2023-10-12|no|yes|
|21|Back Up Computer Files|Fri|2023-10-13|no|yes|
|22|Attend Team Meeting|Tue|2023-10-10|no|yes|
|23|Water Plants|Mon|2023-10-09|no|yes|
|24|Reply to Emails|Wed|2023-10-11|no|yes|
|25|Renew Driver's License|Fri|2023-10-13|no|yes|
|26|Grocery Shopping|Today|2023-10-15|no|no|

### Cause and separate fix

Confirmed defect is authored predicate semantics: weekday strings are treated as absolute next-week dates. Full initialized clock context was present and even the returned cell 14report labels the intended intervalOct16–22; merely supplying more clock prose is not the fix. ModuleNotFoundError for lxml and an incorrect Appium actions import failed before UIactions, were recovered using stdlib XML/Selenium imports, and did not cause20 versus 6.

Proposed behavior: resolve absolute date or trustworthy bounded interval from details/native datefilter before applying week membership; preserve ambiguousweekdayvalues asunknown rather than assume forward. Keep26occurrences and exactMondayboundary; do not smuggle the known templatecount 6into execution instructions. Existing Skill already contains the reference-clock/date invariants. No Runtime or Harness semantic defect is established.

## Actual action ledgers

Each row is one admitted Appium UI interaction. Status200means upstream mutation completed; a laterwait/staleexception can still fail the cell. Session creation, read-only observations, imports and quit are not step actions. Original full code/tool IDs and inner errors are retained in JSON.

### 076 — 3/10

|Step|Cell / raw lines|Action|Upstream|
|---|---|---|---|
|1|3 /883–884|Launch Calendar|200|
|2|5 /1351–1353|Tap Oct 29 calendar day|200|
|3|6 /1677–1678|Next-day arrow to Oct 30|200|

### 091 — 12/20

|Step|Cell / raw lines|Action|Upstream|
|---|---|---|---|
|1|4 /843–844|Launcher drawer swipe|200|
|2|5 /973–974|Launch OpenTracks|200|
|3|7 /1276–1277|Introduction next (post-click enumeration stale)|200|
|4|9 /1504–1505|Introduction next to list|200|
|5|11 /1941–1942|Open aggregated statistics|200|
|6|13 /2177–2178|Open Filter (post-click enumeration stale)|200|
|7|15 /2503–2504|Expand From date picker|200|
|8|18 /2929–2930|Click date-picker header (no changed date evidenced)|200|
|9|19 /3197–3198|Cancel filter|200|
|10|19 /3197–3198|Navigate up to TrackListActivity|200|
|11|20 /3300–3301|Swipe list to older activities|200|
|12|21 /3431–3432|Open Need more strength and conditioning detail|200|

### 106 — 10/10

|Step|Cell / raw lines|Action|Upstream|
|---|---|---|---|
|1|3 /973–974|Launcher drawer swipe (post-action wait timeout)|200|
|2|5 /1416–1417|Launch Tasks|200|
|3|6 /1744–1745|Right swipe intended drawer, later found launcher; wait timeout|200|
|4|8 /2262–2263|Relaunch Tasks|200|
|5|8 /2262–2263|Open More options|200|
|6|9 /2686–2687|Toggle Show completed|200|
|7|12 /3433–3434|Swipe list; no business-row progress evidenced|200|
|8|13 /3595–3596|Open Sort; wait predicate misses actual Grouping/Sorting sheet|200|
|9|17 /4781–4782|Back from Sort|200|
|10|18 /5112–5115|One bounded scroll; returns false and unchanged first eight rows|200|

### 107 — 8/10

|Step|Cell / raw lines|Action|Upstream|
|---|---|---|---|
|1|5 /1677–1678|Launcher drawer W3C swipe|200|
|2|6 /1951–1952|Launch Tasks|200|
|3|7 /2436–2437|mobile scroll down; false/unchanged|200|
|4|8 /2561–2562|mobile scroll up; false/unchanged|200|
|5|10 /3054–3055|W3C swipe advances window|200|
|6|11 /3319–3320|W3C swipe advances window|200|
|7|12 /3580–3581|W3C swipe reaches final rows|200|
|8|13 /3838–3839|W3C swipe unchanged establishes terminal window|200|

