import json
import os
from libs.logger import console_logger
from xml.dom import NotFoundErr


def GetJson(file:str) -> dict:
    """
    Quick get a json file
        params:
            file   - Required  : json file name (Str)
    """
    if file not in os.listdir('./json'):
        raise NotFoundErr(f"Cound not find ``{file}``")

    return json.load(open(f'./json/{file}', 'r', encoding='utf-8'))

def WriteJson(data:dict, file:str) -> None:
    """
    Write a dictionary to a json file
        @params:
            data   - Required  : the data (Dict)
            file   - Required  : the target file (Str)
    """
    if file not in os.listdir('./json'):
        raise NotFoundErr(f"Cound not find ``{file}``")
    
    w = open(f'./json/{file}', 'w', encoding='utf-8')
    json.dump(data,w)
    #console_logger.info(f"Write a data to {file}")
    return 