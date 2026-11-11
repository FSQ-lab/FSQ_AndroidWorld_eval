# Retro Music failure analysis — current r15 campaign

Campaign: `amkernel-0.1.4-r15-current-stack-full-20261109T154403Z`. Scope: cases **058 RetroCreatePlaylist** and **060 RetroPlaylistDuration**, attempt1 only. Structured record: [domain-retro.json](domain-retro.json). Exact offline query code/output and limitations: [domain-retro-queries.md](domain-retro-queries.md). Original evidence remains immutable; no product/config/test changes, device/ADB/Appium/MCP execution, task replay, score rerun, suite, or package installation.

## Findings and confidence

| Case | Proven business outcome | Root diagnosis | Confidence / layer |
|---|---|---|---|
|058|Reopened named playlist has **one song, Dreamer's Awake**, not the requested three ordered songs; official reward0.|Broad containing-ancestor XPath can repeatedly select the first song's menu; per-add membership never checked. Actual clicked IDs absent.|Outcome confirmed; root **probable Agent locator/code-generation failure**.|
|060|Playlist displays **14 Songs •01:08:25**, not45–50min; action budget closes before removal is committed; official reward0.0.|Unmeasured Select all bulk addition, followed by unmeasured correction selection without a commit budget.|Outcome and **Agent aggregate-planning behavior confirmed**. Exact metadata/DB cause unknown.|

**Important task identity correction:** despite the name, **RetroPlaylistDuration is a mutation task**, not a duration question or InformationRetrieval task. The visible original prompt says “Create a playlist…with a duration between45 and50minutes.” Both classes are directly registered in `android_world/android_world/registry.py:175–178`. Information-retrieval registration contains neither class. The official evaluator does not compare the business answer with a numerical duration. Adding answer-normalization fixes would solve the wrong problem.

A separate **current-source oracle initialization omission** is confirmed: `RetroPlaylistDuration.initialize_task` skips its base initializer and internal-storage clearing. This is a reproducibility/isolation risk, **not demonstrated to cause the observed bulk-add failure**. It prevents deriving actual song durations from the declared seed. No historical r12 case is used.

## Evidence conventions and provenance

`R58` = `campaigns/amkernel-0.1.4-r15-current-stack-full-20261109T154403Z/episodes/058-RetroCreatePlaylist/attempt-1/result.json`; `L58` = the same attempt's `raw-private/agent-events.jsonl`; `R60/L60` likewise for060. Raw physical JSONL line numbers also identify receipt event sequence for the first finals. Each JSON timeline entry includes full original toolCall ID, start/end raw lines, execution count, code/excerpt, and structured response facts. The readable table below uses execution counts plus physical lines; it does not pretend the sanitized action ledger retained locators.

Actual responses are parsed from **tool_execution_end**, never inferred from code that intended to run or from outer isError alone. All25/31 Python responses have `kernelState=alive`. Three failed cells in each case are recorded, not treated as Runtime death.

The parent-owned [shared-offline-checks.json](shared-offline-checks.json) confirms original exact goals, initialized reference clock, valid nonempty string submissions, parser/archive equality and submission hash consistency. Current Harness source matches frozen 19-file digest `861905dba1d8dfab232cd977cdfbd3ac7837605a5199c982240ad40895599e66`. AndroidWorld result-declared revision is `55ddaf5edc6f6c25673aed343907d5b9dca66f84`; this analysis read current AndroidWorld source and records its file hashes in JSON, but does not independently establish a frozen oracle-file byte identity.

## Shared official oracle and lifecycle boundary

`retro_music.py:41–76` pulls `/data/data/code.name.monkey.retromusic/databases/playlist.db` and joins `PlaylistEntity pe` with `SongEntity se` on `pe.playlist_id=se.playlist_creator_id`. It projects playlist name, `se.title`, `se.duration` (duration_ms), and computes:

```sql
ROW_NUMBER() OVER (
  PARTITION BY pe.playlist_name ORDER BY se.song_key
) - 1 AS order_in_playlist
```

This is persisted SQLite evidence used by the evaluator, not merely the currently displayed UI order. Empty playlists contribute no rows because of INNER JOIN. **No pulled DB or evaluator row projection was archived for these attempts**, so reward0 is proof only that the official predicate returned false, not a reconstruction of actual rows/order/durations.

`runner.py:716–737` completes the agent and owned-session cleanup before `agent_protocol:745` and evaluator invocation `790–796`. Task teardown follows evaluation. The cleanup cells here contain only retained session ID + `driver.quit()` + exact successful cleanup return; they do not remove/rename/edit playlist contents. There is no captured post-quit app/DB observation, so absolute persistence invariance is unknown. Nevertheless, both business failures were visibly present **before quit**, not discovered only after cleanup. No evidence makes cleanup the primary cause.

## Case058 — RetroCreatePlaylist

### Goal, initialization and exact acceptance

Original prompt `L58:9`:

> Create a playlist in Retro Music titled "Hip Hop Bangers 270" with the following songs, in order: Golden Days, Dreamer's Awake, Hidden Paths

Params: name `Hip Hop Bangers 270`; target files in order `Golden Days.mp3`, `Dreamer's Awake.mp3`, `Hidden Paths.mp3`; seed916405052. Twelve noise names are retained in JSON and R58.task.params.

`retro_music.py:147–160` calls base initialization (time/apps/cache, seed), clears internal storage and playlist tables, writes all15 MP3s with title=file stem, randomized artists and requested durations180000–300000ms, scans music and closes app. Source-requested duration is immaterial to this acceptance criterion and is not actual encoded metadata proof.

`RetroCreatePlaylist.is_successful:162–170` calls `sqlite_validators.verify_playlist:30–70`:

1. Count all rows whose playlist name fuzzy-matches the requested name, ignoring case. Count must be **exactly3**.
2. For each expected zero-based index, find a matching-name row with **exact title equality** and query-computed `order_in_playlist==index`.
3. Return integer0/1; no partial name/order/membership subscores.

The fuzzy-name helper (`utils/fuzzy_match_lib.py:20–50`) lowercases strings and requires `difflib.SequenceMatcher(...).ratio()>=0.9`. This tolerates approximate playlist names, not approximate song titles. Other dissimilar playlist names do not automatically fail058. Exact requested accepted tuple is `(Golden Days,0), (Dreamer's Awake,1), (Hidden Paths,2)` within the matching playlist rows. Playlist creation alone is insufficient; export is not requested.

### Captured actions and narrowing causal chain

- Exec1 creates one UiAutomator2 session, returns completed/alive; exec2–7 navigate launcher and open observed Retro Music. Exec3 returns a **bounded repr instead of the intended facts**, which limits that particular observation but does not prevent later semantic launch. No generalized Runtime defect is assigned here.
- Exec8 (`L58:2134–2135`) sees no playlists. Exec9–11 create the exact name; exec11 response shows **0Songs •00:00**.
- Exec12 (`3334–3335`) sees Songs in this order: Dreamer's Awake first, Golden Days fifth, Hidden Paths seventh. All required targets exist in returned visible facts. Their bounds differ: Dreamer title `[163,326][951,383]`, Golden `[163,1038][951,1095]`, Hidden `[163,1394][951,1451]`.
- Exec13 (`3656–3657`) parent-inspection loop fails with NoSuchElementException on cell line4. Kernel survives. Exec14–15 query bounded XML snippets. Exec15 shows Golden title, artist Hana and menu **within the same closing android.view.ViewGroup**, menu bounds`[951,1034][1077,1160]`. This evidence was sufficient to distinguish row scope from arbitrary containing-screen scope.
- Exec16 (`4284–4285`, `call_izuPucEfeCh4OFZsQDtWAuSM`) submits:

```python
menu = driver.find_element(AppiumBy.XPATH,
    "//android.view.ViewGroup[.//*[@text='Golden Days']]"
    "//*[@resource-id='code.name.monkey.retromusic:id/menu']")
menu.click()
```

  Exec17 selects Add to playlist; exec18 chooses the named playlist. The only postcondition returned is12 song menus and Golden still visible; this does **not** prove which song was added.
- Exec19 (`5021–5022`, `call_CtlyaFbOoRh4tCnoGRwVWBEt`) repeats the same broad selector shape for Dreamer's Awake, then Add to playlist and picker confirmation. Exec20 (`5299–5300`, `call_KwM3kNmp7aqZ4HTl7txn5vfK`) repeats it for Hidden Paths. Both return `songMenus:12`, not playlist membership.
- Exec21 (`5653–5654`) is a SyntaxError from apostrophe quoting in the final verification expression; **nothing in the cell runs**. The pure compiler probe confirms this and exact cell line6. Exec22 (`5987–5988`) is the corrected cell: Playlists click and named row click execute, then the all-three-title wait times out. These are the two accepted actions in the ledger, not the failed compilation's intended actions.
- Exec23 (`6249–6250`) independently reads reopened playlist **Hip Hop Bangers270 /1Song •03:50 /Dreamer's Awake /Olivia**. Count1 + sole visible song supports a complete one-item UI collection. It does not expose SongEntity order keys or post-quit database contents.
- Exec24 (`6590–6591`) opens playlist-wide overflow: Play, Play next, Add to playing queue, Add to playlist, Rename, Delete, Save as file. This is not a membership repair. First business final at`6630` honestly reports incomplete. Exec25 (`6703–6704`) quits successfully; cleanup final at`6723` cannot overwrite business answer.

### Cause and responsibility, not merely terminal label

**Confirmed symptom:** requested membership and order are not present in the reopened UI. **Probable root:** row locator aliasing. The predicate matches every ViewGroup that contains the target somewhere below it. A broad containing view can also contain all song menus, so “first matching menu” can be the first visible Dreamer's Awake regardless of target. Repeating an add to that same song is consistent with final count1; app duplicate suppression is plausible, not directly proven.

The exact clicked menu element IDs are absent. Full historical DOM is not retained. The synthetic standard-library counterexample in queries Q3 shows the structural nonuniqueness, **not Appium replay or certainty about the historical result**. If correctly scoped distinct clicked IDs were later recovered, an app-side add/dedup/DB issue would need consideration. Current evidence makes Agent scoping failure stronger than Runtime or oracle failure.

Action exhaustion is excluded: only23/24 interactions were accepted; closure is`agent_finished`. The reference loop reports24steps because its control/final step is not the same measure as actual Appium interactions. All25 structured Python responses are alive (22completed,3failed). Python-call advisory30 and1560s business deadline did not cause termination.

### Actual accepted-action ledger

Every row below has status200 in R58.stepBudget.actions. Target labels are from submitted code; the ledger itself retains kind/path/status only. Full tool IDs are in JSON.

| Step | Kind | Intended action from code | Exec / raw lines |
|---:|---|---|---|
| 1 | actions | Swipe launcher app drawer | 3 / 910–911 |
| 2 | click | Focus launcher search input | 6 / 1576–1577 |
| 3 | input | Enter Retro Music | 6 / 1576–1577 |
| 4 | click | Open Retro Music icon | 7 / 1830–1831 |
| 5 | click | Open Playlists | 8 / 2134–2135 |
| 6 | click | Open playlist overflow | 9 / 2345–2346 |
| 7 | click | New playlist | 10 / 2571–2572 |
| 8 | click | Focus playlist name | 11 / 2999–3000 |
| 9 | input | Enter Hip Hop Bangers 270 | 11 / 2999–3000 |
| 10 | click | Create playlist | 11 / 2999–3000 |
| 11 | click | Open Songs | 12 / 3334–3335 |
| 12 | click | Open menu nominally for Golden Days; broad ancestor XPath | 16 / 4284–4285 |
| 13 | click | Add to playlist | 17 / 4461–4462 |
| 14 | click | Choose Hip Hop Bangers 270 | 18 / 4734–4735 |
| 15 | click | Open menu nominally for Dreamer's Awake; same broad ancestor shape | 19 / 5021–5022 |
| 16 | click | Add to playlist | 19 / 5021–5022 |
| 17 | click | Choose Hip Hop Bangers 270 | 19 / 5021–5022 |
| 18 | click | Open menu nominally for Hidden Paths; broad ancestor XPath | 20 / 5299–5300 |
| 19 | click | Add to playlist | 20 / 5299–5300 |
| 20 | click | Choose Hip Hop Bangers 270 | 20 / 5299–5300 |
| 21 | click | Open Playlists | 22 / 5987–5988 |
| 22 | click | Open Hip Hop Bangers 270 | 22 / 5987–5988 |
| 23 | click | Open playlist overflow; not a repair | 24 / 6590–6591 |

### Proposed fixes and falsification

1. **Agent locator correction (proposed):** bind the observed title to its nearest actual song-row container; require exactly one menu inside that row and disambiguate using observed same-row attributes/bounds. Do not select all arbitrary ancestors or replace the problem with guessed global indices. Preserve apostrophe-safe locator construction.
2. **Agent acceptance plan (proposed):** distinguish picker closure from membership. A bounded first-add readback can detect aliasing before three repetitions; final acceptance must compare exact count3 and ordered titles. Reserve correction budget rather than spend the last useful action opening unrelated playlist overflow.
3. Existing captured Skill already says a successful find is only a candidate, keep repeated-item fields together (`android-execution.md`, captured raw60 event55 content90–115), and derive/persistently compare identity/content/order (`amkernel-appium.md`, event54 content182–188). A concrete nearest-container example is an optional proposed refinement, **not proof missing policy caused the failure**, and no change was implemented/approved.

Falsification: distinct correct row/menu identities followed by continued one-song state would shift investigation to app-side insertion/dedup/persistence. Correct pre-quit ordered DB rows followed by score0 would shift toward cleanup or oracle translation. Neither evidence exists in the archive.

## Case060 — RetroPlaylistDuration

### Goal and official predicate: no answer-normalization scoring

Original prompt `L60:9`:

> Create a playlist in Retro Music titled "Reggae Rhythms 51" with a duration between 45 and 50 minutes using the provided songs.

Name `Reggae Rhythms51`, seed217200551. The10 source target files and5 noise files appear in the corpus table below. The visible prompt never exposes hidden target partition membership; source params are diagnostic evidence, not an execution route the agent was entitled to use.

`RetroPlaylistDuration.is_successful` (`retro_music.py:286–293`) reads the same joined rows, requires **every joined row's playlist name exactly equals** requested name (a row from another nonempty playlist immediately fails), sums raw`duration_ms`, and returns:

```python
float(45 * 60 * 1000 <= total_ms <= 50 * 60 * 1000)
# inclusive [2_700_000, 3_000_000] milliseconds
```

There is no order predicate, no exact title-set predicate, and no partial credit. Unlike058, name equality here is exact, not fuzzy. An empty playlist contributes zero and fails the lower bound. Hidden “noise” songs are not forbidden by the oracle if an actual chosen set meets duration and name conditions.

Registration and dispatch prove no official numeric answer comparison: both classes are single task classes, not`InformationRetrieval`; runner787–788 assigns stripped answer to`interaction_cache` **only** for that IR type. Official IR comparison (`information_retrieval.py:109–119`) is therefore inapplicable. The business envelope was valid, but its text does not create playlist state or change the reward.

### Initialization: intended metadata is not observed app duration

Current source260–284 clears playlist tables and constructs a nonnegative integer partition of**2,850,000ms=47.5min** across the10target files. The helper236–243 draws/sorts random cuts and allows zero-length parts. Noise requests each lie180000–300000ms. `user_data_generation.py:307–355` makes silent audio and exports MP3, then copies it; the scanner/app may expose encoded metadata, not necessarily the exact requested silence lengths. Neither generated MP3s nor actual scan metadata were archived.

The duration override does **not** call`super().initialize_task`, `TaskEval.initialize_task`, `clear_internal_storage`, or`random.seed`. It therefore bypasses normal TaskEval clock/app snapshot/cache/reset/initialized guard and seed initialization (`task_eval.py:142–157`), and unlike058 does not clear music storage. Campaign manifest says`paramsTransport:json`; runner `_task:471–484` does not seed when explicit params JSON is supplied. This is why a local replay of random seed217200551 would not recover the actual initialized duration set. Source provenance does not prove a specific missing file or stale item; this is a confirmed code-path omission and independent comparability risk.

### Complete-collection boundary and known data

**We cannot rebuild a complete actual14-song/duration collection from this archive.** That is a material missing-evidence result, not a license to invent benchmark answers.

Exec18 (`L60:5213–5214`) returns exactly12 visible titles. Exec22 (`6659–6660`) says14selected. No bottom scroll or full-corpus return exists. All5 declared noise titles are among those12. None of the31 Python responses contains a per-song duration detail; the first nonzero duration evidence is the final playlist aggregate. The exact14 members and all individual duration_ms values remain unknown.

| Source-declared song | Role | Seen among visible 12? | Actual duration |
|---|---|---|---|
| Silent Dreams | target partition member | yes | unknown |
| Hidden Paths | target partition member | yes | unknown |
| Whispering Wind | target partition member | not captured | unknown |
| Return to Paradise | target partition member | yes | unknown |
| Endless Summer | target partition member | not captured | unknown |
| Falling Feathers | target partition member | yes | unknown |
| Heartbeat Away | target partition member | yes | unknown |
| Orbiting Stars | target partition member | yes | unknown |
| Through the Storm | target partition member | not captured | unknown |
| Forever Young | target partition member | yes | unknown |
| Golden Days | noise | yes | unknown |
| Beyond the Horizon | noise | yes | unknown |
| Moonlight Sonata | noise | yes | unknown |
| City of Stars | noise | yes | unknown |
| Eternal Flame | noise | yes | unknown |

Declared15 minus visible12 = **Endless Summer, Through the Storm, Whispering Wind**. Under an additional no-contamination assumption only, exactly2of these3would complete14; the archive does not prove which. An apparent zero-length file/scan omission is a hypothesis, not a finding. Do not infer missing Endless Summer solely from title order without proving sort coverage, actual initialized corpus and boundaries. Duration initializer's storage omission means even the no-contamination assumption is not guaranteed.

### Captured behavior and why the failure is not rounding

- Exec2 (`699–700`) attempts lxml import, fails ModuleNotFoundError; exec3 uses standard-library ElementTree successfully. This was an optional agent import assumption, not a required amkernel dependency failure. No UI action consumed.
- Exec8 sees visible song titles and artists, not durations. Exec9 explores Songs overflow. Exec10–14 creates correct named empty playlist. Exec15 opens it, then times out because its wait incorrectly expects “not0Songs” after merely opening an empty playlist. Exec16 proves the session/UI survives and the playlist is still0Songs. Exec17 explores playlist overflow; exec18 returns to Songs.
- Exec19 (`5757–5758`) generic Selenium ActionChains click-and-hold is denied “Use one touch pointer and one contact cycle per step.” This is one **proxy policy denial, not an accepted action or gate rejection**. Exec20 uses explicit touch PointerInput and succeeds, selecting Beyond the Horizon.
- Exec21 opens selection overflow; exec22 Select all returns14selected. No duration evidence has been gathered. Exec23–24 add all14to Reggae Rhythms51.
- Exec25 (`7669–7670`) now reads **14Songs •01:08:25**, and exec26 (`8559–8560`) reopens target and reads the same total. This is first positive aggregate evidence, after indiscriminate bulk commit.
- `01:08:25` interpreted as HH:MM:SS is**4105s=68min25s**, exceeding50min by**1105s=18min25s**. Official predicate uses inclusive raw milliseconds; it does not round to minutes. App formatter implementation is not archived, but ordinary second rounding cannot explain this overshoot: even a conditional nearest-second lower bound4,104,500ms exceeds3,000,000ms by1,104,500ms. No exact source/app per-song conversion was demonstrated.
- Exec27 selects Beyond the Horizon; exec29 adds City of Stars, Eternal Flame, Falling Feathers to selection, resulting4selected. Three are declared noise, Falling Feathers is a target partition member; the agent has no numeric contribution evidence for this removal set. Selecting is **not removal**.
- Exec30 (`9791–9794`) uses the30th accepted action to open selection overflow. Returned options include **Remove from playlist**, but it is never clicked. No deletion/removal/save result exists. Raw9801 delivers exhaustion control; raw9855 business final honestly reports incomplete. Exec31 quits, preserving no further edits.

The official zero is consistent with visible overshoot, but without DB rows its exact predicate branch is unknown; another nonempty playlist or post-quit difference cannot be excluded absolutely. Visible failure and aggregate planning are independently evidenced, not derived solely from reward.

### Actual accepted-action ledger and denial/exhaustion sequence

All30 accepted actions have status200. Breakdown:23click,2input,3back,2actions. One unsupported ActionChains denial before step18 is separate; accepted count remains30and gate rejectedActionCount0. The final accepted call returned completed/alive before the business submission; no invented missing result or post-exhaustion mutation. The31Python calls exceed advisory30, which explicitly does not affect reward. Business deadline was not reached (termination retains over1500business seconds).

| Step | Kind | Intended action from code | Exec / raw lines |
|---:|---|---|---|
| 1 | click | Open launcher Search | 4 / 1147–1148 |
| 2 | input | Enter Retro Music | 5 / 1403–1404 |
| 3 | click | Open Retro Music icon | 6 / 1638–1639 |
| 4 | click | Open Songs | 8 / 2282–2283 |
| 5 | click | Open Songs overflow | 9 / 2706–2707 |
| 6 | back | Close Songs overflow | 10 / 2971–2972 |
| 7 | click | Open Playlists | 10 / 2971–2972 |
| 8 | click | Open playlist overflow | 11 / 3218–3219 |
| 9 | click | New playlist | 12 / 3528–3529 |
| 10 | click | Focus playlist name | 13 / 3713–3714 |
| 11 | input | Enter Reggae Rhythms 51 | 13 / 3713–3714 |
| 12 | click | Create playlist | 14 / 3949–3950 |
| 13 | click | Open empty Reggae Rhythms 51 | 15 / 4317–4318 |
| 14 | click | Open playlist overflow | 17 / 4834–4835 |
| 15 | back | Close playlist overflow | 18 / 5213–5214 |
| 16 | back | Return to Playlists | 18 / 5213–5214 |
| 17 | click | Open Songs | 18 / 5213–5214 |
| 18 | actions | Touch long-press Beyond the Horizon | 20 / 6173–6174 |
| 19 | click | Open selection overflow | 21 / 6494–6495 |
| 20 | click | Select all: 14 selected | 22 / 6659–6660 |
| 21 | click | Open selection overflow | 23 / 7064–7065 |
| 22 | click | Add to playlist | 23 / 7064–7065 |
| 23 | click | Choose Reggae Rhythms 51 | 24 / 7335–7336 |
| 24 | click | Open Playlists; 14 Songs • 01:08:25 | 25 / 7669–7670 |
| 25 | click | Open Reggae Rhythms 51; same total | 26 / 8559–8560 |
| 26 | actions | Long-press Beyond the Horizon; 1 selected | 27 / 8890–8891 |
| 27 | click | Select City of Stars | 29 / 9578–9579 |
| 28 | click | Select Eternal Flame | 29 / 9578–9579 |
| 29 | click | Select Falling Feathers; now 4 selected | 29 / 9578–9579 |
| 30 | click | Open selection overflow; Remove from playlist is visible, not clicked | 30 / 9791–9794 |

### Cause, proposed fixes, and independent oracle risk

**Confirmed root at behavior level:** unmeasured Select all was used before a numeric acceptance plan, then correction actions lacked measured contributions and a remaining commit/readback budget. It is not proof the agent believed14songs necessarily meant47.5min, but its executed route did not establish the needed measure before mutation.

The captured shared Skill already requires aggregate numeric evidence, states that a selected count/titles/empty-container zero do not prove an aggregate, and permits only safe reversible **in-budget small batches** when increments are unknown (raw60 event54, returned content247–258). Captured Android guide explicitly budgets navigation/input/confirmation/save/readback/correction (event55 content271–276). The trace deviates from existing guidance; a Skill edit remains proposed/decision_needed, not an established missing invariant. No Runtime blame from wrong total or source-seeded metadata mismatch is warranted.

Proposals are independent from causal claims and are fully structured with invariants/risks/falsification in JSON:

1. **Agent numeric plan (proposed):** get reliable per-song contributions from a currently observed allowed Details path/visible numeric surface, or a genuinely in-budget reversible small aggregate batch; compute a set with interior margin before commit. No hidden oracle subset or invented duration API. The archive does not prove a complete low-action route exists within30steps, so do not promise it.
2. **Agent budget plan (proposed):** budget correction through Remove from playlist, confirmation if required, and final target readback. Distinguish Remove from playlist from destructive Delete from device. Four selected rows or an open menu are not a saved-state correction.
3. **Oracle-owner decision needed:** restore intended TaskEval base initialization and explicit storage isolation, or otherwise version/document equivalent deterministic setup; separately archive bounded actual initialized song metadata and evaluator row projections in future campaigns. Do not naively call the parent RetroCreatePlaylist initializer, which writes the wrong random-duration dataset before overwrite. Changing setup changes benchmark instances and comparison baselines; no patch or coordinated owner approval is claimed.

Falsification: actual pre-add numeric evidence predicting45–50min would point to metadata/app mismatch instead; a captured removal commit after9794would change the ledger, but none exists; frozen source/init traces showing correct base initialization/isolation would narrow the source-level omission concern. Absence of persistent evidence is an explicit limitation, not permission to claim success or blame cleanup.

## Business-submission precedence and exact conversion

-058first business final is raw line**6630**, receipt phase`business`, received230.8372605420882s, valid string: “Incomplete: playlist Hip Hop Bangers270 contains only Dreamer's Awake; the requested three-song order was not established.” (Exact spacing/text/envelope retained in JSON/raw archive.)
-060first business final is raw line**9855**, receipt phase`finalization`, received329.42308699991554s, valid string reporting14songs and01:08:25. Both`result.agent.answerSubmission.ignoredFinalMessages=1` correspond to later cleanup finals, not replacement answers.

`omp_supervisor.py:211–234` selects the first assistant stop while no receipt exists, cleanup is not seen, and receipt time is within cutoff. `submission.py:45–93` parses finite JSON, requires dictionary/taskOutcome nonempty string, then **only strips leading/trailing whitespace**. Numeric strings are not coerced; neither case submits a number/object. The saved`rawText`, complete parsedValue and exact stripped answer are in each business-submission.json and copied in structured case record. Shared checks prove parser/archive fidelity. There is no unit conversion or “68:25answer vs47.5expectedanswer” comparison to fix in these mutation tasks.

## Remaining unknowns and hand-off

058unknown: actual clicked menu identities, exact stored SongEntity rows/song_key order, app duplicate-suppression behavior, post-quit persistence.060unknown: full14song set, all actual individual durations, missing/stale initialization items, exact formatter/codec offsets, post-quit/evaluator rows and any other nonempty playlist. No purported successful song subset is reconstructed.

Completed only diagnosis artifacts. No build/lint/test suite/device checks were run or are needed to prove these archival findings. Any future product/Skill/oracle fix needs its own owner decision and acceptance verification; this report does not claim it exists or is approved.
