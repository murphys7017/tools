tools = [
    {
        "type": "function",
        "function": {
            "name": "close_light",
            "description": "关掉机箱的灯。",
            "parameters":{
                "type": "object",
                "properties":{
                },
                "required": []
            }
        },
    },
    {
        "type": "function",
        "function": {
            "name": "open_light",
            "description": "打开机箱的灯。",
            "parameters":{
                "type": "object",
                "properties":{
                },
                "required": []
            }
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run_software",
            "description": "根据给出的名称去运行指定的程序软件或者脚本等可执行的。",
            "parameters":{
                "type": "object",
                "properties":{
                    "software_name":{
                        "type": "string",
                        "enum": [],
                        "description": "需要运行或者执行的软件程序或者脚本的名称"
                    }
                },
                "required": ["software_name"]
            }
        }
    }
]