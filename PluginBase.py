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
        
        
        self.multi_round_count = self.multi_round
        
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
        status code: 200 完成, 400 此插件异常 201多步插件，等待下一轮对话
        return status code,result
        """
        pass
        
        # return status code,result