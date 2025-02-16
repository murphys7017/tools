from loguru import logger
from DeepseekApi import DeepSeekOnline
from BaseScript import BaseScript

class DeepseekTest(BaseScript):
    """所有脚本的抽象基类"""

    def __init__(self, script_name='test', author='xx', need_thread=False , is_multi=False):
        """初始化方法，必须调用 super"""
        self.script_name = script_name
        self.author = author
        self.need_thread = need_thread
        self.is_multi = is_multi

        self.dso = DeepSeekOnline()
        
        
    def check_message(self,message):
        """检查队列消息，判断是否启动脚本，同时移除使用的消息
        """
        logger.info(f"check_message:{message}")
        return True

    def handle(self,message):
        """文件处理方法
        处理完成之后调用send_result返回处理结果
        """
        return self.dso.chat(message)