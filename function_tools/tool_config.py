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
        "description": "关掉机箱的灯。",
    },
    'open_light' :{
        "description": "打开机箱的灯。",
    },    
    'run_software':{
        "description": "打开或者运行程序、软件、应用、脚本等。",
        "parameters":{
            "software_name":{
                "type": "string",
                "required": True,
                "enum": list(tool_list.StatMenuSoftware.keys()),
                "description": "需要打开或者运行的程序的简称或者别称，从enum中选择最相符的传入需要打开、运行或者执行的软件程序或者脚本的名称"
            }
        }
    }
}
