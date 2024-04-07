import discord
from discord.ext import commands
from discord.ext import tasks
from libs import settings
from libs.progressbar import printProgressBar
from libs.school_crawler import get_news_embed
from libs.logger import console_logger, record_logger
import keep_alive
import datetime
import asyncio
import random
import time
import os

class Shubi(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix = settings.comprefix, intents = discord.Intents.all(), help_command = None)
        self.start_time = time.time()

    @tasks.loop(seconds = 60)
    async def status_task(self):
        await self.wait_until_ready()

        custom = random.choice(settings.songs)
        await self.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=custom))

    @tasks.loop(seconds = 60)
    async def update_school_news(self):
        await self.wait_until_ready()

        news_embed = await get_news_embed()
        if news_embed:
            print(news_embed)
            channel = self.get_channel(settings.school_news_channel)
            await channel.send(embed = news_embed)

    async def setup_hook(self):
        cogs = []
        for i in os.listdir("./cogs"):
            if i.endswith('.py') and not i.startswith('_'): cogs.append(i)

        i = 0
        printProgressBar(0,len(cogs),prefix="Loading Cogs",suffix="Complete",length=20)
        for cog in cogs:
            await self.load_extension(f"cogs.{cog[:-3]}")
            i+=1
            printProgressBar(i,len(cogs),prefix="Loading Cogs",suffix="Complete",length=20)
        
        self.status_task.start()
        self.update_school_news.start()

        print(f"{self.user} is online!")
        record_logger.info(f"{self.user} is online")

    async def on_guild_join(self, guild:discord.Guild):
        console_logger.info(f"Joined Guild:``{guild.name}`` Id: {guild.id}")
        record_logger.info(f"Joined Guild:``{guild.name}`` Id: {guild.id}")
        await guild.text_channels[0].send(f"我第一次加入{guild}, 可以使用`s;about`查看我的詳細訊息!")

    async def on_guild_remove(self, guild:discord.Guild):
        console_logger.info(f"Left Guild:``{guild.name}`` Id: {guild.id}")
        record_logger.info(f"Left Guild:``{guild.name}`` Id: {guild.id}")

shubi = Shubi()

@shubi.hybrid_command(name = "about", with_app_command=True)
async def about(ctx:commands.Context):
    """有關我的一切"""
    uptime = datetime.timedelta(seconds=int(time.time() - shubi.start_time))
    servers_n = len(shubi.guilds)
    com_n = len(shubi.tree.get_commands(type=discord.AppCommandType.chat_input))
    ping = round(shubi.latency * 1000)
    Embed = discord.Embed(title = "Shubi", color=discord.Color.gold(),timestamp=datetime.datetime.utcnow())
    Embed.add_field(name = "介紹", value = "我是第二代的Shubi, 我繼承了一代的一些東西, 歡迎使用", inline = False)
    Embed.add_field(name = "指令", value = "我支援使用`/`指令, 使用`s$help`顯示指令列表", inline = False)
    Embed.add_field(name = "統計", value = f":clock1:上線時間: **{uptime}**(since <t:{int(shubi.start_time)}>)\n\n:desktop:服務的伺服器數量: **{servers_n}**\n\n:books:指令數量: **{com_n}**\n\n:hourglass_flowing_sand:目前延遲: **{ping} ms**", inline = False)
    Embed.add_field(name = "備註", value = "我的 / 指令在剛加入新伺服器時有時要等一段時間才能同步", inline = False)
    Embed.set_thumbnail(url=settings.avatar)
    Embed.set_footer(text = "Made by Shinmeow#1338", icon_url = settings.avatar)
    async with ctx.channel.typing():
        await ctx.send(embed = Embed)
  
try:
    keep_alive.keep_alive()
    shubi.run(settings.token)
except Exception as e:
    console_logger.critical(f"{e}")
    record_logger.critical(f"{e}")
    #os.system('kill 1')