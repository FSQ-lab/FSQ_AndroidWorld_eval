# 051 RecipeDeleteDuplicateRecipes2 — offline scorer/source proof

## Scope and evidence classes

- **Direct records:** original `result.json`, the 23 extracted `python_exec` calls, and installed source files. No device, Appium, ADB, env, task initialization, session, full scorer, or live DB access was used.
- **Parameter/source-derived:** initialization order, duplicate equivalence, official predicate semantics, row-group composition, and target placement. These are conclusions from source plus the original task parameters, not from a retained DB dump.
- **Synthetic/offline reproduction:** `Recipe` objects built from the original parameters with synthetic sequential `recipeId` values, then passed through the installed pure `validate_deletion_integrity` logic.
- **Unknown runtime DB:** actual runtime `recipeId` allocation, actual SQLite row order, exact card-to-row identity for each tap, and the historical after-DB/final DB. No retained proof for these exists in this attempt.

## Exact original identity

- Campaign/episode/attempt: `campaigns/amkernel-3388314-r12v2-headless-full-ready-20261107T004632Z/episodes/051-RecipeDeleteDuplicateRecipes2/attempt-1`
- Task: `RecipeDeleteDuplicateRecipes2`, complexity `2.4`
- Parameters: 2 `row_objects` + 10 `noise_row_objects`; canonical params SHA-256 `2a787dbe74070eea35fcd293f7237d759a86adddd09f73155cf523681396626e`
- Original result SHA-256: `084f42fc87da1955b77ce31bcc2a5da89d97abf6a7f221c000baedd9feaf9691`
- Normalized events SHA-256: `8a5b95b38a50f8ac9a1048ab663cd1a35261aa38f151506b5f5b7744973a75d6`
- Raw events SHA-256: `8f1323cdda23ad7ff36d1cf14c31a8d0f3f1c4167b64ae3a1940f2fb43fb27be`
- First complete extracted streaming call: source line `404`; response end line `409`.
- Observed original outcome: `officialReward = 0.0`, `invalidReason = null`, `error = null`, evaluator implementation `android_world.task_eval.is_successful`, evaluator duration `0.11 s`.
- Original final text claimed two remaining Caprese recipes with different descriptions and that one duplicated instance remained. That is the agent's claim, not a DB observation.
- Cleanup: `taskTearDown = completed`, `environment = closed`, agent session `closed`/`absent`, `agentQuitReturned = true`, Appium audit shows one created and one deleted session, no active sessions.

## Source identity and immutability

Installed distribution: `android_world 0.1.0`, revision `55ddaf5edc6f6c25673aed343907d5b9dca66f84`, immutable install from `file:///Users/qunmi/Documents/FSQ_LAB/FSQ_AndroidWorld_eval/android_world` (`editable=false`).

| Installed file | SHA-256 (base64 RECORD form) | RECORD match |
|---|---|---|
| `android_world/task_evals/single/recipe.py` | `9UdVa5aBJnw0oZ-l_DFlkQYJZqE4yPNmxLHheDyYgwk` | yes |
| `android_world/task_evals/common_validators/sqlite_validators.py` | `e5MqzS4Z8dT0POobrfJqzi7TNjJYriaFDRsJiJv6nXg` | yes |
| `android_world/task_evals/utils/sqlite_schema_utils.py` | `07HXlrH6rb3tx45_kZfw7ifj7r8O3UWXzVnz0PbjCVs` | yes |

The installed files were read only. All three hashes match `android_world-0.1.0.dist-info/RECORD`; no production or skill file was edited.

## Source anchors

- `single/recipe.py:183` `RecipeDeleteDuplicateRecipes`
- `single/recipe.py:200` `RecipeDeleteDuplicateRecipes.validate_deletion_integrity`
- `single/recipe.py:214` base duplicate params generation
- `single/recipe.py:229` `RecipeDeleteDuplicateRecipes2`
- `single/recipe.py:245` `RecipeDeleteDuplicateRecipes2.generate_random_params`
- `common_validators/sqlite_validators.py:73` `validate_rows_removal_integrity`
- `common_validators/sqlite_validators.py:257` `SQLiteApp.initialize_task`
- `common_validators/sqlite_validators.py:348` `DeleteMultipleRows.initialize_task`
- `common_validators/sqlite_validators.py:360` `DeleteMultipleRows.is_successful`
- `common_validators/sqlite_validators.py:383` `DeleteDuplicateRows._validate_candidates`
- `common_validators/sqlite_validators.py:400` `DeleteDuplicateRows._validate_initial_state`
- `common_validators/sqlite_validators.py:411` `DeleteDuplicateRows.initialize_task`
- `utils/sqlite_schema_utils.py:198` `Recipe`
- `utils/sqlite_schema_utils.py:484` `get_random_items`

## Initialization trace

1. `SQLiteApp.initialize_task` clears the DB, calls base initialization, clears again, and inserts `noise_row_objects` when present. With these params, 10 noise rows are inserted first.
2. `DeleteMultipleRows.initialize_task` inserts the 2 `row_objects`, reads `before = list_rows(env)`, and sets `rows_to_delete = before[-2:]`. The targets are therefore the last-added rows by source position, not necessarily any particular runtime IDs.
3. `DeleteDuplicateRows._validate_initial_state` requires exactly `2 + n_rows_noise = 12` rows.
4. `DeleteDuplicateRows.initialize_task` validates the candidate pair and assigns `duplicate_rows = rows_to_delete`.
5. `_validate_candidates` compares every dataclass field except `db_key` (`recipeId`). Exact duplicate equivalence therefore means all of `title`, `description`, `servings`, `preparationTime`, `source`, `ingredients`, `directions`, `favorite`, and `imageName` are equal.

The original params indeed contain a target pair equal on all non-ID fields. Their synthetic IDs are 11 and 12 only because the offline reproduction numbers noise 1-10 and targets 11-12 in params order; actual runtime IDs are unknown.

## Duplicate and noise structure in the original params

Total rows: 12. Distinct full-row contents: 11. The only exact duplicate is the two target rows.

Group with the same title **and** same description:

- Title: `Caprese Salad Skewers`
- Description: `An ideal recipe for experimenting with different flavors and ingredients.`
- Members: 5 rows — 2 exact-duplicate target rows plus 3 distinct noise variants.
- Distinct full-row contents within this group: 4 (the two targets share one content; the 3 variants have distinct contents).
- Counts in all params: 6 rows share the title `Caprese Salad Skewers`; 6 rows share the ideal description above (one is a Pan-Seared Salmon row); 5 rows share both title and description. The 5-candidate count applies to the title-filtered group. A global description-only selector was not shown to match only 5 rows.
- Title alone, description alone, and title+description all over-group relative to true exact duplicates.

The three variants differ in fields such as `servings`, `preparationTime`, `ingredients`, and/or `directions`; they are not duplicates. Deleting them violates the task's unique-recipe preservation requirement even though their title and description match the target.

## Official success predicate

`DeleteMultipleRows.is_successful` calls base `TaskEval.is_successful` (returns `1.0` after initialization check), reads `after = list_rows(env)`, then calls `RecipeDeleteDuplicateRecipes.validate_deletion_integrity`.

That override returns true when either:

- `validate_rows_removal_integrity(before, after, [target1.recipeId], "recipeId")`, or
- the same call with `[target2.recipeId]`.

`validate_rows_removal_integrity` for the chosen target ID requires:

- the chosen target row is absent from `after`;
- every other `before` row is still present in `after`;
- no new rows appear in `after`.

Consequences:

- Exactly one of the two exact-duplicate target rows must be deleted.
- The other target row must remain; deleting both duplicates fails because the other target is a non-deleted `before` row.
- All 10 noise rows must remain unchanged.
- Deleting any noise variant fails, even if one target duplicate was correctly deleted.
- Full dataclass equality is used for presence/absence, including `recipeId`; title/description matching is not part of the predicate.

## Offline pure execution

Imports succeeded from the installed package. No env, init, scorer, or device was used. Synthetic IDs: noise `1..10` in params order, targets `11,12`.

| Scenario | Deleted synthetic IDs | Predicate | Rows left | Unique contents left |
|---|---|---:|---:|---:|
| Delete target 1 only | 11 | **true** | 11 | 11 |
| Delete target 2 only | 12 | **true** | 11 | 11 |
| Delete both targets only | 11,12 | false | 10 | 10 |
| Four same-title/desc, keep one target | 7,8,9,11 | false | 8 | 8 |
| Four same-title/desc, keep one variant | 11,12,7,8 | false | 8 | 8 |
| One target plus one noise | 11,7 | false | 10 | 10 |
| One noise only | 7 | false | 11 | 10 |
| All five same-title/desc | 7,8,9,11,12 | false | 7 | 7 |

Before deletion: 12 rows, 11 unique contents.

Enumerating **all five** possible 4-row deletions from the 5 same-title/same-description rows (`{7,8,9,11,12}` choose 4): every subset returns `false`, leaves 8 rows and 8 unique contents, and destroys exactly **3 distinct recipe contents**. The reason is structural: the group contains only one duplicate content plus three unique variant contents, so any 4-of-5 deletion necessarily removes all three variants when it keeps one target, or both targets plus two variants when it keeps a variant. Either way, at least three unique recipes are lost.

Therefore, deleting four records matching the target title and description **does** violate unique-recipe preservation and cannot satisfy the official predicate.

### Reproducible pure execution

Run from the repository root. This imports only schema/predicate code; it does not initialize an environment, app, session, or device.

```bash
cd /Users/qunmi/Documents/FSQ_LAB/FSQ_AndroidWorld_eval && .venv/bin/python - <<'PY'
import json, types, itertools
from android_world.task_evals.utils.sqlite_schema_utils import Recipe
from android_world.task_evals.single.recipe import RecipeDeleteDuplicateRecipes

RESULT = 'campaigns/amkernel-3388314-r12v2-headless-full-ready-20261107T004632Z/episodes/051-RecipeDeleteDuplicateRecipes2/attempt-1/result.json'
params = json.load(open(RESULT))['task']['params']
noise = params['noise_row_objects']
targets = params['row_objects']

def mk(r, rid):
    kw = {k: v for k, v in r.items() if k != 'recipeId'}
    return Recipe(**kw, recipeId=rid)

before = [mk(r, i) for i, r in enumerate(noise, 1)]
before += [mk(r, len(noise) + j) for j, r in enumerate(targets, 1)]
t1, t2 = before[-2], before[-1]
obj = types.SimpleNamespace(rows_to_delete=[t1, t2], db_key='recipeId')

def pred(deleted_ids):
    after = [r for r in before if r.recipeId not in deleted_ids]
    return bool(RecipeDeleteDuplicateRecipes.validate_deletion_integrity(obj, before, after)), after

for name, ids in [
    ('delete_target1_only', [t1.recipeId]),
    ('delete_target2_only', [t2.recipeId]),
    ('delete_both_targets_only', [t1.recipeId, t2.recipeId]),
    ('four_keep_one_target', [7, 8, 9, t1.recipeId]),
    ('four_keep_one_variant', [t1.recipeId, t2.recipeId, 7, 8]),
]:
    print(name, pred(ids)[0])

for sub in itertools.combinations([7, 8, 9, t1.recipeId, t2.recipeId], 4):
    print(sub, pred(sub)[0])
PY
```

The script uses synthetic sequential IDs only. The predicate outcomes depend on distinct target IDs and list membership, not on the numeric values.

## Original trajectory: earliest destructive risk

Extracted calls are 1-based as in `original-python-executions.json`.

- Call 9 is the **earliest opportunity to see repeated summary collisions**: the list view returned 6 `Caprese Salad Skewers` title nodes and 5 `An ideal recipe...` description nodes. This is not divergence or unsafe inference by itself.
- The **earliest visible duplicate hypothesis** is raw1963 (assistant reasoning at exec11): “it seems there might be five among the otherwise unique entries.” It is tentative and does not establish duplicate identity.
- Call 15 searched `Caprese Salad Skewers` and observed `titles = 2`, `descriptions = 3` — already internally inconsistent.
- Call 16 is the **earliest destructive selection risk** and the **first visible detail**: it selected a card by XPath matching only the description text `An ideal recipe...`. In the title-filtered view, 5 candidates share that description: 2 exact duplicates plus 3 distinct variants. The selector has no full-row discriminator, so the first matching card can be a unique variant. The opened detail exposed title/description matching target-visible fields, but no full-field candidate-versus-survivor comparison was recorded.
- Call 17 opened More options; call 18 opened the `Delete this recipe?` confirmation.
- Call 19 is the **first irreversible delete without a retained candidate-versus-survivor comparison**: it clicked `DELETE` and then observed `titles = 4`, `descriptions = 3`. It may have deleted a legitimate duplicate; the exact card-to-row identity is not retained.
- Calls 20, 21, and 22 each performed another full delete flow.
- Call 20 reported `remainingVisibleIdeal = 2`; call 21 again reported `remainingVisibleIdeal = 2`; call 22 observed `titles = 2`, `descriptions = [A delicious..., An ideal...]`.
- Call 23 called `driver.quit()` and returned true.

Four deletion flows occurred (calls 19-22). The retained UI lists are inconsistent in count and are not a DB read. The exact mapping from each tapped card to a runtime row ID is unknown. However, the original params make the structural outcome unavoidable for any 4-row deletion from the 5 same-title/same-description group: three distinct recipe contents are destroyed and the official predicate is false.

The final visible pair containing one ideal-description record and one different-description record is consistent with deleting four of the five title+ideal-description candidates. It is **not** proof that an exact duplicate was retained: the target pair may both have been deleted, or one target may remain while the three variants were deleted. In either case the official predicate fails.

## Conclusions

1. Exact duplicate here means all `Recipe` fields except `recipeId` are equal. In the original params only the two target rows meet this.
2. Five rows share the target's title and description, but three are distinct unique recipes. Title/description matching is not duplicate equivalence.
3. Any 4-row deletion from that five-row group destroys three distinct recipe contents and fails the official predicate. This is independent of which synthetic IDs are chosen.
4. The official predicate requires exactly one target duplicate removed, the other target retained, and all 10 noise rows retained.
5. Call 9 is the earliest opportunity to see repeated summary collisions, not evidence of unsafe inference by itself; the earliest visible duplicate hypothesis is raw1963 (exec11). The earliest destructive selection risk is the description-only card selector at call 16; call 16 also provides the first visible detail but not full equivalence; the first irreversible delete without a retained candidate-versus-survivor comparison is the DELETE confirmation at call 19. Calls 19-22 perform four deletions.
6. The retained evidence does not contain a final DB dump or SQLite read. No claim is made about actual runtime row IDs or the historical final database state. No official score rerun and no fix are claimed.

## Artifacts

- `owner-scorer-proof.json` — structured hashes, source anchors, group members, predicate matrix, enumeration, trajectory notes, limitations.
