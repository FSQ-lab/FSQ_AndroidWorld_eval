# Recipe failure analysis

Campaign: `amkernel-0.1.4-r15-current-stack-full-20261109T154403Z`. Scope is **049 RecipeAddSingleRecipe** and **052 RecipeDeleteDuplicateRecipes3** only. This is diagnosis, not a proposed score change or a product/config/test patch. Machine-readable detail, original generated Python code, complete per-command ledgers, returned facts, full toolCall IDs, and initialization params are in `domain-recipe.json`.

## Evidence and method

- Root C: `campaigns/amkernel-0.1.4-r15-current-stack-full-20261109T154403Z`.
- Case A49: `C/episodes/049-RecipeAddSingleRecipe/attempt-1`; A52: `C/episodes/052-RecipeDeleteDuplicateRecipes3/attempt-1`.
- Raw anchors below are **1-based JSONL line/event sequence** in each attempt's immutable `raw-private/agent-events.jsonl`. A `tool_execution_start.args.path` naming `xd://mcp__amkernel_python_exec` holds code; actual Python status/UI evidence comes from its paired `tool_execution_end.result.content[].text` JSON response, not the normalized success flag. Full logs were streamed; no base64 or full raw log was dumped.
- Read-only queries inspected archived params, exact tool code/structured responses, original prompt, business submission and result stage ordering. A pure stdlib AST extraction exercised the current fuzzy comparison; grouping used actual archived initialization rows, not generated substitutes. No AndroidWorld import with device side effects, device/ADB/Appium/MCP call, task/score replay, test suite, or source/config edit occurred.
- Shared parent receipt `shared-offline-checks.json` proves these cases' prompt goal/reference clock/string answer contract, archived parser equality and submission hash consistency. Its `sourceIdentity` confirms the current 19-file harness digest equals frozen `861905dba1d8dfab232cd977cdfbd3ac7837605a5199c982240ad40895599e66`. Recorded AndroidWorld revision is `55ddaf5edc6f6c25673aed343907d5b9dca66f84`; current oracle-source line references were read, but per-file frozen AndroidWorld hashes were not separately proved here.
- The agent actually read the frozen Skill at raw end lines32/54/55 in both attempts. Returned bodies equal the corresponding current local Skill bodies modulo one terminal newline. Thus focus/readback, budget reservation, duplicate equivalence, and occurrence preservation guidance were already present. A trace violating guidance does **not** show guidance was absent.

### Persistence and cleanup boundary

`recipe.py:28-49` targets `/data/data/com.flauschcode.broccoli/databases/broccoli`, table `recipes`, primary key `recipeId`. `SQLiteApp.list_rows` delegates to `sqlite_utils.get_rows_from_remote_device`; that helper pulls a DB into a temporary local directory and executes `SELECT * FROM recipes;` (`sqlite_utils.py:53-103`). Inserts omit `recipeId`, commit, push DB and close the app (`sqlite_utils.py:173-212`; `sqlite_schema_utils.insert_into_db:439-468`). `recipeId=-1` in result params is an insertion placeholder, **not** the real identity. No original before/after DB export, WAL/SHM snapshot, assigned IDs, or per-predicate evaluator diagnostic is present in either attempt directory.

`SQLiteApp.initialize_task` clears DB, initializes the app, clears again, then inserts noise (`sqlite_validators.py:257-263`). Addition captures that noise as `before`; deletion inserts the two target copies, captures `before`, and takes the last two returned rows as target IDs (`:280-283,348-358`). No guessed DB ID is used in this analysis.

`runner.py:716-737` finishes the agent and verifies/cleans its session **before** `agent_protocol` and evaluator (`:745-796`). Each actual cleanup cell only calls `driver.quit()`; no cleanup UI mutation appears. Task teardown and its DB clear occur **after** evaluator (`:821-838`). Thus task teardown did not clear the DB before scoring; however no post-quit/pre-evaluator persistence snapshot exists, so cleanup's effect on persistence cannot be directly measured. A successful quit is not itself proof of business-state preservation.

## Case 049

### Request, oracle and initialized data

Goal: add **Chicken Caesar Salad Wrap** with:

| Field | Requested value |
|---|---|
| description | An ideal recipe for experimenting with different flavors and ingredients. |
| servings | `3-4 servings` |
| preparationTime | `2 hrs` |
| ingredients | `as desired` |
| directions | Toss chopped romaine lettuce with Caesar dressing, grilled chicken strips, and Parmesan cheese. Wrap in a large tortilla. Feel free to substitute with ingredients you have on hand. |

Archived seed is374064309 and text representation is `text_block`. Ten archived noise recipes initialize the app: Quinoa Salad with Vegetables; Garlic Butter Shrimp; Turkey and Cheese Panini; Stuffed Bell Peppers; Raspberry Almond Smoothie; Lentil Soup; Quick Fried Rice; Vegetarian Chili; Avocado Toast with Egg; Greek Salad Pita Pockets. They are **initialization inputs**, not individually exported persistent records. The requested target is not inserted initially; desired final count is11.

Exact current-source oracle:

- `RecipeAddSingleRecipe` (`recipe.py:412-417`) uses `_RecipeAddMultipleRecipes.validate_addition_integrity` (`:354-384`) and `AddMultipleRows.is_successful` (`sqlite_validators.py:304-310`). Binary reward only; no subscores.
- For every reference target, some after row must match `title, description, servings, preparationTime, source, ingredients, directions, favorite`.
- First seven fields are free-form: `fuzzy_match` lowercases values and accepts `difflib.SequenceMatcher(...).ratio() >=0.9` (`fuzzy_match_lib.py:20-51`). `favorite` must match exactly0. Empty source must also match under that predicate. Target `imageName` and target ID are not compared, but all original noise rows are preserved by full dataclass equality, including their IDs and imageName.
- After count must equal before+1 (11); every before row must remain unchanged (`validate_rows_addition_integrity:149-190`). No answer-text scoring is involved.

### Chronology and earliest proven deviation

1. Session creation succeeds, returned `newCommandTimeout=300`; all15 structured PythonResponses say `kernelState=alive`.
2. Calls3–5 open app drawer, Broccoli, New Recipe. The initial semantic form observation exposes title, description, source, servings, time, ingredients and directions IDs (raw1280).
3. Call6 fills title and description (steps4–7), then `find_element(new_servings)` fails before sending servings (raw1683→1684, `NoSuchElementException`). Call7 observes only title/categories/description/source while description remains focused. **Earliest execution divergence:** assumed form visibility did not survive keyboard/layout change. No rollback occurred; title/description stayed entered.
4. Call8 hides keyboard and scrolls (steps8–9), then sees lower fields. Call9 pre-caches four element handles, types servings (steps10–11), clicks preparation time (step12), and raises its own `Focus failed` before typing time (raw2320). The click returned200 but did not satisfy focus. A failed Python cell was not a failed/rolled-back prefix.
5. Call10 hides keyboard and scrolls (steps13–14). **Earliest directly observed wrong business value:** raw2564 reports `new_servings="3-4 serving size "`, not `3-4 servings`. The supplied input literal was correct, but the mutation's layer is not shown.
6. Call11 focuses servings (step15) then raises `AttributeError: 'WebElement' object has no attribute 'set_value'` (raw2919). This is an unsupported client API choice, not a kernel death or completed replacement. Its planned verification/save never ran.
7. Call12 clears and sends servings again (steps16–17), then a fresh lookup for preparation time fails (`NoSuchElementException`, raw3202). **No readback** validates the repaired servings. Earlier mismatch is therefore not resolved by evidence.
8. Call13 reuses lower handles cached in call9. It performs six clicks/inputs for time, ingredients and directions plus SAVE (steps18–24). It omits the earlier focus checks and all field-value checks. Result `{"actionsSubmitted":7}` (raw3416) is the code's own count, not business verification. This last SAVE succeeds at HTTP200 and exhausts the gate.
9. Read-only call14 (raw3654) shows `.recipe.details.RecipeDetailsActivity`, title and description exact, time2hrs, ingredients`as desired`, full requested directions, and **servings `3-4 serving size of y`**. `Mark as favorite` is consistent with unfavorited UI state, not a DB export.
10. First business final raw3700 accurately reports the saved servings discrepancy. Dedicated cleanup call15 raw3788→3789 returns `quitReturned=true`; cleanup prose raw3808 cannot replace the business submission. Recorded evaluator returns0.0, then teardown clears task state.

### Action ledger and budget

Allocated24 = `int(10*2.4)`, consumed24, all admitted HTTP statuses200. Breakdown: 11clicks,7inputs,3W3C actions (drawer/form swipes),2hideKeyboard,1clear. There are15Python calls, not15UI steps; advisory30calls is not a hard step limit. No rejected actions, denied commands, timeout or business-deadline exhaustion. Four admitted operations (two hides and two form swipes) were keyboard/layout mitigation beyond initial drawer launch; the duplicate servings click/input/clear work and missing `set_value` API consumed correction capacity. Exact attribution follows; free observations/failed lookups are omitted from this charged ledger but retained in call table.

| Step | Call / raw start→end | Kind | Actual admitted effect |
|---:|---|---|---|
| 1 | 3 / 831→832 | `actions` | Open app drawer |
| 2 | 4 / 1062→1063 | `click` | Open Broccoli |
| 3 | 5 / 1279→1280 | `click` | Open New Recipe |
| 4 | 6 / 1683→1684 | `click` | Focus title |
| 5 | 6 / 1683→1684 | `input` | Enter title |
| 6 | 6 / 1683→1684 | `click` | Focus description |
| 7 | 6 / 1683→1684 | `input` | Enter description |
| 8 | 8 / 1952→1953 | `mobile: hideKeyboard` | Hide keyboard |
| 9 | 8 / 1952→1953 | `actions` | Scroll form |
| 10 | 9 / 2319→2320 | `click` | Focus servings |
| 11 | 9 / 2319→2320 | `input` | Enter 3-4 servings |
| 12 | 9 / 2319→2320 | `click` | Click preparation time; focus check fails |
| 13 | 10 / 2563→2564 | `mobile: hideKeyboard` | Hide keyboard |
| 14 | 10 / 2563→2564 | `actions` | Scroll form |
| 15 | 11 / 2918→2919 | `click` | Focus servings; following set_value is unavailable |
| 16 | 12 / 3201→3202 | `clear` | Clear servings |
| 17 | 12 / 3201→3202 | `input` | Enter 3-4 servings again |
| 18 | 13 / 3415→3416 | `click` | Click cached preparation-time handle |
| 19 | 13 / 3415→3416 | `input` | Enter 2 hrs |
| 20 | 13 / 3415→3416 | `click` | Click cached ingredients handle |
| 21 | 13 / 3415→3416 | `input` | Enter as desired |
| 22 | 13 / 3415→3416 | `click` | Click cached directions handle |
| 23 | 13 / 3415→3416 | `input` | Enter full directions |
| 24 | 13 / 3415→3416 | `click` | SAVE |

| Call | Raw lines | ToolCall prefix | PythonResponse | UI steps |
|---:|---|---|---|---|
| 1 | 406→407 | `call_b38eaa91e2c94f82830ab74c8ca7f7d7` | completed; no error; alive | none |
| 2 | 591→592 | `call_ntnKtkkFxRdPqK2sbpP8p6f4` | completed; no error; alive | none |
| 3 | 831→832 | `call_EKGeqz0gNxDtpNqYp6ylPIOH` | completed; no error; alive | 1 |
| 4 | 1062→1063 | `call_J9nt8Zd8mzsVF3RmeE2fdVYH` | completed; no error; alive | 2 |
| 5 | 1279→1280 | `call_M5gPLL4UIIbSKBDB9xwYt2Ya` | completed; no error; alive | 3 |
| 6 | 1683→1684 | `call_Jmof1XMtptSleJefMP9popjO` | failed; selenium.common.exceptions.NoSuchElementException; alive | 4,5,6,7 |
| 7 | 1797→1798 | `call_RjhBVBO1dskCCg9qqPj0jBc5` | completed; no error; alive | none |
| 8 | 1952→1953 | `call_m5If3DWufMUaFyrBQH1qTSQv` | completed; no error; alive | 8,9 |
| 9 | 2319→2320 | `call_Yy4ZRACasZFOvoqFX1WKlimJ` | failed; RuntimeError; alive | 10,11,12 |
| 10 | 2563→2564 | `call_3syYQmpnxFHEqn2NTdxv1YEa` | completed; no error; alive | 13,14 |
| 11 | 2918→2919 | `call_cImUz1nS9jz6KFO0ZCmNVr8n` | failed; AttributeError; alive | 15 |
| 12 | 3201→3202 | `call_xnJd0fKCXsoNILwB3kFaFduZ` | failed; selenium.common.exceptions.NoSuchElementException; alive | 16,17 |
| 13 | 3415→3416 | `call_XZHd8fqa2g9QQaUJLNx4TNyk` | completed; no error; alive | 18,19,20,21,22,23,24 |
| 14 | 3653→3654 | `call_dPlQkBfA2hogADsk8UMhgViU` | completed; no error; alive | none |
| 15 | 3788→3789 | `call_44j78YvzG98yuL8xg09mGtcL` | completed; no error; alive | none |

### Final answer, cleanup and score causation

Original first business `rawText` is:

```json
{"taskOutcome":"Recipe saved, but servings is incorrect: displayed as \"3-4 serving size of y\" instead of \"3-4 servings\"."}
```

The immutable archive has `validContract=true`, reason`valid`, string taskOutcome and the same stripped answer. Receipt is event3700, phase`finalization`, received167.91274245805107s; action gate finalization started154.41219520801678s; cleanup requested168.0404818750685s. No type conversion or cleanup precedence explains this result. Business budget was1560s and was not reached.

Actual evaluator stage:1794255169.2410629→1794255169.3760252 Unix; teardown starts1794255169.3760252. Quit result precedes evaluator at1794255165.781. UI proof therefore exists before cleanup and aggregate DB score after cleanup, but **not** an archived persistent row connecting the two.

**Outcome confidence:** confirmed wrong post-save UI field, confirmed reward0/step_budget, unknown exact DB rowset. **Root confidence:** confirmed Agent invariant failure (save without validating repaired content); probable that the displayed servings mismatch caused the DB oracle rejection; unknown origin of phrase transformation. Pure current-source comparison of the actual displayed string gives ratio0.7272727272727273 and false at0.9. This is a sufficient conditional explanation if DB stored that displayed value, not proof that no additional oracle predicate failed.

Do **not** label this an AMKernel mutation/serialization bug: the Python literal and response disagree at the UI boundary, but no IME/input trace identifies the changing layer. IME composition/autocorrection, UiAutomator2 input delivery and app transformation remain alternatives. No persistent data shows which.

### Mechanism targets and falsification

- **Agent / existing Skill enforcement, proposed:** `.agents/skills/amkernel/references/android-execution.md`, Input/submit and budget sections. Preserve executed-prefix/readback locals; reacquire after layout changes; compare every requested field after final input before SAVE; reserve correction+save permits. Existing frozen guidance already requires focus/readback and acceptance; an additional generic example is reinforcement, not evidence of a missing rule. Falsify sufficiency if a captured field is correct pre-save and only becomes wrong after verified save.
- **Agent client API, proposed:** raw2918 `.set_value` is absent; use only observed supported official-client methods, and ensure replacement clear+input has positive focus and equality readback. Avoid calling a removed method as a one-action workaround. Falsify the diagnosis only with evidence this exact run exposed that method; the captured AttributeError currently rules that out.
- **Environment boundary, decision needed:** obtain existing historical IME/input metadata or an authorized isolated generic text-entry trace before prescribing a keyboard/device change. No blanket autocorrect-disable recommendation and no config change in this diagnosis. A layer-specific trace is the discriminator.

## Case 052

### Request and exact oracle

Visible goal: “Delete all but one of any recipes in the Broccoli app that are exact duplicates, ensuring at least one instance of each unique recipe remains.”

`RecipeDeleteDuplicateRecipes3` (`recipe.py:272-315`) sets complexity3.4, noise30 and inserts two identical targets. It starts with22 random non-Avocado rows, removes one as target, adds3Avocado noise rows, and adds same-title/same-description target variants until30noise rows. The variants are not necessarily exact duplicates. Actual archived params, rather than generator possibilities, determine this case.

Exact duplicate **initialization** predicate is equality across every Recipe dataclass field except `recipeId`: `title, description, servings, preparationTime, source, ingredients, directions, favorite, imageName` (`sqlite_schema_utils.py:197-214`; `DeleteDuplicateRows._validate_candidates:383-398`). Equality of title and description alone does not meet it.

Exact **score** is the OR of two removal-integrity checks (`RecipeDeleteDuplicateRecipes.validate_deletion_integrity:200-211`): remove target1's actual captured ID while every other before row remains exactly unchanged, **or** remove target2's ID with that same preservation rule. Every remaining after row must have existed before; no changed/new row is allowed (`sqlite_validators.validate_rows_removal_integrity:73-115`). Binary1/0, no subscores. With32initial rows this requires31after rows and one target copy retained. It does not merely check that same-title counts fell.

### Actual initialized collection, not guessed duplicate answers

Offline exact-field grouping of the **archived params** gives32occurrences,31full-content groups, and exactly one duplicate group: zero-based concatenated occurrence indices`[30,31]` (the two `row_objects`, not actual DB IDs). The10Butternut occurrences are`[0,12,24,25,26,27,28,29,30,31]`; only30/31are equal. All32rows and original per-origin params references are in JSON. Distinct content must survive, even when title/description match.

All10Butternut rows have title **Butternut Squash Soup** and description **A quick and easy meal, perfect for busy weekdays.**, favorite0, empty source/imageName, and the same base directions “Sauté onions and garlic, add cubed butternut squash and broth. Puree until smooth and season with nutmeg, salt, and pepper.” They differ as follows. Directions suffixes: **T**=`Try adding a pinch of your favorite spices for extra flavor.`; **G**=`Garnish with fresh herbs for a more vibrant taste.`; **F**=`Feel free to substitute with ingredients you have on hand.`

| Param occurrence | Servings | Time | Ingredients | Directions suffix |
|---:|---|---|---|---|
|0|6 servings|4 hrs|as desired|T|
|12|3-4 servings|1 hrs|subject to change|G|
|24|8 servings|4 hrs|varies|F|
|25|2 servings|45 mins|subject to change|F|
|26|8 servings|2 hrs|to your liking|G|
|27|8 servings|45 mins|flexible ingredients|T|
|28|3-4 servings|1 hrs|varies|F|
|29|1 serving|1 hrs|quantities to taste|F|
|30 target|3-4 servings|30 mins|quantities to taste|G|
|31 target|3-4 servings|30 mins|quantities to taste|G|

Other same-title populations are Avocado3, BBQ Chicken Quesadillas2, Grilled Cheese with Tomato and Basil2, Pan-Seared Salmon with Quinoa2; all are unique by full content. The other13titles have one occurrence each. Params prove the intended initialized population, while task initialization completed and UI scans corroborate its shape; lack of DB export means no claim that param index maps to a particular primary key.

### Raw UI identities, coverage and first deviation

1. Calls3–4 open drawer/Broccoli (steps1–2). Call6 records7bounded list windows using6scrollGesture actions (steps3–8) and returned `canScrollMore=false` (raw1863). It reaches the bottom, but windows overlap and have only title/summary/source/bounds; repeated equal summaries lack stable row IDs. The full window facts are in JSON. They nominate many Butternut candidates but cannot reconstruct an exact occurrence count or pair from titles alone.
2. Search opens (step9), full Butternut title entered (step10). Call8 returns only a repr of a2-element nested tuple list (raw2578), **not two total recipes**. Agent reasoning raw2897 explicitly says keyboard leaves only two visible and total may be10.
3. **Earliest execution divergence:** call9 raw2898→2899 tries the first title's `../..` parent, fails before click, and consumes no action. Read-only call10 raw3147 shows3currently visible CardViews: clipped first `[21,422][1059,609]` with description only, second `[21,630][1059,945]`, third `[21,966][1059,1281]`. They are viewport occurrences, not the full filtered collection.
4. Call11 opens visible `cards[1]` (step11). Raw3352 shows a Butternut detail with3-4servings,30mins,`quantities to taste`, Gdirections, matching content of initialized target30/31. **One target-content instance is now observed; which copy/ID is unknown.**
5. Call12 captures its seven-field `detail_signature`, navigates up (step12), opens visible `cards[2]` (step13), captures a second signature. Raw3745 collapses the dict containing tuple lists to repr, losing comparison data at that response boundary. Read-only calls13–14 recover exact inequality: first3-4servings/30mins/G versus second1serving/1hrs/F (raw3824,3909). Second matches unique noise29. Neither equality nor duplicate deletion is authorized. `detail_signature` also omits source, favorite, imageName and any offscreen detail, so equality of that partial signature would still need a completeness boundary.
6. Call15 opens More options (step14). Its tuple-list response is repr (raw4879); call16 recovers menu labels Edit/Delete (raw5063). **Seeing Delete is not clicking Delete.** No destructive operation follows.
7. Call17 dismisses menu and navigates to search (steps15–16), then `.set_value` raises AttributeError. Call18 clears/enters Gsuffix text (steps17–18), observes no cards. These actions do not identify the missing Butternut counterpart. Underlying search fields/index semantics are not captured.
8. The agent leaves the unresolved Butternut group. Call19 spends5actions (steps19–23) comparing Avocado visible cards0/2; readback proves unequal servings6vs3-4, time4hrsvs1hrs, ingredients`various amounts`vs`n/a`. These correspond to unique noise21/23, not duplicates.
9. Call20 navigates/clears/types full `Pan-Seared Salmon with Quinoa` (steps24–26), then its explicit wait times out. Call21 shows correct query but zero cards, not lost session. Call22 clears/types `Pan` (steps27–28), now sees two candidates. This establishes query-specific behavior, **not** a proven punctuation/root cause.
10. Call23 compares Pan cards0/1 (steps29–31), returns unequal servings6vs1, ingredients`n/a`vs`varies`, TsuffixvsFsuffix. Those match unique noise7/13. No deletion is correct for this pair.
11. Call24 returns to search and clears/types `Butternut` (steps32–34), ending with3currently visible cards (raw7319). It does not enumerate10candidates, bind the true counterpart, click Delete, or confirm deletion. The last input exhausts the34action gate. Honest first business final says no recipes deleted. Quit-only cleanup succeeds.

**Strategy deviation versus safety:** preserving unequal/uncertain candidates was correct. The failure is not an unsafe deletion based on names; it is failing to complete an occurrence-aware comparison/deletion path. After a target-content instance was found, remaining actions migrated to unrelated groups/search recovery without retaining a fully addressable Butternut counterpart or commit reserve. This is a probable strategy cause, not proof of a generally feasible34-operation solution. No claim that positional guessing would have been a legitimate fix.

### Action ledger and budget

34=`int(10*3.4)` permits, consumed34, all forwarded statuses200, rejected0/denied0. Breakdown:15clicks,6scrollGesture,6input,5clear,1back,1W3C drawer gesture.25Python calls, advisory30. No business deadline reached (2160s available).

Charged phases: launch2; initial list scan6; Butternut title search+first two details5 (steps9–13); menu exploration/dismiss/navigation3; directions search2; Avocado search/detail comparison5; failed full-Pan query3; shorter-Pan recovery2; Pan comparison3; return-to-Butternut search3. Sum34. Zero charged operations are Delete or deletion confirmation. API/locator exceptions before an action cost no permit; executed prefixes retain their charges.

| Step | Call / raw start→end | Kind | Actual admitted effect |
|---:|---|---|---|
| 1 | 3 / 948→949 | `actions` | Open app drawer |
| 2 | 4 / 1144→1145 | `click` | Open Broccoli |
| 3 | 6 / 1862→1863 | `mobile: scrollGesture` | List scan scroll 1 |
| 4 | 6 / 1862→1863 | `mobile: scrollGesture` | List scan scroll 2 |
| 5 | 6 / 1862→1863 | `mobile: scrollGesture` | List scan scroll 3 |
| 6 | 6 / 1862→1863 | `mobile: scrollGesture` | List scan scroll 4 |
| 7 | 6 / 1862→1863 | `mobile: scrollGesture` | List scan scroll 5 |
| 8 | 6 / 1862→1863 | `mobile: scrollGesture` | List scan scroll 6 |
| 9 | 7 / 2451→2452 | `click` | Open Search |
| 10 | 8 / 2577→2578 | `input` | Enter Butternut Squash Soup |
| 11 | 11 / 3351→3352 | `click` | Open filtered visible cards[1] |
| 12 | 12 / 3744→3745 | `click` | Navigate up |
| 13 | 12 / 3744→3745 | `click` | Open filtered visible cards[2] |
| 14 | 15 / 4878→4879 | `click` | Open More options |
| 15 | 17 / 5277→5278 | `back` | Back dismisses menu |
| 16 | 17 / 5277→5278 | `click` | Navigate up |
| 17 | 18 / 5437→5438 | `clear` | Clear search |
| 18 | 18 / 5437→5438 | `input` | Enter Garnish with fresh herbs |
| 19 | 19 / 5804→5805 | `clear` | Clear search |
| 20 | 19 / 5804→5805 | `input` | Enter Avocado Toast with Egg |
| 21 | 19 / 5804→5805 | `click` | Open avocado cards[0] |
| 22 | 19 / 5804→5805 | `click` | Navigate up |
| 23 | 19 / 5804→5805 | `click` | Open avocado cards[2] |
| 24 | 20 / 6276→6277 | `click` | Navigate up |
| 25 | 20 / 6276→6277 | `clear` | Clear search |
| 26 | 20 / 6276→6277 | `input` | Enter Pan-Seared Salmon with Quinoa |
| 27 | 22 / 6678→6679 | `clear` | Clear search |
| 28 | 22 / 6678→6679 | `input` | Enter Pan |
| 29 | 23 / 6960→6961 | `click` | Open Pan cards[0] |
| 30 | 23 / 6960→6961 | `click` | Navigate up |
| 31 | 23 / 6960→6961 | `click` | Open Pan cards[1] |
| 32 | 24 / 7316→7319 | `click` | Navigate up |
| 33 | 24 / 7316→7319 | `clear` | Clear search |
| 34 | 24 / 7316→7319 | `input` | Enter Butternut |

| Call | Raw lines | ToolCall prefix | PythonResponse | UI steps |
|---:|---|---|---|---|
| 1 | 424→425 | `call_lptsFXe2wMafe7iPQ3QEVYOg` | completed; no error; alive | none |
| 2 | 684→685 | `call_mNySStgvwVDpakQxmh8A6qeX` | completed; no error; alive | none |
| 3 | 948→949 | `call_mKQsem7LQXhFVZeYt6q0jN7k` | completed; no error; alive | 1 |
| 4 | 1144→1145 | `call_f2cd2765a48d436e8f3fd052286a949b` | completed; no error; alive | 2 |
| 5 | 1531→1532 | `call_y22CB6ZV1IyAs9uL13A5FT8f` | completed; no error; alive | none |
| 6 | 1862→1863 | `call_iuq2CafKXWeI02UBPVhiTLLh` | completed; no error; alive | 3,4,5,6,7,8 |
| 7 | 2451→2452 | `call_z5e8Fl5r2L7pC4nGbP8b9qjc` | completed; no error; alive | 9 |
| 8 | 2577→2578 | `call_IEOi6eZN00YSLdHoFfhiaPR4` | completed; no error; alive | 10 |
| 9 | 2898→2899 | `call_LMaB3aGXwqShCZMZSIvAT1Wh` | failed; selenium.common.exceptions.NoSuchElementException; alive | none |
| 10 | 3146→3147 | `call_hUsGKG9RZR7aOFJUrPMmUZmF` | completed; no error; alive | none |
| 11 | 3351→3352 | `call_xnAizmYTpbhg75eJ24IEuAtu` | completed; no error; alive | 11 |
| 12 | 3744→3745 | `call_YTGriLGANTuOZALe2X3avfU3` | completed; no error; alive | 12,13 |
| 13 | 3823→3824 | `call_q8X9NNnIS6gPzC2lfZC98hxU` | completed; no error; alive | none |
| 14 | 3908→3909 | `call_tfyXBBPRsyVL7D8imSXyPGBU` | completed; no error; alive | none |
| 15 | 4878→4879 | `call_7IYSBXLbneSVEP9PQURSAdum` | completed; no error; alive | 14 |
| 16 | 5062→5063 | `call_ewI9RLWHr1NHC94y0A9UAXQT` | completed; no error; alive | none |
| 17 | 5277→5278 | `call_R0yYD6gJd3mDDmP50Ndz9Jpi` | failed; AttributeError; alive | 15,16 |
| 18 | 5437→5438 | `call_38hzfS78D1KgkD60zfNwpbL6` | completed; no error; alive | 17,18 |
| 19 | 5804→5805 | `call_vQH3vxMAywlmQDoXc3Q0Fp4X` | completed; no error; alive | 19,20,21,22,23 |
| 20 | 6276→6277 | `call_6mMVPgoMpyKfcyIc395GZqga` | failed; selenium.common.exceptions.TimeoutException; alive | 24,25,26 |
| 21 | 6410→6411 | `call_XcedW4FQ7FfQBVs40uzybOTV` | completed; no error; alive | none |
| 22 | 6678→6679 | `call_HkcAqAhqVwVSDul1MBbu9O5c` | completed; no error; alive | 27,28 |
| 23 | 6960→6961 | `call_AqGMuEIzLYMgDnLTiVwizqfz` | completed; no error; alive | 29,30,31 |
| 24 | 7316→7319 | `call_WRmX0rgt0Q9zqRlb24TP74C2` | completed; no error; alive | 32,33,34 |
| 25 | 7423→7424 | `call_VWSF8b0DuVCq4WoIrQR7Rg4L` | completed; no error; alive | none |

### Submission, surviving recipes and confidence

Original first business rawText:

```json
{"taskOutcome":"Unable to complete: no recipes were deleted before the UI action budget was exhausted."}
```

Valid parsed nonempty string, receipt event7353, phase`finalization`, received317.76614945789333s; finalization started312.4733818329405s; cleanup requested318.16660199989565s. Raw7326 is the exhaustion control; raw7363 separate cleanup control; raw7424 quit success; raw7436 cleanup-only final is ignored for business answer.

Evaluator1794255980.097749→1794255980.240979 Unix follows quit result1794255970.214, precedes task teardown1794255980.240979. Reward0.0 is expected if the initial pair remained; no persistent snapshot independently confirms all32surviving rows. **Proven:** no Delete/confirmation call in the complete action ledger, no claimed deletion, last main-view search still shows3visible Butternut cards, and reward0. **Strong inference, not DB proof:** all initialized recipes including both target copies survived because only inspection/navigation/search occurred. **Unknown:** exact final row IDs/contents and any cleanup-time persistence effect. Three visible cards do not mean only three survived.

Outcome confidence is confirmed for no attempted UI deletion and aggregate failure; persistent final collection unknown. Root confidence is probable for incomplete occurrence tracking and budget allocation. No observed transport/kernel failure supports Runtime blame; all25responses are alive. Nested tuple repr loss in calls8/12/15 is a real observation limitation and cost recovery calls, but does not by itself establish the cause of the wrong task outcome or a serializer defect.

### Concrete mechanism targets and offline discriminators

- **Agent / existing Skill, proposed:** `amkernel-appium.md` coverage, content-equivalence and budget sections. Maintain a temporary occurrence-aware candidate ledger; distinguish overlapping windows from distinct equal-content objects; complete a promising group before changing groups; reserve actual menu/confirmation/retention actions. Never infer duplicates from titles or appended DB position. Existing frozen Skill already states these invariants; reinforcement requires decision, not an assertion that the Skill caused failure.
- **Agent output payload, proposed:** raw3744 `detail_signature` returns tuples. Use JSON-native string dictionaries/lists plus explicit completeness/occurrence evidence; do not rely on partial signatures or `zip` differences as full equivalence proof. A JSON-native scalar follow-up recovered the inequality here, so no wrong deletion resulted from omitted values.
- **Runtime serialization interface, decision needed:** raw2578/3745/4879 return bounded repr instead of the nested primitive facts. A separately owned pure serializer probe can distinguish intentional unsupported tuple behavior from a preserveable result-shape defect. Mechanism owner must identify the exact serializer symbol; no coordinated fix is approved in this report. Boundedness and safe object handling must remain invariant.
- **Harness comparability, decision needed:** official allocator is complexity×10, but proxy charges each clear/input/focus/navigation interaction separately. Reaching34with no deletion is observed; universal infeasibility is not. Any future authorized feasibility study must preserve this attempt/reward and show a legal occurrence/equivalence/deletion/retention route, not raise the frozen budget or give the Agent initialization answers.
- **Search environment boundary, unknown:** full Pan title returned0, `Pan` returned2. Existing logs cannot discriminate tokenizer/query syntax/index state. An offline source/APK inspection or authorized separate query study is the discriminator; do not install a speculative search fix from this trace.

## Reproducible offline checks

The following exact read-only query combines the pure checks exercised during this investigation. It does not import AndroidWorld modules, evaluate a formal task or contact a device. The displayed malformed servings string is copied from raw3654, not assumed from the submission. IDs in the equivalence result are occurrence positions in params, not persistent recipeIds.

```python
import ast, collections, difflib, json, pathlib
C = pathlib.Path("campaigns/amkernel-0.1.4-r15-current-stack-full-20261109T154403Z")
r49 = json.loads((C / "episodes/049-RecipeAddSingleRecipe/attempt-1/result.json").read_text())
r52 = json.loads((C / "episodes/052-RecipeDeleteDuplicateRecipes3/attempt-1/result.json").read_text())
# Pure source extraction; imports only stdlib difflib, no AndroidWorld imports/device effects.
p = pathlib.Path("android_world/android_world/utils/fuzzy_match_lib.py")
tree = ast.parse(p.read_text())
selected = ast.Module(body=[n for n in tree.body if isinstance(n, (ast.Import, ast.ImportFrom, ast.Assign, ast.FunctionDef))], type_ignores=[])
ns = {}
exec(compile(ast.fix_missing_locations(selected), "<offline-fuzzy-source>", "exec"), ns)
expected, observed = r49["task"]["params"]["row_objects"][0]["servings"], "3-4 serving size of y"
print({"expected": expected, "observed": observed, "ratio": difflib.SequenceMatcher(None, expected.lower(), observed.lower()).ratio(), "threshold": ns["_MIN_DIFF_SIMILARITY"], "oracleFuzzyMatch": ns["fuzzy_match"](expected, observed)})
p = r52["task"]["params"]
rows = p["noise_row_objects"] + p["row_objects"]
groups = collections.defaultdict(list)
for i, row in enumerate(rows):
    groups[tuple(sorted((k, v) for k, v in row.items() if k != "recipeId"))].append(i)
print({"initializedRowsFromParams": len(rows), "uniqueFullContentGroups": len(groups), "duplicateOccurrenceIndices": [v for v in groups.values() if len(v) > 1], "butternutOccurrences": [i for i, row in enumerate(rows) if row["title"] == "Butternut Squash Soup"], "titleCounts": dict(collections.Counter(row["title"] for row in rows))})
# For addition, only noise rows are inserted initially, not target rows.
print({"case49InitialNoiseRows": len(r49["task"]["params"]["noise_row_objects"]), "case49RequestedNewRows": len(r49["task"]["params"]["row_objects"])})
```

Actual outputs:

```json
{"expected": "3-4 servings", "observed": "3-4 serving size of y", "ratio": 0.7272727272727273, "threshold": 0.9, "oracleFuzzyMatch": false}
{"initializedRowsFromParams": 32, "uniqueFullContentGroups": 31, "duplicateOccurrenceIndices": [[30, 31]], "butternutOccurrences": [0, 12, 24, 25, 26, 27, 28, 29, 30, 31], "titleCounts": {"Butternut Squash Soup": 10, "Raspberry Almond Smoothie": 1, "Beef Stir Fry": 1, "BBQ Chicken Quesadillas": 2, "Grilled Cheese with Tomato and Basil": 2, "Salmon with Dill Sauce": 1, "Stuffed Bell Peppers": 1, "Pan-Seared Salmon with Quinoa": 2, "Lentil Soup": 1, "Chicken Alfredo Pasta": 1, "Quick Fried Rice": 1, "Garlic Butter Shrimp": 1, "Mango Chicken Curry": 1, "Sweet Potato and Black Bean Tacos": 1, "Pesto Pasta with Peas": 1, "Lemon Garlic Tilapia": 1, "Veggie and Hummus Sandwich": 1, "Avocado Toast with Egg": 3}}
{"case49InitialNoiseRows": 10, "case49RequestedNewRows": 1}
```

Limitations: the fuzzy false result is conditional on DB containing the captured UI value; grouping proves initialized input equivalence, not post-agent persistence. No final DB/subscore was fabricated. No tests/build/lint were run. All proposed changes are separate from causes and remain unimplemented; only these diagnosis artifacts were created.
