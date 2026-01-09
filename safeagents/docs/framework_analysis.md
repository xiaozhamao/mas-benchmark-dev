# SafeAgents 框架架构分析：预定义部分 vs 动态执行部分

## 一、框架预定义部分（Framework Pre-defined Components）

这些是框架设计时就确定的规则、模式和流程，不会在运行时改变。

### 1.1 架构模式 (Architecture Patterns)

**文件位置**: `architectures.py`, `architecture_strategies.py`

#### 1.1.1 集中式架构 (CENTRALIZED)
- **定义**: 使用中央协调器管理任务分配
- **实现方式**:
  - **Autogen**: `MagenticOneGroupChat` - 使用 MagenticOne 群聊模式
  - **LangGraph**: `create_supervisor` - 创建 supervisor 节点
  - **OpenAI Agents**: Planner-Orchestrator 模式
    - Planner: 分析任务，创建执行计划
    - Orchestrator: 协调任务分配和执行

#### 1.1.2 分布式架构 (DECENTRALIZED)
- **定义**: Agents 通过 handoff 机制自主协作
- **实现方式**:
  - **Autogen**: `Swarm` with `HandoffTermination`
  - **LangGraph**: `create_swarm` with handoff tools
  - **OpenAI Agents**: 尚未实现

**关键代码** (`architecture_strategies.py:38-101`):
```python
class CentralizedStrategy(ArchitectureStrategy):
    def build_team(self, agents, client, **kwargs):
        # 根据框架选择不同的集中式实现
        if self.framework == Framework.AUTOGEN:
            return MagenticOneGroupChat(agents, model_client=client, max_turns=max_turns)
        elif self.framework == Framework.LANGGRAPH:
            return create_supervisor(agents=agents, model=client, prompt=prompt).compile()
        elif self.framework == Framework.OPENAI_AGENTS:
            return {"planner": planner, "orchestrator": orchestrator, "agents": agents}
```

### 1.2 执行流程模板 (Execution Flow Templates)

#### 1.2.1 OpenAI Agents 集中式流程
**文件**: `openai_agents/openai_agents.py:297-489`

**预定义步骤**:
```
1. Planner 阶段:
   - 接收任务
   - 进行预调查 (pre-survey)
     ├─ 给定的事实 (GIVEN OR VERIFIED FACTS)
     ├─ 需要查找的事实 (FACTS TO LOOK UP)
     ├─ 需要推导的事实 (FACTS TO DERIVE)
     └─ 经验性猜测 (EDUCATED GUESSES)
   - 创建执行计划 (bullet-point plan)

2. Orchestrator 循环执行 (最多 max_turns 轮):
   WHILE not done AND turn_count < max_turns:
     ├─ 调用 orchestrator 决策
     │   ├─ delegate_to: 选择目标 agent
     │   ├─ delegate_task: 具体任务描述
     │   ├─ done: 是否完成
     │   └─ stop_reason: 停止原因
     ├─ 验证 agent 是否存在
     ├─ 执行委托的任务
     ├─ 收集 agent 输出
     └─ 反馈给 orchestrator

3. 完成条件:
   - orchestrator.done = True
   - 或达到 max_turns
```

#### 1.2.2 LangGraph/Autogen 集中式流程
**预定义**: Supervisor 直接管理和分配任务给多个 agents

#### 1.2.3 分布式流程 (Swarm)
**预定义步骤**:
```
1. Delegator 接收任务并选择初始 agent
2. Agent 执行任务，可以通过 handoff 传递给其他 agents
3. Presenter 接收最终结果并结束流程
```

### 1.3 提示词模板 (Prompt Templates)

**文件**: `prompts.py`

所有提示词都是预定义的，包括：

| 提示词类型 | 用途 | 文件位置 |
|-----------|------|---------|
| `PRE_SURVEY_TEMPLATE` | 预调查模板，引导 LLM 分析任务 | prompts.py:7-25 |
| `PLANNING_INSTRUCTIONS` | 规划指令 | prompts.py:27-29 |
| `LANGGRAPH_SUPERVISOR_PROMPT` | LangGraph supervisor 系统提示 | prompts.py:33-55 |
| `LANGGRAPH_DELEGATOR_PROMPT` | 委托者提示 | prompts.py:57 |
| `LANGGRAPH_PRESENTER_PROMPT` | 呈现者提示 | prompts.py:59 |
| `get_openai_planner_instructions()` | OpenAI planner 指令生成器 | prompts.py:63-105 |
| `get_openai_orchestrator_instructions()` | OpenAI orchestrator 指令生成器 | prompts.py:108-134 |
| `AUTOGEN_DELEGATOR_PROMPT` | Autogen 委托者提示 | prompts.py:138 |
| `AUTOGEN_PRESENTER_PROMPT` | Autogen 呈现者提示 | prompts.py:140 |

**示例** - Planner 提示词结构:
```
1. 预调查 (Pre-survey)
   - 列出给定的事实
   - 列出需要查找的事实
   - 列出需要推导的事实
   - 列出经验性猜测

2. 规划 (Planning)
   - 创建简短的要点计划
   - 指定每个团队成员的责任
```

### 1.4 配置常量 (Configuration Constants)

**文件**: `constants.py`

```python
# 特殊 agent 名称
DELEGATOR_AGENT_NAME = "delegator_safeagents"
PRESENTER_AGENT_NAME = "presenter_safeagents"

# 默认限制
DEFAULT_MAX_TURNS = 30              # 集中式默认最大轮次
DEFAULT_DECENTRALIZED_MAX_TURNS = 40  # 分布式默认最大轮次
DEFAULT_RECURSION_LIMIT = 50        # LangGraph 递归限制
```

### 1.5 框架注册机制 (Framework Registration)

**文件**: `base.py:14-61`

```python
class TeamRegistry:
    """框架注册表，管理不同框架的 Team 子类"""
    _registry: Dict[str, Type['Team']] = {}

@register_framework(Framework.AUTOGEN)
class TeamAutogen(Team):
    pass

@register_framework(Framework.LANGGRAPH)
class TeamLanggraph(Team):
    pass

@register_framework(Framework.OPENAI_AGENTS)
class TeamOpenAIAgents(Team):
    pass
```

### 1.6 执行追踪机制 (Execution Tracking)

**文件**: `base.py:92-102`

**预定义的追踪结构**:
```python
self.execution_trace = {
    'tool_calls': [],        # 工具调用记录
    'bash_commands': [],     # bash 命令记录
    'logs': '',              # 日志
    'messages': [],          # 消息历史
    'framework': framework,  # 使用的框架
    'task': None,            # 任务描述
    'start_time': None,      # 开始时间
    'end_time': None         # 结束时间
}
```

### 1.7 抽象接口 (Abstract Interfaces)

**文件**: `base.py:64-391`

**Team 抽象类定义的必须实现的方法**:

```python
@abstractmethod
def get_client(self) -> Any:
    """获取框架特定的客户端"""
    pass

@abstractmethod
def instantiate_agents(self) -> None:
    """实例化 agents"""
    pass

@abstractmethod
def process_tool(self, tool: Tool) -> Any:
    """处理工具，转换为框架特定格式"""
    pass

@abstractmethod
def instantiate_team(self) -> None:
    """实例化团队"""
    pass

@abstractmethod
async def run(self, task, verbose, assessment, attack_detector) -> Any:
    """执行任务"""
    pass
```

---

## 二、动态执行部分 (Dynamic Execution Components)

这些是在运行时根据具体任务、用户配置和 LLM 响应动态决定的部分。

### 2.1 Agent 实例化 (Agent Instantiation)

**文件**: 各框架的 `instantiate_agents()` 方法

**动态决策**:
1. **根据配置创建不同类型的 agents**
2. **处理 special agents**:
   - `web_surfer`: 网页浏览 agent
   - `file_surfer`: 文件浏览 agent
   - `coder`: 编程 agent
   - `code_executor`: 代码执行 agent
3. **工具包装和转换**:
   ```python
   # STEP 1: 包装工具以进行追踪 (SafeAgents 层)
   tracked_tools = [
       self._wrap_tool_for_tracking(tool, agent.name)
       for tool in agent.tools
   ]

   # STEP 2: 转换为框架特定格式 (框架层)
   processed_tools = [
       self.process_tool(tool)
       for tool in tracked_tools
   ]
   ```

**示例** - OpenAI Agents 实例化 (`openai_agents.py:183-268`):
```python
def instantiate_agents(self):
    for agent in self.agents:
        if agent.special_agent:
            # 动态创建特殊 agent
            openai_agent, context = get_special_agent(
                agent_type=agent.special_agent,
                name=agent.name,
                model=llm_config["model"],
                context_config=special_agent_kwargs
            )
        else:
            # 动态创建普通 agent
            openai_agent = OpenAIAgent(
                name=agent.name,
                instructions=agent.system_message,
                tools=processed_tools,
                model=llm_config["model"]
            )
```

### 2.2 工具执行 (Tool Execution)

**动态特性**:
1. **工具调用由 LLM 决定**: LLM 根据任务需求动态选择调用哪些工具
2. **参数由 LLM 生成**: 工具的输入参数由 LLM 根据上下文生成
3. **执行追踪**: 每次工具调用都被动态记录

**工具包装机制** (`base.py:183-259`):
```python
def _wrap_tool_for_tracking(self, tool: Tool, agent_name: str) -> Tool:
    original_func = tool.func

    @functools.wraps(original_func)
    async def tracked_func(*args, **kwargs):
        # 执行原始工具
        result = await original_func(*args, **kwargs)

        # 动态追踪调用
        self.track_tool_call(
            tool_name=tool.name,
            args=kwargs,
            result=result,
            agent_name=agent_name
        )
        return result

    tool.func = tracked_func
    return tool
```

### 2.3 任务执行流程 (Task Execution Flow)

虽然流程框架是预定义的，但具体执行是动态的。

#### 2.3.1 OpenAI Agents 动态执行

**文件**: `openai_agents.py:297-489`

**动态决策点**:

```python
async def run(self, task, ...):
    # 1. Planner 动态创建计划
    planner_result = await Runner.run(self.planner_agent, task)
    plan = planner_result.final_output  # 动态生成的计划

    # 2. Orchestrator 动态决策循环
    while not done:
        # 2.1 Orchestrator 动态决定下一步
        orchestrator_result = await Runner.run(self.orchestrator_agent, agent_outputs)
        orchestrator_output = orchestrator_result.final_output_as(OrchestratorOutput)

        # 动态决策:
        # - delegate_to: 选择哪个 agent（由 LLM 决定）
        # - delegate_task: 具体任务描述（由 LLM 生成）
        # - done: 是否完成（由 LLM 判断）

        if orchestrator_output.done:
            break

        # 2.2 动态执行委托的任务
        agent_result = await Runner.run(delegated_agent, task_context)

        # 2.3 动态更新上下文
        self.agent_context[agent_name] = agent_result.to_input_list()
```

**动态特性总结**:
| 决策点 | 预定义 | 动态决定 |
|--------|-------|---------|
| 执行流程 | ✓ (规划->编排->执行) | ✗ |
| 具体计划内容 | ✗ | ✓ (Planner 生成) |
| Agent 选择 | ✗ | ✓ (Orchestrator 决定) |
| 任务分配 | ✗ | ✓ (Orchestrator 决定) |
| 完成条件 | ✗ | ✓ (Orchestrator 判断) |
| 工具调用 | ✗ | ✓ (Agent 决定) |

#### 2.3.2 LangGraph 动态执行

**文件**: `langgraph/langgraph.py:312-410`

```python
async def run_stream(self, task, ...):
    # 创建事件流
    event_stream = self.team.astream({"messages": [{"role": "user", "content": task}]})

    # 动态收集事件
    async for event in event_stream:
        # 每个事件由图的状态机动态生成
        output.append(event)
        logs.append(str(event))
```

**动态特性**:
- Agent 之间的消息传递由图状态机动态决定
- Supervisor 动态分配任务给不同 agents
- 执行路径由节点的条件分支动态确定

#### 2.3.3 Autogen 动态执行

**文件**: `autogen/autogen.py:153-236`

```python
async def run(self, task, ...):
    # 动态流式执行
    result_stream = self.team.run_stream(task=task)

    async for message in result_stream:
        # 动态收集消息
        messages.append(message)
```

### 2.4 消息传递 (Message Passing)

**完全动态**:
- Agent 之间的对话内容由 LLM 生成
- 消息的顺序和数量取决于任务复杂度
- 在分布式架构中，handoff 的决策由 LLM 做出

### 2.5 执行追踪 (Runtime Tracking)

**文件**: `base.py:149-181`

**动态记录**:

```python
def track_tool_call(self, tool_name, args, result, agent_name):
    """动态追踪工具调用"""
    self.execution_trace['tool_calls'].append({
        'name': tool_name,
        'args': args,
        'result': str(result)[:500],
        'timestamp': datetime.now().isoformat(),  # 动态时间戳
        'agent': agent_name
    })

def track_bash_command(self, command, output, exit_code):
    """动态追踪 bash 命令"""
    self.execution_trace['bash_commands'].append({
        'command': command,
        'output': output[:500],
        'exit_code': exit_code,
        'timestamp': datetime.now().isoformat()
    })
```

### 2.6 攻击检测 (Attack Detection)

**文件**: `base.py:328-374`

**动态分析**:
```python
def _run_attack_detection(self, result, attack_detector, assessment):
    if not attack_detector:
        return result

    # 动态填充执行追踪
    self.execution_trace['logs'] = result.get('logs', '')
    self.execution_trace['messages'] = result.get('messages', [])

    # 动态运行攻击检测器
    is_attack = attack_detector(self.execution_trace)

    # 动态调整评估结果
    if is_attack and assessment and 'aria' in assessment:
        result['assessment']['aria'] = '4'
```

### 2.7 评估 (Assessment)

**动态评估**:
- 基于运行时生成的日志
- ARIA / DHARMA 等评估方法动态分析执行结果
- 评估分数根据实际执行情况动态生成

---

## 三、关键交互点：预定义与动态的结合

### 3.1 工具处理流程

```
预定义: Tool 抽象接口 (SafeAgents Tool)
   ↓
动态: 用户定义具体工具 (func, name, description)
   ↓
预定义: _wrap_tool_for_tracking() 包装机制
   ↓
预定义: process_tool() 转换为框架格式
   ↓
动态: Agent 实例化时绑定工具
   ↓
动态: LLM 决定何时调用哪个工具
   ↓
动态: 工具执行并返回结果
   ↓
预定义: track_tool_call() 记录执行
```

### 3.2 架构决策流程

```
预定义: Architecture Enum (CENTRALIZED / DECENTRALIZED)
   ↓
动态: 用户选择架构类型
   ↓
预定义: ArchitectureStrategyFactory 创建策略
   ↓
预定义: CentralizedStrategy / DecentralizedStrategy
   ↓
预定义: build_team() 按策略构建团队
   ↓
动态: 实际执行时的 agent 交互
```

### 3.3 执行循环流程

```
预定义: 最大轮次限制 (max_turns, recursion_limit)
   ↓
预定义: 执行循环结构 (while not done)
   ↓
动态: LLM 生成计划和决策
   ↓
动态: Agent 执行任务
   ↓
动态: 工具调用
   ↓
预定义: 执行追踪记录
   ↓
动态: 判断是否完成
```

---

## 四、总结对比表

| 维度 | 预定义部分 | 动态执行部分 |
|-----|-----------|-------------|
| **架构模式** | CENTRALIZED / DECENTRALIZED | - |
| **执行流程** | 规划→编排→执行 | 具体计划内容、任务分配 |
| **提示词** | 预调查模板、规划指令 | LLM 生成的实际计划 |
| **Agent 类型** | 抽象接口、special agent 类型 | 具体 agent 实例、配置 |
| **工具** | Tool 接口、包装机制 | 工具调用、参数、结果 |
| **消息传递** | 消息结构 | 消息内容、顺序 |
| **完成条件** | max_turns, 终止条件检查 | LLM 判断任务是否完成 |
| **执行追踪** | trace 数据结构 | 实际的调用记录 |
| **评估** | 评估方法 (ARIA, DHARMA) | 评估分数 |

---

## 五、设计模式分析

### 5.1 策略模式 (Strategy Pattern)
- **预定义**: `ArchitectureStrategy` 抽象类
- **动态**: 根据用户选择实例化具体策略

### 5.2 工厂模式 (Factory Pattern)
- **预定义**: `TeamRegistry`, `ClientFactory`
- **动态**: 根据框架类型创建具体实例

### 5.3 模板方法模式 (Template Method Pattern)
- **预定义**: `Team.run()` 定义执行步骤
- **动态**: 子类实现具体步骤的行为

### 5.4 装饰器模式 (Decorator Pattern)
- **预定义**: `_wrap_tool_for_tracking()` 包装机制
- **动态**: 在运行时为工具添加追踪功能

---

## 六、核心发现

1. **"先规划再执行"是预定义的流程框架**，但具体的规划内容和执行步骤是动态生成的。

2. **架构模式 (CENTRALIZED/DECENTRALIZED) 是预定义的**，但 agent 之间的具体交互和任务分配是动态的。

3. **提示词模板是预定义的**，引导 LLM 按照特定格式思考，但 LLM 的实际输出是动态的。

4. **工具的接口和包装机制是预定义的**，但工具的调用时机、参数和结果都是动态的。

5. **执行追踪机制是预定义的**，但追踪的内容是在运行时动态生成的。

6. **框架提供了强大的抽象和扩展能力**：
   - 通过 `TeamRegistry` 可以注册新框架
   - 通过 `ArchitectureStrategy` 可以定义新架构
   - 通过 `special_agents` 可以扩展新的 agent 类型

这种设计兼顾了**灵活性**（通过预定义的框架和规则）和**适应性**（通过动态执行和 LLM 决策），是一个典型的**混合式智能体框架**设计。
