
from types import SimpleNamespace
from unittest.mock import Mock

from main import run_agent


def test_agent_calculator():
    # 1. 模拟 LLM 第一次响应：请求计算器
    tool_call = SimpleNamespace(
        id="call_001",
        function=SimpleNamespace(
            name="calculator",
            arguments='{"a":5999,"b":3,"operation":"multiply"}'
        )
    )

    first_response = SimpleNamespace(
        choices=[
            SimpleNamespace(
                finish_reason="tool_calls",
                message=SimpleNamespace(
                    content=None,
                    tool_calls=[tool_call]
                )
            )
        ]
    )

    # 2. 模拟 LLM 第二次响应：最终回答
    final_response = SimpleNamespace(
        choices=[
            SimpleNamespace(
                finish_reason="stop",
                message=SimpleNamespace(
                    content="5999 × 3 = 17997",
                    tool_calls=None
                )
            )
        ]
    )

    # 3. 创建假的 API Client
    client = Mock()
    client.chat.completions.create.side_effect = [
        first_response,
        final_response
    ]

    # 4. 执行真实 Agent Loop
    messages = [
        {"role": "user", "content": "计算5999乘以3"}
    ]

    run_agent(client, "test-model", messages)

    # 5. 验证 API 调用次数
    assert client.chat.completions.create.call_count == 2

    # 6. 验证 Tool Result 被正确保存
    assert messages[2] == {
        "role": "tool",
        "tool_call_id": "call_001",
        "content": "17997"
    }


def test_agent_max_rounds(capsys):
    # 模拟 LLM 持续请求计算器
    tool_call = SimpleNamespace(
        id="call_002",
        function=SimpleNamespace(
            name="calculator",
            arguments='{"a":10,"b":5,"operation":"add"}'
        )
    )

    response = SimpleNamespace(
        choices=[
            SimpleNamespace(
                finish_reason="tool_calls",
                message=SimpleNamespace(
                    content=None,
                    tool_calls=[tool_call]
                )
            )
        ]
    )

    client = Mock()
    client.chat.completions.create.return_value = response

    messages = [
        {"role": "user", "content": "计算10加5"}
    ]

    # 最多允许一轮模型决策
    run_agent(client, "test-model", messages, max_rounds=1)

    # 验证 LLM 只被调用一次
    assert client.chat.completions.create.call_count == 1

    # 验证工具执行结果仍被保存
    assert messages[2]["content"] == "15"

    # 验证 Agent 因达到最大轮数而停止
    output = capsys.readouterr().out
    assert "maximum rounds reached" in output