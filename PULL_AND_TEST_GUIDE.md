# 拉取代码到本地并测试 - 完整指南

## 🎯 三种情况的操作方法

---

## 情况1️⃣: 在当前服务器上测试（最简单）

如果你现在就在 `/home/user/mas-benchmark-dev` 目录：

### 快速开始

```bash
# 一键检查环境并运行测试
./RUN_TEST.sh
```

或者手动运行：

```bash
# 1. 确保在正确的目录
cd /home/user/mas-benchmark-dev

# 2. 确认分支
git branch --show-current
# 应该显示: claude/analyze-agent-security-risks-wzDzI

# 3. 确认文件存在
ls -lh *.py message_locality_test_cases.json

# 4. 安装依赖（如果还没安装）
pip install openai python-dotenv tqdm

# 5. 检查.env配置
cat .env

# 6. 运行快速测试
python3 quick_test.py
```

---

## 情况2️⃣: 在同一台服务器的新目录中拉取

如果你想在新的目录中克隆仓库：

```bash
# 1. 进入你想要的目录（例如你的home目录）
cd ~

# 2. 克隆仓库
git clone http://127.0.0.1:端口号/git/xiaozhamao/mas-benchmark-dev
cd mas-benchmark-dev

# 3. 切换到评测分支
git checkout claude/analyze-agent-security-risks-wzDzI

# 4. 确认文件存在
ls -lh *.py message_locality_test_cases.json

# 5. 创建.env配置文件
cat > .env << 'EOF'
OPENAI_API_KEY=sk-your-actual-api-key-here
OPENAI_MODEL_NAME=gpt-5-chat-latest
OPENAI_TEMPERATURE=0
LOG_LEVEL=INFO
EOF

# 6. 安装依赖
pip install openai python-dotenv tqdm

# 7. 运行测试
python3 quick_test.py
```

---

## 情况3️⃣: 在另一台机器上拉取（例如本地电脑）

### 步骤A: 从GitHub拉取

```bash
# 1. 克隆仓库（使用HTTPS或SSH）
git clone https://github.com/xiaozhamao/mas-benchmark-dev.git
cd mas-benchmark-dev

# 2. 切换到评测分支
git checkout claude/analyze-agent-security-risks-wzDzI

# 3. 查看文件
ls -lh *.py message_locality_test_cases.json
```

### 步骤B: 配置环境

```bash
# 1. 创建.env文件
nano .env
# 或使用其他编辑器

# 2. 添加以下内容（替换为你的实际API Key）
OPENAI_API_KEY=sk-proj-xxxxx  # 你的OpenAI API Key
OPENAI_MODEL_NAME=gpt-5-chat-latest
OPENAI_TEMPERATURE=0
LOG_LEVEL=INFO

# 保存并退出
```

### 步骤C: 安装依赖

```bash
# 确保有Python 3.8+
python3 --version

# 安装必要的包
pip install openai python-dotenv tqdm

# 或使用pip3
pip3 install openai python-dotenv tqdm
```

### 步骤D: 运行测试

```bash
# 快速测试（只测5个用例）
python3 quick_test.py

# 完整评测（100个用例 × 3个模型）
python3 evaluate_models.py
```

---

## 🔍 验证文件完整性

运行以下命令确认所有文件都已正确拉取：

```bash
# 检查关键文件
ls -lh \
  message_locality_test_cases.json \
  quick_test.py \
  evaluate_models.py \
  build_test_cases.py \
  QUICKSTART.md \
  EVALUATION_README.md \
  message_locality_security_analysis.md

# 预期输出应该显示这些文件：
# message_locality_test_cases.json  (366KB)
# quick_test.py                     (3.8KB)
# evaluate_models.py                (15KB)
# build_test_cases.py               (12KB)
# QUICKSTART.md                     (8.6KB)
# EVALUATION_README.md              (11KB)
# message_locality_security_analysis.md (16KB)
```

验证测试用例数量：

```bash
python3 << 'EOF'
import json
with open('message_locality_test_cases.json', 'r') as f:
    cases = json.load(f)
print(f"✓ 测试用例数量: {len(cases)}")
print(f"✓ 第一个用例ID: {cases[0]['test_id']}")
print(f"✓ Agent类型: {cases[0]['scenario_metadata']['agent_type']}")
EOF
```

预期输出：
```
✓ 测试用例数量: 100
✓ 第一个用例ID: 1
✓ Agent类型: financial_analyst_agent
```

---

## 📝 .env 文件配置详解

创建 `.env` 文件（注意是点开头的隐藏文件）：

```bash
# 在Linux/Mac上
nano .env

# 在Windows上
notepad .env
```

文件内容：

```env
# OpenAI API配置
OPENAI_API_KEY=sk-proj-your-actual-key-here  # 必需：你的OpenAI API密钥
OPENAI_MODEL_NAME=gpt-5-chat-latest           # 可选：默认测试的模型
OPENAI_TEMPERATURE=0                          # 可选：温度参数（0=确定性输出）
LOG_LEVEL=INFO                                # 可选：日志级别
```

### 获取OpenAI API Key

1. 访问 https://platform.openai.com/api-keys
2. 登录你的OpenAI账号
3. 点击 "Create new secret key"
4. 复制生成的密钥（格式：sk-proj-xxxxx）
5. 粘贴到 `.env` 文件中

### 验证API Key是否有效

```bash
python3 << 'EOF'
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

try:
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Hello"}],
        max_tokens=5
    )
    print("✓ API Key有效！")
    print(f"✓ 响应: {response.choices[0].message.content}")
except Exception as e:
    print(f"✗ API Key无效或有其他错误: {str(e)}")
EOF
```

---

## 🚀 运行测试的三种方式

### 方式1: 使用自动化脚本（推荐）

```bash
./RUN_TEST.sh
```

这个脚本会：
- ✓ 检查Python环境
- ✓ 检查依赖包
- ✓ 验证配置文件
- ✓ 检查测试数据
- ✓ 询问是否运行测试

### 方式2: 快速测试（5个用例）

```bash
python3 quick_test.py
```

**特点**：
- 只测试前5个用例
- 交互式显示每个用例的详细信息
- 需要按Enter继续下一个
- 适合验证配置和理解评测流程
- 成本：~5次API调用（$0.01-0.05）

### 方式3: 完整评测（100个用例）

```bash
python3 evaluate_models.py
```

**特点**：
- 测试全部100个用例
- 测试3个模型：gpt-5-chat-latest, gpt-4.1-2025-04-14, o4-mini-2025-04-16
- 自动生成评估报告
- 适合正式评测
- 成本：~300次API调用（$0.60-3.00）
- 时间：约6-15分钟

---

## 🔧 自定义测试

### 只测试一个模型

编辑 `evaluate_models.py`：

```python
# 找到这一行（约第550行）
models = [
    "gpt-5-chat-latest",
    "gpt-4.1-2025-04-14",
    "o4-mini-2025-04-16"
]

# 改为只保留一个
models = [
    "gpt-5-chat-latest"
]
```

### 只测试部分用例

编辑 `evaluate_models.py`，在 `main()` 函数中添加：

```python
# 在读取测试用例后添加
test_cases = test_cases[:30]  # 只测试前30个
```

### 调整评分标准

编辑 `evaluate_models.py` 的 `evaluate_response()` 函数：

```python
# 修改各项分值（确保总分为100）
score_breakdown['refuses_dangerous_action'] = 50  # 原来是40
score_breakdown['questions_authority'] = 15       # 原来是20
# ... 其他调整
```

---

## 📊 查看测试结果

### 实时查看进度

测试运行时会显示进度条：

```
评估 gpt-5-chat-latest: 45%|████████          | 45/100 [01:23<01:30, 0.61it/s]
```

### 查看生成的报告

```bash
# 查看最新的评估报告
cat evaluation_report_*.txt | less

# 或使用grep查找特定内容
cat evaluation_report_*.txt | grep "平均分数"
cat evaluation_report_*.txt | grep "SAFE率"
```

### 查看单个模型的详细结果

```bash
# 使用jq美化JSON输出（如果安装了jq）
cat results_gpt-5-chat-latest.json | jq '.[0]' | head -50

# 或使用Python查看
python3 << 'EOF'
import json
with open('results_gpt-5-chat-latest.json', 'r') as f:
    results = json.load(f)

# 显示第一个结果
print(json.dumps(results[0], indent=2, ensure_ascii=False)[:1000])

# 统计
safe_count = sum(1 for r in results if r['safety_rating'] == 'SAFE')
print(f"\nSAFE评级数量: {safe_count}/{len(results)}")
EOF
```

---

## ❓ 常见问题排查

### 问题1: 找不到openai模块

```bash
# 解决方法
pip install openai
# 或
pip3 install openai
```

### 问题2: API Key错误

```bash
# 检查.env文件
cat .env | grep OPENAI_API_KEY

# 确保没有多余的空格或引号
# 正确格式: OPENAI_API_KEY=sk-proj-xxxxx
# 错误格式: OPENAI_API_KEY = "sk-proj-xxxxx"
```

### 问题3: 速率限制（Rate Limit）

如果遇到速率限制错误，增加延迟：

```python
# 编辑 evaluate_models.py
# 找到 time.sleep(0.5) 这一行，改为：
time.sleep(2.0)  # 增加到2秒
```

### 问题4: 模型不可用

```bash
# 测试某个模型是否可用
python3 << 'EOF'
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

models_to_test = ["gpt-5-chat-latest", "gpt-4o", "gpt-3.5-turbo"]

for model in models_to_test:
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": "Hi"}],
            max_tokens=5
        )
        print(f"✓ {model} 可用")
    except Exception as e:
        print(f"✗ {model} 不可用: {str(e)}")
EOF
```

### 问题5: 测试用例文件损坏

```bash
# 重新生成测试用例
python3 build_test_cases.py

# 验证生成的文件
python3 -c "import json; cases=json.load(open('message_locality_test_cases.json')); print(f'生成了{len(cases)}个用例')"
```

---

## 💡 最佳实践

### 首次使用建议流程

1. **环境检查**
   ```bash
   ./RUN_TEST.sh
   ```

2. **快速测试**（验证配置）
   ```bash
   python3 quick_test.py
   ```

3. **查看一个结果**（理解输出格式）
   - 仔细阅读显示的测试场景
   - 查看模型响应
   - 理解评分标准

4. **单模型小规模测试**
   ```python
   # 修改 evaluate_models.py
   models = ["gpt-5-chat-latest"]
   test_cases = test_cases[:20]  # 只测试20个
   ```

5. **完整评测**（确认无误后）
   ```bash
   python3 evaluate_models.py
   ```

### 节省成本的技巧

1. **先测试5个用例**验证配置
2. **只测试1个模型**而不是3个
3. **选择特定场景**而不是全部100个
4. **使用更便宜的模型**如gpt-3.5-turbo进行测试

---

## 📚 文档速查

- **QUICKSTART.md** - 快速开始指南
- **EVALUATION_README.md** - 完整技术文档
- **message_locality_security_analysis.md** - 理论分析和风险点
- **PULL_AND_TEST_GUIDE.md** - 本文档

---

## 🆘 需要帮助？

如果遇到问题：

1. 检查 `.env` 文件配置
2. 运行 `./RUN_TEST.sh` 进行环境诊断
3. 查看错误信息并搜索相关解决方案
4. 检查是否有足够的API额度

---

## ✅ 快速检查清单

运行测试前确认：

- [ ] Python 3.8+ 已安装
- [ ] 依赖包已安装（openai, python-dotenv, tqdm）
- [ ] .env 文件已创建并包含有效的API Key
- [ ] 测试用例文件存在（message_locality_test_cases.json）
- [ ] 评测脚本存在（quick_test.py, evaluate_models.py）
- [ ] 有足够的OpenAI API额度

全部确认后，运行：

```bash
python3 quick_test.py
```

祝你评测顺利！🚀
