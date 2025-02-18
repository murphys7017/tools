import os
from loguru import logger
from PluginBase import PluginBase
from Config import GlobalVarManager
from tools import tools
class CommandSoftwareRunner(PluginBase):
    """所有脚本的抽象基类"""

    def __init__(self, script_name='test1', author='xx', need_thread=False , is_multi=False):
        """初始化方法，必须调用 super"""
        super().__init__(
            script_name,
            author,
            category='command',
            route='startswith:/run',
            is_multi = True,
            multi_round = 2
            )
        self.script_name = script_name
        self.author = author
        self.need_thread = need_thread
        self.is_multi = True
        self.multi_round = 2
        self.multi_round_count = self.multi_round
        self.tools_variable = GlobalVarManager.get('ToolsSet')
        logger.info("开始加载程序列表")
        self.StatMenuSoftware = self.generate_name_path_map(
            folder_paths=self.tools_variable['RunSoftware']['Paths'], 
            exclude_name=self.tools_variable['RunSoftware']['Exclude']['Name'], 
            exclude_path=self.tools_variable['RunSoftware']['Exclude']['Path'],
            alias = self.tools_variable['RunSoftware']['Alias']
            )
        # 将固定回复向量化
        logger.info("程序列表加载完成，开始向量化")
        self.SoftwareVectors = [tools.get_vector(response) for response in self.StatMenuSoftware.keys()]
        logger.info("程序列表向量化完成")
    def next_multi_round(self):
        self.multi_round_count -= 1
        if self.multi_round_count < 1:
            self.multi_round_count = self.multi_round
            return False
        else:
            return True


    def generate_name_path_map(self,folder_paths, exclude_name, exclude_path,alias):
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
                            if name in alias:
                                pgo[alias[name]] = os.path.join(filepath, filename)
                            name = name.lower()
                            if name in alias:
                                pgo[alias[name]] = os.path.join(filepath, filename)
                            pgo[name] = os.path.join(filepath, filename)
        return pgo
    def run_software(self,software_name):
        
        
        if software_name in self.StatMenuSoftware.keys():
            file_path = self.StatMenuSoftware[software_name]
            if file_path.endswith('.lnk'):
                    os.startfile(file_path)
            elif file_path.endswith('.exe'):
                    os.system(file_path)
            return {
                    "status": 200,
                    "message": "程序已启动"
                }
        else:
            if key:= tools.get_best_match_response(software_name,self.SoftwareVectors,self.StatMenuSoftware.values()):
                file_path = self.StatMenuSoftware[key]
                if file_path.endswith('.lnk'):
                    os.startfile(file_path)
                elif file_path.endswith('.exe'):
                    os.system(file_path)
                return {
                    "status": 200,
                    "message": "程序已启动"
                    }
        import difflib
        return {
                "status": 404,
                "message": "并未找到您指定的程序，请问是以下几个之一吗："+'、'.join(difflib.get_close_matches(software_name,self.StatMenuSoftware.keys(),3, cutoff=0.5))
            }

    def check_message(self,message):
        """检查队列消息，判断是否启动脚本，同时移除使用的消息
        """
        logger.info(f"check_message:{message}")
        return bool(message.startswith('/run '))

    def handle(self,message):
        """文件处理方法
        处理完成之后调用send_result返回处理结果
        """
        commands = message.split(' ')
        # Todo: 结束程序
        if commands[1] == 'stop':
            software_name = commands[2]
            
        software_name = commands[1]
        res = self.run_software(software_name)
        if res['status'] == 200:
            return 200,[res['message']]
        elif res['status'] == 404:
            return 201,res['message']