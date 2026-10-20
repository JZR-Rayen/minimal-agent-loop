import os
import json
import requests
from dotenv import load_dotenv
from openai import OpenAI

from weather import get_weather
from search import search_web


# ==========================
# 1. 定义计算器
# ==========================

def calculator(a, b, operation):
    if operation == "add":
        return a + b
    elif operation == "subtract":
        return a - b
    elif operation == "multiply":
        return a * b
    elif operation == "divide":
        if b == 0:
            return "Error: Cannot divide by zero"
        return a / b
    else:
        return "Error: Unknown operation"


# ==========================
# 2. 定义工具 JSON Schema
# ==========================

calculator_tool = {
    "type": "function",
    "function": {
        "name": "calculator",
        "description": "Perform basic arithmetic calculations.",
        "parameters": {
            "type": "object",
            "properties": {
                "a": {"type": "number"},
                "b": {"type": "number"},
                "operation": {
                    "type": "string",
                    "enum": ["add", "subtract", "multiply", "divide"]
                }
            },
            "required": ["a", "b", "operation"],
            "additionalProperties": False
        }
    }
}

weather_tool = {
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get the current temperature of a city.",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "City name in English, e.g. Shanghai"
                }
            },
            "required": ["city"],
            "additionalProperties": False
        }
    }
}

search_tool = {
    "type": "function",
    "function": {
        "name": "search_web",
        "description": "Search the web for current information.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search keywords or question"
                }
            },
            "required": ["query"],
            "additionalProperties": False
        }
    }
}

tools = [calculator_tool, weather_tool, search_tool]


# ==========================
# 3. 初始化 LLM API
# ==========================
def run_agent(client, model, messages, max_rounds=5):
    round_num = 0

    while round_num < max_rounds:
        round_num += 1
        print(f"\n--- Round {round_num} ---")

        # 5.1 调用 LLM
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )

        choice = response.choices[0]
        message = choice.message

        print("Finish reason:", choice.finish_reason)

        # 5.2 模型请求调用工具
        if choice.finish_reason == "tool_calls" and message.tool_calls:

            # 保存模型的 Tool Call 消息
            messages.append(message)

            # 处理本轮的每一个 Tool Call
            for tool_call in message.tool_calls:

                tool_name = tool_call.function.name
                print("Tool name:", tool_name)

                try:
                    # 解析工具参数
                    arguments = json.loads(
                        tool_call.function.arguments
                    )
                    print("Tool arguments:", arguments)

                    # 根据名称执行对应工具
                    if tool_name == "calculator":
                        result = calculator(
                            a=arguments["a"],
                            b=arguments["b"],
                            operation=arguments["operation"]
                        )

                    elif tool_name == "get_weather":
                        result = get_weather(
                            city=arguments["city"]
                        )

                    elif tool_name == "search_web":
                        result = search_web(
                            query=arguments["query"]
                        )

                    else:
                        result = f"Error: Unknown tool {tool_name}"

                # JSON 或参数错误
                except (ValueError, KeyError, TypeError) as e:
                    result = f"Tool input error: {e}"

                # requests 网络请求错误
                except requests.exceptions.RequestException as e:
                    result = f"Tool network error: {e}"

                print(f"Tool: {tool_name} → {result}")

                # 5.3 将 Tool Result 反馈给 LLM
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": str(result)
                })

        # 5.4 模型正常完成回答
        elif choice.finish_reason == "stop":
            print("\nFinal answer:", message.content)
            break

        # 5.5 其他终止原因
        else:
            print("Abnormal stop:", choice.finish_reason)
            break

    else:
        print("Agent stopped: maximum rounds reached.")


def main():
    # 1. 读取配置
    load_dotenv()

    api_key = os.environ["HKUST_API_KEY"]
    model = os.environ["MODEL"]

    # 2. 初始化 API Client
    client = OpenAI(
        api_key=api_key,
        base_url="https://hkust.azure-api.net/hkust-genai/v1",
        default_headers={"api-key": api_key}
    )

    print("API Key 已加载:", bool(api_key))
    print("模型:", model)

    # 3. 准备用户任务
    messages = [
        {
            "role": "user",
            "content": (
                "请使用计算器计算 5999 乘以 3，"
                "然后根据计算结果给出最终答案。"
            )
        }
    ]

    # 4. 执行 Agent Loop
    run_agent(
        client=client,
        model=model,
        messages=messages,
        max_rounds=5
    )


if __name__ == "__main__":
    main()
