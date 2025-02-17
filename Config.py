import asyncio
import yaml
from loguru import logger

class GlobalVarManager:
    def __init__(self, config_file_path='Config.yml'):
        self._variables = {}
        with open(config_file_path, 'r', encoding='utf-8') as file:
            data = yaml.load(file, Loader=yaml.FullLoader)
            for key in data:
                self.set(key, data[key])
            logger.info(f"loaded config file {config_file_path}")

    def set(self, key, value):
        self._variables[key] = value
        logger.info(f"Set global variable: {key} = {value}")

    def get(self, key, default=None):
        return self._variables.get(key, default)

    def remove(self, key):
            if key in self._variables:
                del self._variables[key]
                logger.info(f"Removed global variable: {key}")
            else:
                logger.warning(f"Attempt to remove non-existing key: {key}")

    def clear(self):
            self._variables.clear()
            logger.info("Cleared all global variables")

    def exists(self, key):
            return key in self._variables

    def get_all(self):
            return dict(self._variables)

GlobalVarManager = GlobalVarManager()



