# Browser offline query receipt

Scope: cases003/004 only in campaign `amkernel-0.1.4-r15-current-stack-full-20261109T154403Z`. No live tool/device invocation, task/score rerun, side-effecting Android source import, or test suite. Logs streamed; image bytes decoded in memory, never printed. Line numbers are1-based original JSONL lines. PythonResponse means actual tool_execution_end.result.content structured JSON, not attempted tool arguments. Main narrative: [domain-browser.md](domain-browser.md); full exact cell code/original responses: [domain-browser.json](domain-browser.json).

## Q1 — Actual response/action ledger

Executed read-only code:

```python
import collections,json,pathlib
root=pathlib.Path('campaigns/amkernel-0.1.4-r15-current-stack-full-20261109T154403Z')
for case in ['003-BrowserMaze','004-BrowserMultiply']:
 p=root/'episodes'/case/'attempt-1'; starts={}; rows=[]
 with (p/'raw-private/agent-events.jsonl').open() as f:
  for ln,line in enumerate(f,1):
   e=json.loads(line)
   if e.get('type')=='tool_execution_start':
    starts[e['toolCallId']]=(ln,e)
   if e.get('type')!='tool_execution_end':continue
   sl,s=starts[e['toolCallId']]
   if s.get('toolName')!='write' or s.get('args',{}).get('path')!='xd://mcp__amkernel_python_exec':continue
   r=json.loads(next(x['text'] for x in e['result']['content'] if x['type']=='text'))
   rows.append((r['executionCount'],sl,ln,r['status'],r['kernelState'],r.get('error',{}).get('type')))
 result=json.loads((p/'result.json').read_text())
 print(case, 'accepted',result['stepBudget']['executedActionCount'],'allocated',result['stepBudget']['maxSteps'],'rejectedUI',result['stepBudget']['rejectedActionCount'])
 for row in rows:print(*row,sep=' | ')
 print('statusCounts',dict(collections.Counter(r[3] for r in rows)))
```

Actual output (executionCount | tool start line | actual tool end line | status | kernelState | exception type):

```text
003-BrowserMaze accepted 20 allocated 20 rejectedUI 1
1 | 364 | 365 | completed | alive | None
2 | 502 | 503 | completed | alive | None
3 | 808 | 809 | failed | alive | ModuleNotFoundError
4 | 1028 | 1029 | completed | alive | None
5 | 1168 | 1169 | completed | alive | None
6 | 1342 | 1343 | failed | alive | selenium.common.exceptions.StaleElementReferenceException
7 | 1470 | 1471 | completed | alive | None
8 | 1642 | 1643 | completed | alive | None
9 | 1832 | 1833 | failed | alive | selenium.common.exceptions.TimeoutException
10 | 1960 | 1961 | completed | alive | None
11 | 2132 | 2133 | failed | alive | selenium.common.exceptions.TimeoutException
12 | 2267 | 2268 | completed | alive | None
13 | 2465 | 2466 | completed | alive | None
14 | 2739 | 2740 | completed | alive | None
15 | 2915 | 2916 | completed | alive | None
16 | 3018 | 3019 | completed | alive | None
17 | 3226 | 3227 | failed | alive | selenium.common.exceptions.UnknownMethodException
18 | 3279 | 3281 | completed | alive | None
19 | 3498 | 3499 | completed | alive | None
20 | 3699 | 3701 | completed | alive | None
21 | 3777 | 3779 | completed | alive | None
22 | 3961 | 3962 | failed | alive | selenium.common.exceptions.WebDriverException
23 | 4018 | 4020 | completed | alive | None
24 | 4135 | 4136 | completed | alive | None
statusCounts {'completed': 18, 'failed': 6}
004-BrowserMultiply accepted 15 allocated 22 rejectedUI 0
1 | 315 | 316 | completed | alive | None
2 | 511 | 512 | failed | alive | ModuleNotFoundError
3 | 694 | 695 | completed | alive | None
4 | 979 | 980 | completed | alive | None
5 | 1179 | 1180 | completed | alive | None
6 | 1395 | 1396 | completed | alive | None
7 | 1636 | 1637 | completed | alive | None
8 | 1843 | 1844 | completed | alive | None
9 | 2060 | 2061 | failed | alive | selenium.common.exceptions.TimeoutException
10 | 2310 | 2311 | completed | alive | None
11 | 2522 | 2523 | completed | alive | None
12 | 2836 | 2837 | completed | alive | None
13 | 3047 | 3048 | completed | alive | None
14 | 3393 | 3394 | failed | alive | selenium.common.exceptions.UnknownMethodException
15 | 3572 | 3573 | completed | alive | None
16 | 3914 | 3915 | failed | alive | selenium.common.exceptions.NoSuchElementException
17 | 4164 | 4165 | completed | alive | None
18 | 4538 | 4539 | completed | alive | None
19 | 4778 | 4779 | completed | alive | None
20 | 5016 | 5017 | completed | alive | None
21 | 5186 | 5188 | completed | alive | None
22 | 5287 | 5288 | completed | alive | None
statusCounts {'completed': 18, 'failed': 4}
```

Gate metadata carries sanitized action kind/path/status, not locators. Action labels in JSON reconstruct exact code order plus terminal result. HTTP200 proves admitted request, not Chrome onclick dispatch. Context refusals occur before action gate. Lookup/import failures before mutation consume no UI permit. Reference loop iterations can include detecting agent completion: Multiply16 iterations/15 accepted UI actions.

## Q2 — Exact inline JavaScript, inert DOM only

AST literal extraction, no browser.py import. Actual browser_task_seed substituted. Local Node executes no Chrome/Appium/MCP/device operations. Does not simulate accessibility or real click dispatch. This reproducible code is the corrected combined form of the completed two task probes:

```python
import ast,json,pathlib,re,subprocess
p=pathlib.Path('android_world/android_world/task_evals/single/browser.py')
t=ast.parse(p.read_text())
for name,seed in [('BrowserMaze',1364588068),('BrowserMultiply',3143940091)]:
 cls=next(n for n in t.body if isinstance(n,ast.ClassDef) and n.name==name)
 h=ast.literal_eval(next(n.value for n in cls.body if isinstance(n,ast.Assign) and any(isinstance(v,ast.Name) and v.id=='HTML' for v in n.targets)))
 script=re.search(r'<script>(.*?)</script>',h,re.S)[1].replace('%%SEED%%',str(seed))
 stub="const els={};const document={body:{innerHTML:''},getElementById(id){return els[id]??=( {textContent:'',innerHTML:'',value:'',style:{},classList:{add(){}},appendChild(){}} )},createElement(){return {className:'',innerHTML:'',classList:{add(){}},appendChild(){}}}};"
 if name=='BrowserMaze':
  suffix="console.log(JSON.stringify({name:'BrowserMaze',seed:1364588068,layout:mazeLayout,position:characterPosition}));for(const d of ['right','down','down','down','right','right'])moveCharacter(d);console.log(JSON.stringify({afterShortestPath:characterPosition,body:document.body.innerHTML}));"
 else:
  suffix="let states=[{clicks:0,number:els.number.textContent,numbers:[...numbers]}];for(let i=1;i<=5;i++){handleButtonClick();states.push({clicks:i,number:els.number.textContent,numbers:[...numbers],buttonDisplay:els.button.style.display??'default',numberDisplay:els.number.style.display??'default',formDisplay:els.form.style.display??'default'})}els.answer.value='20250';checkAnswer();console.log(JSON.stringify({name:'BrowserMultiply',seed:3143940091,states,product:numbers.reduce((a,b)=>a*b,1),correctResult:els.result.innerHTML}));els.answer.value='81000';checkAnswer();console.log(JSON.stringify({wrongAnswer:81000,result:els.result.innerHTML}));"
 print(subprocess.run(['node','-e',stub+"for(const id of ['number','button','form','answer','result'])document.getElementById(id);"+script+suffix],capture_output=True,text=True,check=True).stdout,end='')
```

Actual successful **offline source-probe** output (Maze from first invocation; Multiply from corrected Multiply-only invocation). Values20250 and source arrays below are conditional current-source/recorded-seed reconstructions, not captured historical browser numbers[]/clickCount:

```json
{"name":"BrowserMaze","seed":1364588068,"layout":[[" "," ","#","#"],["#"," "," "," "],[" "," "," "," "],[" "," "," ","$"]],"position":{"row":0,"col":0}}
{"afterShortestPath":{"row":3,"col":3},"body":"<h1>Success!</h1>"}
{"name":"BrowserMultiply","seed":3143940091,"states":[{"clicks":0,"number":9,"numbers":[9]},{"clicks":1,"number":10,"numbers":[9,10],"buttonDisplay":"default","numberDisplay":"default","formDisplay":"default"},{"clicks":2,"number":9,"numbers":[9,10,9],"buttonDisplay":"default","numberDisplay":"default","formDisplay":"default"},{"clicks":3,"number":5,"numbers":[9,10,9,5],"buttonDisplay":"default","numberDisplay":"default","formDisplay":"default"},{"clicks":4,"number":5,"numbers":[9,10,9,5,5],"buttonDisplay":"default","numberDisplay":"default","formDisplay":"default"},{"clicks":5,"number":5,"numbers":[9,10,9,5,5],"buttonDisplay":"none","numberDisplay":"none","formDisplay":"block"}],"product":20250,"correctResult":"<h2>Success!</h2>"}
{"wrongAnswer":81000,"result":"<h2></h2>"}
```

Execution history: first invocation completed Maze then failed during Multiply stub inspection with subprocess.CalledProcessError: minimal DOM had not pre-created controls read by suffix. Only failed Multiply step was retried after adding inert control creation, succeeding. This is investigator stub limitation, not episode/browser failure. No product modules imported; no files/devices mutated.

Limit: stub does not parse CSS/HTML. formDisplay="default" before fifth click means **unset in stub**, not historically visible. Source HTML explicitly starts form display:none (browser.py385). Fifth-click assignments are exact current-source logic. This probe conditionally reconstructs sequence/product20250 only if initialized HTML matches inspected current source and uses the recorded seed; it cannot establish the historical full generated array/product or which native click delivered. Actual live numbers[], clickCount and initialized task.html are unarchived. Initial9/final10 do not recover those unknowns. Maze generated layout additionally agrees with all16 visible cells.

## Q3 — Retained screenshot inspection

Equivalent reproducible in-memory extraction/rendering for the same selected retained tool-end lines (actual execution used already indexed matching objects):

```python
import base64,io,json,pathlib
from PIL import Image,ImageDraw
root=pathlib.Path('campaigns/amkernel-0.1.4-r15-current-stack-full-20261109T154403Z/episodes')
selected={'003-BrowserMaze':{3281:18,3701:20,3779:21,4020:23},'004-BrowserMultiply':{5188:21}}
shots=[]
for case,lines in selected.items():
 with (root/case/'attempt-1/raw-private/agent-events.jsonl').open() as f:
  for ln,line in enumerate(f,1):
   if ln not in lines:continue
   e=json.loads(line)
   z=next(z for z in e['result']['content'] if z['type']=='image')
   im=Image.open(io.BytesIO(base64.b64decode(z['data']))).convert('RGB')
   shots.append((case,lines[ln],im))
canvas=Image.new('RGB',(1080,1250),'#ddd'); d=ImageDraw.Draw(canvas)
for i,(case,num,im) in enumerate(shots):
 canvas.paste(im.resize((216,480)),(i*216,30)); d.text((i*216,5),f'{case} call{num}',fill='black')
 if 'Maze' in case:canvas.paste(im.crop((0,330,620,960)).resize((270,275)),((i%4)*270,550))
# Investigation Eval printed the PIL image, rendering it inline without a file.
print(canvas)
```

Actual rendered-image observations, separated from byte provenance:

| Task/call | End JSONL line | Original PNG SHA-256 | Interpretation |
|---|---:|---|---|
|Maze18 |3281 |478504cea5b6864dec8be5363f052e9f94566ad9134aed7e7804ee18f34813d1 | Full4×4 board; X=(0,0), walls=(0,2),(0,3),(1,0), green goal=(3,3). |
|Maze20 |3701 |275a8036005964121d8653dc79436b2b8b72190a74cda1a97d61dbaa95cfea14 | After six element clicks X remains(0,0). |
|Maze21 |3779 |dbe42e332acfa7b7cb9d8e880d5b2eb7de841eac9a1156c7b004be8d20866406 | Coordinate Right tap moves X=(0,1). |
|Maze23 |4020 |edbdaee3c6c5242608315ab8a30c62217699f1ca8179466ea7aad7d454db4a52 | Three admitted Down taps, then refusal; X=(3,1), goal two Right moves away. |
|Multiply21 |5188 |05738f0ac07d2ad3dd8573b7053b3e5e858fc9e6d3d5dae801bf63c8f15a3689 | Page10/Click Me; no product form or Success!. |

Images are historical screenshots, not new device observations. Coordinate recovery worked in Maze; this does not prove all native clicks broken or all web buttons require coordinates. No image artifact copied into reports; original line anchors/hashes reproduce provenance.

## Shared source/parser receipt

shared-offline-checks.json#/sourceIdentity/actualOutput records all19 current Harness inputs matching frozen hash861905dba1d8dfab232cd977cdfbd3ac7837605a5199c982240ad40895599e66. Shared parser/prompt/receipt-precedence checks cover both tasks: original goal/clock/string contract, faithful first-final parsing. They do not prove task correctness. Official AndroidWorld revision recorded55ddaf5edc6f6c25673aed343907d5b9dca66f84; inspected current browser.py SHA-2561f4befd3c069874861ac0144063b0d62e697dff418a82abd9801e25a350010cf. Assigned evidence lacks independently archived initialized HTML/JS variables; do not overstate frozen per-file identity.

## Scope and limitations

No test/build/formatter/linter run. No formal tasks, devices, ADB, Appium, or MCP execution. Inert source probes and JSON/image analysis only. No temporary script files created. Initial incomplete investigator Node DOM stub and an initially malformed report-construction Python cell were corrected without side effects; no original artifact was edited. Underlying native click dispatch and post-quit evaluator UI remain unknown.
