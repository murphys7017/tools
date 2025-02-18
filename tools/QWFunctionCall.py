from loguru import logger
from function_tools import tool_list
import ollama
import yaml
import tools.tools as tools

class QWFunctionCall():

    def __init__(self, model_name: str='qwen2.5:7b'):
        self.model_name = model_name
        logger.info(f"服务开始初始化，大模型版本{self.model_name}")
        
        logger.info("指定应用读取完成：")
        self.tools = tool_list.generate_tools_desc()
        logger.info(self.tools)
    
    def ollama_chat(self,message):
        # TODO: checl tool call
        response = ollama.chat(
            model=self.model_name,
            messages=message,
            tools=self.tools
            )
        logger.info(f"Tool call response {response.tool_calls}")
        logger.info(f"Tool call response {response.get('tool_calls', None)}")
        if tool_calls := response.get("tool_calls", None):
            logger.info(f"激活工具:{tool_calls}")
            for tool_call in tool_calls:
                if fn_call := tool_call.get("function"):
                    fn_name: str = fn_call["name"]
                    fn_args: dict = fn_call["arguments"]
                    logger.info(f"function name: {fn_name}")
                    logger.info(f"function args: {fn_args}")
                    fn_res = tool_list.get_tool_res(fn_name, fn_args)
                    logger.info(f"tool response is: {self.messages[-1]}")
                    return fn_name,fn_res
        return None,None
    