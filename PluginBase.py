from abc import ABC, abstractmethod
class PluginBase(ABC):
    """所有脚本的抽象基类"""

    def __init__(self, 
                 script_name: str, 
                 author: str,
                 category: str, 
                 route: str = '*',
                 priority: int=10,
                 need_thread=False):
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

        self.thread = None
        
        self._initialized = True  # 标记初始化完成
        if not hasattr(self, "_initialized"):  # 检查子类是否已经初始化
            raise RuntimeError(f"{self.__class__.__name__} must call super().__init__()")
    
    @abstractmethod
    def check_message(self,message):
        """检查队列消息，判断是否启动脚本，同时移除使用的消息
        """
        pass

    @abstractmethod
    def handle(self,message):
        """文件处理方法
        处理完成之后调用send_result返回处理结果
        """
        pass
        # send_result(self, status,userid, data)