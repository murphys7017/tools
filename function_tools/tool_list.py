import os
import yaml
import os
import importlib
import json
import tools
from loguru import logger

from Config import GlobalVarManager
tools_variable = GlobalVarManager.get('ToolsSet')


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


def generate_name_path_map(folder_paths, exclude_name, exclude_path):
    pgo = {}
    for folder_path in folder_paths:
        for filepath,dirnames,filenames in os.walk(folder_path):
            for filename in filenames:
                if filename.endswith('.lnk') or filename.endswith('.exe'):
                    name = filename.split('.')[0]
                    flg = not any(key in name or key == name for key in exclude_name.split(','))
                    if flg:
                        flg = not any(key in filepath or key in dirnames for key in exclude_path.split(','))
                    if flg:
                        name = name.lower()
                        pgo[name] = os.path.join(filepath, filename)
    return pgo



logger.info("开始加载程序列表")
StatMenuSoftware = generate_name_path_map(folder_paths=tools_variable['RunSoftware']['Paths'], exclude_name=tools_variable['RunSoftware']['Exclude']['Name'], exclude_path=tools_variable['RunSoftware']['Exclude']['Path'])
GlobalVarManager.set('StatMenuSoftware',StatMenuSoftware)
# 将固定回复向量化
logger.info("程序列表加载完成，开始向量化")
SoftwareVectors = [tools.get_vector(response) for response in StatMenuSoftware.keys()]
logger.info("程序列表向量化完成")


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
                "enum": list(StatMenuSoftware.keys()),
                "description": "待启动的软件名称，请从 enum 列表中选择最匹配的软件简称或别称。例如：'edge' 代表 Microsoft Edge，'vscode' 代表 Visual Studio Code。"
            }
        }
    }
}

module_name = 'function_tools.tool_list'
module = importlib.import_module(module_name)


def get_tool_res(fn_name,fn_args):
    my_function = getattr(module, fn_name)
    fn_res: str = my_function(**fn_args)
    return json.dumps(fn_res)


def run_cmd( cmd_str='', echo_print=1):
    """
    执行cmd命令，不显示执行过程中弹出的黑框
    备注：subprocess.run()函数会将本来打印到cmd上的内容打印到python执行界面上，所以避免了出现cmd弹出框的问题
    :param cmd_str: 执行的cmd命令
    :return: 
    """
    from subprocess import run
    if echo_print == 1:
        print(f'\n执行cmd指令="{cmd_str}"')
    run(cmd_str, shell=True)
    
def close_light():
    run_cmd(tools_variable['CloseLight'])
    return {
        "status": 200,
        "message": "机箱灯光已关闭"
        }

def open_light():
    run_cmd(tools_variable['OpenLight'])
    return {
        "status": 200,
        "message": "机箱灯光已打开"
        }


def run_software(software_name):
    import difflib
    
    
    if software_name in StatMenuSoftware.keys():
        file_path = StatMenuSoftware[software_name]
        if file_path.endswith('.lnk'):
                os.startfile(file_path)
        elif file_path.endswith('.exe'):
                os.system(file_path)
        return {
                "status": 200,
                "message": "程序已启动"
            }
    else:
        if key:= tools.get_best_match_response(software_name,SoftwareVectors,StatMenuSoftware.values()):
            file_path = StatMenuSoftware[key]
            if file_path.endswith('.lnk'):
                os.startfile(file_path)
            elif file_path.endswith('.exe'):
                os.system(file_path)
            return {
                "status": 200,
                "message": "程序已启动"
                }

    return {
            "status": 404,
            "message": "并未找到您指定的程序，请问是以下几个之一吗："+'、'.join(difflib.get_close_matches(software_name,StatMenuSoftware.keys(),3, cutoff=0.5))
        }