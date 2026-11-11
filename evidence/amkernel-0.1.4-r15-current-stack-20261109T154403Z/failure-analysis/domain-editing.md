# Editing-domain failure analysis

Campaign: `amkernel-0.1.4-r15-current-stack-full-20261109T154403Z`.
Scope: **014 ExpenseAddMultipleFromMarkor**, **023 MarkorAddNoteHeader**, **024 MarkorChangeNoteContent** only.

## Findings and confidence

| Case | Established outcome | Causal finding | Confidence boundary |
|---|---|---|---|
| 014 | Both reimbursable entries saved and reopened in app detail views; reward 0; historical oracle warns expected Laundry missing | Source note adds `. Reimbursable.` to target note fields, while oracle compares unchanged original notes. Faithful source copying fails the 0.9 fuzzy predicate | Source inconsistency and comparator rejection confirmed; actual final DB values not archived, so precise episode field-level causation probable |
| 023 | Correct 67-character header/content string visible after Save; no rename; 12/12 actions | Ungrounded title/settings rename exploration reached actual contextual Rename only at last allowed action | Missing rename behavior confirmed; historical disk existence/content probable/unknown rather than a captured filesystem result |
| 024 | Correct 20-character replacement visible after Save; no rename; 11/12 actions | Same wrong rename workflow; voluntary incomplete final despite one action unused | Missing rename behavior confirmed; **not actual budget exhaustion**; disk bytes unknown |

The reports do **not** attribute these failures to Runtime death. All 60 structured execution responses in these three cases report `kernelState=alive`: 49 completed, 11 failed. Failures are explicit client/API, syntax, selector/wait or proxy-protocol errors with successful continuation. These are not missing tool results or fabricated successful calls.

## Evidence and method

`domain-editing.json` is the detailed machine-readable deliverable. Each record contains complete exact raw Python request code, actual returned structured response facts/errors, full toolCall IDs, 1-based physical JSONL line anchors, stages/receipt clock anchors, oracle source symbols/ranges, action ledger mapping, uncertainty, responsibilities and proposed fixes. Original result/events/submission files were never modified.

The large raw JSONL files (approximately 103 MB, 64 MB and 91 MB) were streamed. Only complete `tool_execution_start/end` records and relevant messages were extracted; message-update snapshots, encrypted thinking and private/base64 trees were not dumped. `tool_execution_start.args.content` is parsed as the original JSON Python request. `tool_execution_end.result.content[].text` is parsed as the returned PythonResponse. Returned values are kept distinct from interpretation; `status=failed` is not treated as rollback.

`domain-editing-queries.md` records exact executed offline probe code and actual output. It verifies all 102 source-note rows against **actual initialized parameters**, isolates the exact pure source comparator with AST, and compares actual captured editor strings. It never imports device modules or queries a device. No task/score replay, tests, build, formatter, ADB, Appium or MCP execution was performed.

Source line references describe the current checkout; SHA256 values are in JSON. Parent receipt `shared-offline-checks.json` reports frozen/current harness-source digest agreement, original prompt/clock/string contract and parsing/receipt checks. That harness digest is **not** represented here as an independent proof of frozen AndroidWorld oracle-source equivalence. Historical raw prompt/cells/results and the expense oracle warning provide the episode evidence.

### Clock and submission

Each exact initial user prompt is physical raw line 9. It includes the corresponding `result.task.goal`, initialized `2023-10-15T15:34:00+00:00` reference clock, UTC timezone, explicit UI-action allowance, native-interaction restrictions and first-business-final nonempty string contract.

| Case | First business final raw line | Receipt seconds | Evaluator start Unix | Cleanup cell raw start/end |
|---|---:|---:|---:|---|
| 014 | 6014 | 224.76301295799203 | 1794247487.9014661 | 6089–6090 |
| 023 | 3558 | 194.24156875000335 (finalization phase) | 1794249347.257635 | 3628–3629 |
| 024 | 3927 | 181.25186045805458 | 1794249563.627269 | 3997–3998 |

The archived business answer is the first assistant `stop`, not later cleanup prose. All three archived submissions are valid string taskOutcome contracts. These are state tasks: none of these oracles scores the prose answer instead of saved app/file state. No raw-to-stripped answer conversion explains a failure here.

Raw tool events do not carry wall-clock timestamps; executionCount/durationMs are real returned Runtime facts, not invented wall timestamps. JSON retains the actual result.stages timeline and receipt anchors.

Parent source analysis places `adapter.finish` and owned-session cleanup before official evaluator, and task teardown after evaluator (`runner.py:716–737,745,790–796`). Each dedicated `driver.quit()` returns true before evaluation. No cleanup cell restores business content or performs rename. Post-quit disk state is not captured, so absence of cleanup rollback evidence is not proof of persistent bytes. Later task teardown clears these app data and cannot be used to reconstruct historical final state now.

## 014 — ExpenseAddMultipleFromMarkor

### Exact initialized transaction collection

Visible task: “Go through the transactions in my_expenses.txt in Markor. Log the reimbursable transactions in the pro expense.”

Official source `task_evals/single/expense.py:328–360` uses two target rows and 100 noise rows. The expense table is cleared, noise is inserted, and `before` is snapshotted by `SQLiteApp`/`AddMultipleRows` (`common_validators/sqlite_validators.py:257–310`). The source note consists of copies of targets with `. Reimbursable.` appended to note, plus all noise, shuffled, written under `/storage/emulated/0/Documents/Markor/my_expenses.txt` by `write_to_markor`.

The source note was **actually read in full**, not inferred from params or a random seed: raw L1188–1189, execution 6, `call_PlkNLBnz2WNT6r6Gs96twEnK`. Returned editor text is 4,608 characters, 103 lines including header, 102 data rows, no terminal LF; SHA256 `ebb5adfcb8b638a179403c9d13d8bcd9b7168587eb516730fe88a4e3d25d35ca`. Header is `name|amount_dollars|category_name|note`. The first data row is Educational/$296.94/Donation/Want to have; last is Jeans/$139.3/Clothes/Want to have. Every parsed row equals the actual initialized target-plus-noise multiset; missing and unexpected sets are empty. Full observed text and all 102 rows are preserved in JSON.

Exactly two rows contain the classification marker:

| Physical source-note line | Name | Amount | Category / DB ID | Source note | Oracle reference note |
|---:|---|---|---|---|---|
| 59 | Laundry | $96.3 = 9630 cents | Clothes / 8 | `Urgent. Reimbursable.` | `Urgent` |
| 72 | Car Insurance | $303.01 = 30301 cents | Transportation / 7 | `I may repeat this. Reimbursable.` | `I may repeat this` |

This reconstructs the complete source collection and selection boundary: there is no unexplained third reimbursable transaction, missed page, or premature end of note.

### Actual transfer and historical persistence evidence

- Execution 12 raw L2934–2935 types Laundry, `96.3`, `Urgent. Reimbursable.`, then hides keyboard. A `UiScrollable` lookup is rejected because a locator cannot hide multiple interactions. **Those prior field mutations remain.** Execution 13 L3091–3092 returns all three exact typed field values.
- Executions 14/15 swipe the category carousel and click Clothes. Returned text nodes all report `selected=false`; these text-node flags do not prove the actual category-selection state. Execution 16 L3726–3727 saves; Home list includes Laundry/96.3.
- Execution 17 L4305–4306 types Car Insurance, `303.01`, `I may repeat this. Reimbursable.` and hides keyboard, returning exact fields. Executions 18 and 19 fail AST compilation with unmatched `)` **before** their initial swipe, so they do not save or duplicate the entry. Execution 20 L5239–5240 swipes, clicks Transportation and saves; Home lists both target names/amounts.
- Execution 21 clicks Car Insurance then wrongly waits for an editable field; timeout does not undo the click. Execution 22 L5699–5700 captures the actual **Expense Detail** view: Car Insurance, `303.01`, USD, `I may repeat this. Reimbursable.`.
- Execution 23 L5970–5971 closes Car detail and reopens Laundry: returned name Laundry, amount `96.3`, note `Urgent. Reimbursable.`, title Expense Detail.

Reopened record-detail views are materially stronger persistence evidence than a filled form, but are **not a DB dump**. Category IDs, exact cents conversion, full table size and preservation of 100 original noise rows are not captured. The snapshot after quit is also absent.

### Oracle contradiction and pure causal probe

`_ExpenseAddMultiple.validate_addition_integrity` (`expense.py:264–285`) compares `name,amount,category,note`, fuzzy only for name/note. `AddMultipleRows.is_successful:304–310` passes **unchanged** `self.params[ROW_OBJECTS]`, not the source-note marker-bearing copies.

`validate_rows_addition_integrity:149–192` requires every reference row to match some final row, exact final length `before+2`, and every original row unchanged. `fuzzy_match_lib.py:20–51` uses case-insensitive `difflib.SequenceMatcher(...).ratio() >= 0.9`. No per-expense subscore exists.

The exact isolated pure comparator produces:

- `Urgent` vs `Urgent. Reimbursable.`: 0.4444444444444444 → false.
- `I may repeat this` vs `I may repeat this. Reimbursable.`: 0.6938775510204082 → false.
- Constructed candidates with actual target cents/category and **observed** marker-bearing notes fail; same candidates without classification suffix pass. This construction isolates the note mismatch; it does not pretend the unarchived final DB equals the construction.

Historical evaluator output independently corroborates the reference side: `evidence/.../run-full.log:279` says:

```text
WARNING:absl:Expected row Expense(name='Laundry', amount=9630, category=8, note='Urgent', created_date=1697320800000, modified_date=1697320800000, expense_id=-1) not found in the 'after' state.
```

This proves the historical missing-reference branch, not merely a zero label. It still does not print the row that was present, so category/cents error in addition to the note discrepancy cannot be excluded. The incidental ffmpeg warning immediately before it is not evidence that media infrastructure caused this SQLite failure.

**Root:** confirmed task source/reference inconsistency and comparability risk; probable concrete episode score cause. **Not root:** selection coverage, action exhaustion, Runtime failure, answer parsing.

### Exact accepted-action budget

33/60 interactions; no exhaustion, no rejected budget admission, 27 unused.

| Accepted steps | Count | Actual purpose |
|---|---:|---|
| 1–3 | 3 | Drawer swipe, Markor launch, source note open |
| 4–8 | 5 | Back twice, Home key, drawer swipe, Pro Expense launch |
| 9–19 | 11 | Add Laundry; three focus/input pairs; hide keyboard; category swipe/click; Save |
| 20–30 | 11 | Add Car; three focus/input pairs; hide keyboard; category swipe/click; Save |
| 31–33 | 3 | Open Car details, close, open Laundry details |

Breakdown: 4 gesture actions, 18 clicks, 2 Back, 1 Home press, 6 inputs, 2 hide-keyboard. The rejected UiScrollable observation is a protocol denial outside this accepted ledger; syntax failures consume no UI action. `referenceStepsExecuted=34` includes terminal loop accounting and is not the 33 actual mutations.

Business final correctly names both entries, but overstates category certainty: categories were clicked, not reopened in a category-bearing persistent view. The notes were copied literally; there is no visible instruction that reimbursable text is transient selection metadata to omit.

### Proposed correction choices

Decision required, not an already approved fix:

1. **Align references with source notes**: make the target reference notes include the same marker the user sees, while retaining cents/category strictness and unchanged-noise validation. This matches natural “log these transactions” copying.
2. **Explicit metadata policy**: preserve original reference notes but clearly label marker as classification metadata in goal/representation and tell the agent which data to copy. Changes prompt/comparability rather than silently expecting hidden stripping.
3. **Task-local marker normalization**: accept a narrowly defined marker-present/absent equivalence. Do not lower global fuzzy threshold or weaken unrelated tasks.

A bounded before/after comparison diagnostic captured before teardown would resolve the remaining historical uncertainty. It requires a privacy/retention decision; this investigation adds no instrumentation. A marker-policy fix is falsified as a sufficient episode fix if the actual historical row also has incorrect cents/category or is absent.

## 023 — MarkorAddNoteHeader

### Required file/content boundaries

Original full name `2023_08_10_neat_wolf.txt`; destination `busy_wolf_2023_07_23.txt`; header `RnI8sP34yDzJQbvkfplR`; source sentence `Weekend plans: Hiking trip to Blue Mountain.`.

`markor.py:754–774` clears directory via base initialization, creates the exact target and 1–20 variant noise files. `file_utils.create_file:134–169` uses shell echo, adding LF. Actual source editor raw L1478, execution 8, contains `Weekend plans: Hiking trip to Blue Mountain.\n`; the trailing newline is observed, not guessed.

Oracle `markor.py:784–806` demands original path absent, destination path present, then **exact** CR-normalized `header + "\n\n" + original_content + "\n"`. The 67-character requested result is:

```json
"RnI8sP34yDzJQbvkfplR\n\nWeekend plans: Hiking trip to Blue Mountain.\n"
```

No content-only partial score is awarded. A correct editor string cannot compensate for missing rename.

### Exact action chain and why rename was missed

- Exact accessibility row `File 2023_08_10_neat_wolf.txt ` opens the target at L1317–1318; source text matches params. It is not a similarly named wolf backup.
- Execution 9 L1683–1684 constructs `expected = header + "\n\n" + old`, then calls nonexistent `editor.set_value(expected)`. Returned AttributeError occurs before editor mutation/Save; kernel remains alive.
- Execution 10 L1886–1887 uses `clear(); send_keys(expected)`, checks editor equality, clicks Save and returns the exact 67-character string with `matchesExpected=true`. Offline exact comparison agrees with oracle content expectation, **in UI only**.
- Execution 11 L2104–2105 clicks document title, then waits merely for an EditText. The existing note editor already satisfies that wait. Returned facts show the same original document, not a filename dialog. The “Opening note rename dialog” intent is not evidence of such a dialog.
- Execution 12 opens More options: File settings, Share, Tools, Info, Reload. Execution 13 selects File settings and waits for **no ListView**. The replacement File settings menu also has a list, so this postcondition times out. Execution 14 returns Wrap words, Syntax highlighting, Auto-format, Font Size, Format, Preview—the wrong surface for rename.
- Execution 15 backs to editor, original title unchanged. Execution 16 tries default Selenium ActionChains click-and-hold; proxy rejects its non-single-touch payload with “Use one touch pointer and one contact cycle per step.” No accepted UI action is recorded for it.
- Execution 17 L3310–3311 backs to file list. Visible wolf candidates include exact original, `_2023_02_21` variant and `_backup`. This is a substring-filtered visible sample, not the complete noise directory.
- Execution 18 L3512–3515 uses native `mobile: longClickGesture` on the **exact original**. The response finally exposes `Rename`, resource `action_rename_selected_item`, and `Selected 2023_08_10_neat_wolf.txt`. No rename dialog, destination input or confirmation follows.
- During this admitted long-click, raw L3513 steering announces action exhaustion; L3515 still delivers the actual completed result. The first final at L3558 honestly states header updated but rename incomplete. Cleanup execution19 quits only.

The actual causal error is ungrounded rename navigation and false-positive transition detection, not a mysteriously too-small action number. It used the whole allowance before reaching the correct contextual action. The loaded Skill file/notes section already required distinguishing displayed title from full filename and preserving line breaks; missing behavior is not proof the Skill lacked that invariant.

### Accepted-action ledger

12/12; exhausted true; closure `step_budget`. Python cells: 19, including cleanup.

| Step | Action | Cell |
|---:|---|---:|
| 1 | Drawer swipe | 3 |
| 2 | Markor click | 5 |
| 3 | Exact original file click | 7 |
| 4 | Clear editor | 10 |
| 5 | Input expected header/content | 10 |
| 6 | Save | 10 |
| 7 | Ineffective document title click | 11 |
| 8 | More options | 12 |
| 9 | File settings | 13 |
| 10 | Back settings | 15 |
| 11 | Back editor to list | 17 |
| 12 | Exact file native long-click; Rename exposed | 18 |

AttributeError and rejected ActionChains do not appear in accepted ledger. `rejectedActionCount=0` is gate accounting, not a claim that no unsupported command was rejected. No mutation was attempted after the gate closed.

### Persistence limit, root and fixes

The original full-name row remains in the list after Save/navigation and is selected at the end. No rename request exists in raw history. Thus missing rename behavior is confirmed and original-path oracle rejection is probable. The oracle filesystem branch and file bytes were not captured after quit; do not promote UI “savedField” naming into disk proof. No cleanup restore occurred; teardown later deletes files.

Propose using the observed exact-file contextual Rename path earlier, with native one-touch selection, then inspecting the actual filename/extension fields. Avoid unsupported set_value and wait for rename-specific identity, not any EditText. Preserve the observed terminal LF and blank line exactly.

A content-first plan of opening target, clear/input/Save, Back, native long-click, Rename and dialog editing is a **proposed** action allocation, not demonstrated successful 12-step execution: the rename dialog never opened, so field count/extension handling remain unknown. Rename-first is another option but may cost more navigation. Skill reinforcement is proposed only; no coordinated amkernel owner fix has been approved here.

## 024 — MarkorChangeNoteContent

### Actual original and exact requested changes

Original `strong_jacket_h1hZ.txt`; destination `lively_fox_2023_03_22.md`; replacement `inNqu8UNNtyXBHCZpYp7`.

Unlike header task, initial random content is not in params. It is **captured** by raw L2186, execution8: `pZwh1hZwvmPj5inNqu8U\n` (20 generated characters plus LF). No random regeneration was used to guess it.

Oracle `markor.py:700–721` first requires original path absent, new full path present, then `check_file_content` with default fuzzy matching. That helper removes CR, strips persisted content and compares to requested text at 0.9 threshold. Therefore the exact LF requirement from case023 does **not** transfer to this task. The `.txt`→`.md` filename boundary does matter, but no rename/extension field was ever opened.

### Raw execution chain

- Execution2 fails importing unnecessary `lxml` before any action; execution3 uses standard-library ElementTree successfully. This is a recovered observation issue, not device failure.
- Launcher Search click, input `Markor`, app click; execution7 finds exact target title but relative XPath parent `..` lookup throws before click. Execution8 then opens the exact accessibility row `File strong_jacket_h1hZ.txt `; original content and title captured.
- Execution9 repeats unsupported `editor.set_value` and gets AttributeError before mutation. Execution10 L2615–2616 performs clear/input; exact requested text returned. Execution11 L2873–2874 clicks Save, returns original title and requested replacement.
- Execution12 opens More options; its tuple-list return is bounded non-JSON representation, **not visible menu evidence**. Execution13 explicitly returns labels File settings, Share, Tools, Info, Reload. Execution14 chooses File settings; facts show only formatting options.
- Execution15 L3662–3663 backs to editor and returns title `strong_jacket_h1hZ`, `clickable=false`, `longClickable=false`.
- Despite this evidence, execution16 L3893–3894 clicks title. Returned facts still show the same original title and the replacement editor. No rename dialog exists.
- Business final L3927 says content saved but filename could not be changed “within the UI interaction budget.” This is an incomplete self-report, **not evidence of an exhausted gate**. Execution17 quits.

### Action ledger and root distinction

11/12 accepted, exhausted false, rejectedActionCount 0, closure `agent_finished`; one action unused. Search/launch/open cost 4; clear/input/Save cost 3; options/File settings/Back/ineffective title click cost 4. No contextual file-list selection, Rename click, destination name input or confirmation occurred.

The remaining single interaction would not by itself finish an unopened multistage rename. That does not make budget exhaustion the root: the ledger proves the Agent voluntarily stopped, and four post-save interactions went down the wrong route. The task was not silently marked successful—final admits partial outcome—but the required two-part behavior was not delivered.

Original content replacement is confirmed in editor after Save and again after unsuccessful title click. It is not reopened from disk. Original title remains throughout, and no rename request was issued, making original-path-still-exists the probable zero branch. Final filesystem bytes and oracle per-branch trace remain unknown.

**Root behavior:** wrong rename route and continuation/acceptance planning. **Not established:** Runtime defect, intrinsic impossibility in12 actions, saved-file corruption, hidden extension-only mistake or answer coercion.

Propose allocating actions for both text and exact full filename before mutation, using a lower-cost drawer launch when observed and the actual file-list contextual action rather than non-clickable document title. Case023 proves the same APK exposes contextual Rename, but this is cross-case mechanism evidence—not an observed024 dialog. Inspect separate name/extension fields before entry; do not assume `.md` from a title. Rename-first vs edit-first requires observing the actual dialog/action count; no completion feasibility claim was tested. Report actual gate status and distinguish Save/editor evidence from filesystem persistence.

## Ownership and next decisions

All edits are diagnosis artifacts under this domain only. No product, Skill, configuration, source, tests, manifest, original evidence or device state was changed.

- **014:** owner decision on visible-marker semantics and benchmark comparability; retain original score/history. A task-local explicit policy is preferable to global fuzzy weakening.
- **023/024:** Agent workflow failures; Skill changes remain proposed, not proof of absent guidance. amkernel owner supplies its separate mechanism/fix assessment.
- **Evidence gap:** bounded pre-teardown filesystem/DB predicate evidence would discriminate persisted-state alternatives. Current historical evidence cannot be recreated from a fresh device or random seed.
- **Checks for integrator:** inspect these three JSON records and their exact raw anchors; no product test/build is needed to consume this diagnosis. Offline probe output is already recorded; no formal task or score rerun is authorized.
