import discord
import requests
from libs import settings
from fake_useragent import UserAgent
import json

uid = "WID_0_2_0516b5aba93b58b0547367faafb2f1dbe2ebba4c"

cookies = {
    'PHPSESSID': '6omgipkd69j145k0fn5bjkpp33',
}

ua = UserAgent()
headers = {
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
    'Connection': 'keep-alive',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    # 'Cookie': 'PHPSESSID=6omgipkd69j145k0fn5bjkpp33',
    'Origin': 'https://www.hchs.hc.edu.tw',
    'Referer': 'https://www.hchs.hc.edu.tw/ischool/widget/site_news/main2.php?uid=WID_0_2_0516b5aba93b58b0547367faafb2f1dbe2ebba4c&maximize=5',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': ua.random,
    'X-Requested-With': 'XMLHttpRequest',
    'sec-ch-ua': '"Chromium";v="104", " Not A;Brand";v="99", "Google Chrome";v="104"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
}


def getNewsPage(page:int) -> dict:
    school_url = "https://www.hchs.hc.edu.tw/ischool/widget/site_news/news_query_json.php"
    
    payload = {
        'field': 'time',
        'order': 'DESC',
        'pageNum': f"{(page)}",
        'maxRows': '20',
        'keyword': '',
        'uid': uid,
        'tf': '1',
        'auth_type': 'user',
    }
    response:requests.Response = requests.post(school_url, cookies=cookies, headers=headers, data=payload)
    data = json.loads(response.content)
    news = {
        t["newsId"]:{
            key:value
            for key,value in t.items() if key in ["time","attr_name","title","unit_name"]
        }
        for index, t in enumerate(data) if index > 0
    }
    news = select_new(news)
    return news


def select_new(data:dict):
    history = json.load(open("./json/history.json","r",encoding = "utf-8"))
    result = {
        key:value
        for key,value in data.items() if key not in history.keys()
    }

    if len(result.keys()): 
        update_history(data)

    return result

def update_history(data:dict):
    history:dict = json.load(open("./json/history.json","r",encoding = "utf-8"))
    news = {key:1 for key in data.keys()}
    history.update(news)
    w = open("./json/history.json","w",encoding = "utf-8")
    json.dump(history,w)

async def get_news_embed(pages:int = 2):
    news = {}
    limit = 25

    for p in range(pages):
        data = getNewsPage(p)
        news.update(data)
    
    if not len(news):
        return None

    Embed = discord.Embed(title = "新竹高中最新訊息", color = discord.Color.red())
    for i, (k, t) in enumerate(news.items()):
        if (i >= limit): 
            break
        time = t["time"]
        attr = t["attr_name"]
        title = t["title"]
        unit = t["unit_name"]
        Embed.add_field(name = title, value = f"{time}  {unit}{attr}\n[連結](https://www.hchs.hc.edu.tw/ischool/public/news_view/show.php?nid={k})", inline = False)


    Embed.set_footer(text = "學校公告", icon_url=settings.avatar)

    return Embed