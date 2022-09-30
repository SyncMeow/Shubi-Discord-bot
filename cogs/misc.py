import discord
from discord.ext import commands
from libs import settings
from textwrap import wrap
import cexprtk


class misc(commands.Cog):
    def __init__(self, bot:discord.Client):
        self.bot = bot
    
    @commands.command()
    async def m(self, ctx:commands.Context, *formula:str):
        f = "".join(list(formula))
        if '=' in f: return await ctx.reply("算式不得包含``=``", ephemeral=True)
        a = cexprtk.evaluate_expression(f,{})
        if '*' in f: f = "×".join(f.split('*'))
        if '/' in f: f = "÷".join(f.split('/'))
        Embed = discord.Embed(title = f"{f}\n = {a}", color = discord.Color.dark_gray())
        Embed.set_footer(text = "簡易計算機", icon_url = settings.avatar)
        await ctx.reply(embed = Embed)

    @commands.hybrid_command(name = "repeat", with_app_command=True)
    async def repeat(self, ctx:commands.Context, msg:str, times:int):
        """重複發送訊息"""
        s = ""
        for i in range(times):s += f"{msg}\n"
        strs = wrap(s,2000)
        for i in strs:
            await ctx.send(i)

    @commands.hybrid_command(name = "status", with_app_command=True)
    async def status(self,ctx:commands.Context,hidden:bool):
        """取得當前伺服器所有成員的狀態"""
        list = discord.Embed(title = "成員狀態",color = discord.Color.green())
        n = 0
        online = ""
        offline = []
        mobile_n = 0
        desktop_n = 0
        mobile = ""
        desktop = ""
        for member in ctx.guild.members:
            if (member.bot):
                continue
            n += 1
            if str(member.status) != "offline":
                online += f"<@{member.id}> "
                if member.is_on_mobile():
                    mobile_n += 1
                    mobile += f"<@{member.id}> "
                else:
                    desktop_n += 1
                    desktop += f"<@{member.id}>"
            else:
                offline.append(f"<@{member.id}>")

        list.add_field(name = f"線上人數 {n - len(offline)} / {n}人",value = online,inline = False)
        if desktop_n: list.add_field(name = f"使用電腦 {desktop_n} / {n - len(offline)}人",value = desktop,inline = False)
        if mobile_n: list.add_field(name = f"使用手機 {mobile_n} / {n - len(offline)}人",value = mobile,inline = False)
        await ctx.send(embed = list,hidden = hidden)


async def setup(bot):
    await bot.add_cog(misc(bot))
