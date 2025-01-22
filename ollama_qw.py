from loguru import logger
from tools import tool_config
import ollama
class OllamaQW():

    def __init__(self, model_name: str='qwen2.5:7b-instruct-q2_K'):
        self.bot_name = 'Alice'
        self.user_name = 'Yakumo Aki'
        self.model_name = model_name
        self.fixed_replay_path = r'data/fixed_replay.xlsx'
        self.fixed_replay = {}
        self.tools = tool_config.generate_tools_desc()
        self.base_message = [
            {"role": "system", "content": f"你是{self.bot_name},是{self.user_name}在设计的智能语音助手"}]
        self.messages = []
        logger.info(self.tools)
        self.load_fixed_replay()
    
    def load_fixed_replay(self):
        import pandas as pd
        df = pd.read_excel(self.fixed_replay_path)
        for index,row in df.iterrows():
            
            if row['key'] in self.fixed_replay:
                self.fixed_replay[row['key']].append(row['response'])
            else:
                self.fixed_replay[row['key']] = []
                self.fixed_replay[row['key']].append(row['response'])
                
    def get_fixed_replay(self,msg):
        msg = msg.lower()
        import difflib
        if msg in self.fixed_replay.keys():
            key = msg
        else:
            try:
                key = difflib.get_close_matches(msg.lower(),list(self.fixed_replay.keys()),1, cutoff=0.9)
                logger.info(key)
                if len(key) > 0:
                    key = key[0]
            except Exception as e:
                print(e)
            finally:
                key = []
        if len(key) > 0:
            content = "这个一个系统给出的固定回复，用户已经输入了，你需要从下面列出来的几个中选一个回复用户，不要调用其他工具："
            count = 1
            for line in self.fixed_replay[key]:
                line = line.replace('{name}', self.user_name).replace('{me}', self.bot_name)
                content = content + f"\n {line}"
                count += 1
            return {
                        "role": "system",
                        "content": content
                    }
        else:
            return None
    
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
        
        if fixed_reply_message:= self.get_fixed_replay(msg):
            self.messages.append(fixed_reply_message)
            logger.info(f"fixed reply message: {self.messages[-1]}")
            
        self.ollama_chat()
        
        # 工具调用
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