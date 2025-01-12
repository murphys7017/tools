from loguru import logger
from tools import tool_config
import ollama
class OllamaQW():
    # 加载tool文件中所有工具函数
    import importlib
    module_name = 'tools.tool_list'
    module = importlib.import_module(module_name)
    # 加载工具函数定义
    tools = tool_config.tools
    
    # 模型预设
    base_message = [
            {"role": "system", "content": "你是Alice,是YakumoAki在设计的智能语音助手"}
        ]
    messages = []
    def __init__(self, model_name: str):
        import yaml
        self.model_name = model_name
        logger.info(self.tools)
        
    def chat(self, msg):
        self.messages.append({'role': 'user', 'content': msg})
        logger.info(f"input message: {self.messages[-1]}")
        response = ollama.chat(
            model=self.model_name,
            messages=self.base_message + self.messages[-20:],
            tools=self.tools,
        )
        self.messages.append(response["message"])
        logger.info(f"model response is: {response}")
        if tool_calls := self.messages[-1].get("tool_calls", None):
            for tool_call in tool_calls:
                if fn_call := tool_call.get("function"):
                    fn_name: str = fn_call["name"]
                    fn_args: dict = fn_call["arguments"]
                    logger.info(f"function name: {fn_name}")
                    logger.info(f"function args: {fn_args}")
                    my_function = getattr(self.module, fn_name)
                    fn_res: str = my_function(**fn_args)

                    self.messages.append({
                        "role": "tool",
                        "name": fn_name,
                        "content": fn_res,
                    })
                    logger.info(f"tool response is: {self.messages[-1]}")
            response = ollama.chat(
                model=self.model_name,
                messages=self.base_message + self.messages[-20:],
                tools=self.tools,
            )
            self.messages.append(response["message"])
            logger.info(f"model response is: {response}")
        return self.messages[-1]
