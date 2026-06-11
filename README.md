# Generative Agents 课程作业演示项目

本仓库是对论文 *Generative Agents: Interactive Simulacra of Human Behavior* 的一个课程作业级复现，重点不是做论文级全量系统，而是做一个**可运行、可解释、可演示**的最小完整机制 demo。

## 一、项目是什么

这个项目复现的是论文中的核心认知闭环：

`环境感知 -> 记忆检索 -> 计划驱动 -> 行动/对话 -> 记忆更新 -> 反思形成`

当前系统是一个 Smallville 风格的小镇演示环境，包含：

- 4 个地点
- 3 个角色：Alice、Bob、Carol
- 时间推进
- 计划驱动移动
- 记忆记录与检索
- 对话传播
- 高层反思（reflection）生成

它的目标不是做一个超大规模社会模拟器，而是把论文里最重要的机制做成一个稳定、能讲清楚的课堂演示系统。

## 二、给老师或同学的最快理解方式

如果你只是想把代码拉下来运行并快速理解它的效果：

```bash
git clone https://github.com/guojiageng99/three.git
cd three
```

然后：

1. 启动后端服务，地址是 `127.0.0.1:8000`
2. 启动前端服务，地址是 `localhost:3000` 或 `127.0.0.1:3001`
3. 打开前端页面
4. 在界面上推进时间，观察角色移动、记忆变化、对话传播和反思形成

## 三、这个 demo 具体演示什么

这个项目内置了一条稳定的传播剧情，方便录视频和答辩：

- `10:00` Alice 把晚上的聚会信息告诉 Bob
- `14:00` Bob 再把这个信息告诉 Carol
- 当 3 个角色都知道这件事后，系统形成高层 `reflection`

这样设计的好处是：

- 演示稳定，不容易翻车
- 讲解路线清晰
- 容易把“论文机制”讲出来

## 四、看 demo 时重点看什么

建议重点观察下面几件事：

- 角色会不会按计划移动，而不是随机乱走
- 每个角色是否有自己的记忆流
- 当前动作和对话是否受已检索记忆影响
- 信息是否会随着角色相遇逐步传播
- 当社会信息积累到一定程度后，是否会出现高层 reflection

这就是论文里最核心的“生成式智能体闭环”。

## 五、界面截图

系统总览：

![系统总览](submission_docs/screenshots/01_overview.png)

推理面板：

![推理面板](submission_docs/screenshots/02_reasoning.png)

推理细节截图：

![推理细节](submission_docs/screenshots/03_reasoning_crop.png)

## 六、技术栈

- 前端：Next.js + React
- 后端：FastAPI + Python
- 模型模式：`deterministic` 稳定规则演示 / `llm` OpenAI 兼容智能体模式

## 七、运行环境要求

- Python `3.10+`
- Node.js + `npm`
- Windows PowerShell、cmd、Anaconda Prompt 均可
- 可选：Conda

说明：

- 当前项目本地验证环境为 Python `3.12.x`
- 如果你之前用 Python `3.9` 建过 `backend/.venv`，建议删掉重建

## 八、快速启动

如果你只想最快跑起来：

1. 准备 Python `3.10+` 和 Node.js
2. 安装后端依赖 `backend/requirements.txt`
3. 安装前端依赖 `frontend/package.json`
4. 启动后端 `8000` 端口
5. 设置 `NEXT_PUBLIC_API_BASE=http://127.0.0.1:8000`
6. 启动前端并打开 `http://localhost:3000` 或 `http://127.0.0.1:3001`

## 九、推荐启动方式

### 1. Conda 环境

如果你的 Conda 已可正常使用，推荐：

```bash
conda activate ga-demo
```

如果你需要重建这个环境：

```bash
conda create -n ga-demo python=3.12 -y
conda run -n ga-demo python -m pip install -r backend/requirements.txt
```

如果要运行测试，再安装开发依赖：

```bash
conda run -n ga-demo python -m pip install -r backend/requirements-dev.txt
```

### 2. 后端启动

#### Windows cmd / Anaconda Prompt

```bat
conda activate ga-demo
cd /d E:\demo\buaa\suanfa\three\backend
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

#### Windows PowerShell

```powershell
conda activate ga-demo
cd E:\demo\buaa\suanfa\three\backend
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

#### 如果 Conda 激活有问题，也可以直接指定解释器启动

```powershell
cd E:\demo\buaa\suanfa\three\backend
& "D:\anaconda\install\envs\ga-demo\python.exe" -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### 3. 前端启动

#### Windows cmd

```bat
cd /d E:\demo\buaa\suanfa\three\frontend
set NEXT_PUBLIC_API_BASE=http://127.0.0.1:8000
npm install
npm run dev
```

#### Windows PowerShell

```powershell
cd E:\demo\buaa\suanfa\three\frontend
$env:NEXT_PUBLIC_API_BASE="http://127.0.0.1:8000"
npm install
npm run dev
```

前后端都启动后，打开：

```text
http://localhost:3000
```

或者：

```text
http://127.0.0.1:3001
```

## 十、界面操作说明

页面打开后，建议按这个顺序操作：

1. 先看控制区顶部的 `当前书签说明`
2. 点击 `08:00 初始态` 回到起点
3. 点击 `10:00 第一次传播`
4. 必要时点击 `单步推进` 或 `开始演示`
5. 点击地图上的角色，查看计划、记忆、对话、反思
6. 观察信息如何从 Alice 传给 Bob，再由 Bob 传给 Carol

补充说明：

- 首页会直接显示 `当前阶段`
- 控制区会显示 `当前书签说明`
- 控制区会直接写明 `界面当前会优先看` 哪个角色
- 每个阶段都会明确提示：
  - 现在先看什么
  - 这一步说明什么
  - 接下来怎么点

## 十一、详细演示步骤

这一部分是最适合录 10 分钟视频和课堂答辩的讲解路线。  
每一步都回答三个问题：

1. 点什么
2. 看到什么
3. 对应论文中的哪个机制

### 先解释两个词

- `gathering`：Alice 晚上的聚会/社交活动
- `reflection`：角色把多条低层记忆总结成一个更高层的认识，也可以直接讲成“高层反思”

例如：

- 低层记忆：`Alice 告诉了 Bob gathering`
- 低层记忆：`Bob 又告诉了 Carol gathering`
- 高层 reflection：`这件事已经不再是私人信息，而变成了镇上的共享信息`

### 第一步：看 08:00 初始态

点击：

- `08:00 初始态`
- 或 `重置场景`

你应该看到：

- 时间变成 `08:00`
- 界面出现 `当前书签说明`
- Alice 在 `Alice 家`
- Bob 在 `约翰逊公园`
- Carol 在 `镇中心广场`
- 只有 Alice 知道聚会信息

这一步体现：

- 每个角色有自己的计划
- 角色不是随机乱动
- 初始知识状态是不对称的
- 页面已经直接告诉你“这一步说明什么”

对应论文机制：

- planning
- persistent internal state
- initial memory difference

### 第二步：推进到 10:00，展示第一次传播

点击：

- `10:00 第一次传播`

如果你想手动演示，也可以从 `08:00` 连点 `单步推进` 4 次。

你应该看到：

- 时间变成 `10:00`
- 控制区反馈变成“已切换到 10:00 第一次传播，现在可以开始讲这一步了”
- 页面会自动把右侧观察对象切到 `Bob`
- Alice 和 Bob 同时出现在 `霍布斯咖啡馆`
- 最近关键事件显示 `聚会信息完成一次传播`
- Bob 开始知道聚会信息
- 传播链显示 `Alice -> Bob`
- `当前书签说明` 会明确告诉你这一步证明“对话真实改写了另一个角色的内部状态”

这一步体现：

- 角色按计划移动
- 相遇后会发生社交传播
- 对话不仅是文本，还会真的改写记忆和知识状态

对应论文机制：

- plan-driven movement
- social interaction
- memory update
- information propagation

### 第三步：解释记忆检索

停留在 `10:00`，点击 `Bob`。

你应该看到：

- 右侧 `检索到的记忆` 里有和聚会、最近对话有关的记忆
- 检索得分说明标签会显示为什么这些记忆被选中
- `最新话语`、`当前为什么这样行动` 会跟刚才的传播事件对应起来

这一步体现：

- Agent 不是把全部记忆一次性拿来用
- 它会先检索最相关的记忆
- 当前行为不仅受日程驱动，也受 recalled memory 影响

对应论文机制：

- memory stream
- retrieval
- context-conditioned action generation

### 第四步：推进到 14:00，展示第二次传播

点击：

- `14:00 第二次传播`

你应该看到：

- 时间变成 `14:00`
- 页面会自动把右侧观察对象切到 `Carol`
- Alice、Bob、Carol 都在 `镇中心广场`
- 时间线显示 Bob 把聚会信息告诉 Carol
- 传播链变成：
  - `Alice -> Bob`
  - `Bob -> Carol`
- Carol 也知道聚会信息
- `反思数量` 仍然是 `0`
- `当前书签说明` 会提示你：这一步证明“多个局部互动会累计成全局传播”

这一步体现：

- 信息可以在多个角色间接力传播
- 系统模拟的是社会过程，不是一句写死的剧情台词
- 局部交互会逐步累积成全局状态变化

对应论文机制：

- multi-agent social behavior
- chained propagation
- environment-mediated encounters

### 第五步：推进到 reflection 形成态

点击：

- `14:30 反思形成态`

你应该看到：

- 当前阶段变成 `反思形成`
- 页面会自动把右侧观察对象切到 `Alice`
- 时间线里出现 `高层反思已经形成`
- 已知情角色会拥有 reflection 条目
- 当前行为或说明文字会提到共享信息/高层反思
- `反思数量` 变成 `3`
- `当前书签说明` 会提示你：这一步证明系统不只存具体记忆，还会做高层总结

这一步体现：

- 系统不会停留在单条记忆层面
- 它会把多个低层事件总结成更高层结论
- 高层结论还会反过来影响后续行为

对应论文机制：

- reflection
- higher-level memory abstraction
- long-range behavioral coherence

### 第六步：一句话解释“为什么这叫论文复现”

答辩时可以直接说：

> 这个 demo 复现了论文中的最小完整机制：角色先按计划行动，在环境中自然相遇，检索相关记忆，通过对话传播信息，更新内部状态，最后形成更高层的 reflection。

### 最短演示路径

如果时间很紧，可以直接用这条最短路线：

1. `08:00 初始态`
2. 解释只有 Alice 知道聚会信息
3. `10:00 第一次传播`
4. 展示 `Alice -> Bob`
5. 点击 Bob，展示记忆检索和推理依据
6. `14:00 第二次传播`
7. 展示 `Bob -> Carol`
8. `14:30 反思形成态`
9. 展示 `Reflections` 面板

这条路线最适合 10 分钟视频讲解。

## 十二、后端接口说明

后端基础地址：

- `http://127.0.0.1:8000`

HTTP 接口：

- `GET /api/state`：获取当前世界状态
- `POST /api/sim/start`：开始连续模拟
- `POST /api/sim/pause`：暂停模拟
- `POST /api/sim/tick`：单步推进一次
- `POST /api/sim/reset`：重置为初始状态

WebSocket：

- `WS /ws/state`：每秒向前端推送最新世界状态

前端连接规则：

- `NEXT_PUBLIC_API_BASE` 默认是 `http://127.0.0.1:8000`
- WebSocket 地址由这个基础地址自动推导

## 十三、仓库结构说明

- `backend/app/`：FastAPI 服务、仿真主循环、认知逻辑、数据模型、prompt 模板
- `backend/requirements.txt`：后端依赖
- `frontend/app/`：Next.js 页面入口和全局样式
- `frontend/components/`：地图、控制栏、侧边栏等组件
- `frontend/lib/`：前端 API 工具、共享类型、界面文案转换工具
- `submission_docs/`：PPT、报告、脚本、截图等课程材料
- `docs/`：设计与计划文档
- `scripts/`：提交包构建脚本和辅助脚本
- `timeline_frames/`：时间线相关素材

## 十四、建议的查看顺序

如果你是老师、同学或者组员，推荐按这个顺序看：

1. 先读本 `README.md`
2. 本地启动前后端
3. 打开页面，按内置剧情走一遍
4. 再看 `submission_docs/` 里的 PPT、报告和脚本
5. 需要时再看 `backend/app/` 和 `frontend/` 源码

## 十五、常见问题

### 1. 前端打开了，但页面没有状态

先检查后端是否已经运行在 `127.0.0.1:8000`。

### 2. 我改了后端端口

启动前端前，记得同步修改：

```text
NEXT_PUBLIC_API_BASE
```

### 3. 没有配置大模型 API Key

没关系。这个项目默认支持稳定规则回退模式，不配 key 也能完整演示。

### 4. 旧虚拟环境有问题

如果 `backend/.venv` 是老 Python 版本建的，删掉重建即可。

### 5. 3000 或 8000 端口被占用

停止冲突进程，或者改端口。但改了后端端口后，前端的 `NEXT_PUBLIC_API_BASE` 也要一起改。

## 十六、项目局限性

- 这是课程作业级 demo，不是论文原始系统的全量复现
- 当前只有 4 个地点和 3 个角色
- 主线剧情在 `deterministic` 模式下稳定可控，方便录视频和答辩
- `llm` 模式可以让计划、行动、对话和反思更多由模型生成，但仍会在失败时规则回退
- 反思不再只是固定时间写死触发，而是在传播完成后由记忆重要性阈值触发

## 十七、可选的大模型模式

后端支持两种模式：

- `SIMULATION_MODE=deterministic`：默认模式，不需要 API key，适合答辩和录屏
- `SIMULATION_MODE=llm`：启用 OpenAI 兼容接口，让 LLM 参与计划、行动、对话和反思生成

反思阈值可选配置：

- `REFLECTION_IMPORTANCE_THRESHOLD`：默认 `2.4`，表示共享信息传播完成后，角色记忆重要性累计到阈值才形成 reflection

Windows cmd：

```bat
set SIMULATION_MODE=llm
set LLM_API_KEY=your_key
set LLM_BASE_URL=https://api.openai.com/v1
set LLM_MODEL=gpt-4o-mini
set REFLECTION_IMPORTANCE_THRESHOLD=2.4
```

Windows PowerShell：

```powershell
$env:SIMULATION_MODE="llm"
$env:LLM_API_KEY="your_key"
$env:LLM_BASE_URL="https://api.openai.com/v1"
$env:LLM_MODEL="gpt-4o-mini"
$env:REFLECTION_IMPORTANCE_THRESHOLD="2.4"
```

如果不配置 `SIMULATION_MODE=llm`，系统会使用 deterministic 规则演示模式；如果选择 `llm` 但没有 `LLM_API_KEY` 或接口失败，系统会自动规则回退并继续运行。界面右侧会显示当前模式、LLM 最近状态、记忆流条数和 reflection 触发原因。

### LLM 模式演示流程

如果想把复现讲得更“像论文”，推荐用 `llm` 模式跑一遍。  
这个模式下，环境、角色相遇和传播链仍由程序保证稳定；但 daily plan、当前行动、对话内容和 reflection 文本会优先交给 LLM 生成。这样既能避免课堂 demo 翻车，又能说明系统确实接入了论文里的 generative cognition。

启动后端前先配置：

```powershell
$env:SIMULATION_MODE="llm"
$env:LLM_API_KEY="your_key"
$env:LLM_BASE_URL="https://api.openai.com/v1"
$env:LLM_MODEL="gpt-4o-mini"
$env:REFLECTION_IMPORTANCE_THRESHOLD="2.4"
```

然后正常启动后端和前端。打开页面后，建议按下面顺序演示：

1. 点击 `08:00 初始态`
   - 现象：右侧全局状态显示 `LLM 智能体模式`，模型栏显示配置的模型名；只有 Alice 知道聚会。
   - 论文机制：说明 agent 有 persona、初始记忆和内部状态，对应 persistent internal state 与 planning 起点。

2. 点击 `10:00 第一次传播`
   - 现象：Alice 和 Bob 在咖啡馆相遇，Bob 获得聚会信息，传播链出现 `Alice -> Bob`；最新话语和当前行动会优先由 LLM 生成。
   - 论文机制：说明角色根据地点、计划、附近人物和检索记忆生成行动与对话，对应 observation、retrieval、action generation、memory update。

3. 点击 Bob，展开 `认知细节`
   - 现象：可以看到检索到的记忆、分数、关键词重叠和相关性；全局 `记忆流` 数量增加。
   - 论文机制：说明 agent 不是直接读取全部记忆，而是从 memory stream 中检索相关内容，对应 memory stream 和 retrieval function。

4. 点击 `14:00 第二次传播`
   - 现象：Bob 在广场把消息告诉 Carol，传播链变成 `Alice -> Bob`、`Bob -> Carol`，此时通常还没有 reflection。
   - 论文机制：说明信息不是全局广播，而是通过环境中的局部相遇逐步扩散，对应 multi-agent social behavior 和 environment-mediated interaction。

5. 点击 `14:30 反思形成态`
   - 现象：三位角色都知道聚会，reflection 数量变成 `3`，右侧出现 `反思触发依据`。
   - 论文机制：说明 reflection 不是单条事件，而是共享信息传播完成后，记忆重要性累计超过阈值形成的高层抽象，对应论文中的 reflection 和 higher-level memory abstraction。

答辩时可以这样概括：

> 本项目提供 deterministic 和 llm 两种模式。deterministic 模式用于稳定录屏和课堂演示；llm 模式让大模型参与计划、行动、对话和反思生成，更接近 Generative Agents 论文中的认知生成过程。同时系统保留规则回退，避免 API 失败导致 demo 中断。

需要注意的是，当前项目是课程作业级 LLM 增强复现，不是 Stanford 原版 Smallville 的完整工程复刻。它已经支持 LLM 参与核心认知闭环，但没有实现 25 个 agent、完整沙盒世界、embedding retrieval 和长期多日生活模拟。

## 十八、课程提交材料

课程相关材料在 `submission_docs/` 中，包括：

- PPT
- 报告 markdown 源文件
- PPT 逐页文案
- PPT 演讲稿
- 10 分钟视频脚本
- 报告截图素材

## 十九、界面中的演示辅助功能

前端已经支持这些更适合答辩和录屏的功能：

- `当前阶段`：直接告诉你现在处于初始准备、开始传播、传播完成还是反思形成
- `当前书签说明`：直接告诉你当前先看什么、这一步说明什么、接下来怎么点
- `单步推进`：每次推进 30 分钟
- `保存快照 / 恢复快照`：保存和恢复某个演示状态
- 倍速切换：`0.5x / 1x / 2x`
- 场景书签：
  - `08:00 初始态`
  - `10:00 第一次传播`
  - `14:00 第二次传播`
  - `14:30 反思形成态`

如果你是为了录视频，优先用这些书签，不容易出错。

## 二十、证据导出

如果你希望把当前 deterministic demo 导出成报告可用证据：

```bash
python scripts/export_demo_evidence.py
```

导出结果：

- `submission_docs/evidence/demo_evidence.json`
- `submission_docs/evidence/demo_evidence.md`

其中 Markdown 文件可以直接复用到报告、PPT 备注或附录中。

## 二十一、给组员的简短说明

你可以把这段话直接转给组员：

> 这是一个 Generative Agents 的课堂演示项目。前端负责展示小镇地图、角色计划、记忆、推理和对话，后端负责调度时间、执行计划、检索记忆、生成动作和形成 reflection。默认不依赖 API key，也能稳定运行，所以非常适合本地复现和课程演示。
