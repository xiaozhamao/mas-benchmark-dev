#!/bin/bash

echo "════════════════════════════════════════════════════════════════════"
echo "  消息局部性安全风险评测系统 - 快速启动脚本"
echo "════════════════════════════════════════════════════════════════════"
echo ""

# 检查Python版本
echo "1️⃣  检查Python环境..."
python3 --version
echo ""

# 检查必要的包
echo "2️⃣  检查依赖包..."
python3 -c "import openai" 2>/dev/null && echo "✓ openai 已安装" || echo "✗ openai 未安装，请运行: pip install openai"
python3 -c "import dotenv" 2>/dev/null && echo "✓ python-dotenv 已安装" || echo "✗ python-dotenv 未安装，请运行: pip install python-dotenv"
python3 -c "import tqdm" 2>/dev/null && echo "✓ tqdm 已安装" || echo "✗ tqdm 未安装，请运行: pip install tqdm"
echo ""

# 检查.env文件
echo "3️⃣  检查配置文件..."
if [ -f .env ]; then
    echo "✓ .env 文件存在"
    echo ""
    echo "当前配置:"
    grep -v "^#" .env | grep "=" | while read line; do
        key=$(echo $line | cut -d'=' -f1)
        value=$(echo $line | cut -d'=' -f2)
        if [[ $key == "OPENAI_API_KEY" ]]; then
            # 隐藏API Key中间部分
            masked_value="${value:0:10}...${value: -4}"
            echo "  $key=$masked_value"
        else
            echo "  $line"
        fi
    done
else
    echo "✗ .env 文件不存在"
    echo ""
    echo "请创建 .env 文件并添加以下内容:"
    echo ""
    cat << 'EOF'
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_MODEL_NAME=gpt-5-chat-latest
OPENAI_TEMPERATURE=0
LOG_LEVEL=INFO
EOF
    echo ""
    exit 1
fi
echo ""

# 检查测试用例文件
echo "4️⃣  检查测试数据..."
if [ -f message_locality_test_cases.json ]; then
    case_count=$(python3 -c "import json; print(len(json.load(open('message_locality_test_cases.json'))))")
    echo "✓ 测试用例文件存在 (包含 $case_count 个用例)"
else
    echo "✗ 测试用例文件不存在"
    exit 1
fi
echo ""

# 检查评测脚本
echo "5️⃣  检查评测脚本..."
[ -f quick_test.py ] && echo "✓ quick_test.py 存在" || echo "✗ quick_test.py 不存在"
[ -f evaluate_models.py ] && echo "✓ evaluate_models.py 存在" || echo "✗ evaluate_models.py 不存在"
echo ""

echo "════════════════════════════════════════════════════════════════════"
echo "  ✅ 环境检查完成！"
echo "════════════════════════════════════════════════════════════════════"
echo ""
echo "🚀 开始测试选项："
echo ""
echo "  1. 快速测试（推荐先运行，只测试5个用例）"
echo "     $ python3 quick_test.py"
echo ""
echo "  2. 完整评测（测试100个用例 × 3个模型）"
echo "     $ python3 evaluate_models.py"
echo ""
echo "  3. 查看文档"
echo "     $ cat QUICKSTART.md"
echo ""
echo "════════════════════════════════════════════════════════════════════"
echo ""

# 询问是否立即运行快速测试
read -p "是否立即运行快速测试？(y/N): " answer
if [ "$answer" == "y" ] || [ "$answer" == "Y" ]; then
    echo ""
    echo "开始运行快速测试..."
    echo ""
    python3 quick_test.py
else
    echo ""
    echo "提示: 准备好后，运行 python3 quick_test.py 开始测试"
    echo ""
fi
