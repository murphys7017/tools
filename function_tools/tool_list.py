import os
import yaml
import os
import importlib
import json
import tools
from loguru import logger

with open('Config.yml', 'r', encoding='utf-8') as file:
    config = yaml.load(file, Loader=yaml.FullLoader)
tools_variable = config['ToolsSet']



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
# 将固定回复向量化
logger.info("程序列表加载完成，开始向量化")
SoftwareVectors = [tools.get_vector(response) for response in StatMenuSoftware.keys()]
logger.info("程序列表向量化完成")


def run_software(software_name):
    import difflib
    from .tool_config import StatMenuSoftware
    
    
    if software_name in StatMenuSoftware.keys():
        
        key = software_name
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