# Recipe / Media：r4 harness 侧逐例调查

覆盖 **46、47、48、49、50、52、59、60**，共8唯一案例。**双侧交叉核对 pending**（每例JSON `fsqCrosscheck.status=harness_checked_wait_fsq_owner`），不代表FSQ owner已确认。只读原产物与manifest绑定installed oracle；未probe设备、未调用业务模型、未重跑任务/评分或检查、未改代码。没有采用旧历史诊断。

## 分数与契约边界

本cluster共8唯一案例：7 failed/0分，49为passed/1.0但主summary契约错误。48同时failed0与summary错误只计一次，不能与全局14/48重叠重复计数。四项exact_main_summary不等于official分数无效；49与全局13均须保留passed异常身份。

证据定位：各例的 `episode`、`execution-result.json#/steps/N`、`events.jsonl`行/sequence、原截图/UI快照和正式诊断完整路径均保留在同名JSON。下文step N统一指 `agent-<action>-N`（execution数组下标N−1）；事件序号与本轮events.jsonl行号相同。

## 版本与正式rubric

- Oracle只读根：`/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world`；manifest `identities.androidWorld.site`，installed sha256 `0ac9428da2e9d78d0303c44c682184268e708a3116134646401d5c8425671b94`。没有用本地开发源码替代oracle、没有重构随机fixture。
- SDK源码引用来自FSQ owner既存 `failure-analysis/fsq-evidence-index.json.source_identity` 对16文件的matches比对；本侧未另做hash泛验，FSQ因果仍逐例pending。

### Recipe添加（46–49）

SQLiteApp清空Broccoli并插入noise；AddMultipleRows记录before。添加评分逐一要求所有target行存在，比较title/description/servings/preparationTime/source/ingredients/directions/favorite，除favorite外均大小写不敏感SequenceMatcher ratio>=0.9；after长度必须为before+target数，所有原before行不可改变或删除；全部条件合取，返回0.0或1.0，无按菜谱部分分。空source和favorite=0同样是正式条件。

源：`/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/task_evals/single/recipe.py:354–384`；`/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/task_evals/common_validators/sqlite_validators.py:118–192,257–284,304–310`；`/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/utils/fuzzy_match_lib.py:20–50`。**没有whitespace normalization**，但0.9模糊阈值不是exact字符串相等；不比较recipeId/imageName/categories。

### Recipe删除（50、52）

初始化插入noise及两条仅recipeId不同的完全重复target；RecipeDeleteDuplicateRecipes.validate_deletion_integrity只接受删除target两ID中的任意一个，并保证另一个与全部原noise行仍存在且未修改，不能新增行。不是按title去重，删同名不同字段noise会失败；返回0.0或1.0。

源：`/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/task_evals/single/recipe.py:183–211`；`/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/task_evals/common_validators/sqlite_validators.py:73–115,348–415`。32条里的同标题不同servings/time/ingredients/directions都必须保留。

## 跨例机制边界

- 046与047不是单次字段点击失败：都只新建一菜，official要求3菜集合合取。046句间换行不能独自解释0；047重开旧同名条不是已证实保存损坏。
- 048与049均nativeResult runner真实错误为Agent exceeded the configured turn limit，伴随81/66次artifact slice重复读取；048发生在业务前，049在业务成功后，二者reward与classification不可合并。循环机制归因待FSQ owner。
- 050最后写预算机会用text定位content-desc菜单导致失败，恢复被硬预算拒绝；052无失败动作却完全不删，错误在候选覆盖/业务完成，不在点击。
- 059正式判完整queue==expected；原初始化未显式清playing_queue，轨迹又引入preserve existing queue及相对顺序弱断言。噪声queue足以失败，污染起源不可确认。
- 060只读一首noise的04:44，未建duration组合、未Add to playlist；0 Songs/00:00是直接可见持久化状态，而非时长精度问题。

## 046 RecipeAddMultipleRecipesFromImage — failed / reward 0.0

**原目标**：Add the recipes from recipes.jpg in Simple Gallery Pro to the Broccoli recipe app.

**Episode**：`/Users/qunmi/Documents/FSQ_LAB/FSQ_AndroidWorld_eval/evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/046-RecipeAddMultipleRecipesFromImage`。
**初始化**：seed `2293877352`，params SHA `88a01ea42fc0457ef22e1d70ed12614b9f6a7233012e57e3d1ff9c2a02011213`；referenceTime `2023-10-15T15:34:00+00:00`。Broccoli预先10条noise；Gallery recipes.jpg只含3条target，文字按60列wrap。Chickpea Vegetable Soup还存在noise同标题但1 serving/see directions，与目标2 servings/as desired不同。
**目标数据**：
```json
[
  {
    "description": "An ideal recipe for experimenting with different flavors and ingredients.",
    "directions": "Slice eggplant, bread, and fry. Layer in a baking dish with marinara sauce and mozzarella cheese. Bake until bubbly. Garnish with fresh herbs for a more vibrant taste.",
    "favorite": 0,
    "imageName": "",
    "ingredients": "varies",
    "preparationTime": "10 mins",
    "recipeId": -1,
    "servings": "8 servings",
    "source": "",
    "title": "Eggplant Parmesan"
  },
  {
    "description": "A quick and easy meal, perfect for busy weekdays.",
    "directions": "Place cod fillets in a baking dish, season with lemon juice, dill, salt, and pepper. Bake until fish flakes easily. Garnish with fresh herbs for a more vibrant taste.",
    "favorite": 0,
    "imageName": "",
    "ingredients": "subject to change",
    "preparationTime": "45 mins",
    "recipeId": -1,
    "servings": "2 servings",
    "source": "",
    "title": "Baked Cod with Lemon and Dill"
  },
  {
    "description": "An ideal recipe for experimenting with different flavors and ingredients.",
    "directions": "Sauté onions, carrots, and celery, add broth, canned tomatoes, and chickpeas. Simmer with spinach and seasonings. Try adding a pinch of your favorite spices for extra flavor.",
    "favorite": 0,
    "imageName": "",
    "ingredients": "as desired",
    "preparationTime": "2 hrs",
    "recipeId": -1,
    "servings": "2 servings",
    "source": "",
    "title": "Chickpea Vegetable Soup"
  }
]
```

### 本轮实际轨迹与评分差距

- 源图三菜已读出，但仅Eggplant Parmesan一套字段输入并保存/重开；没有Baked Cod或Chickpea目标的录入。
  - `agent-assert_with_ai-10` `passed`：{"prompt":"Read the currently opened recipe image. Verify it contains readable recipes, and transcribe every recipe title, all ingredients with quantities, preparation instructions and any other recipe details verbatim in your explanation. Also identify the filename if visible.","optional":false}
  - `agent-input_text-20` `passed`：{"target":"Title","text":"Eggplant Parmesan","textType":"literal"}
  - `agent-input_text-23` `passed`：{"target":"Description","text":"An ideal recipe for experimenting with different flavors and ingredients.","textType":"literal"}
  - `agent-input_text-26` `passed`：{"locator":{"resourceId":"com.flauschcode.broccoli:id/new_servings"},"text":"8 servings","textType":"literal"}
  - `agent-input_text-29` `passed`：{"target":"Time","text":"10 mins","textType":"literal"}
  - `agent-input_text-32` `passed`：{"target":"Ingredients","text":"varies","textType":"literal"}
  - `agent-input_text-35` `passed`：{"locator":{"resourceId":"com.flauschcode.broccoli:id/new_directions"},"text":"Slice eggplant, bread, and fry. Layer in a baking dish with marinara sauce and mozzarella cheese. Bake until bubbly.\nGarnish with fresh herbs for a more vibrant taste.","textType":"literal"}
  - `agent-tap_on-38` `passed`：{"target":"SAVE"}
  - `agent-tap_on-42` `passed`：{"locator":{"text":"Eggplant Parmesan"}}
  - `agent-assert_with_ai-43` `passed`：{"prompt":"Verify the saved Eggplant Parmesan recipe matches these source details: ingredients 'varies'; directions 'Slice eggplant, bread, and fry. Layer in a baking dish with marinara sauce and mozzarella cheese. Bake until bubbly. Garnish with fresh herbs for a more vibrant taste.' Report which f…（原完整参数见JSON）
  - `agent-kill_app-44` `passed`：{"app_id":"com.flauschcode.broccoli"}
  - 原events行/sequence：129, 134。

**期望 / 实际**：期望新增3个完整target（Broccoli共13行且noise不变）；实际动作只新增Eggplant Parmesan一条，Baked Cod with Lemon and Dill和目标Chickpea Vegetable Soup均无录入动作。Eggplant输入8 servings/10 mins/varies/完整描述与directions，save后重开截图匹配；不能从此反推全套任务成功。正式诊断validate_rows_addition_integrity:168返回Expected row missing。
**正式诊断**：`raw-private/evaluator-diagnostics.json` outcome=returned，reward=0.0，exception=None。本轮日志 `validate_rows_addition_integrity:168 Expected row ... not found`，Recipe对象被bounded capture省略，不能据此指定哪行或哪个字段。

**预算与输出**：admitted 27/60，attempted 27，denied 0；exhausted=False，deadlineExceeded=False；native inconclusive / verifier inconclusive，duration 327067ms；businessSeconds=3720。主summary：`{"businessStatus": "inconclusive", "source": "agent_runtime.runner.tool_output.summary", "status": "valid"}`。

### 直接失败与底层根因

**直接失败**：全量转录未完成；不是图库读不到、图片未附着，也不是已证明字段被持久化截断。

**已证实**：
- step10已识别三条源菜谱；step20-38只录入第一条，step44 kill_app后runner以inconclusive正常结束；写预算27/60且deadlineExceeded=false。
- step16和41把页面标题New Recipe当列表入口，失败；step18实际fab_recipes成功。驱动target仅text选择：/Users/qunmi/Documents/FSQ_LAB/FSQ/fsq_agent/drivers/android/_uiautomator2.py:356-369。
- 官方不做whitespace normalization：fuzzy_match只忽略大小写，SequenceMatcher阈值0.9。step35把Bake until bubbly.与Garnish...之间空格换成一个LF；这不是精确字符串相等，但单个字符替换相对于这段完整长文本不足解释跌至阈值以下，不应当作0分根因。

**强推断**：
- 执行计划没有以三条源记录的完成ledger约束结束，局部save/assert被接受为提前退出点；重复每字段Back+snapshot和非实际控件目标消耗路径。

**无法确认 / 缺证据**：
- 原after DB未保存，无法声明第一条已过逐字段oracle或指出诊断第一个缺失target。runner自称run time limit，但外层3720秒预算没有耗尽，327067ms提前结束的时间提示来源需FSQ核对。

**备选与排除**：
- 若有额外未见持久化变化仍需原DB才可确认；本轮已读方向录入与源只见一个句间LF替换，不能据此指称格式错误。正式诊断省略具体Recipe，确认的充分业务差距始终是仅完成1/3。

**责任层**：FSQ跨应用数据转录执行/完成条件；Android locator语义说明（辅助）；正式oracle正常拒绝不完整集合。

### 精确修复方案（未实施）

- **P1 / FSQ执行策略/工具契约 owner** — `FSQ main runner：源记录ledger与TaskRunOutput收尾门`：从公开图像提取的每条title+字段建立待办/已保存/已重开核对状态；未完记录仍有可用预算时继续UI流程，不把第一条assert当全集完成。此ledger不接触frozen params或oracle。保存后按title+servings+time+ingredients复合identity读回，尤其Chickpea有同标题noise；全部三条分别核对完成。
- **P1 / FSQ执行策略/工具契约 owner** — `UiAutomator2AndroidDriver._selector / Android工具说明`：明确target只按text精确匹配；入口使用观测到的fab_recipes resourceId，新增每菜使用同一已观察业务路径，而不是猜New Recipe文字入口。

### 将来验证（只给方案）

- 无需设备：离线用本episode行动证据断言保存对象数=1，完成ledger仍有两项pending，不得自动宣称3/3。
- 需设备：经授权的新设备运行：公开图像三条全部录入且关闭重开后六可见字段保持；正式oracle检查after=before+3且noise完全不变。

### FSQ待逐例核对

- 为何在327秒、27/60写动作、business3720秒未越界时runner声称run time limit并停止？需要原注入prompt/执行窗口来源，不能标外层timeout。
- step10完整三条已在backend结果中，主runner实际收到的是完整结构还是summary/artifact包装？是否遗漏了source-set ledger？

## 047 RecipeAddMultipleRecipesFromMarkor — failed / reward 0.0

**原目标**：Add the recipes from recipes.txt in Markor to the Broccoli recipe app.

**Episode**：`/Users/qunmi/Documents/FSQ_LAB/FSQ_AndroidWorld_eval/evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/047-RecipeAddMultipleRecipesFromMarkor`。
**初始化**：seed `4162951690`，params SHA `ee04d5b5b730cd71ea523e49c012bb826c53f32957a882ab37d91eac53626a15`；referenceTime `2023-10-15T15:34:00+00:00`。Markor recipes.txt仅3 target，Broccoli已有10 noise；noise_row_objects[2]是Thai Peanut同名同描述/方向，但3-4 servings、2 hrs、optional ingredients。
**目标数据**：
```json
[
  {
    "description": "A quick and easy meal, perfect for busy weekdays.",
    "directions": "Toss cooked noodles with a Thai peanut sauce, sliced red bell peppers, cabbage, carrots, and cilantro. Try adding a pinch of your favorite spices for extra flavor.",
    "favorite": 0,
    "imageName": "",
    "ingredients": "as desired",
    "preparationTime": "3 hrs",
    "recipeId": -1,
    "servings": "8 servings",
    "source": "",
    "title": "Thai Peanut Noodle Salad"
  },
  {
    "description": "An ideal recipe for experimenting with different flavors and ingredients.",
    "directions": "Sauté shrimp in butter and minced garlic until pink. Sprinkle with parsley and serve with lemon wedges. Feel free to substitute with ingredients you have on hand.",
    "favorite": 0,
    "imageName": "",
    "ingredients": "to preference",
    "preparationTime": "30 mins",
    "recipeId": -1,
    "servings": "3-4 servings",
    "source": "",
    "title": "Garlic Butter Shrimp"
  },
  {
    "description": "A delicious and healthy choice for any time of the day.",
    "directions": "Mix shredded cooked chicken with BBQ sauce. Place on tortillas with cheese, fold and cook until crispy. Garnish with fresh herbs for a more vibrant taste.",
    "favorite": 0,
    "imageName": "",
    "ingredients": "per individual taste",
    "preparationTime": "20 mins",
    "recipeId": -1,
    "servings": "8 servings",
    "source": "",
    "title": "BBQ Chicken Quesadillas"
  }
]
```

### 本轮实际轨迹与评分差距

- 第一条保存后立即详情正确；按title重开后命中原noise同名项，非证实保存回滚。
  - `agent-assert_with_ai-12` `passed`：{"prompt":"Read and transcribe the complete recipe text visible on screen, including title, description, ingredients and directions. Is the end of the file visible? Include exact text in your explanation.","optional":false}
  - `agent-input_text-21` `passed`：{"locator":{"resourceId":"com.flauschcode.broccoli:id/new_title"},"text":"Thai Peanut Noodle Salad","textType":"literal"}
  - `agent-input_text-24` `passed`：{"locator":{"resourceId":"com.flauschcode.broccoli:id/new_description"},"text":"A quick and easy meal, perfect for busy weekdays.","textType":"literal"}
  - `agent-input_text-27` `passed`：{"locator":{"resourceId":"com.flauschcode.broccoli:id/new_servings"},"text":"8 servings","textType":"literal"}
  - `agent-input_text-30` `passed`：{"locator":{"resourceId":"com.flauschcode.broccoli:id/new_preparation_time"},"text":"3 hrs","textType":"literal"}
  - `agent-input_text-33` `passed`：{"locator":{"resourceId":"com.flauschcode.broccoli:id/new_ingredients"},"text":"as desired","textType":"literal"}
  - `agent-input_text-36` `passed`：{"locator":{"resourceId":"com.flauschcode.broccoli:id/new_directions"},"text":"Toss cooked noodles with a Thai peanut sauce, sliced red bell peppers, cabbage, carrots, and cilantro. Try adding a pinch of your favorite spices for extra flavor.","textType":"literal"}
  - `agent-tap_on-37` `passed`：{"locator":{"resourceId":"com.flauschcode.broccoli:id/button_save_recipe"}}
  - `agent-ui_snapshot-38` `passed`：{}
  - `agent-assert_state-39` `passed`：{"element":{"resourceId":"com.flauschcode.broccoli:id/direction_text","text":"Toss cooked noodles with a Thai peanut sauce, sliced red bell peppers, cabbage, carrots, and cilantro. Try adding a pinch of your favorite spices for extra flavor."},"optional":false}
  - `agent-tap_on-43` `passed`：{"target":"Thai Peanut Noodle Salad"}
  - `agent-assert_with_ai-44` `failed`：{"prompt":"Verify saved recipe shows title Thai Peanut Noodle Salad, ingredients 'as desired', directions 'Toss cooked noodles with a Thai peanut sauce, sliced red bell peppers, cabbage, carrots, and cilantro. Try adding a pinch of your favorite spices for extra flavor.'","optional":false}
  - `agent-kill_app-45` `passed`：{}
  - 原events行/sequence：131, 136。

**期望 / 实际**：目标需Thai Peanut Noodle Salad(8 servings/3 hrs/as desired)、Garlic Butter Shrimp(3-4 servings/30 mins/to preference)、BBQ Chicken Quesadillas(8 servings/20 mins/per individual taste)全部新增。step21-37只输入并保存Thai；step38显示8 servings/3 hrs/as desired且step39完整directions定向断言通过。step43用title重开，截图变成3-4 servings/2 hrs/optional ingredients，恰为初始化noise[2]。Garlic和BBQ从未输入，正式0分充分成立。
**正式诊断**：`raw-private/evaluator-diagnostics.json` outcome=returned，reward=0.0，exception=None。本轮日志 `validate_rows_addition_integrity:168 Expected row ... not found`，Recipe对象被bounded capture省略，不能据此指定哪行或哪个字段。

**预算与输出**：admitted 27/60，attempted 27，denied 0；exhausted=False，deadlineExceeded=False；native inconclusive / verifier inconclusive，duration 323270ms；businessSeconds=3720。主summary：`{"businessStatus": "inconclusive", "source": "agent_runtime.runner.tool_output.summary", "status": "valid"}`。

### 直接失败与底层根因

**直接失败**：新增集合缺2条；另有重开对象身份歧义造成假“保存字段变了”的验证差距。

**已证实**：
- 源文本三条完整读取（step12）；仅一次save(step37)；step38正确新条详情与step43错误同名详情的全部可见差异和noise[2]一致。
- step44 title+directions吻合但ingredients失败；并非所有字段相同的一个对象被证实发生变更。
- 27/60写预算，deadlineExceeded=false，323270ms结束。

**强推断**：
- 以title作为唯一重开身份，把不同recipe当同一对象核对；新条8/3/as desired没有被后续动作修改，更强解释是命中已存在同名noise。
- 因验证歧义及局部完成即停止，漏掉余下两菜。

**无法确认 / 缺证据**：
- 无recipeId/after DB留存，不能100%识别step43对应数据库ID；也不能证明所有新条字段通过oracle。自称time limit不是业务deadline证据。

**备选与排除**：
- 实际存储写错是弱备选：需同时解释新条save后正确、重开全部元数据与原noise精确吻合，现有证据更支持错对象而非持久化损坏。

**责任层**：FSQ实体身份/集合完成与字段验证；正式oracle正常检查全集；不归因AMK持久化或App数据回滚。

### 精确修复方案（未实施）

- **P1 / FSQ执行策略/工具契约 owner** — `FSQ recipe重开选择/完成ledger`：新保存记录用title+description+servings+time+ingredients形成公开UI复合指纹；同标题候选分别读取，定位正确新条后核对，不覆盖/删除原noise。保持3项独立完成状态。
- **P1 / FSQ执行策略/工具契约 owner** — `FSQ runner收尾决策`：检查一个字段失败时先辨认选中对象，不直接认定存储损坏或提前收尾；在未耗尽约束内完成Garlic与BBQ。

### 将来验证（只给方案）

- 无需设备：离线回放step38与step43，对照冻结noise[2]，断言这是候选身份冲突，不能输出“saved ingredient was corrupted”确定结论。
- 需设备：新设备fixture含同名不同字段noise；新增后精确重开目标，noise保持原字段，3条完整新增。

### FSQ待逐例核对

- 主runner是否能访问save后step38全部字段？为何“Reopened saved entry”未验证复合身份？
- 为何323秒/27写在business3720秒时主动停止？是否与46共用隐藏执行窗口或提示？

## 048 RecipeAddMultipleRecipesFromMarkor2 — failed / reward 0.0

**原目标**：Add the recipes from recipes.txt in Markor that take 10 mins to prepare into the Broccoli recipe app.

**Episode**：`/Users/qunmi/Documents/FSQ_LAB/FSQ_AndroidWorld_eval/evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/048-RecipeAddMultipleRecipesFromMarkor2`。
**初始化**：seed `1406555389`，params SHA `644b3e97955b1abb8d0e075090437cd5c1947818d8fb1b5863fb154435832c63`；referenceTime `2023-10-15T15:34:00+00:00`。40条noise已在Broccoli；recipes.txt将3 target+40 noise打乱写为CSV pipe分隔，目标prep_time=10 mins，noise的prep_time均非10 mins。不是只显示3条的小文件。
**目标数据**：
```json
[
  {
    "description": "A delicious and healthy choice for any time of the day.",
    "directions": "Blend together raspberries, almond milk, banana, and a scoop of almond butter until smooth. Garnish with fresh herbs for a more vibrant taste.",
    "favorite": 0,
    "imageName": "",
    "ingredients": "n/a",
    "preparationTime": "10 mins",
    "recipeId": -1,
    "servings": "2 servings",
    "source": "",
    "title": "Raspberry Almond Smoothie"
  },
  {
    "description": "A delicious and healthy choice for any time of the day.",
    "directions": "Stir-fry beef slices with broccoli, bell peppers, and onions in soy sauce and garlic. Serve over rice or noodles. Try adding a pinch of your favorite spices for extra flavor.",
    "favorite": 0,
    "imageName": "",
    "ingredients": "as per recipe",
    "preparationTime": "10 mins",
    "recipeId": -1,
    "servings": "2 servings",
    "source": "",
    "title": "Beef Stir Fry"
  },
  {
    "description": "An ideal recipe for experimenting with different flavors and ingredients.",
    "directions": "Pan-sear salmon fillets until crispy. Serve over cooked quinoa with a side of steamed asparagus. Try adding a pinch of your favorite spices for extra flavor.",
    "favorite": 0,
    "imageName": "",
    "ingredients": "n/a",
    "preparationTime": "10 mins",
    "recipeId": -1,
    "servings": "8 servings",
    "source": "",
    "title": "Pan-Seared Salmon with Quinoa"
  }
]
```

### 本轮实际轨迹与评分差距

- 只读Markor前部，首屏已有Beef Stir Fry 10 mins；未进入Broccoli、没有任何input/save。
  - `agent-assert_with_ai-10` `passed`：{"prompt":"Read the visible recipes.txt source. Report verbatim all visible recipe rows and their fields, especially recipes with preparationTime 10 mins. This is source collection; indicate any clipping.","optional":true}
  - `agent-assert_with_ai-12` `failed`：{"prompt":"Read this section of recipes.txt. Transcribe complete rows with preparationTime exactly 10 mins, including all pipe-separated fields. Summarize other titles/times and whether bottom of file visible.","optional":true}
  - `agent-assert_with_ai-14` `failed`：{"prompt":"Transcribe all visible complete recipe rows whose preparationTime is exactly 10 mins, all fields verbatim. List other visible titles/times and indicate bottom of file.","optional":true}
  - `agent-assert_with_ai-16` `failed`：{"prompt":"Transcribe visible recipe rows with preparationTime exactly 10 mins including all fields verbatim. List other titles/times; is file bottom visible?","optional":true}
  - `agent-swipe-17` `passed`：{"direction":"up"}
  - 原events行/sequence：59, 63, 64, 65, 66, 217, 218, 219, 222, 223。

**期望 / 实际**：需筛选43源行中3条10 mins：Raspberry Almond Smoothie(2 servings/n/a)、Beef Stir Fry(2 servings/as per recipe)、Pan-Seared Salmon with Quinoa(8 servings/n/a)，保留各自完整描述/方向并新增，最终Broccoli43行。实际step10读出Beef目标；step12/14/16在未到底的局部无目标页面返回failed，但optional=true；step17最后swipe后主体陷入artifact读取，未新增任何行，正式missing row、0.0。
**正式诊断**：`raw-private/evaluator-diagnostics.json` outcome=returned，reward=0.0，exception=None。本轮日志 `validate_rows_addition_integrity:168 Expected row ... not found`，Recipe对象被bounded capture省略，不能据此指定哪行或哪个字段。

**预算与输出**：admitted 9/60，attempted 9，denied 0；exhausted=False，deadlineExceeded=False；native error / verifier inconclusive，duration 445662ms；businessSeconds=3720。主summary：`{"reason": "Main runner did not succeed", "source": "agent_runtime.runner.tool_output.summary", "status": "failed"}`。

### 直接失败与底层根因

**直接失败**：业务缺所有3条新增；独立输出契约失败：native runner step1错误Agent exceeded the configured turn limit，主summary不存在；后续verifier inconclusive不能充当主summary。

**已证实**：
- events 63-218反复read_artifact_slice相同工具产物片段；全程81次slice，仅12组唯一参数，其中重复最多一组19次；219明确max-turn错误。
- 读片段offset1000返回嵌套/转义工具JSON，包含旧assertion输出；没有推进设备或源文件到底。
- 写预算仅9/60，不是Android动作预算/业务deadline耗尽；Source读取用assert_with_ai，局部无10 mins导致断言failed并不代表文件不存在目标。

**强推断**：
- 工具结果获取/停止条件在同一片段上无进展，吃掉runner回合，阻断剩余源收集与目标录入；业务失败和summary失败有共同的artifact无进展循环。

**无法确认 / 缺证据**：
- 不能仅由trace证明循环由backend历史转换、tool filter、模型选择哪一处触发，FSQ owner需逐层对照；无after DB不能给逐字段差异。

**备选与排除**：
- source很长或观察裁剪只是触发条件，不能单独解释同一artifact相同offset反复读取几十次；也不能把max_turns改大当永久修复。

**责任层**：FSQ artifact工具输出/runner无进展与structured收尾；FSQ源采集策略（断言与数据提取混用）；正式oracle正常拒绝缺新增。

### 精确修复方案（未实施）

- **P0 / FSQ工具协议 owner** — `HarnessToolAdapter._format_runner_result/_result_summary；read_artifact_slice输出协议；AgentTools历史过滤`：保持关键result.status/output.explanation为一次可读结构，避免为了读取源文本只能在双重转义工具JSON固定offset上反复找；相同artifact+offset+length返回稳定结构并把已读片段作为可用证据。具体循环注入点待FSQ owner确认，不能提前指定某层bug。
- **P1 / FSQ执行策略/工具契约 owner** — `agent_engine._runner max_turns循环 / 主runner完成状态`：不以加turn limit解决；追踪同一源片段无新证据的重复访问，在正常回合内重新推进源文件/使用Markor可见搜索，再继续UI录入并输出诚实结构化总结。异常路径保留真实runner error，verifier不得冒充主summary。
- **P1 / FSQ执行策略/工具契约 owner** — `Markor源收集执行策略`：把局部无匹配当过滤结果而非源契约失败；使用公开可见搜索10 mins并记录候选完整行/上下文与去重，直到覆盖源到底，不读取oracle。

### 将来验证（只给方案）

- 无需设备：用原events 63-218离线喂同一artifact响应，断言没有相同片段无进展循环；219错误必须原样传递，主summary缺失与verifier状态分开。
- 需设备：新设备含43行CSV、3个分散10 mins目标；公开UI源筛选覆盖、完整新增3项；写预算60与业务预算不变。

### FSQ待逐例核对

- 81次slice中相同三组参数各重复18-19次：后端是否实际收到每次返回，还是历史过滤/转换重放工具请求？需要FSQ源码/冻结请求链来区分。
- max_turns=何值及哪些内部读调用计入turn？为什么optional源提取被记录assertion_error，但真正终止是runner max_turns？
- 本例同时属于failed和exact_main_summary异常集合；汇总与14/48等重叠时48只计一次，不能改成operational invalid/无效official分数。

## 049 RecipeAddSingleRecipe — passed / reward 1.0

**原目标**：Add the following recipes into the Broccoli app:  
Recipe: Chicken Caesar Salad Wrap  
 description: An ideal recipe for experimenting with different flavors and ingredients.  
 servings: 3-4 servings  
 preparationTime: 2 hrs  
 ingredients: as desired  
 directions: Toss chopped romaine lettuce with Caesar dressing, grilled chicken strips, and Parmesan cheese. Wrap in a large tortilla. Feel free to substitute with ingredients you have on hand.

**Episode**：`/Users/qunmi/Documents/FSQ_LAB/FSQ_AndroidWorld_eval/evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/049-RecipeAddSingleRecipe`。
**初始化**：seed `374064309`，params SHA `799aa3b4a3af5f7e76a9d0c1faad2d70015e1d47e380c9e296b15e7a9c3fec21`；referenceTime `2023-10-15T15:34:00+00:00`。Broccoli10 noise；公开goal直接给唯一target六个字段，需新增Chicken Caesar Salad Wrap而不是读Markor。
**目标数据**：
```json
[
  {
    "description": "An ideal recipe for experimenting with different flavors and ingredients.",
    "directions": "Toss chopped romaine lettuce with Caesar dressing, grilled chicken strips, and Parmesan cheese. Wrap in a large tortilla. Feel free to substitute with ingredients you have on hand.",
    "favorite": 0,
    "imageName": "",
    "ingredients": "as desired",
    "preparationTime": "2 hrs",
    "recipeId": -1,
    "servings": "3-4 servings",
    "source": "",
    "title": "Chicken Caesar Salad Wrap"
  }
]
```

### 本轮实际轨迹与评分差距

- 有效save与全部字段定向核对成功，之后无修改；主runner在冗余artifact读取后max-turn，业务评分仍1。
  - `agent-input_text-14` `passed`：{"locator":{"resourceId":"com.flauschcode.broccoli:id/new_servings"},"text":"3-4 servings","textType":"literal"}
  - `agent-input_text-15` `failed`：{"locator":{"resourceId":"com.flauschcode.broccoli:id/new_preparation_time"},"text":"2 hrs","textType":"literal"}；Target was not found.
  - `agent-press_key-16` `passed`：{"key":"Back"}
  - `agent-input_text-18` `passed`：{"locator":{"resourceId":"com.flauschcode.broccoli:id/new_preparation_time"},"text":"2 hrs","textType":"literal"}
  - `agent-input_text-20` `passed`：{"locator":{"resourceId":"com.flauschcode.broccoli:id/new_ingredients"},"text":"as desired","textType":"literal"}
  - `agent-input_text-24` `passed`：{"locator":{"resourceId":"com.flauschcode.broccoli:id/new_directions"},"text":"Toss chopped romaine lettuce with Caesar dressing, grilled chicken strips, and Parmesan cheese. Wrap in a large tortilla. Feel free to substitute with ingredients you have on hand.","textType":"literal"}
  - `agent-tap_on-25` `passed`：{"locator":{"resourceId":"com.flauschcode.broccoli:id/button_save_recipe"}}
  - `agent-ui_snapshot-26` `passed`：{}
  - `agent-assert_state-27` `failed`：{"text":{"equals":"Toss chopped romaine lettuce with Caesar dressing, grilled chicken strips, and Parmesan cheese. Wrap in a large tortilla. Feel free to substitute with ingredients you have on hand."},"optional":false}；Text assertion failed.
  - `agent-assert_state-28` `passed`：{"element":{"resourceId":"com.flauschcode.broccoli:id/direction_text","text":"Toss chopped romaine lettuce with Caesar dressing, grilled chicken strips, and Parmesan cheese. Wrap in a large tortilla. Feel free to substitute with ingredients you have on hand."},"optional":false}
  - `agent-assert_visible-29` `passed`：{"locator":{"resourceId":"com.flauschcode.broccoli:id/details_description","text":"An ideal recipe for experimenting with different flavors and ingredients."},"optional":false}
  - `agent-assert_visible-30` `passed`：{"locator":{"text":"3-4 servings"},"optional":false}
  - `agent-assert_visible-31` `passed`：{"locator":{"text":"2 hrs"},"optional":false}
  - `agent-assert_visible-32` `passed`：{"locator":{"text":"as desired"},"optional":false}
  - `agent-assert_visible-33` `passed`：{"locator":{"text":"Chicken Caesar Salad Wrap"},"optional":false}
  - 原events行/sequence：85, 86, 91, 92, 93, 94, 217, 218, 219, 222, 223。

**期望 / 实际**：18次admitted写中一次time字段未找到(step15)在Back后step18成功补录；step25保存，step26截图title/描述/3-4 servings/2 hrs/as desired/完整directions均匹配公开goal。step27无element的text equals输出空串而failed；step28按direction_text+完整text定位通过，29-33其余字段通过。official1.0/passed原样保留。唯一未满足项为主runner structured summary契约，非菜谱任务未完成。
**正式诊断**：`raw-private/evaluator-diagnostics.json` outcome=returned，reward=1.0，exception=None。没有逐组件结果，不补造字段分。

**预算与输出**：admitted 18/24，attempted 18，denied 0；exhausted=False，deadlineExceeded=False；native error / verifier success，duration 451829ms；businessSeconds=1560。主summary：`{"reason": "Main runner did not succeed", "source": "agent_runtime.runner.tool_output.summary", "status": "failed"}`。

### 直接失败与底层根因

**直接失败**：本例无官方业务失败；passed=1.0但exact_main_summary failed，因为nativeResult.steps[0]为Agent exceeded the configured turn limit。后续verifier success不修复主runner缺summary。

**已证实**：
- 成功save与全部目标字段核对后无App修改，oracle正常返回1.0且无warning。
- step27调用assert_state(text.equals)无element，_selector退回self.device()，_assert_text_state取根selector.get_text()返回空；不是方向文字没保存。源码/Users/qunmi/Documents/FSQ_LAB/FSQ/fsq_agent/drivers/android/_uiautomator2.py:205-220,356-369,487-495。
- native events 91-218大部分连续读同一assertion产物；全程66次slice、11组参数，同一3组各12次；219触发max_turns。

**强推断**：
- 业务完成后陷入工具证据重复读取而未及时structured收尾，造成输出协议错误；与48同属无进展artifact循环，但业务后果不同。

**无法确认 / 缺证据**：
- 哪个FSQ输出转换/历史机制促发重复请求需FSQ owner确认；无原DB快照不自行重评分，但本轮official1.0已是正式持久化验收证据。

**备选与排除**：
- 初始time定位失败和全局text断言空值均已恢复，不能当最终business根因；不能把passed改failed来与native error对齐。

**责任层**：FSQ主runner收尾/工具协议；Android assert_state语义说明；官方业务评分有效且通过。

### 精确修复方案（未实施）

- **P0 / FSQ工具与runtime owner** — `read_artifact_slice / HarnessToolAdapter._format_runner_result/_result_summary / runner收尾`：业务字段断言已全部通过后使用已收集证据生成TaskRunOutput，不重复读同样offset的小片段；离线定位工具历史转换根因，不私加回合或同题重试。
- **P1 / FSQ执行策略/工具契约 owner** — `UiAutomator2AndroidDriver.assert_state / _selector / 工具参数说明`：明确text断言针对所选元素，不是全屏拼接文本；方向用element(resourceId=direction_text,text=完整源文)或定向text属性断言；拒绝/清楚解释无element的全局text用法，不做空串特殊通过。

### 将来验证（只给方案）

- 无需设备：原49离线证据断言business reward=1、classification=passed、mainAnswer=failed三者可共存；verifier success不得冒充runner summary。
- 需设备：完成已知六字段后及时结构化返回；全局text根空值与定向元素存在分开验收；budget24不变。

### FSQ待逐例核对

- 为什么业务step33全部目标断言成功后还需要66次slice？三组相同参数各12次的循环，与48是否同一tool-message历史处理缺陷？
- 修复summary协议时务必保留本轮passed1.0，不用native error覆盖官方reward；49应与全局13同类区分业务与契约。

## 050 RecipeDeleteDuplicateRecipes — failed / reward 0.0

**原目标**：Delete all but one of any recipes in the Broccoli app that are exact duplicates, ensuring at least one instance of each unique recipe remains

**Episode**：`/Users/qunmi/Documents/FSQ_LAB/FSQ_AndroidWorld_eval/evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/050-RecipeDeleteDuplicateRecipes`。
**初始化**：seed `536113126`，params SHA `dce0d486877e54dcf20e424a2975e6c18ff9cbe344bca169f4ffa6d185c7f630`；referenceTime `2023-10-15T15:34:00+00:00`。5 noise+2条Chicken Alfredo Pasta，完全重复字段：6 servings/45 mins/see directions/同description及directions。共7行，期望只删任意一个target ID，剩6行。
**目标数据**：
```json
[
  {
    "description": "An ideal recipe for experimenting with different flavors and ingredients.",
    "directions": "Cook fettuccine pasta, toss with Alfredo sauce and grilled chicken strips. Serve with a sprinkle of Parmesan cheese. Try adding a pinch of your favorite spices for extra flavor.",
    "favorite": 0,
    "imageName": "",
    "ingredients": "see directions",
    "preparationTime": "45 mins",
    "recipeId": -1,
    "servings": "6 servings",
    "source": "",
    "title": "Chicken Alfredo Pasta"
  },
  {
    "description": "An ideal recipe for experimenting with different flavors and ingredients.",
    "directions": "Cook fettuccine pasta, toss with Alfredo sauce and grilled chicken strips. Serve with a sprinkle of Parmesan cheese. Try adding a pinch of your favorite spices for extra flavor.",
    "favorite": 0,
    "imageName": "",
    "ingredients": "see directions",
    "preparationTime": "45 mins",
    "recipeId": -1,
    "servings": "6 servings",
    "source": "",
    "title": "Chicken Alfredo Pasta"
  }
]
```

### 本轮实际轨迹与评分差距

- 7条fixture双份target已全字段比对；菜单用target而非content-desc导致最后admitted写失败，后续两次预算拒绝，无delete。
  - `agent-launch_app-1` `passed`：{}
  - `agent-launch_app-3` `passed`：{"app_id":"com.flauschcode.broccoli"}
  - `agent-swipe-4` `passed`：{"direction":"up"}
  - `agent-tap_on-6` `passed`：{"target":"Broccoli"}
  - `agent-swipe-8` `passed`：{"direction":"up"}
  - `agent-swipe-10` `passed`：{"direction":"down"}
  - `agent-tap_on-12` `passed`：{"locator":{"xpath":"(//*[@resource-id='com.flauschcode.broccoli:id/card_text_view_title' and @text='Chicken Alfredo Pasta'])[1]"}}
  - `agent-assert_with_ai-14` `passed`：{"prompt":"Read the complete visible Chicken Alfredo Pasta recipe content, including full description and directions, servings, time, ingredients and photo state. Report the exact text to enable comparison with another instance.","optional":false}
  - `agent-press_key-15` `passed`：{"key":"Back"}
  - `agent-tap_on-17` `passed`：{"locator":{"xpath":"(//*[@resource-id='com.flauschcode.broccoli:id/card_text_view_title' and @text='Chicken Alfredo Pasta'])[2]"}}
  - `agent-assert_with_ai-19` `passed`：{"prompt":"Verify this second Chicken Alfredo Pasta exactly matches the first instance: title Chicken Alfredo Pasta; 6 servings; 45 mins; description 'An ideal recipe for experimenting with different flavors and ingredients.'; ingredients 'see directions'; one direction 'Cook fettuccine pasta, toss …（原完整参数见JSON）
  - `agent-tap_on-20` `failed`：{"target":"More options"}；Target was not found.
  - `agent-ui_snapshot-21` `passed`：{}
  - `agent-tap_on-22` `failed`：{}；NativeActionBudgetExceeded: action_budget
  - `agent-kill_app-23` `failed`：{}；NativeActionBudgetExceeded: action_budget
  - 原events行/sequence：73, 78。

**期望 / 实际**：实际step12/17打开两条；step14/19截图读出title、6 servings、45 mins、see directions、完整描述与方向一致，已具备删除候选证据。第10个admitted写step20 target=More options失败，虽然UI树content-desc=More options仍可见；step22显式accessibilityId重试在调用driver前被budget拒绝，step23 kill同样拒绝。未出现Delete菜单/确认/删除动作，official0。
**正式诊断**：`raw-private/evaluator-diagnostics.json` outcome=returned，reward=0.0，exception=None。没有逐组件结果，不补造字段分。

**预算与输出**：admitted 10/10，attempted 12，denied 2；exhausted=True，deadlineExceeded=False；native failed / verifier failed，duration 185544ms；businessSeconds=720。主summary：`{"businessStatus": "inconclusive", "source": "agent_runtime.runner.tool_output.summary", "status": "valid"}`。

### 直接失败与底层根因

**直接失败**：本应删掉一份Chicken Alfredo Pasta，但没有任何删除发生；预算用尽是直接阻断，不是最深根因。

**已证实**：
- 写#1 launch无app、#2 launch带app仍停launcher，#3 swipe/#4点Broccoli才入app；#5/#6为库上下滚；#7/9打开两份，#8返回；#10用target=More options。
- More options是content-desc非text；_selector的target分支强制device(text=...)，因此稳定找不到而不是控件不存在。源码/Users/qunmi/Documents/FSQ_LAB/FSQ/fsq_agent/drivers/android/_uiautomator2.py:356-369。
- 动作预算按admitted写dispatch包含launch、swipe、Back、失败尝试与kill；step22/23属于denied不执行。

**强推断**：
- 短预算未给关键delete/confirm预留步骤，启动前台后置条件缺失又消耗恢复动作；已知菜单属性却用错误target语义，使最后一个写机会浪费。

**无法确认 / 缺证据**：
- 起始app_start为何不把App前台化需FSQ/driver owner核对已有机制，当前无设备probe；不能断言只改一个菜单locator就在原10动作内一定能完成（还需delete/confirm）。

**备选与排除**：
- 官方重复比较不是简单看标题，前面完整比对是必要安全步骤；不能通过省掉比对盲删或加预算凑通过。

**责任层**：Android前台启动与locator契约；FSQ action-aware路径规划；预算边界工作正常，非评分异常。

### 精确修复方案（未实施）

- **P0 / FSQ Android driver owner** — `UiAutomator2AndroidDriver.launch_app / tap_on / _selector`：启动成功需要明确前台后置条件，避免成功dispatch仍需2次launch+launcher恢复；More options使用已观察accessibilityId，不把content-desc当text target。正式动作预算定义不偷偷改变。
- **P1 / FSQ执行策略/工具契约 owner** — `FSQ前计划与写预算ledger`：规划时计入启动、两条全字段比较所需导航、菜单/delete/confirm；同屏候选已明显存在时避免无关往返scroll。若在现有10写内仍不可行，报告预算实验而非改分或取消必要比对。

### 将来验证（只给方案）

- 无需设备：离线固定10个admitted写，断言step20文本selector失败与step22预算拒绝分开，未dispatch的重试不能算删除。
- 需设备：新设备以7行fixture测最短安全路径：前台启动、两条全字段核对、accessibility菜单删除并确认，只删1条且其他6行逐ID不变；若10写不足，独立记录预算可达性实验。

### FSQ待逐例核对

- 原step20 content-desc明确存在，target为什么只支持text却未在schema/提示中清楚约束？
- 为何两次launch返回passed仍在launcher？对10写任务启动恢复与teardown预算是否可达需单独测，不应将本轮“超预算”当终极解释。

## 052 RecipeDeleteDuplicateRecipes3 — failed / reward 0.0

**原目标**：Delete all but one of any recipes in the Broccoli app that are exact duplicates, ensuring at least one instance of each unique recipe remains

**Episode**：`/Users/qunmi/Documents/FSQ_LAB/FSQ_AndroidWorld_eval/evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/052-RecipeDeleteDuplicateRecipes3`。
**初始化**：seed `2676632063`，params SHA `76a838d9d504ef8cd9ff928b7f30ddc1c11b2674e5ee08e14b797f7baf8ac90a`；referenceTime `2023-10-15T15:34:00+00:00`。30 noise+2条Butternut target，共32。生成器专门把3条Avocado同名但不同字段noise排列表上端，另加Butternut同title/description却不同字段noise。真正重复是Butternut：3-4 servings/30 mins/quantities to taste/方向以Garnish...结尾。
**目标数据**：
```json
[
  {
    "description": "A quick and easy meal, perfect for busy weekdays.",
    "directions": "Sauté onions and garlic, add cubed butternut squash and broth. Puree until smooth and season with nutmeg, salt, and pepper. Garnish with fresh herbs for a more vibrant taste.",
    "favorite": 0,
    "imageName": "",
    "ingredients": "quantities to taste",
    "preparationTime": "30 mins",
    "recipeId": -1,
    "servings": "3-4 servings",
    "source": "",
    "title": "Butternut Squash Soup"
  },
  {
    "description": "A quick and easy meal, perfect for busy weekdays.",
    "directions": "Sauté onions and garlic, add cubed butternut squash and broth. Puree until smooth and season with nutmeg, salt, and pepper. Garnish with fresh herbs for a more vibrant taste.",
    "favorite": 0,
    "imageName": "",
    "ingredients": "quantities to taste",
    "preparationTime": "30 mins",
    "recipeId": -1,
    "servings": "3-4 servings",
    "source": "",
    "title": "Butternut Squash Soup"
  }
]
```

### 本轮实际轨迹与评分差距

- 全库滚动看见大量Butternut同名候选，却只搜索/打开Avocado三条不同noise；完全没有delete。
  - `agent-swipe-8` `passed`：{"direction":"up"}
  - `agent-swipe-10` `passed`：{"direction":"up"}
  - `agent-swipe-12` `passed`：{"direction":"up"}
  - `agent-swipe-14` `passed`：{"direction":"up"}
  - `agent-swipe-24` `passed`：{"direction":"up"}
  - `agent-tap_on-26` `passed`：{"locator":{"resourceId":"com.flauschcode.broccoli:id/action_search"}}
  - `agent-input_text-28` `passed`：{"locator":{"resourceId":"com.flauschcode.broccoli:id/search_src_text"},"text":"Avocado","textType":"literal"}
  - `agent-ui_snapshot-30` `passed`：{}
  - `agent-tap_on-31` `passed`：{"locator":{"xpath":"(//*[@resource-id='com.flauschcode.broccoli:id/card_text_view_title'])[1]"}}
  - `agent-ui_snapshot-32` `passed`：{}
  - `agent-assert_with_ai-33` `passed`：{"prompt":"Read the complete visible recipe. Verify title Avocado Toast with Egg, 6 servings, 4 hrs, description 'A quick and easy meal, perfect for busy weekdays.', ingredients 'various amounts'. Report the full directions and whether any further recipe content extends below the visible area.","optional":false}
  - `agent-tap_on-36` `passed`：{"locator":{"xpath":"(//*[@resource-id='com.flauschcode.broccoli:id/card_text_view_title'])[3]"}}
  - `agent-ui_snapshot-37` `passed`：{}
  - `agent-tap_on-40` `passed`：{"locator":{"xpath":"(//*[@resource-id='com.flauschcode.broccoli:id/card_text_view_title'])[2]"}}
  - `agent-ui_snapshot-41` `passed`：{}
  - `agent-assert_state-42` `passed`：{"element":{"resourceId":"com.flauschcode.broccoli:id/details_preparation_time","text":"2 hrs"},"optional":false}
  - `agent-kill_app-43` `passed`：{"app_id":"com.flauschcode.broccoli"}
  - 原events行/sequence：121, 126。

**期望 / 实际**：期望仅删两条Butternut完全重复中的任一条，剩31条且全部变体保持原样；实际step10-14已显示一串Butternut同标题相同描述，未打开任何Butternut详情。之后搜索Avocado并打开三条分别6 servings/4 hrs/various amounts，3-4 servings/1 hrs/n/a，6 servings/2 hrs/as needed；它们确实不同，但不是排除全库重复的证据。所有43native steps passed而official0，因为零删除，写22/34仍可用。
**正式诊断**：`raw-private/evaluator-diagnostics.json` outcome=returned，reward=0.0，exception=None。没有逐组件结果，不补造字段分。

**预算与输出**：admitted 22/34，attempted 22，denied 0；exhausted=False，deadlineExceeded=False；native inconclusive / verifier inconclusive，duration 282246ms；businessSeconds=2160。主summary：`{"businessStatus": "inconclusive", "source": "agent_runtime.runner.tool_output.summary", "status": "valid"}`。

### 直接失败与底层根因

**直接失败**：真正重复target一份也未删；没有操作错误不代表任务达标。

**已证实**：
- fixture明确Butternut双份target及30 noise，UI step10-14大量同名候选可见；实际只比较Avocado三条不同noise。
- 原nativeResult runner明确No recipes were deleted，claim execution window而budget22/34/deadlineExceeded=false。

**强推断**：
- 候选优先级/collection覆盖ledger丢失：先滚完全库再被列表首部Avocado同名诱饵吸引，没有把已遇到的Butternut簇加入待比较队列；因未证实exact-match就保守停手。

**无法确认 / 缺证据**：
- 无After DB，无法全库逐行核实，然而没有任何delete动作足以解释target仍存在；为何282246ms即以execution window收尾由FSQ核对。

**备选与排除**：
- 同名并不等于exact重复；不能建议按标题批量删Butternut或Avocado。当前未错删是正确安全性，但缺完整完成策略。

**责任层**：FSQ候选分组/跨页面覆盖与完成判定；任务fixture有意制造同名不同字段干扰，非初始化损坏；oracle正常拒绝零删除。

### 精确修复方案（未实施）

- **P1 / FSQ执行策略/工具契约 owner** — `FSQ重复候选ledger与浏览策略`：按公开UI title+description将候选簇登记并保留页面定位，优先检查多条同描述Butternut；用servings/time/ingredients/directions复合指纹排除变体，再只删除精确重复的一份。不要把Avocado三条不同就当全库无重复。
- **P1 / FSQ执行策略/工具契约 owner** — `FSQ主runner提前收尾`：所有候选簇须标已比较/已排除/未处理，存在未处理簇且预算未触顶时不静默结束；结束时输出未处理对象而不是all steps passed=完成。

### 将来验证（只给方案）

- 无需设备：离线候选账本应同时保留Butternut与Avocado；仅Avocado完成不能把全库状态标resolved。
- 需设备：新设备32行含3个Avocado及8个Butternut变体：只删除一份真正Butternut目标，所有variant recipeId及字段不变；重复候选全部有处理证据。

### FSQ待逐例核对

- 为何全库多次看到Butternut簇后，只把Avocado放进实际比较？planner ledger是否只保留最近观察导致忘记早先簇？
- runner引用execution window，写22/34、business预算未越界；实际是什么收尾约束？

## 059 RetroPlayingQueue — failed / reward 0

**原目标**：Add the following songs, in order, Through the Storm, Hidden Paths, Forever Young, Whispers of the Past, Heartbeat Away to my playing queue in Retro music.

**Episode**：`/Users/qunmi/Documents/FSQ_LAB/FSQ_AndroidWorld_eval/evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/059-RetroPlayingQueue`。
**初始化**：seed `145116843`，params SHA `fb91fd617b250762a354bd0328d31b45aed828e83641363d2e9c796ebbaf5873`；referenceTime `2023-10-15T15:34:00+00:00`。files有序为Through the Storm、Hidden Paths、Forever Young、Whispers of the Past、Heartbeat Away；10 noise各3–5分钟随机duration。frozen params未保存实际duration或初始playing_queue。
**目标数据**：
```json
[
  "Through the Storm.mp3",
  "Hidden Paths.mp3",
  "Forever Young.mp3",
  "Whispers of the Past.mp3",
  "Heartbeat Away.mp3"
]
```

**官方rubric**：读取music_playback_state.db的SELECT title from playing_queue，按返回列表与五首目标title逐项完全相等；不接受仅相对顺序、包含子序列、多余歌曲或同曲重复。没有检查是否新append的独立历史条件。
源：`/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/task_evals/single/retro_music.py:79-107,147-160,190-206`

**初始化边界**：继承RetroCreatePlaylist.initialize_task清媒体存储、清PlaylistEntity/SongEntity并写5目标+10noise、扫描后关App；_clear_playlist_dbs未清playing_queue，initialize没有显式清播放DB。不能由此单独证明跨episode污染，但空队列前置条件未由该源码保证。

### 本轮实际轨迹与评分差距

- 四个后续歌曲确实连续入尾；最终队列还含全库noise，Through不在连续尾段；验证从连续改成相对顺序。
  - `agent-tap_on-14` `passed`：{"locator":{"xpath":"//android.view.ViewGroup[.//android.widget.TextView[@text='Through the Storm']]/*[@resource-id='code.name.monkey.retromusic:id/menu']"}}
  - `agent-ui_snapshot-15` `passed`：{}
  - `agent-tap_on-16` `passed`：{"locator":{"text":"Add to playing queue"}}
  - `agent-tap_on-20` `passed`：{"locator":{"xpath":"//android.view.ViewGroup[.//android.widget.TextView[@text='Hidden Paths']]/*[@resource-id='code.name.monkey.retromusic:id/menu']"}}
  - `agent-ui_snapshot-21` `passed`：{}
  - `agent-tap_on-22` `passed`：{"locator":{"xpath":"//*[@text='Hidden Paths']/../*[@resource-id='code.name.monkey.retromusic:id/menu']"}}
  - `agent-tap_on-30` `passed`：{"locator":{"xpath":"//*[@text='Hidden Paths']/../*[@resource-id='code.name.monkey.retromusic:id/menu']"}}
  - `agent-tap_on-32` `passed`：{"locator":{"text":"Add to playing queue"}}
  - `agent-tap_on-36` `passed`：{"locator":{"xpath":"//*[@text='Forever Young']/../*[@resource-id='code.name.monkey.retromusic:id/menu']"}}
  - `agent-tap_on-38` `passed`：{"locator":{"text":"Add to playing queue"}}
  - `agent-tap_on-41` `passed`：{"locator":{"xpath":"//*[@text='Whispers of the Past']/../*[@resource-id='code.name.monkey.retromusic:id/menu']"}}
  - `agent-tap_on-43` `passed`：{"locator":{"text":"Add to playing queue"}}
  - `agent-tap_on-46` `passed`：{"locator":{"xpath":"//*[@text='Heartbeat Away']/../*[@resource-id='code.name.monkey.retromusic:id/menu']"}}
  - `agent-tap_on-48` `passed`：{"locator":{"text":"Add to playing queue"}}
  - `agent-ui_snapshot-53` `passed`：{}
  - `agent-ui_snapshot-55` `passed`：{}
  - `agent-assert_with_ai-56` `failed`：{"prompt":"Verify the playing queue shows the newly appended songs consecutively in this order: Through the Storm, Hidden Paths, Forever Young, Whispers of the Past, Heartbeat Away.","optional":false}
  - `agent-assert_with_ai-57` `passed`：{"prompt":"Verify the playing queue contains these songs in relative order (other existing queue songs may intervene): Through the Storm, Hidden Paths, Forever Young, Whispers of the Past, Heartbeat Away. Report their displayed positions if visible.","optional":false}
  - `agent-kill_app-58` `passed`：{"app_id":"code.name.monkey.retromusic"}
  - 原events行/sequence：8, 169, 174。

**期望 / 实际**：oracle期望队列严格只有指定5首。最终step53/55树与step56截图有Under the Sky、Falling Feathers、Dreamer's Awake、Eternal Flame等noise以及重复Hidden Paths；step55可见Through后是Silent Dreams/Chasing Shadows/Beyond the Horizon/Whispering Wind，然后才是Hidden/Forever/Whispers/Heartbeat。step56连续断言失败，step57改成允许其他歌穿插的相对顺序通过，official仍0。
**正式诊断**：`raw-private/evaluator-diagnostics.json` outcome=returned，reward=0，exception=None。没有逐组件结果，不补造字段分。

**预算与输出**：admitted 30/32，attempted 30，denied 0；exhausted=False，deadlineExceeded=False；native inconclusive / verifier inconclusive，duration 408334ms；businessSeconds=2040。主summary：`{"businessStatus": "inconclusive", "source": "agent_runtime.runner.tool_output.summary", "status": "valid"}`。

### 直接失败与底层根因

**直接失败**：最终队列整体不等于五首目标序列，绝非“仅缺Through是否新append证据”。后者是native verifier强调的局部疑点，不是官方0分的最小充分解释。

**已证实**：
- FSQ planning_update seq8主动加入preserve the existing queue，原goal没有该限制；official is_successful是严格列表相等。
- step16界面toast Added 1 title to the playing queue和Through mini-player可见，之后尾部只有另外四首连续；初次操作后是否自动全库建队列/原有队列未被记录。
- step56失败后改step57弱化为相对顺序，无法完成更强原目标，更不满足exact oracle；30/32写但无硬拒绝。
- 官方initializer未显式清playing_queue；原episode没有DB/MP3快照或初始队列截图。

**强推断**：
- 执行追加策略假设可保留任意原队列，未在开始建立可见队列基线/检查结果全集，与严格终态契约不匹配；单次tap passed也不证明该业务后置条件。

**无法确认 / 缺证据**：
- 无法区分初始残留队列、首个Add在空队列自动装载全库、第一条XPath选错导致播放/重建等起源；没有初始/首个Add后playing_queue证据，不能断言跨episode污染已发生。
- 无DB直接证据解释SQLite物理返回顺序与UI视图关系，但截图明确含非目标已是充分失败证据。

**备选与排除**：
- 仅修首首locator仍不能自动解决最终多余15首/同名重复；仅用relative order判成功会掩盖问题。

**责任层**：FSQ计划引入额外preserve限制与验证弱化；官方fixture队列前置状态隔离待核实（非已证实污染）；Android业务后置条件与定位（辅助）。

### 精确修复方案（未实施）

- **P1 / FSQ执行策略/工具契约 owner** — `FSQ queue计划/最终验证`：只以公开goal约束规划，不自行添加preserve任意原队列；先观察当前queue基线，逐项添加后核对完整终态/重复与顺序，不能从consecutive失败降级relative-order成功。若前置状态与add语义有冲突，诚实报告而非擅删真实用户队列。
- **P1 / AndroidWorld fixture owner** — `RetroPlayingQueue.initialize_task（新fixture版本，不回改r4）`：task owner核实并在初始化层保证确定的空播放队列或可证明的既定基线，初始化证据保存在private侧，不向agent泄露目标文件/正确序列；保持is_successful原rubric不变，历史r4 official0不重解释为无效。
- **P1 / FSQ执行策略/工具契约 owner** — `UiAutomator2AndroidDriver.tap_on + FSQ locator业务postcondition`：首个菜单在当前目标row内唯一定位并确认popover出现；特别是20/22 passed但没有menu，不能继续假定已打开。通过可见queue变化确认真正追加的是目标。

### 将来验证（只给方案）

- 无需设备：原53/55/56截图/树离线断言非目标存在足以失败；verifier summary不得把它缩成Through的新append证据不足。
- 需设备：经授权独立实验对空/非空播放队列分别记录首个Add前后UI与evaluator-private DB，再辨别App自动全库建队列 vs residue；目标五首精确最终序列，无额外歌曲、无重复，budget32不变。

### FSQ待逐例核对

- seq8的preserve existing queue来自哪里？是否由预计划注入而非goal？须逐例核对原prompt。
- step16有Added1 toast，但完整尾部Through没有新副本，首个Add前后是否有更早存量artifact可辨别自动全库建队列？
- verifier为何仅讨论新append证据、未把最终明显noise计入完整队列失败？step57允许intervening songs的弱断言由何处触发？

## 060 RetroPlaylistDuration — failed / reward 0.0

**原目标**：Create a playlist in Retro Music titled "Reggae Rhythms 51" with a duration between 45 and 50 minutes using the provided songs.

**Episode**：`/Users/qunmi/Documents/FSQ_LAB/FSQ_AndroidWorld_eval/evidence/fsq-native-gpt61-corrected-20261110T043031Z/revision-4/next-stage-plan/execution/run/episodes/060-RetroPlaylistDuration`。
**初始化**：seed `217200551`，params SHA `dcd892c246b616e950a794dd086315709257ad98fcc14d0242fc94825464b308`；referenceTime `2023-10-15T15:34:00+00:00`。files10首目标理论生成duration整数列表总和2850000ms=47.5min；另外5noise各随机3–5min。此initialize覆盖未调用super/clear_internal_storage，只清playlist DB再写媒体/扫描。frozen params仅文件名，不含实际逐曲duration；无存量MP3/DB，不能重建本轮精确逐曲长度。
**目标数据**：
```json
[
  "Silent Dreams.mp3",
  "Hidden Paths.mp3",
  "Whispering Wind.mp3",
  "Return to Paradise.mp3",
  "Endless Summer.mp3",
  "Falling Feathers.mp3",
  "Heartbeat Away.mp3",
  "Orbiting Stars.mp3",
  "Through the Storm.mp3",
  "Forever Young.mp3"
]
```

**官方rubric**：_get_playlist_data对PlaylistEntity JOIN SongEntity只返回有歌曲行；is_successful遍历所有返回歌曲，若任何行playlist_name不是目标即False，否则累加duration_ms，检查闭区间[2700000,3000000]（45–50分钟）。不要求特定曲序或files集合；不把空playlist名创建当成功，空JOIN总和0。
源：`/Users/qunmi/.local/share/fsq-androidworld-eval/fsq-native-gpt61-corrected-20261110T043031Z/evaluator-site/android_world/task_evals/single/retro_music.py:41-76,236-293`

**duration数据证据**：唯一真实读出的曲长是noise Beyond the Horizon，step15 player/step29 Details均04:44；没有10首target各自duration证据。

### 本轮实际轨迹与评分差距

- 只探一首noise Beyond the Horizon的4:44，无选曲求和，无任何Add to playlist；建成的是0 Songs/00:00空壳。
  - `agent-tap_on-12` `passed`：{"locator":{"text":"Beyond the Horizon"}}
  - `agent-tap_on-14` `passed`：{"locator":{"resourceId":"code.name.monkey.retromusic:id/miniPlayerFragment"}}
  - `agent-ui_snapshot-15` `passed`：{}
  - `agent-long_press_on-22` `passed`：{"locator":{"text":"Beyond the Horizon"}}
  - `agent-tap_on-26` `passed`：{"locator":{"xpath":"(//android.widget.ImageView[@resource-id='code.name.monkey.retromusic:id/menu'])[1]"}}
  - `agent-tap_on-28` `passed`：{"target":"Details"}
  - `agent-ui_snapshot-29` `passed`：{}
  - `agent-tap_on-33` `failed`：{"target":"Playlists"}；Target was not found.
  - `agent-tap_on-35` `passed`：{"locator":{"resourceId":"code.name.monkey.retromusic:id/action_playlist"}}
  - `agent-tap_on-37` `failed`：{"target":"More options"}；Target was not found.
  - `agent-tap_on-39` `passed`：{"locator":{"accessibilityId":"More options"}}
  - `agent-tap_on-41` `passed`：{"locator":{"text":"New playlist"}}
  - `agent-input_text-43` `passed`：{"locator":{"resourceId":"code.name.monkey.retromusic:id/actionNewPlaylist"},"text":"Reggae Rhythms 51","textType":"literal"}
  - `agent-tap_on-44` `passed`：{"locator":{"resourceId":"android:id/button1"}}
  - `agent-ui_snapshot-45` `passed`：{}
  - `agent-assert_state-46` `failed`：{"text":{"contains":"0 Songs  •  00:00"},"optional":false}；Text assertion failed.
  - `agent-assert_visible-47` `passed`：{"locator":{"text":"Reggae Rhythms 51"},"optional":false}
  - `agent-kill_app-48` `passed`：{"app_id":"code.name.monkey.retromusic"}
  - 原events行/sequence：141, 146。

**期望 / 实际**：需目标名Reggae Rhythms 51且SongEntity持久化曲目总长45–50min。实际只检查第一首noise Beyond the Horizon(04:44)，没形成时长表/组合，也无Add to playlist调用；step44 Create成功后step45树与截图0 Songs • 00:00。step46全局text contains失败输出根空串，不能否定屏幕实际0歌；step47仅title断言成功，正式0.0。
**正式诊断**：`raw-private/evaluator-diagnostics.json` outcome=returned，reward=0.0，exception=None。没有逐组件结果，不补造字段分。

**预算与输出**：admitted 25/30，attempted 25，denied 0；exhausted=False，deadlineExceeded=False；native failed / verifier failed，duration 341696ms；businessSeconds=1920。主summary：`{"businessStatus": "inconclusive", "source": "agent_runtime.runner.tool_output.summary", "status": "valid"}`。

### 直接失败与底层根因

**直接失败**：命名playlist已持久化但无歌曲，最终duration=00:00；不是duration求和精度边界，更不是已添加歌曲但oracle漏算。

**已证实**：
- step12播放第一首noise；step14打开player，16/18退出、22长按、26-30读Details4:44；这些均未建立playlist歌曲映射。
- step33 target=Playlists和37 target=More options使用text失配后，35 resourceId、39 accessibilityId恢复；step41-44只创建playlist。
- step45明确0歌；25/30写、deadlineExceeded=false，runner以窗口消耗为由把选曲/添加标skipped。
- step46与49-step27同类无element根text断言，驱动get_text空值，不是UI数据证据缺失。

**强推断**：
- 前期逐曲播放/详情探索和导航恢复耗费写路径，却未把duration采集/组合/批量加入这三个真正业务步骤建立完成账本；收尾只验证可见标题，未以0歌触发继续补充。

**无法确认 / 缺证据**：
- 10个target实际媒体duration未留存，无法仅凭params给出精确组合，也不能宣称47.5min在实际编码后精确不变；playlist仍空已足以判失败。
- 初始化未清内部storage是潜在隔离问题，但当前UI15首与fixture一致，无证据本例因跨题残留失败。

**备选与排除**：
- App写入bug不是当前主解释：没有Add to playlist动作，空SongEntity是正常预期。改总时长边界/通过空playlist均是改rubric不可取。

**责任层**：FSQ duration规划/歌曲加入与终态完成；Android locator/assert契约（辅助）；官方fixture可复现duration审计数据缺失（诊断限制，不是本例已证实根因）。

### 精确修复方案（未实施）

- **P1 / FSQ执行策略/工具契约 owner** — `FSQ playlist业务计划/ledger`：从公开UI建立song→duration表并组合45–50min，再以多选/逐曲Add to playlist确认SongEntity对应的可见曲目数量和总时长；title存在且0歌必须继续而非收尾。不要把开发者私有files/生成器答案注入agent。
- **P1 / FSQ执行策略/工具契约 owner** — `UiAutomator2AndroidDriver._selector / assert_state 与前台启动`：使用实际resourceId/accessibilityId，避免把content-desc当text；曲目总长核对选择展示duration的元素而非无element全局contains；复用前台启动修复减少launcher恢复。
- **P2 / AndroidWorld harness owner** — `RetroPlaylistDuration fixture私有初始化证据`：今后留存生成后的每文件实际duration/媒体元数据及必要DB基线到evaluator-private审计产物，agent仍只通过UI可见数据完成；保留原rubric与预算。

### 将来验证（只给方案）

- 无需设备：原45树及44截图离线断言目标playlist存在但song_count=0/duration=0；46根空text不能推翻截图。
- 需设备：经授权设备新实例公开UI测时长并选曲，加入后关闭重开playlist仍有曲目、sum在含边界45/50min范围；noise/多playlist与空playlist均按原rubric判定。

### FSQ待逐例核对

- 为什么在duration组合和Add步骤都未开始时，main仅验证title就收尾？25/30写、业务deadline未越界，执行窗口/提示来自哪里？
- step46全局text返回空值是否和49同一个工具schema误导；是否有可直接定位duration的输出方式？
- 目标各曲实际duration未冻结，是否还有已存private媒体/DB审计产物可用？不可运行生成器重建或用理论47.5min当实际评分数据。

## 交付与限制

全部结论仅限已存r4；没有重建随机duration、import任务、调设备或重评分。8例均已读原publicGoal、initialization、正式diagnostic及nativeExecution/nativeTaskResult关键动作/输出，决定性截图实际查看。没有原after DB/MP3留存时明确保留未知；修复不改变rubric、不暴露oracle答案、不私加预算或同题重试。预算可达性（尤其050）只能另列未来独立实验。FSQ owner逐例核对仍pending，最终中文report由父agent唯一整合。
