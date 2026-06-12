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
4. 在 `backend/` 目录启动后端（默认 `127.0.0.1:8000`）
5. 设置 `NEXT_PUBLIC_API_BASE=http://127.0.0.1:8000`
6. 在 `frontend/` 目录启动前端，打开终端提示的地址（常见 `localhost:3000` 或 `127.0.0.1:3001`）

若后端报 `[WinError 10013]`，先释放 8000 端口，详见「九、推荐启动方式 → 启动失败」。

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

在 **`backend/` 目录** 下执行（命令本身没有变，仍是 uvicorn）：

#### Windows cmd / Anaconda Prompt

```bat
conda activate ga-demo
cd E:\demo\buaa\suanfa\three\backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

#### Windows PowerShell

```powershell
conda activate ga-demo
cd E:\demo\buaa\suanfa\three\backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

看到 `Application startup complete` 后，另开终端启动前端。可用下面命令确认后端已就绪：

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/state | Select-Object time_label, simulation_mode
```

#### 如果 Conda 激活有问题，也可以直接指定解释器启动

```powershell
cd E:\demo\buaa\suanfa\three\backend
& "D:\anaconda\install\envs\ga-demo\python.exe" -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

#### 启动失败：`[WinError 10013]` 或 `[WinError 10048]`

这通常表示 **8000 端口已被占用**（上次 uvicorn 没关、IDE 里还跑着旧进程、或别的程序占了端口），不是启动命令改了。

PowerShell 查占用并结束进程：

```powershell
Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue |
  Select-Object -ExpandProperty OwningProcess -Unique |
  ForEach-Object { Stop-Process -Id $_ -Force -ErrorAction SilentlyContinue }
```

或用 cmd：

```bat
netstat -ano | findstr :8000
taskkill /PID <上一步最后一列的 PID> /F
```

然后重新执行上面的 uvicorn 命令。

若仍报 10013，可换端口（需同步改前端 `NEXT_PUBLIC_API_BASE`）：

```powershell
python -m uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload
```

### 3. 前端启动

#### Windows cmd

```bat
cd E:\demo\buaa\suanfa\three\frontend
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

前后端都启动后，打开终端里 **Next.js 提示的地址**（常见如下）：

```text
http://localhost:3000
```

若 3000 已被占用，Next 会自动改用 3001：

```text
http://127.0.0.1:3001
```

页面长时间显示「正在等待后端仿真状态」时，先确认 `http://127.0.0.1:8000/api/state` 能打开。

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

## 十一、从开始到结束录制复现视频

这一节可以直接当作录屏脚本使用。主视频建议走书签路线，少用自动播放，这样更稳定，也更容易把论文机制讲清楚。  
如果你启用了 LLM 模式，可以把它作为加分展示：角色的行动、话语和反思优先由百炼/Qwen 生成；如果某次大模型调用失败，系统会用规则兜底，机制展示仍然成立。

### 录制前先做一次检查

先确认后端和前端都已经启动，然后打开前端页面。

你应该先看三个地方：

- 右上角连接状态是否是 `已连接`
- 右侧 `全局状态` 里的模式是否是 `规则模式` 或 `大模型智能体模式`
- 如果使用 LLM 模式，`大模型` 状态最好是 `大模型已就绪` 或 `最近一次大模型调用成功`

录屏时可以这样说：

> 这个系统有两种运行方式。规则模式保证录屏稳定，大模型模式让角色的行动、对话和反思更多由百炼/Qwen 生成，而计划始终由程序硬编码以保证剧情节点稳定。无论哪种模式，世界时间、相遇检测、传播链和反思触发都由程序护栏保证，所以演示不会因为一次 API 波动而中断。

### 第一步：重置到 08:00 初始态

点击：

- **重置场景**
- 或 **08:00 初始态**

看哪里：

- 右侧 **时间线** 区域
- 中间 **地图视图**
- 右侧 **三人状态**
- 下方 **当前阶段**

应该看到：

- 当前时间变成 `08:00`
- Alice 在 `Alice 家`
- Bob 在 `约翰逊公园`
- Carol 在 `镇中心广场`
- 三人状态里只有 Alice 是 `已知聚会`
- Bob 和 Carol 仍然是 `未知聚会`
- 当前阶段是 `初始准备`

这一步体现的论文机制：

- `persona`：每个角色都有自己的身份、性格和初始设定
- `planning`：每个角色一开始就有计划，不是随机移动
- `memory stream`：每个角色拥有自己的初始记忆
- `internal state`：三个人知道的信息不同，内部状态不对称

建议讲法：

> 这里先看起点状态。Alice 知道晚上有聚会，但 Bob 和 Carol 还不知道。三个角色分布在不同地点，并且每个人都有自己的计划和记忆。这个起点对应论文里的 persona、planning 和 memory stream。

### 第二步：推进到 10:00 第一次传播

点击：

- **10:00 第一次传播**

看哪里：

- 地图上的 `霍布斯咖啡馆`
- 右侧 **三人状态**
- 下方 **最近发生的关键事件**
- 右侧 **传播链**

应该看到：

- 当前时间变成 `10:00`
- Alice 和 Bob 出现在 `霍布斯咖啡馆`
- Bob 从 `未知聚会` 变成 `已知聚会`
- 最近关键事件会出现一次聚会信息传播
- 传播链出现 `Alice -> Bob`
- 页面通常会把当前观察对象切到 Bob

这一步体现的论文机制：

- `plan-driven movement`：角色按计划到达咖啡馆
- `social interaction`：两个角色同处一个地点后发生对话
- `memory update`：Bob 的记忆和知识状态被改写
- `information propagation`：信息从 Alice 传播给 Bob

建议讲法：

> 这一刻不是简单显示一句台词，而是一次对话真正改变了 Bob 的内部状态。Bob 原来不知道聚会，现在知道了，并且传播链记录了 Alice 到 Bob 的信息流动。

### 第三步：点击 Bob，解释记忆检索

点击：

- 地图上的 **Bob**
- 或右侧 **三人状态** 里的 **Bob**

看哪里：

- 右侧 **当前行为**
- 右侧 **最新话语**
- 展开 **认知细节（计划、记忆、时间线）**
- 看 **检索到的记忆**
- 看 **当前为什么这样行动**

应该看到：

- Bob 的位置是 `霍布斯咖啡馆`
- Bob 已经知道聚会信息
- `检索到的记忆` 中会出现与当前位置、计划、Alice 或聚会相关的记忆
- 记忆旁边会有得分和标签，例如重要性、最近发生、同一地点、相关角色
- Bob 的行为说明会把计划、地点、附近角色和记忆线索联系起来

这一步体现的论文机制：

- `memory retrieval`：行动前先检索相关记忆
- `relevance / recency / importance`：检索不是全量读取，而是按相关性、最近性和重要性排序
- `context-conditioned action generation`：当前行动受计划、地点、附近角色和记忆共同影响

建议讲法：

> Generative Agents 不是把所有记忆一次性塞给模型，而是先从 memory stream 中检索当前最相关的记忆。这里可以看到 Bob 的行为不是孤立生成的，而是由计划、当前位置、附近角色和召回记忆共同决定。

### 第四步：推进到 14:00 第二次传播

点击：

- **14:00 第二次传播**

看哪里：

- 地图上的 `镇中心广场`
- 右侧 **三人状态**
- 右侧 **传播链**
- 下方 **传播进度**
- 下方 **最近发生的关键事件**

应该看到：

- 当前时间变成 `14:00`
- Alice、Bob、Carol 出现在 `镇中心广场`
- Carol 从 `未知聚会` 变成 `已知聚会`
- 传播链变成：
  - `Alice -> Bob`
  - `Bob -> Carol`
- 传播进度变成 `3/3`
- 此时 `反思数量` 仍然可以是 `0`，因为系统还没有进入反思形成阶段

这一步体现的论文机制：

- `multi-agent social behavior`：多个角色通过局部相遇形成社会过程
- `chained propagation`：信息不是广播，而是接力传播
- `environment-mediated encounters`：地点和时间安排影响谁会遇到谁

建议讲法：

> 第二次传播说明系统模拟的是一个社会过程，而不是一句写死的剧情。Bob 在之前从 Alice 那里获得信息，现在又把信息传给 Carol。多个局部互动累计起来，形成了全局传播。

### 第五步：点击 Carol，确认接收者状态变化

点击：

- 地图上的 **Carol**
- 或右侧 **三人状态** 里的 **Carol**

看哪里：

- Carol 的 **当前行为**
- Carol 的 **最新话语**
- Carol 的 **近期记忆**
- Carol 的 **检索到的记忆**

应该看到：

- Carol 已经是 `已知聚会`
- 她的近期记忆中会有 Bob 告诉她聚会信息的记录
- 她的当前行为或推理说明会受新获得的信息影响

这一步体现的论文机制：

- `memory write`：对话结果写入接收者的私有记忆
- `state change`：角色知识状态发生变化
- `socially grounded behavior`：后续行为会受到刚接收到的信息影响

建议讲法：

> 这里重点看接收者 Carol。她不是只在界面上变了一个标签，而是新增了和 Bob 对话相关的记忆。这个记忆会进入她自己的 memory stream，后续行动可以继续使用。

### 第六步：推进到 14:30 反思形成态

点击：

- **14:30 反思形成态**

看哪里：

- 下方 **反思数量**
- 右侧 **传播与反思**
- 右侧 **反思触发依据**
- 下方 **当前阶段**
- 右侧 **事件时间线**

应该看到：

- 当前时间变成 `14:30`
- 当前阶段变成 `反思形成`
- `反思数量` 变成 `3`
- 三位角色都已经知道聚会
- 右侧出现 reflection 文本
- 反思触发依据会说明共享知识已经覆盖所有角色，并且记忆重要性达到阈值
- 时间线里出现 `高层反思已经形成` 或类似事件

这一步体现的论文机制：

- `reflection`：从多条低层记忆中形成高层总结
- `higher-level memory abstraction`：系统不只保存事件，还会抽象成社会性认知
- `long-range behavioral coherence`：高层反思会成为后续计划和行动的上下文

建议讲法：

> 反思是论文中很关键的机制。系统不会停在“谁告诉了谁”这种低层事件，而是把多次传播总结成更高层的认知：这场聚会已经从 Alice 的私人信息变成了小镇共享事件。

### 第七步：点击任意角色，展示“每个人都有自己的认知状态”

点击：

- **Alice**
- **Bob**
- **Carol** 任意一个角色

看哪里：

- 角色身份
- 当前行为
- 最新话语
- 近期记忆
- 检索到的记忆
- 反思文本

应该看到：

- 每个角色都有自己的 profile
- 每个角色都有自己的计划和记忆
- 每个角色的检索结果不完全相同
- 每个角色都可以形成 reflection，但 reflection 文本会从自己的记忆角度出发

这一步体现的论文机制：

- `agent identity`：每个 Agent 有稳定身份
- `private memory stream`：记忆属于单个角色，不是所有人共享一个大文本
- `individual cognition`：同一事件会进入不同角色的认知上下文

建议讲法：

> 这一步可以说明“每个人物都是一个独立智能体”。他们共享同一个小镇环境，但各自有自己的 persona、计划、记忆和反思。系统把共享世界和私有认知分开处理，这也是复现论文机制时最重要的结构。

### 第八步：用一句话收尾

录屏最后可以直接说：

> 这个 demo 复现的是 Generative Agents 论文中的最小完整闭环：角色先基于 persona 和计划行动，在环境中自然相遇，检索自己的相关记忆，通过对话传播信息，把新信息写回 memory stream，最后从多条低层记忆中形成高层 reflection。

### 10 分钟视频推荐节奏

如果视频控制在 10 分钟左右，可以按这个节奏录：

1. `0:00 - 1:00`：介绍论文目标和系统界面
2. `1:00 - 2:00`：点击 **08:00 初始态**，讲 persona、planning、memory stream
3. `2:00 - 3:30`：点击 **10:00 第一次传播**，讲 Alice 到 Bob 的传播
4. `3:30 - 5:00`：点击 **Bob**，讲记忆检索和当前行为生成
5. `5:00 - 6:30`：点击 **14:00 第二次传播**，讲 Bob 到 Carol 的接力传播
6. `6:30 - 7:30`：点击 **Carol**，讲接收者记忆更新
7. `7:30 - 9:00`：点击 **14:30 反思形成态**，讲 reflection
8. `9:00 - 10:00`：切换任意角色，总结完整闭环和项目边界

### 录屏时的注意事项

- 主录屏优先使用书签按钮，不要一开始就长时间点 **开始演示**。
- 如果使用 LLM 模式，点击 **单步推进** 后可能需要等待 `30-90` 秒。
- 如果右侧出现 `大模型调用失败`，可以解释系统已进入规则兜底；论文机制展示仍然有效。
- 每到一个关键阶段，建议先点 **暂停演示** 或直接使用书签停住，再讲 20-60 秒。
- 如果讲乱了，点 **重置场景** 回到 `08:00`，再从书签路线重新开始。

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

### 5. 8000 端口被占用 / 启动报 WinError 10013、10048

**启动方式没有变**，仍是 `cd backend` 后执行 uvicorn。报错多半是 **8000 已被占用**。

1. 结束占用 8000 的进程（见「九、推荐启动方式 → 启动失败」里的 PowerShell 命令）
2. 重新启动后端
3. 或改用 `--port 8001`，并设置 `NEXT_PUBLIC_API_BASE=http://127.0.0.1:8001`

### 6. 3000 端口被占用

Next.js 会自动尝试 **3001**，看 `npm run dev` 输出里的 `Local:` 地址即可。无需改后端。

## 十六、项目局限性

- 这是课程作业级 demo，不是论文原始系统的全量复现
- 当前只有 4 个地点和 3 个角色
- 主线剧情在 `deterministic` 模式下稳定可控，方便录视频和答辩
- `llm` 模式可以让行动、对话和反思更多由模型生成（计划始终硬编码以保证剧情），但仍会在失败时规则回退
- 反思不再只是固定时间写死触发，而是在传播完成后由记忆重要性阈值触发

## 十七、可选的大模型模式

当前代码支持 LLM 模式，但需要先说清楚边界：

- LLM 会参与：当前行动生成、对话生成、reflection 反思生成（计划始终由程序硬编码，保证 10:00 咖啡馆相遇、14:00 广场传播等剧情节点不被覆盖）
- 程序仍保证：时间推进、角色相遇、传播链稳定、失败后规则回退
- 检索仍是规则评分：`importance + recency + relevance + location + social`，不是 embedding 检索

后端支持两种运行模式：

- `SIMULATION_MODE=deterministic`：默认模式，不需要 API key，适合答辩和录屏
- `SIMULATION_MODE=llm`：启用 OpenAI 兼容接口，让 LLM 参与行动、对话和反思生成（计划始终硬编码）

这种设计适合答辩：**稳定演示不翻车，LLM 模式体现论文里的 generative cognition。**

### LLM 模式配置方式

后端必须在启动前设置环境变量，因为 `SimulationEngine` 会在服务启动时读取配置。

推荐本地创建 `backend/.env`。这个文件用于放真实 key，已经被 `.gitignore` 忽略，不要提交。

```env
SIMULATION_MODE=llm
DASHSCOPE_API_KEY=你的阿里云百炼 API Key
LLM_BASE_URL=https://token-plan.cn-beijing.maas.aliyuncs.com/compatible-mode/v1
LLM_MODEL=qwen3.6-flash
LLM_TIMEOUT_SECONDS=60
REFLECTION_IMPORTANCE_THRESHOLD=2.4
LLM_DEBUG_LOG=true
LLM_LOG_FILE=backend/logs/llm_debug.log
```

也可以继续使用通用变量名 `LLM_API_KEY`；如果两个变量都设置，优先使用 `LLM_API_KEY`。当前默认供应商是阿里云百炼，默认模型是 `qwen3.6-flash`，默认 OpenAI 兼容地址是 `https://token-plan.cn-beijing.maas.aliyuncs.com/compatible-mode/v1`。

然后直接启动后端即可：

```powershell
cd E:\demo\buaa\suanfa\three\backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

如果不想使用 `.env`，也可以在启动后端的终端里手动设置环境变量。

Windows PowerShell：

```powershell
cd E:\demo\buaa\suanfa\three\backend

$env:SIMULATION_MODE="llm"
$env:DASHSCOPE_API_KEY="你的阿里云百炼 API Key"
$env:LLM_BASE_URL="https://token-plan.cn-beijing.maas.aliyuncs.com/compatible-mode/v1"
$env:LLM_MODEL="qwen3.6-flash"
$env:LLM_TIMEOUT_SECONDS="60"
$env:REFLECTION_IMPORTANCE_THRESHOLD="2.4"
$env:LLM_DEBUG_LOG="true"
$env:LLM_LOG_FILE="backend/logs/llm_debug.log"

python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Windows cmd：

```bat
cd E:\demo\buaa\suanfa\three\backend

set SIMULATION_MODE=llm
set DASHSCOPE_API_KEY=your_bailian_key
set LLM_BASE_URL=https://token-plan.cn-beijing.maas.aliyuncs.com/compatible-mode/v1
set LLM_MODEL=qwen3.6-flash
set LLM_TIMEOUT_SECONDS=60
set REFLECTION_IMPORTANCE_THRESHOLD=2.4
set LLM_DEBUG_LOG=true
set LLM_LOG_FILE=backend/logs/llm_debug.log

python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

前端启动：

```powershell
cd E:\demo\buaa\suanfa\three\frontend

$env:NEXT_PUBLIC_API_BASE="http://127.0.0.1:8000"
npm run dev
```

阿里云百炼的 OpenAI 兼容接口会请求 `{LLM_BASE_URL}/chat/completions`，所以上面的配置实际调用 `https://token-plan.cn-beijing.maas.aliyuncs.com/compatible-mode/v1/chat/completions`。如使用海外地域或其他百炼 endpoint，按百炼控制台/文档替换 `LLM_BASE_URL` 即可。

如果使用中转或其他 OpenAI 兼容接口，把 `LLM_BASE_URL` 改成服务商要求的 base URL，`LLM_MODEL` 改成服务商支持的模型名即可。代码仍然请求 `{LLM_BASE_URL}/chat/completions`。

`LLM_TIMEOUT_SECONDS` 默认是 `60`。百炼/Qwen 这类大模型如果首次响应慢，建议先保持 `60`，不要用很短的超时时间。

`REFLECTION_IMPORTANCE_THRESHOLD` 默认是 `2.4`，表示共享信息传播完成后，角色记忆重要性累计到阈值才形成 reflection。

如果不配置 `SIMULATION_MODE=llm`，系统会使用 deterministic 规则演示模式；如果选择 `llm` 但没有 `LLM_API_KEY` / `DASHSCOPE_API_KEY` 或接口失败，系统会自动规则回退并继续运行。界面右侧会显示当前模式、LLM 最近状态、记忆流条数和 reflection 触发原因。

在机制上，可以把每个角色理解成一个“由同一个百炼模型扮演、但上下文相互隔离”的 LLM Agent：`profile_summary`、`personality`、`role` 是人物设定，`memory_bank`、`recent_memories`、`reflections` 是私有记忆流，`active_plan`、当前位置和附近角色是当前感知，`retrieved_memories` 是行动前召回的上下文。LLM 只返回结构化 JSON；时间推进、位置移动、相遇检测、传播链和反思触发仍由程序护栏负责。

### LLM 调用日志和定位方式

如果界面显示 `LLM 调用失败，已规则回退`，先看本地日志：

```powershell
Get-Content backend\logs\llm_debug.log -Tail 80
```

日志是 JSONL 格式，每次 LLM 调用一行。里面会记录请求 URL、模型名、HTTP 状态码、错误正文、异常类型、JSON 解析失败片段等信息，但不会记录完整 API key。

如果日志里是 `ReadTimeout`，说明请求已经发出但在超时时间内没有读到完整响应。常见原因是模型响应慢、网络不稳定，或者启动后端的 PowerShell 没有走代理。浏览器能访问不等于 Python 后端也走了 Clash 代理；如需让后端走本机代理，可以在启动后端前设置：

```powershell
$env:HTTPS_PROXY="http://127.0.0.1:7897"
$env:HTTP_PROXY="http://127.0.0.1:7897"
```

端口以你本机 Clash 的 HTTP 代理端口为准。新的日志会记录 `http_proxy_present`、`https_proxy_present` 和 `timeout_seconds`，方便判断后端是否看到了代理环境变量。

也可以直接查看后端当前状态：

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/state |
  Select-Object simulation_mode,llm_enabled,llm_provider,llm_model,last_llm_call_status
```

LLM 调用成功时应看到：

```text
simulation_mode      llm
llm_enabled          True
llm_provider         aliyun-bailian
llm_model            qwen3.6-flash
last_llm_call_status ok
```

### LLM 模式演示流程

如果想把复现讲得更“像论文”，推荐用 `llm` 模式跑一遍。打开 `http://localhost:3000` 后，建议按下面顺序演示。

1. 打开页面
   - 现象：右侧全局状态显示 `LLM 智能体模式`，模型栏显示配置的模型名，LLM 状态应为 `LLM 已就绪` 或后续变成 `最近一次 LLM 调用成功`。
   - 论文机制：agent 有 persona、初始记忆和计划起点，对应 persona、memory stream 与 planning setup。

2. 点击 `08:00 初始态`
   - 现象：只有 Alice 知道聚会，Bob 和 Carol 还不知道；三人各自在不同地点，有各自计划和当前行为。
   - 论文机制：展示初始 internal state。每个 agent 不是空壳，而是带有角色设定、计划和记忆。

3. 点击 `10:00 第一次传播`
   - 现象：Alice 和 Bob 在咖啡馆相遇，Bob 获得聚会信息，传播链出现 `Alice -> Bob`；最新话语和当前行动会优先由 LLM 生成。
   - 论文机制：角色感知到同地点其他 agent，检索相关记忆，并由 LLM 生成行动与对话，对应 observation、retrieval、dialogue/action generation、memory update。

4. 点击 Bob，查看右侧角色详情
   - 现象：Bob 状态从“未知聚会”变成“已知聚会”；当前行为、最新话语、推理说明发生变化；展开 `认知细节` 后可以看到检索记忆和评分解释。
   - 论文机制：对话和新信息写入 memory stream；检索评分解释为什么某些记忆被召回。

5. 点击 `14:00 第二次传播`
   - 现象：Bob 和 Carol 在广场相遇，Carol 获得聚会信息，传播链新增 `Bob -> Carol`，三人都知道聚会。
   - 论文机制：social interaction 让信息从局部对话扩散为全局共享事实，对应 multi-agent social behavior 和 chained propagation。

6. 点击 `14:30 反思形成态`
   - 现象：右侧反思数量增加，出现 reflection 文本；`reflection_trigger_reason` 显示触发原因：共享知识达到所有 agent，记忆重要性超过阈值；LLM 模式下 reflection 文本优先由模型生成。
   - 论文机制：reflection 不是简单保存一条事件，而是从多条记忆中形成高层总结，对应论文里的 reflection 和 higher-level memory abstraction。

答辩时可以这样概括：

> 我们提供 deterministic 和 LLM 两种模式。deterministic 模式用于稳定演示，LLM 模式则让大模型参与行动、对话和反思生成。角色计划始终由程序硬编码，保证 10:00 咖啡馆相遇、14:00 广场传播等关键剧情节点不被覆盖。时间推进和相遇关系仍由程序保证稳定，这样能避免现场 API 波动导致演示失败；但角色说什么、怎么行动、如何总结反思，会优先由 LLM 根据 persona、计划、地点、附近角色和检索记忆生成，因此更接近论文中的 generative agent cognition。

### LLM 模式检查与异常

- 如果右侧显示 `规则模式未调用 LLM`：说明没有设置 `SIMULATION_MODE=llm`，或后端没有重启。
- 如果右侧显示 `LLM 模式缺少 API Key`：说明 `LLM_API_KEY` 和 `DASHSCOPE_API_KEY` 都为空。
- 如果右侧显示 `LLM 调用失败，已规则回退`：说明 key、base url、网络、模型名或代理有问题，但演示仍会继续。
- 如果使用代理，建议确保启动后端的 PowerShell 能访问 LLM 接口；必要时设置 `HTTPS_PROXY` / `HTTP_PROXY`。
- 如果只是课程答辩，推荐先用 deterministic 录一版保底，再用 LLM 模式现场展示“模型参与生成”的差异。

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
