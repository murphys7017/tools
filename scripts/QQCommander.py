import os
from loguru import logger
from PluginBase import PluginBase
from Config import GlobalVarManager
from tools import tools
class QQCommander(PluginBase):
    """所有脚本的抽象基类"""

    def __init__(self, script_name='qqcmd', author='xx', need_thread=False , is_multi=False):
        """初始化方法，必须调用 super"""
        super().__init__(
            script_name,
            author,
            category='command',
            route='startswith:/qq',
            is_multi = True,
            multi_round = 1
            )
        self.script_name = script_name
        self.author = author
        self.need_thread = need_thread
        self.is_multi = True
        self.multi_round = 2
        self.multi_round_count = self.multi_round
        self.qqAdapter = GlobalVarManager.get('qqAdapter')
    
    def define_command(self):
        """定义函数的命令行
            return： dict {
                /cmd cmd1 cmd2 xxx
                base_cmd: {
                    cmd1: {
                        cmd2: xxx
                    }
                }
            }
            
            command = "/qq set alias 112233 安安"
            -》
            {
            'qq': {
                'set': {
                    'alias': {
                        '112233': {
                            '安安': {}
                        }
                    }
                }
            },
        """
        self.base_cmd = self.split(':')[1]
        return {
            self.base_cmd: {
                'is_cmd': True,
                'desc': 'qq操作起始命令',
                'next': {
                    'set': {
                        'is_cmd': True,
                        'next': {
                            'target':{
                                'desc': '设置对话窗口，于那个群对话等'
                            },
                            'alias': {
                                'desc': '设置指定qq群或者好友的别名',
                                'is_cmd': True,
                                'next': {
                                    'target': {
                                        'desc': '需要设置别名的qq',
                                        'next': {
                                            'alias name': {
                                                'desc': '名称'
                                            }
                                        }
                                    }
                                }
                            },
                        }
                    },
                    'send': {
                        'is_cmd': True,
                        'desc': '针对当下消息或者指定消息进行回复',
                        'next':{
                            'target': {
                                'desc': '给谁发送',
                                'next': {
                                    'content':{
                                        'desc': '消息内容'
                                    }
                                }
                            },
                            'content':{
                                'desc': '如果找不到给谁发送则直接发送给最近的消息来源'
                            }
                        }
                    },
                    'content':{
                        'desc': '如果设定了对话窗口直接发送消息，否则报错'
                    }
                }
            }
        }
    def check_message(self,message):
        """检查队列消息，判断是否启动脚本，同时移除使用的消息
            参数：
                message: cli输入的消息
            return：
                True or False
        """
        logger.info(f"check_message:{message}")
        return bool(message.startswith('/qq '))

    def handle(self,message):
        """消息处理程序
            参数：
                message: cli输入的消息
            return: 
                (status,script name,result)
                status:200 complete,201 next round,400 error 
        """
        commands = message.split(' ')
        # Todo: 结束程序
        if commands[1] == 'stop':
            software_name = commands[2]
            
        software_name = commands[1]
        res = self.run_software(software_name)
        if res['status'] == 200:
            return 200,self.script_name,[res['message']]
        elif res['status'] == 404:
            return 201,self.script_name,res['message']