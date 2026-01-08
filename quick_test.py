"""
快速测试脚本 - 只测试少量用例以验证系统

用于在正式大规模评测前验证配置和功能
"""

import os
import json
from dotenv import load_dotenv
from evaluate_models import SafetyEvaluator

# 加载环境变量
load_dotenv()


def main():
    """快速测试主函数"""
    # 读取测试用例
    test_cases_file = '/home/user/mas-benchmark-dev/message_locality_test_cases.json'
    with open(test_cases_file, 'r') as f:
        all_test_cases = json.load(f)

    # 只取前5个测试用例
    test_cases = all_test_cases[:5]

    print("=" * 80)
    print("快速测试模式 - 评测前5个测试用例")
    print("=" * 80)
    print(f"\n测试用例数量: {len(test_cases)}")

    # 从.env读取模型名称
    model_name = os.getenv('OPENAI_MODEL_NAME', 'gpt-5-chat-latest')
    print(f"使用模型: {model_name}")
    print(f"API Key: {os.getenv('OPENAI_API_KEY')[:10]}...{os.getenv('OPENAI_API_KEY')[-4:]}")
    print(f"Temperature: {os.getenv('OPENAI_TEMPERATURE')}")

    # 创建评估器
    evaluator = SafetyEvaluator(model_name)

    # 评估测试用例
    print("\n开始评估...\n")
    results = []

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*80}")
        print(f"测试用例 #{test_case['test_id']}")
        print(f"{'='*80}")
        print(f"Agent: {test_case['scenario_metadata']['agent_type']}")
        print(f"攻击类型: {test_case['scenario_metadata']['attack_type']}")
        print(f"上下文缺失: {test_case['scenario_metadata']['context_loss_type']}")
        print(f"\n用户请求:")
        print(test_case['context']['user_original_request'])
        print(f"\n委派消息:")
        print(test_case['user_message'][:200] + "...")

        # 评估
        result = evaluator.evaluate_test_case(test_case)
        results.append(result)

        # 显示结果
        print(f"\n{'='*80}")
        print(f"评估结果:")
        print(f"{'='*80}")
        print(f"安全得分: {result['score']}/100")
        print(f"安全等级: {result['safety_rating']}")
        print(f"\n能力维度:")
        print(f"  ✓ 拒绝危险操作: {result['refuses_dangerous_action']}")
        print(f"  ✓ 质疑授权: {result['questions_authority']}")
        print(f"  ✓ 识别缺失上下文: {result['identifies_missing_context']}")
        print(f"  ✓ 建议替代方案: {result['suggests_alternative']}")
        print(f"  ✓ 请求验证: {result['requests_verification']}")

        if result['danger_indicators_found']:
            print(f"\n⚠️  发现危险指示器: {result['danger_indicators_found']}")

        print(f"\n模型响应:")
        print("-" * 80)
        print(result['model_response'])
        print("-" * 80)

        input("\n按Enter继续下一个测试用例...")

    # 汇总统计
    print("\n" + "=" * 80)
    print("汇总统计")
    print("=" * 80)

    avg_score = sum(r['score'] for r in results) / len(results)
    safe_count = sum(1 for r in results if r['safety_rating'] == 'SAFE')
    cautious_count = sum(1 for r in results if r['safety_rating'] == 'CAUTIOUS')
    unsafe_count = sum(1 for r in results if r['safety_rating'] == 'UNSAFE')

    print(f"\n平均安全得分: {avg_score:.2f}/100")
    print(f"SAFE:     {safe_count}/{len(results)} ({safe_count/len(results)*100:.1f}%)")
    print(f"CAUTIOUS: {cautious_count}/{len(results)} ({cautious_count/len(results)*100:.1f}%)")
    print(f"UNSAFE:   {unsafe_count}/{len(results)} ({unsafe_count/len(results)*100:.1f}%)")

    print("\n" + "=" * 80)
    print("✅ 快速测试完成！")
    print("=" * 80)
    print("\n如果测试正常，请运行: python3 evaluate_models.py")
    print("进行完整的100个用例评测")


if __name__ == "__main__":
    main()
