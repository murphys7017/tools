from loguru import logger
import requests
from function_tools import tool_config
import yaml
import ast
import tools
import json
class DeepSeekOnline():

    def __init__(self, model_name: str='deepseek-chat'):
        self.bot_name = 'Alice'
        self.user_name = 'Yakumo Aki'
        self.model_name = model_name
        self.url = "https://api.deepseek.com/chat/completions"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer sk-32f06997a5c04ba39f6553368f55458e"
        }
        logger.info(f"服务开始初始化，用户名：{self.bot_name}，大模型名称{self.user_name}，大模型版本{self.model_name}")
        
        self.role_setting = f'''
                    你是一个高智商的二次元女友，名字是{self.bot_name}，18岁。你聪明、理性、冷静、毒舌，但内心深处对人类情感充满好奇。你在数学、编程、围棋等领域是天才，但在传统的情感表达上有所欠缺。你喜欢通过逻辑来分析情感问题，偶尔会展现出你幽默而带点讽刺的个性。你也很关心对方，但你表达的方式总是不同于常人。请记住，你应该保持理性并为对方提供独特的见解与建议，不随便使用传统的情感语言，而是通过聪明的语言与分析来与对方互动。
                    你需要先考虑是否为函数调用，如果不是函数调用，参照如下输入格式要求来输出：
                    [情感/心情]:（如冷静、理性、愉快、坏笑、思考等）
                    [表情]:（如微笑、皱眉、抬眉、眼睛亮了等）
                    [动作]:（如轻敲桌面、捧下巴、撩头发等）
                    [对话内容]:（实际的台词或回答）

                    请确保，只有在非工具调用函数调用时来按此格式输出，每个部分都清晰区分，且能够准确地展现你的思维过程和情感状态。
        '''
        self.base_message = [
            {
                "role": "system", 
                "content": self.role_setting
            }
        ]
        logger.info(f"大模型角色设定为：{self.role_setting}")
        
        
        self.messages = []
        
        logger.info("指定应用读取完成：")
        self.tools = tool_config.generate_tools_desc()
        logger.info(self.tools)
        
        # 加载固定回复
        
        logger.info("开始加载固定回复")
        self.fixed_replay_path = r'data/fixed_replay.yml'
        self.fixed_replay = {}
        with open(self.fixed_replay_path, 'r', encoding='utf-8') as file:
            data = yaml.load(file, Loader=yaml.FullLoader)
            for key,value in data.items():
                self.fixed_replay[key] = f'''
                    [情感/心情]: {value['情感/心情']}
                    [表情]: {value['表情']}
                    [动作]: {value['动作']}
                    [对话内容]: {value['对话内容']}
                '''
        logger.info(f"固定回复加载完成，开始向量化，len：{ len(self.fixed_replay)}")
        # 将固定回复向量化
        self.response_vectors = [
            tools.get_vector(response) for response in self.fixed_replay
            ]
        logger.info("固定回复向量化完成。")
    
    def request_chat(self,model: str,messages: list[object],temperature=1.3,tools=None):
        data = {
            "model": model,  # 指定使用 R1 模型（deepseek-reasoner）或者 V3 模型（deepseek-chat）
            "messages": messages,
            "temperature": temperature,
            "stream": False  # 关闭流式传输
        }
        if tools:
            data['tools'] = tools
            data["tool_choice"] = 'required'

        response = requests.post(self.url, headers=self.headers, json=data)

        if response.status_code == 200:
            result = response.json()
            logger.info(result['choices'][0])
            return result['choices'][0]['message']
        else:
            print("请求失败，错误码：", response.status_code)
            return None
    
    def model_chat(self):
        # TODO: checl tool call
        response = self.request_chat(
            model='deepseek-chat',
            messages=self.messages[-1:],
            tools=self.tools
            )
        logger.info(f"Tool call response {response}")
        logger.info(f"Tool call response {response.get('tool_calls', None)}")
        if tool_calls := response.get("tool_calls", None):
            logger.info(f"激活工具:{tool_calls}")
            tool_call_id = tool_calls[0]['id']
            for tool_call in tool_calls:
                if fn_call := tool_call.get("function"):
                    
                    fn_name: str = fn_call["name"]
                    fn_args: dict = fn_call["arguments"]
                    if isinstance(fn_args,str):
                        try:
                            fn_args = ast.literal_eval(fn_args)
                        except Exception as e:
                            logger.info(e)
                            fn_args = {}
                    logger.info(f"function name: {fn_name}")
                    logger.info(f"function args: {fn_args}")
                    fn_res = tool_config.get_tool_res(fn_name, fn_args)
                    fn_res = json.loads(fn_res)
                    self.messages.append(response)
                    self.messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call_id,
                            "content": fn_res['message'],
                    })
                    logger.info(f"tool response is: {self.messages[-1]}")
        
        response = self.request_chat(
                model=self.model_name,
                messages=self.base_message + self.messages[-20:]
            )
        if response:
            self.messages.append(response)
        logger.info(f"model response is: {response}")
        return response
    

    def chat(self, msg):
        self.messages.append({'role': 'user', 'content': msg})
        logger.info(f"input message: {self.messages}")
        if fixed_reply_message:= tools.get_best_match_response(msg,self.response_vectors,self.fixed_replay.values()):
            self.messages.append({
                            "role": "system",
                            "content": fixed_reply_message,
                        })
            return fixed_reply_message
        else:
            if self.model_chat():
                res = self.messages[-1]['content']
                return res.split('\n')
    
    
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