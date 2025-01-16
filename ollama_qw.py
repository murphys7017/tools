from loguru import logger
from tools import tool_config
import ollama
class OllamaQW():

    def __init__(self, model_name: str='qwen2.5:3b'):
        self.model_name = model_name
        self.tools = tool_config.generate_tools_desc()
        self.base_message = [
            {"role": "system", "content": "你是Alice,是YakumoAki在设计的智能语音助手"}]
        self.messages = []
        logger.info(self.tools)
    
    def ollama_chat(self):
        response = ollama.chat(
                model=self.model_name,
                messages=self.base_message + self.messages[-20:],
                tools=self.tools,
            )
        self.messages.append(response["message"])
        logger.info(f"model response is: {response}")
        return response
    

    def chat(self, msg):
        self.messages.append({'role': 'user', 'content': msg})
        logger.info(f"input message: {self.messages[-1]}")
        self.ollama_chat()
        
        if tool_calls := self.messages[-1].get("tool_calls", None):
            for tool_call in tool_calls:
                if fn_call := tool_call.get("function"):
                    fn_name: str = fn_call["name"]
                    fn_args: dict = fn_call["arguments"]
                    logger.info(f"function name: {fn_name}")
                    logger.info(f"function args: {fn_args}")
                    fn_res = tool_config.get_tool_res(fn_name, fn_args)

                    self.messages.append({
                        "role": "tool",
                        "name": fn_name,
                        "content": fn_res,
                    })
                    logger.info(f"tool response is: {self.messages[-1]}")
            self.ollama_chat()

        return self.messages[-1]