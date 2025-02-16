import yaml
import os
import importlib
import json
import tools
from loguru import logger

from function_tools import tool_list

def generate_tools_desc():
    tools_desc = []
    for name,desc in tools_description.items():
        temp ={
            "type": "function",
            "function": {
                "name": name,
                "description": desc['description'],
                "parameters":{
                    "type": "object",
                    "properties":{
                    },
                    "required": []
                }
            }
        }
        if "parameters" in desc:
            for param_name, param_info in desc['parameters'].items():
                temp["function"]['parameters']['properties'][param_name] = {
                    "type": param_info['type'],
                    "description": param_info['description']
                }
                if 'enum' in param_info:
                    temp["function"]['parameters']['properties'][param_name]["enum"]= param_info['enum']
                if param_info['required']:
                    temp["function"]['parameters']['required'].append(param_name)

        tools_desc.append(temp)
    return tools_desc


module_name = 'function_tools.tool_list'
module = importlib.import_module(module_name)
def get_tool_res(fn_name,fn_args):
    my_function = getattr(module, fn_name)
    fn_res: str = my_function(**fn_args)
    return json.dumps(fn_res)



tools_description = {
    'close_light' :{
        "description": "帮用户关掉机箱的灯。",
    },
    'open_light' :{
        "description": "帮用户打开机箱的灯。",
    },    
    'run_software':{
        "description": "用于根据用户指令打开或运行指定的软件、应用、程序或脚本。适用于启动本地安装的软件，例如浏览器、文本编辑器、终端、开发工具等。",
        "parameters":{
            "software_name":{
                "type": "string",
                "required": True,
                "enum": list(tool_list.StatMenuSoftware.keys()),
                "description": "待启动的软件名称，请从 enum 列表中选择最匹配的软件简称或别称。例如：'edge' 代表 Microsoft Edge，'vscode' 代表 Visual Studio Code。"
            }
        }
    }
}
