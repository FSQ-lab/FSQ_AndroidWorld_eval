# BrowserDraw跨项目追踪：AMKernel交界核对与空forest来源

## 当前结论

评测项目单次复现已证明：**画面仍成功、Chrome仍前台，但官方A11y forwarder输入为零窗口forest，因而ui_elements为空并判0。** 本轮在AMKernel侧核对提交/quit与Appium wire记录，并追踪forwarder接收/累积路径。没有发现要求修改AMKernel核心的证据；空forest产生或滞留的具体原因仍待动态来源记录。

两个新增调查点：

1. 官方读取的是累积区最后一个forest，不保证是本次get_state期间新生成的。没有新RPC与收到空forest不同；旧空forest可能继续被取用。
2. 本地存在disableSuppressAccessibilityService=true的Appium配置文件，但这次共享Appium启动没有--config，会话请求和返回均没有该能力。不能把文件存在当作能力已生效；也不能把能力省略直接当作运行时flags=0或已经发生服务压制。

## 已核对的执行边界

原复现目录：`evidence/browserdraw-field-diagnosis-20261109T052514Z`，以下记为E。

- E/python-cells/018.py与E/python-executions.json第18次请求一致。执行completed、kernel alive、2714ms；原wire source中恰有一个text=Success!节点。
- 第19次请求为driver.quit及返回字典，与保存脚本一致；completed、kernel alive、213ms；对应DELETE是同一session，HTTP200，wire耗时212.618ms。
- 最后的source、screenshot、package/activity查询和DELETE响应的保存body均匹配各自SHA256；wire在DELETE之后没有记录其他请求。
- evaluator约在DELETE响应后4.947秒开始；判分包名为Chrome，forest.pb为0字节、ui_elements=[]，browser.py:109返回0.0，最终保存reward=0.0。
- 已直接读取E/evaluator-0/pixels.png：画布与Success!仍可见。未发现提交丢失、quit乱序、奖励被保存逻辑覆盖等现象。HTTP200不证明Appium内部每一步清理均无异常，更不证明accessibility服务恢复。

逐项关联与输入哈希：[execution-alignment.json](execution-alignment.json)。这是离线核对，不是新设备重跑。

## 空forest在Python路径中如何流动

版本：复现记录android-env1.2.3；源码分为E/official-source快照和评测.venv已安装库。普通调用链：

`get_state → controller.step → wrapper.step内收集extras → controller._process_timestep → get_a11y_tree内再次收集extras → accessibility_tree[-1]`

注意一次get_state内不只一处接收缓冲区drain；只在最后取[-1]处打点会漏掉前一次drain。

### 收到一条空消息，会被当作有效消息保存

`.venv/lib/python3.11/site-packages/android_env/components/a11y/a11y_servicer.py:49-55,145-152,189-199`：

- SendForest把传入的forest交给_process_forest，返回ForestResponse确认；确认不是forest数据。
- 未暂停时保存请求；latest_forest_only只保留最后到达的一条，不校验window数。
- gather_forests取出列表后清空待收列表，不会自己构造空forest。

E/official-source/android_env/wrappers/a11y_grpc_wrapper.py:482-489用“消息列表非空”判断是否打包，不是“消息有窗口”。所以包含一条零窗口消息的列表会正常写入accessibility_tree。

### 没有新消息，不等于返回一条默认空消息

wrapper.py:418-432：累积模式下，没有新key时保留旧key；get_a11y_tree返回累积区最后一条。task_extras():492-500能改变下一次累积行为；必须追踪实际调用时序。

因此同一份判分空forest可以来自：新收到的空forest、早前收到而滞留的空forest、较新的空forest替换非空消息，或转发停止后保留的旧空消息。仅凭0字节无法区分。

controller.py:63-105只对缺key重试；存在但零窗口的forest立即返回。representation_utils.py:136-163随后遍历零窗口，自然得到空列表。这不是图像画面被清空的证据。

### 已执行的本地机制回放

用评测.venv中的真实A11yServicer及打包函数，载入本次保存的forest.pb：

- 未发送消息：gather返回0条，不产生accessibility_tree key。
- 未暂停时发送保存的零窗口forest：返回1条，产生accessibility_tree，选中forest仍为零窗口/0字节。
- 再drain一次：0条、没有新key。
- 暂停时发送：0条被接纳；SendForest正常返回不代表消息被保存。

见[receiver-replay.json](receiver-replay.json)，包含执行代码、退出码0和原输出。没有启动gRPC服务、模拟器或Appium session。它证明库的接收/打包语义，**不证明历史forest何时产生，也不证明quit因果**。

## Appium侧：未见保护能力生效证据，不是已确认根因

### 已确认的配置事实

- E/preflight.json记录共享进程启动为node appium，带address/port/log参数，没有--config；Appium启动日志也没有默认能力块。
- `.venv/appium-androidworld.json:8-10`确实写了`appium:disableSuppressAccessibilityService: true`，但文件存在不能证明被读取。
- E/appium-run.log:5-13与E/appium-responses/0001.json的实际请求、返回均没有disableSuppressAccessibilityService。
- Appium3.7.0 / driver8.7.0，日志选择server10.6.6；设备已有APK未重装。版本日志不是设备APK逐字节身份核验。

### 参数路径与不确定性

已安装driver的`build/lib/uiautomator2-server/core.js:297-317`只在选项为boolean时向am instrument增加`DISABLE_SUPPRESS_ACCESSIBILITY_SERVICES`。

版本匹配的上游[server10.6.6源码](https://github.com/appium/appium-uiautomator2-server/blob/v10.6.6/app/src/main/java/io/appium/uiautomator2/server/ServerInstrumentation.java#L280-L296)表明：省略参数则不改Configurator；显式false设置flags=0；显式true设置FLAG_DONT_SUPPRESS_ACCESSIBILITY_SERVICES。**省略不等于代码显式设置false**。实际AndroidX继承值及连接flags没有动态记录；上游源码也不等于设备二进制身份验证。

该能力的用途可由已安装driver README.md:198核对；不能据此把运行时服务压制写成已发生。

[DeleteSession10.6.6](https://github.com/appium/appium-uiautomator2-server/blob/v10.6.6/app/src/main/java/io/appium/uiautomator2/handler/DeleteSession.java#L42-L63)在响应后延迟15ms停止server并释放shutdown latch，使instrumentation测试入口可返回；driver退出路径再等待进程终止并清理相关进程。所查路径没有AndroidWorld forwarder恢复确认。已有清理成功证据不等于forwarder已恢复绑定。

## 最小下一步：先补来源，不先改参数

由评测侧继续作为唯一设备操作方。新独立目录、先核对当前服务/session所有权；本轮不自动重跑。

### A. 保持能力省略及原流程，只加被动来源追踪

从Appium session创建前开始，到现有官方判分返回后结束：

1. 在SendForest/_process_forest入口记host时间、接收序号、window数、序列化长度、paused状态及是否接纳；在latest-only替换处记被替换的接收序号，保留非空消息被空消息覆盖的轨迹。连续空forest字节相同，不能仅按hash关联；需要接收序号与对象/条目关联。
2. 在gather_forests、pause_and_clear/resume、wrapper每次fetch/accumulate/task_extras记录取出/清空/保留的序号；覆盖一次get_state中的所有drain。
3. 在官方最后选中forest处记录来源序号及接收年龄，区分“本次新接收的空forest”和“早前接收、仍被累积区选中的空forest”；接收年龄不是Android端生成年龄。
4. 关联Appium创建、Success观察、quit、判分的时间。只被动记录已有数据，不加get_state、重试、等待，不改窗口后端。
5. 用时间标记的现有logcat/可用系统状态核对服务连接与中断，区分enabled设置和实际bound。额外系统查询须明确为诊断输入，不冒充原判分状态。

这一步能确认host接收/缓冲来源，但若要证明Android端为什么windows为空，还需对应的生产/连接证据。checkout Kotlin代码能解释空windows如何生成0字节forest，但尚未证明与安装APK完全一致；不得为此擅自重装或修改冻结APK。

### B. 只有A锁定与Appium共存有关，才做显式true单变量对照

新的隔离实验仅修改session请求能力`appium:disableSuppressAccessibilityService: true`；不改共享服务配置、不重启服务、不换观察后端、不加等待。保存实际返回能力、instrumentation参数、服务绑定及同样来源序号链。

若一次true运行成功，只能称候选缓解；来源明确的对照若显示空/非空随能力改变，可支持该能力与故障有关，还需实际连接flags及服务解绑/重绑或抑制状态证据，才能确认压制机制为根因。不得给历史失败补分。

## 当前可交付的判定

- 已确认的直接失败环节：官方forwarder观察为空，并非画图失败、包名错误或reward保存覆盖。
- 已确认的AMKernel边界：第18/19次调用与wire一致；本次无核心修复依据。
- 新增可检验机制：累积区可能返回旧空forest；显式保护accessibility服务的本地配置没有证据被加载。
- 未确认：空forest最初产生时点、生产端窗口来源、Appium抑制是否发生、quit是否导致中断。
- 本轮未操作设备、未创建session、未改生产代码/正式skill/候选方案/冻结安装；原复现目录只读。用户提供的3782个受保护文件哈希结果作为既有证据，不重跑该检查。
