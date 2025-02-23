from abc import ABC, abstractmethod
class PluginBase(ABC):
    """所有脚本的抽象基类"""

    def __init__(
        self, 
        script_name: str, 
        author: str,
        category: str, 
        route: str = '*',
        priority: int=10,
        need_thread=False,
        is_multi=False,
        multi_round=1
        ):
        """初始化方法，必须调用 super
            script_name 
            author
            category = message|command|event
            route: str = path startswith:xxx,endswith:xxx,containswith:xxx
            priority = 1-> 999
        """
        
        
        self.script_name = script_name
        self.author = author
        self.category = category
        self.route = route
        self.priority = priority
        self.need_thread = need_thread
        self.is_multi = is_multi
        self.multi_round = multi_round
        self.thread = None
        # 自行定义
        self.command_structure = self.define_command()
        
        self.multi_round_count = self.multi_round
        
        self._initialized = True  # 标记初始化完成
        if not hasattr(self, "_initialized"):  # 检查子类是否已经初始化
            raise RuntimeError(f"{self.__class__.__name__} must call super().__init__()")
    def next_multi_round(self):
        self.multi_round_count -= 1
        if self.multi_round_count < 1:
            self.multi_round_count = self.multi_round
            return False
        else:
            return True
    @abstractmethod
    def define_command(self):
        """定义函数的命令,如果是*直接返回null
            return： dict {
                /cmd cmd1 cmd2 xxx
                base_cmd: {
                    cmd1: {
                        cmd2: xxx
                    }
                }
            }
        """
        if self.route == '*':
            return None
        else:
            """定义函数的命令行
            return： dict {
                /cmd cmd1 cmd2 xxx
                base_cmd: {
                    cmd1: {
                        cmd2: xxx
                    }
                }
            }
        """
            return {}
    @abstractmethod
    def check_message(self,message):
        """检查队列消息，判断是否启动脚本，同时移除使用的消息
            参数：
                message: cli输入的消息
            return：
                True or False
        """
        pass

    @abstractmethod
    def handle(self,message):
        """文件处理方法
        处理完成之后调用send_result返回处理结果
        status code: 200 完成, 400 此插件异常 201多步插件，等待下一轮对话
        return status code,result
        """
        pass
        
        # return status code,result
    
    def parse_command(self,command):
        parts = command.split()  # 拆分命令字符串
        structure = self.command_structure
        
        def parse_part(parts, current_structure):
            if not parts:
                return {}

            part = parts[0]  # 当前命令部分
            
            # 如果当前部分是命令，且该命令有 'next'，递归解析
            if part in current_structure and current_structure[part].get('is_cmd', False):
                next_structure = current_structure[part].get('next', {})
                # 递归解析下一部分
                next_result = parse_part(parts[1:], next_structure)
                return {
                    part: next_result
                }

            # 如果当前部分是参数，提取值并返回
            else :
                for key,value in current_structure.items():
                    if not value.get('is_cmd', False):
                        param_name = key
                
                current_structure = current_structure.get(param_name,{})
                next_structure = current_structure.get('next',None)
                if next_structure:
                    next_result = parse_part(parts[1:], next_structure)
                    next_param_name = next(iter(next_structure)) 
                    return {
                        param_name: {
                            'value': part,
                            next_param_name:next_result
                        }
                    }
                else:
                    return {
                        param_name: {
                            'value': part,
                        }
                    }
        # 从根命令开始解析
        result = parse_part(parts, structure)
        return result
