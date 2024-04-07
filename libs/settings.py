import json

with open("./json/settings.json","r",encoding="utf-8") as r: data = json.load(r)

token:str = data["token"]
comprefix:str = data["comprefix"]
songs:list = data["songs"]
lavalink:dict = data["lavalink"]
avatar:str = data["avatar"]
school_news_channel:int = data["school_news_channel"]