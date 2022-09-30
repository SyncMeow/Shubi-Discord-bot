import discord
from discord import app_commands
from discord.ext import commands
from libs.logger import anony_logger
from datetime import datetime
import json
import re


class anonymous(commands.Cog):
  def __init__(self,bot):
    self.bot = bot
  
  @commands.Cog.listener()
  async def on_message(self,message):
    if message.author == self.bot.user: 
      return
    
    anonymous_channels = json.load(open("./json/anony.json","r",encoding = "utf-8")).keys()

    if str(message.channel.id) in anonymous_channels:
      await message.delete()
      settings = json.load(open("./json/anony.json","r",encoding="utf-8"))
      
      #log
      anony_logger.info(f"\n{message.guild}({message.guild.id}) / {message.channel} / {message.author} : {message.content}, with_files: {bool(len(message.attachments))}")

      urls=[]
      if len(message.attachments):
        if not settings[str(message.channel.id)]["allow_files"]: return await message.channel.send("抱歉, 本頻道被設定為禁止附加檔案")
        for url in message.attachments:
          urls.append(await discord.Attachment.to_file(url))
      
      if len(message.content):
        if not settings[str(message.channel.id)]["allow_urls"] and re.search(r'(http://|https://)',message.content):
          return await message.channel.send("抱歉, 本頻道被設定為禁止內文包含連結")
        embed = discord.Embed(color = discord.Color.red() ,timestamp = datetime.utcnow())
        embed.add_field(name = "匿名",value = message.content,inline = False)
        await message.channel.send(embed = embed)
        if len(urls): await message.channel.send(files = urls)
      else:
        await message.channel.send(files = urls)
  
  @commands.hybrid_group(name = "anony",with_app_command=True)
  async def anony(self,ctx:commands.Context):
    if not ctx.invoked_subcommand: return await ctx.send("[Error]Invalid sub command passed", ephemeral=True)

  @anony.command(name = "add", with_app_command=True)
  @commands.has_permissions(administrator = True)
  async def add(self,ctx:commands.Context):
    """設定當前頻道為匿名頻道"""
    if not isinstance(ctx.channel, discord.TextChannel): return await ctx.send("Current channel is not a **TextChannel**.", ephemeral=True)
    
    data = json.load(open("./json/anony.json","r",encoding="utf-8"))
    
    if self.check_anony(ctx.channel.id): return await ctx.send("當前頻道已經是**匿名頻道**了", ephemeral=True)
    else: 
      data[str(ctx.channel.id)] = {"allow_files":True, "allow_urls":True}
      with open("./json/anony.json","w",encoding="utf-8") as w: json.dump(data,w)
      await ctx.send(f"已成功將此頻道(<#{ctx.channel.id}>)設置為**匿名頻道**, 使用`/anony settings view` 查看設定")

  @anony.command(name = "remove", with_app_command=True)
  @commands.has_permissions(administrator = True)
  async def remove(self,ctx:commands.Context):
    """解除此匿名頻道"""
    if not isinstance(ctx.channel, discord.TextChannel): return await ctx.send("Current channel is not a **TextChannel**.", ephemeral=True)

    data = json.load(open("./json/anony.json","r",encoding="utf-8"))
    
    if not self.check_anony(ctx.channel.id): return await ctx.send("當前頻道不是**匿名頻道**!", ephemeral=True)
    else: 
      del data[str(ctx.channel.id)]
      with open("./json/anony.json","w",encoding="utf-8") as w: json.dump(data,w)
      await ctx.send(f"已成功將此**匿名頻道**(<#{ctx.channel.id}>)解除")
  
  @anony.group(name = "settings", with_app_command=True)
  @commands.has_permissions(administrator = True)
  async def settings(self,ctx:commands.Context):
    if not ctx.invoked_subcommand: return await ctx.send("[Error]Invalid sub command passed", ephemeral=True)
  
  @settings.command(name = "view", with_app_command=True)
  @commands.has_permissions(administrator = True)
  async def view(self,ctx:commands.Context):
    """檢視匿名頻道的設定"""

    if not self.check_anony(ctx.channel.id): return await ctx.send("當前頻道不是**匿名頻道**!", ephemeral=True)
    else:
      setting = json.load(open("./json/anony.json","r",encoding="utf-8"))[str(ctx.channel.id)]
      allow_files = "允許" if setting["allow_files"] else "禁止"
      allow_urls = "允許" if setting["allow_urls"] else "禁止"
      Embed = discord.Embed(color = discord.Color.blue())
      Embed.add_field(name = f"{ctx.channel} 的當前設置", value = f"允許檔案上傳: {allow_files}\n\n允許文字含有連結: {allow_urls}")
      await ctx.send(embed = Embed)

  @settings.command(name = "set", with_app_command=True)
  @app_commands.choices(rule = [
    app_commands.Choice(name = "AllowFiles", value = "AllowFiles"),
    app_commands.Choice(name = "AllowUrls", value = "AllowUrls")
  ])
  async def set(self,ctx:commands.Context, rule:str, arg:bool):
    """設定匿名頻道的規則"""
    if not self.check_anony(ctx.channel.id): return await ctx.send("當前頻道不是**匿名頻道**!", ephemeral=True)

    data = json.load(open("./json/anony.json","r",encoding="utf-8"))

    if rule == "AllowFiles":
      data[str(ctx.channel.id)]["allow_files"] = arg
    elif rule == "AllowUrls":
      data[str(ctx.channel.id)]["allow_urls"] = arg
    else:
      return await ctx.send("[Error]Invalid argument", ephemeral=True)
    
    with open("./json/anony.json","w",encoding="utf-8") as w: json.dump(data,w)
    await ctx.send(f"**匿名頻道**(<#{ctx.channel.id}>)的設定{rule}已設為{arg}")

  def check_anony(self, channel_id):
    data = json.load(open("./json/anony.json","r",encoding="utf-8"))
    if str(channel_id) in data.keys(): return True
    else: False 
       
async def setup(bot):
  await bot.add_cog(anonymous(bot))