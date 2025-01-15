from .tool_config import tools_variable
import os
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
    from .tool_config import StatMenuSoftware
    key = difflib.get_close_matches(software_name.lower(),StatMenuSoftware.keys(),1, cutoff=0.5)
    if len(key) > 0:
        file_path = StatMenuSoftware[key[0]]
        if file_path.endswith('.lnk'):
            os.startfile(file_path)
        elif file_path.endswith('.exe'):
            os.system(file_path)
        return {
            "status": 200,
            "message": "程序已启动"
            }
    else:
        return {
            "status": 404,
            "message": "并未找到您指定的程序，请问是以下几个之一吗："+'、'.join(difflib.get_close_matches(software_name,StatMenuSoftware.keys(),3, cutoff=0.5))
            }