
def run_cmd( cmd_str='', echo_print=1):
    """
    执行cmd命令，不显示执行过程中弹出的黑框
    备注：subprocess.run()函数会将本来打印到cmd上的内容打印到python执行界面上，所以避免了出现cmd弹出框的问题
    :param cmd_str: 执行的cmd命令
    :return: 
    """
    from subprocess import run
    if echo_print == 1:
        print('\n执行cmd指令="{}"'.format(cmd_str))
    run(cmd_str, shell=True)
    
def close_light():
    cmd_line = r'"C:\Users\Administrator\Downloads\OpenRGB_0.9_Windows_64_b5f46e3\OpenRGB Windows 64-bit\OpenRGB.exe" --profile close'
    run_cmd(cmd_line)
    return "关了"

def open_light():
    cmd_line = r'"C:\Users\Administrator\Downloads\OpenRGB_0.9_Windows_64_b5f46e3\OpenRGB Windows 64-bit\OpenRGB.exe" --profile nomal'
    run_cmd(cmd_line)
    return "打开了"