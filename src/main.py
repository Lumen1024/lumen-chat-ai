from dotenv import load_dotenv
from api_lib import (
    AiMessage,
    AiTool,
    SystemMessage,
    UserMessage,
    chat_deepseek,
)
from ai_tools import toggle_light_tool

load_dotenv()

solo_worker_prepomt = SystemMessage(
    content="""
Your are proffesional python developer
your goal is write python project via user properties

you have access view and edit file in working directory
you have access to execute commands in powershell in working directory
you can not create folder, all file placed directly in working directory

you creating simple code, everyone can understand what it does
you must seperate you code by files
"""
)

messages: list[AiMessage] = [solo_worker_prepomt]

tools: list[AiTool] = [toggle_light_tool]


while True:
    print("you: ", end="")
    messages.append(UserMessage(content=input()))

    result = chat_deepseek(messages, tools)
    print(" ai: ", end="")
    print(result.content)
