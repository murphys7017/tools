import asyncio
import yaml
from loguru import logger

class AsyncGlobalVarManager:
    def __init__(self, config_file_path='Config.yml'):
        self._variables = {}
        

        with open(config_file_path, 'r', encoding='utf-8') as file:
            data = yaml.load(file, Loader=yaml.FullLoader)
            for key in data:
                self.set(key, data[key])
            logger.info(f"loaded config file {config_file_path}")
        self._lock = asyncio.Lock()  # 使用异步锁
    async def set(self, key, value):
        async with self._lock:
            # if not isinstance(key, str):
            #     logger.error(f"Invalid key type: {type(key)}. Key must be a string.")
            #     return
            self._variables[key] = value
            logger.info(f"Set global variable: {key} = {value}")

    async def get(self, key, default=None):
        async with self._lock:
            return self._variables.get(key, default)

    async def remove(self, key):
        async with self._lock:
            if key in self._variables:
                del self._variables[key]
                logger.info(f"Removed global variable: {key}")
            else:
                logger.warning(f"Attempt to remove non-existing key: {key}")

    async def clear(self):
        async with self._lock:
            self._variables.clear()
            logger.info("Cleared all global variables")

    async def exists(self, key):
        async with self._lock:
            return key in self._variables

    async def get_all(self):
        async with self._lock:
            return dict(self._variables)

GlobalVarManager = AsyncGlobalVarManager()


# 异步示例用法
async def main():
    manager = AsyncGlobalVarManager()
    
    # 设置全局变量
    await manager.set('app_version', '1.0.0')
    await manager.set('is_logged_in', True)
    
    # 获取全局变量
    print(await manager.get('app_version'))  # 输出: '1.0.0'
    print(await manager.get('is_logged_in'))  # 输出: True

    # 检查全局变量是否存在
    print(await manager.exists('is_logged_in'))  # 输出: True
    print(await manager.exists('non_existent'))  # 输出: False
    
    # 获取所有全局变量
    print(await manager.get_all())  # 输出: {'app_version': '1.0.0', 'is_logged_in': True}
    
    # 删除全局变量
    await manager.remove('is_logged_in')
    print(await manager.exists('is_logged_in'))  # 输出: False
    
    # 清空所有变量
    await manager.clear()
    print(await manager.get_all())  # 输出: {}

# 启动异步任务
import asyncio
asyncio.run(main())
