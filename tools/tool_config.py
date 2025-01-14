import yaml
import os
with open('Config.yml', 'r', encoding='utf-8') as file:
    config = yaml.load(file, Loader=yaml.FullLoader)
tools_variable = config['ToolsSet']

def generate_name_path_map(folder_paths, exclude_name, exclude_path):
    pgo = {}
    for folder_path in folder_paths:
        for filepath,dirnames,filenames in os.walk(folder_path):
            for filename in filenames:
                if filename.endswith('.lnk') or filename.endswith('.exe'):
                    name = filename.split('.')[0]
                    flg = not any(key in name or key == name for key in exclude_name.split(','))
                    if flg:
                        flg = not any(key in filepath or key in dirnames for key in exclude_path.split(','))
                    if flg:
                        pgo[name] = os.path.join(filepath, filename)
    return pgo

def generate_tools_desc():
    tools_desc = []
    for name,desc in tools_description.items():
        temp ={
            "type": "function",
            "function": {
                "name": name,
                "description": desc['description'],
                "parameters":{
                    "type": "object",
                    "properties":{
                    },
                    "required": []
                }
            }
        }
        if "parameters" in desc:
            for param_name, param_info in desc['parameters'].items():
                temp["function"]['parameters']['properties'][param_name] = {
                    "type": param_info['type'],
                    "description": param_info['description']
                }
                if 'enum' in param_info:
                    temp["function"]['parameters']['properties'][param_name]["enum"]= param_info['enum']
                if param_info['required']:
                    temp["function"]['parameters']['required'].append(param_name)

        tools_desc.append(temp)
    return tools_desc



tools_description = {
    'close_light' :{
        "description": "关掉机箱的灯。",
    },
    'open_light' :{
        "description": "打开机箱的灯。",
    },    
    'run_software':{
        "description": "打开或者运行程序、软件、应用、脚本等。",
        "parameters":{
            "software_name":{
                "type": "string",
                "required": True,
                "enum": list(generate_name_path_map(folder_paths=tools_variable['RunSoftware']['Paths'], exclude_name=tools_variable['RunSoftware']['Exclude']['Name'], exclude_path=tools_variable['RunSoftware']['Exclude']['Path']).keys()),
                "description": "需要打开、运行或者执行的软件程序或者脚本的名称"
            }
        }
    }
}














        
tools_desc = [
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