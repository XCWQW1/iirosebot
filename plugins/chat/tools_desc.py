from functools import partial
from openai import OpenAI
import json
import inspect
import re
from loguru import logger
import inspect
import re

tools = []

available_functions = {}

def tool(func):
    # 解析函数名
    func_name = func.__name__

    if func_name in available_functions:
        logger.info(f"函数 {func_name} 已经存在，跳过添加")
        return func
        
    # 解析函数注释
    func_doc = func.__doc__
    
    func_desc = re.match(r'[^:\n]+', func_doc)
    if func_desc:
        func_desc = func_desc.group(0)

    # 解析参数类型和描述
    signature = inspect.signature(func)
    parameters = signature.parameters
    param_info = {}
    param_names = []
    for param_name, param in parameters.items():
        # 解析参数类型
        param_type = map_type(param.annotation)

        # 解析参数描述
        param_desc = None
        if func_doc:
            matches = re.findall(r':param\s+{}:\s*(.+)'.format(param_name), func_doc)
            if matches:
                param_desc = matches[0]

        # 判断参数是否有默认值
        if param.default is inspect.Parameter.empty:
            param_names.append(param_name)

        # 添加到参数信息字典中
        param_info[param_name] = {'type': param_type, 'description': param_desc}

    available_functions[func_name] = func
    logger.info(f"已添加函数 {func_name} 到 available_functions")
    tools.append(
        {"type": "function",
         "function":
            {
                "name": func_name,
                "description": func_desc,
                "parameters": {
                    "type": "object",
                    "properties": param_info,
                    "required": param_names,
                },
            } 
        }
    )

    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper


type_maps = {
    "None": "null",
    "str": "string",
    "int": "integer",
    "float": "number",
    "bool": "boolean",
    "list": "array",
    "tuple": "array",
    "dict": "object"
}


def map_type(param_type):
    param_type = type_maps.get(str(param_type)[7:-1], "string")
    return param_type