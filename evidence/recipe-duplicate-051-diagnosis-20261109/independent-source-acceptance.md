# Independent source/pure-predicate acceptance — original051

**Verdict: accepted; no correctness findings in the scoped source diagnosis.**

Reviewer: independent trajectory/source reviewer. This signature covers the frozen source-proof artifacts below, installed-source semantics, and actual offline pure-predicate behavior. It does not re-sign or modify the prior trajectory report, parent diagnosis/proposal, installation, skill or campaign.

## Accepted frozen versions
- `owner-scorer-proof.json`: `400507aa011e644964d2410a16d36cf2cc35d269b246847215a9eff7515f01f8` (matches supplied frozen SHA).
- `owner-source-report.md`: `881be6239213ccc05e587fc5c92078ddefa1f5d16761e97b30625aa597708e21` (matches supplied frozen SHA).

## Installed source identity
- `recipe.py`: `f547556b9681267c34a19fa5fc316591060966a138c8f366c4b1e1783c988309`; installed RECORD hash and byte size match.
- `sqlite_validators.py`: `7b932acd2e19f1d4f43cea1badf26ace2ed3363258ae26850d1b09889bfa9d78`; installed RECORD hash and byte size match.
- `sqlite_schema_utils.py`: `d3b1d796b1faadbdedc78e7f9197f0ee27e3eebf0edd4597cd59f3d0f6e3095b`; installed RECORD hash and byte size match.

The three modules were imported from the installed `.venv/lib/python3.11/site-packages/android_world` package. Independent SHA256/RECORD checks also match byte sizes. Installed direct_url records the local source origin with editable=false. The RECORD file SHA256 is `f1ec3aeb12c77dc16db17a5b5d1f2ecd509110814b395d90de20fb4aa05ceb7b`. These are current installed-source identity checks; original result separately records distribution version0.1.0 and revision55ddaf5edc6f6c25673aed343907d5b9dca66f84. No original runtime DB is inferred from installation metadata.

## Source routing and predicate semantics
Read the following installed source sections directly:

- `single/recipe.py:183–270`: RecipeDeleteDuplicateRecipes2 inherits the base recipe deduplication override; recipe fields and db_key are bound by `_RecipeApp` (`recipe.py:31,46–49`). The override at200–211 calls the removal-integrity helper for target1 OR target2.
- `common_validators/sqlite_validators.py:257–264,348–368,383–415`: initialization inserts noise first, then target rows, obtains before, takes the last two rows according to the returned list, validates pair equality excluding db_key, and dispatches the deletion outcome to the recipe override. The source assumes newly added rows are at the end; this is not an independent observation of actual runtime order or IDs.
- `sqlite_validators.py:73–118`: removal validation uses full row membership, requires the chosen target absent, all other before rows still present and no new row content added.
- `utils/sqlite_schema_utils.py:198–217`: frozen Recipe dataclass equality includes recipeId; content equivalence for duplicate-candidate validation excludes that ID but includes every other Recipe field, not just title/description.
- `task_evals/task_eval.py:160–181`: base is_successful checks initialization and returns1.0; the delete subclass then reads after and evaluates the helper. This entry point was read, **not called**.

Thus, for after-states obtained by deleting rows from the recorded synthetic before-set, success requires exactly one target removed, its counterpart retained and all ten noise rows unchanged. IDs distinguish stored instances; different IDs do not negate content equivalence. There is no title/description dispatch shortcut in this predicate.

## Actual independent pure execution
Used installed `.venv/bin/python -B` to import the real Recipe class and recipe override. Built synthetic Recipe instances from original parameters, replacing recipeId with sequential noise1..10/target11,12. Passed only a SimpleNamespace carrying rows_to_delete and db_key to the actual unbound installed method; no task constructor, environment, initialization, is_successful, device or database access occurred.

Results retained in the JSON companion:

- Delete target11 only: true; delete target12 only: true. Each leaves11 rows/11 unique contents.
- Delete both targets: false; leaves10 rows/10 unique contents.
- Enumerate all five ways to remove four of the five same-title+description candidates: all false; each leaves8 rows/8 unique contents, compared with12/11 before. This is **synthetic conditional loss of three content classes**, not an observed historical loss count.
- Exhaustively evaluate all4096 pure deletion subsets of the12 synthetic rows: only singleton deletions[11] and[12] pass.
- No deletion, deletion plus changed noise, and deletion plus added synthetic row all fail.

Installed imports emitted the same pydub missing-ffmpeg RuntimeWarning recorded by the parent receipt. The pure process completed successfully; no audio/ffmpeg operation was requested.

## Parent receipt and owner code
Read the owner reproduction source in both frozen artifacts and the full `code` field of parent `051-RecipeDeleteDuplicateRecipes2/parent-installed-predicate-smoke.json`. Owner uses SimpleNamespace; parent uses object.__new__ without constructor/init and sets rows_to_delete for the pure method. Neither code invokes env/init/is_successful or a device operation.

All eight owner matrix scenarios match the independent execution. Parent receipt exitCode0 and its two singleton successes, both-target failure and five four-of-five failures match independently. Its two recorded setup mistakes concern synthetic keyword construction and method arity; they are transparently documented and are not represented as historical application failures. Receipt SHA256: `9e704a8274edd5a37d780330d98cd91dcaf13d1b97616e01172870059efb05e1`.

## Corrected boundaries accepted
- Across **all parameters**, same description=6 (including a different-title recipe), same title=6. Only the title+description intersection has5 rows/4 content classes. A global description-only XPath must not be described as having only five possible records.
- Call9 is an opportunity to observe repeated summaries, not evidence that the model already reasoned incorrectly. Raw1963 contains the earliest retained **tentative** duplicate hypothesis.
- Exec16 returns one detail snapshot, not an equivalent pair. Exec19 is the first irreversible confirmation without a recorded candidate-versus-retained-counterpart comparison; it may still be a legitimate first deletion. Exec20–22 do not read and compare the newly selected candidate details.
- Four completed confirmation chains do **not** establish four durable database removals or any exact historical after-cardinality. Owner statements about performing four deletions are accepted only in the explicitly documented UI-flow sense. Parameter+pure-predicate results apply conditionally to actual removal of the corresponding rows.
- A final two-card viewport is not a full DB or filtered-result enumeration. Actual IDs, card-to-row mapping, durable deletion count and historical after-DB remain unknown.

No new official score, successful fix or skill benefit is claimed. No device/Appium/ADB/session/service/init/full scorer, build/lint/test suite/formatter or next task was run. Only independent-source-acceptance.md/json were written for this source acceptance.
