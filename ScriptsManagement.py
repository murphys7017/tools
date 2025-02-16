import importlib
import inspect
import os
import sys
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import os
import time
from loguru import logger
from BaseScript import BaseScript


class ScriptChangeHandler(FileSystemEventHandler):
    """处理脚本目录变化的事件处理器"""

    def __init__(self, script_manager):
        """
        初始化处理器
        
        :param script_manager: ScriptManager 实例，用于调用其加载/卸载脚本的方法
        """
        self.script_manager = script_manager

    def on_created(self, event):
        """处理文件创建事件"""
        if event.src_path.endswith(".py"):
            script_name = os.path.splitext(os.path.basename(event.src_path))[0]
            logger.info(f"Script created: {script_name}")
            self.script_manager.load_script(event.src_path)

    def on_modified(self, event):
        """处理文件修改事件"""
        if event.src_path.endswith(".py"):
            time.sleep(1)
            script_name = os.path.splitext(os.path.basename(event.src_path))[0]
            logger.info(f"Script modified: {script_name}")
            self.script_manager.unload_script('WatchDogTest')
            time.sleep(1)
            self.script_manager.load_script(event.src_path)

    def on_deleted(self, event):
        """处理文件删除事件"""
        if event.src_path.endswith(".py"):
            time.sleep(1)
            script_name = os.path.splitext(os.path.basename(event.src_path))[0]
            logger.info(f"Script deleted: {script_name}")
            self.script_manager.unload_script(script_name)
            


class ScriptManager:
    """管理和监听脚本的类"""

    def __init__(self, scripts_directory):
        self.SCRIPTS_REGISTY = {}
        self.scripts_directory = scripts_directory
        sys.path.append(scripts_directory)

        # 设置文件监控
        self.observer = Observer()
        self.event_handler = ScriptChangeHandler(self)
        self.observer.schedule(self.event_handler, path=scripts_directory, recursive=False)
        self.observer.start()


        """遍历文件夹下的所有文件"""
        for root, dirs, files in os.walk(scripts_directory):
            for file in files:
                file_path = os.path.join(root, file)
                if file_path.endswith('.py'):
                    self.load_script(file_path)
        
        logger.info('ScriptManager initialized')
    
    def load_script(self, file_path):
        """动态加载并注册Python文件"""
        logger.info('Loading Scripts')
        script_name = os.path.splitext(os.path.basename(file_path))[0]
        importlib.invalidate_caches()
        if script_name in self.SCRIPTS_REGISTY:
            del self.SCRIPTS_REGISTY[script_name]

        try:
            # 构造模块的完整路径
            spec = importlib.util.spec_from_file_location(script_name, file_path)
            module = importlib.util.module_from_spec(spec)
            sys.modules[script_name] = module
            spec.loader.exec_module(module)

            # 查找继承自 ScriptBase 的类
            script_class = None
            for name, obj in inspect.getmembers(module):
                if inspect.isclass(obj) and issubclass(obj, BaseScript) and obj is not BaseScript:
                    script_class = obj
                    break
            
            if script_class:
                self.SCRIPTS_REGISTY[script_name] = script_class()
                logger.info('Loaded Script {script_name}',script_name=script_name,)
            else:
                logger.info(f"No valid ScriptBase implementation found in {script_name}")

        except Exception as e:
            logger.info(f"Failed to load script {script_name}: {e}")
        
    def reload_script(self,script_name):
        if script_name in sys.modules:
            # 从 sys.modules 中获取模块对象
            module = sys.modules[script_name]
            try:
                importlib.invalidate_caches()
                # 强制重新加载模块
                importlib.reload(module)
                logger.info(f"Module {script_name} reloaded successfully.")
            except Exception as e:
                logger.info(f"Failed to reload module {script_name}: {e}")
        else:
            logger.info(f"Module {script_name} is not loaded.")
    def unload_script(self, script_name):
        """卸载脚本"""
        if script_name in self.SCRIPTS_REGISTY:
            # 从脚本注册表中删除
            importlib.invalidate_caches()
            del self.SCRIPTS_REGISTY[script_name]
            logger.info(f"Unloaded script: {script_name}")

            # 检查并从 sys.modules 中移除
            if script_name in sys.modules:
                del sys.modules[script_name]
                logger.info(f"Removed {script_name} from sys.modules")
            else:
                logger.info(f"{script_name} not found in sys.modules")
        else:
            logger.info(f"{script_name} not found in script registry")
    def shutdown(self):
        """关闭文件监控器"""
        self.observer.stop()
        self.observer.join()


    def message_handler(self, message):
        # 使用生成器表达式快速找到第一个符合条件的脚本
        for script in self.SCRIPTS_REGISTY.values():
            logger.info(script.check_message(message))
            if script.check_message(message):
                logger.info(f'Activate Script: {script.__class__.__name__}')
                response = script.handle(message)
                logger.info(f'Activate Script response: {response}')
                
                return response if isinstance(response, list) else [response]
        # if script := next(
        #     (
        #         script
        #         for script in self.SCRIPTS_REGISTY.values()
        #         if script['script_instance'].check_message(message)
        #     ),
        #     None,
        # ):

        #     response = script['script_instance'].handle(message)
        #     logger.info(f'Activate Script: {script.__class__.__name__}')
        #     logger.info(f'Activate Script response: {response}')
            
        #     return response if isinstance(response, list) else [response]

if __name__ == "__main__":
    st =  ScriptManager(os.path.join('scripts'))
    st.message_handler('帮我打开cpuz')