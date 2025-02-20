import os
import sys
import json
import uuid
import websocket
import datetime
import time
from loguru import logger

    
class MiraiSingleAdapter:
    def __init__(self, ws_link="ws://192.168.5.3:8081/all"):
        self.ws_link = ws_link
        self.function_response_wait_time = 1000 * 5
        self.message_list_max_length = 100
        self.messages = []  # 存储消息
        self.message_func_res = {}  # 存储同步ID与消息的映射
        self.allow_user = {  # 用户权限
            "815049548": {
                "response_group": [830954892],
                "user_access": {
                    "message": "ALL",
                    "event": "ALL",
                    "command": "ALL"
                }
            }
        }
        
        self.ws = websocket.create_connection(ws_link)
    def message_flattener(self,response):
        # 获取消息类型
        message_type = response['data'].get('type')
        # 获取消息内容和发送者信息
        messageChain = response['data'].get('messageChain', [])
        sender = response['data'].get('sender', {})
        
        sender_group = sender.get('group',None)
        
        sender_id = sender.get('id')
        
        
        show_text = ""
        for item in messageChain:
            if item['type'] == 'Source':
                continue
            elif item['type'] == 'Plain':
                show_text += item['text']
                show_text += ' '
            elif item['type'] == 'Image':
                show_text += ' 收到图片'
            elif item['type'] == 'App':
                app_info = json.loads(item['content'])
                if 'meta' in app_info and 'detail_1' in app_info['meta']:
                    detail_1 = app_info['meta']['detail_1']
                    if detail_1['title'] == '哔哩哔哩':
                        show_text += f"{detail_1['title']} {detail_1['desc']} {detail_1['qqdocurl'].split('?')[0]}"
                    else:
                        show_text += f"{detail_1['title']} {detail_1['desc']} {detail_1['qqdocurl']}"
            else:
                show_text += ' 非文本消息'
                
        
        if message_type == 'FriendMessage':
            sender_name = sender.get('remark',sender.get('nickname'))
            
            return f"{sender_name}({sender_id}) ->{show_text}"
        elif message_type == 'GroupMessage':
            sender_name = sender.get('memberName')
            
            return f"[{sender_group['name']}({sender_group['id']})]{sender_name}({sender_id}) ->{show_text}"
            
        
    def message_handle(self):
        """消息处理函数，根据插件决定如何处理"""
        while True:
            response = self.base_message_receiver()

            # 获取消息类型
            message_type = response['data'].get('type')
            # 获取消息内容和发送者信息
            messageChain = response['data'].get('messageChain', [])
            sender = response['data'].get('sender', {})


    def base_message_receiver(self):
        """接收消息"""
        response = self.ws.recv()
        response = json.loads(response)
        response['data']['RecvTime'] = int(datetime.datetime.now().timestamp())
        if response['syncId'] == -1:
            self.messages.append(response['data'])
        else:
            self.message_func_res[response['syncId']] = response['data']
        return response

    def base_message_sender(self, command, content, subCommand=None):
        """发送消息并等待响应"""
        syncId = uuid.uuid4().hex  # 生成唯一的syncId
        data = {
            "syncId": syncId,
            "command": command,
            "subCommand": subCommand,
            "content": content
        }
        self.ws.send(json.dumps(data))
        return self.wait_response(syncId=syncId)

    def wait_response(self, syncId):
        
        """等待syncId对应的消息返回"""
        start_timestamp = int(datetime.datetime.now().timestamp() * 1000)
        while syncId not in self.message_func_res:
            if int(datetime.datetime.now().timestamp() * 1000) - start_timestamp > self.function_response_wait_time:
                logger.info(f"MESSAGE_WAITE_TOO_LONG:{syncId}")
                return {
                    "STATUS": "ERROR",
                    "MESSAGE": "MESSAGE_WAITE_TOO_LONG"
                }
            time.sleep(0.1)  # 防止忙等待，释放CPU
        response = self.message_func_res[syncId]
        del self.message_func_res[syncId]
        return response
    def generate_plain_message(self, text):
        """生成纯文本消息"""
        return [{"type": "Plain", "text": text}]

    def generate_at_message(self, target, text):
        """生成@某个用户的消息"""
        return [{"type": "At", "target": target}, {"type": "Plain", "text": text}]

    def generate_image_message(self, image_url):
        """生成图片消息"""
        return [{"type": "Image", "url": image_url}]

    def generate_forward_message(self, messages):
        """生成转发消息"""
        return  [{"type": "Forward", "messages": messages}]

    