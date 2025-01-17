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
    
    
    def parse_tool_description(self,tool_info):
        """
        解析单个工具的描述，生成易读的格式。
        
        :param tool_info: dict, 单个工具的详细信息。
        :return: str, 解析后的工具说明。
        """
        tool_name = tool_info["function"]["name"]
        tool_desc = tool_info["function"]["description"]
        params = tool_info["function"]["parameters"]

        # 解析参数
        param_desc = "参数：\n"
        for param_name, param_details in params["properties"].items():
            param_type = param_details.get("type", "未知类型")
            param_description = param_details.get("description", "无描述")
            allowed_values = param_details.get("enum", None)
            if allowed_values:
                param_desc += f"  - {param_name} ({param_type}, 允许值: {', '.join(allowed_values)}): {param_description}\n"
            else:
                param_desc += f"  - {param_name} ({param_type}): {param_description}\n"
        
        # 标注必填参数
    
        if required_params:= params.get("required", []):
            param_desc += f"  必填参数: {', '.join(required_params)}\n"

        return f"{tool_name}：{tool_desc}\n{param_desc}"


    def generate_tools_section(self,tools_info):
        """
        根据工具信息列表生成工具说明部分。
        
        :param tools_info: list, 包含多个工具信息的字典列表。
        :return: str, 格式化后的工具说明文本。
        """
        tools_section = "工具说明：\n"
        for tool_info in tools_info:
            tools_section += self.parse_tool_description(tool_info) + "\n"
        return tools_section


    def generate_prompt_with_tools(self,dialog_list, tools_info):
        """
        根据对话历史和工具信息生成完整 prompt。
        
        :param dialog_list: list, 包含对话的字典列表。
        :param tools_info: list, 包含工具的详细信息。
        :return: str, 完整的 prompt 文本。
        
        # 示例对话历史
        dialog_list = [
            {"role": "system", "content": "你是Alice,是YakumoAki在设计的智能语音助手"},
        ]
        tool_info = tool_config.generate_tools_desc()
        # 生成完整 prompt
        prompt = generate_prompt_with_tools(dialog_list, tool_info)
        print(prompt)
        """
        system_message = next((msg["content"] for msg in dialog_list if msg["role"] == "system"), "你是一个智能助手")
        tools_section = self.generate_tools_section(tools_info)

        dialog_section = "对话历史：\n"
        for dialog in dialog_list:
            if dialog["role"] == "user":
                dialog_section += f"用户：{dialog['content']}\n"
            elif dialog["role"] == "assistant":
                dialog_section += f"Alice：{dialog['content']}\n"

        return f"{system_message}\n\n{tools_section}\n{dialog_section}"