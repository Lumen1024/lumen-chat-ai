from typing import Any
from api_lib import AiTool, AiToolParam
from smart_home import LIGHT_IDS, TOKEN, yandex_iot_power_change


def toggle_ligth_action(args: dict[str, Any]) -> str:
    for id in LIGHT_IDS:
        yandex_iot_power_change(id, args["state"], TOKEN)
    return "Success"


toggle_light_tool = AiTool(
    name="toggle_light",
    description="toggle light in the room",
    parameters=[
        AiToolParam(
            name="state",
            type="boolean",
            description="true for on, false for off",
        )
    ],
    action=toggle_ligth_action,
)

view_file_tool = AiTool(
    name="view_file",
    description="return file content str (can returns ERROR(reason))",
    parameters=[
        AiToolParam(
            name="filename", type="string", description="filename with extention"
        )
    ],
    action=lambda a: "a",
)

edit_file_tool = AiTool(
    name="edit_file",
    description="edit file (if file dont exist creates it)",
    parameters=[
        AiToolParam(
            name="filename", type="string", description="filename with extention"
        ),
        AiToolParam(
            name="content",
            type="string",
            description="new file content (overrides old)",
        ),
    ],
    action=lambda a: "a",
)

install_dependency_tool = AiTool(
    name="install_dependency",
    description="install python dependency via pip install $dependency$",
    parameters=[
        AiToolParam(
            name="dependency_name",
            type="string",
            description="name in command pip install",
        )
    ],
    action=lambda a: "a",
)

execute_command_tool = AiTool(
    name="execute_command",
    description="execute command in working directory (returns Success or Error)",
    parameters=[
        AiToolParam(
            name="command",
            type="string",
            description="command to execute",
        )
    ],
    action=lambda a: "a",
)
