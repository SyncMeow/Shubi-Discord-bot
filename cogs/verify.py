import discord
from discord.ext import commands
from discord import app_commands
from libs.Access_class import QuestionsSetModal, VerifyModal, QuestionContext
import json

class verify(commands.Cog):
  def __init__(self,bot):
    self.bot = bot

  @commands.hybrid_group(name = "verify", with_app_command=True)
  async def verify(self,ctx:commands.Context):
    if not ctx.invoked_subcommand: return await ctx.send("[Error]Invalid sub command passed", ephemeral=True)

  @verify.command(name = "start",with_app_command=True)
  async def start(self,ctx:commands.Context):
    """開始驗證流程"""
    if not self.check_guild(ctx.guild.id) or not self.check_has_channel(ctx.guild.id): 
      return await ctx.send("此伺服器並未設定**驗證頻道**!", ephemeral=True)

    data = json.load(open("./json/access.json","r",encoding = "utf-8"))[str(ctx.guild.id)]
    channel = data["channel"]
    if not self.check_verify_channel(ctx.guild.id,ctx.channel.id): return await ctx.send(f"這裡不是**驗證頻道**!請去<#{channel}>", ephemeral=True)
    
    for role in ctx.author.roles: 
      if role.id == data["role"]: return await ctx.send("你已經通過了驗證", ephemeral=True)

    verifyModal = VerifyModal(ctx)
    
    for q,a in data["questions"].items():
      question = QuestionContext(q,a)
      verifyModal.add_item(question)

    await ctx.interaction.response.send_modal(verifyModal)
    
  @verify.command(name = "add", with_app_command=True)
  @commands.has_permissions(administrator = True)
  async def add(self,ctx:commands.Context):
    """將當前頻道設定為驗證頻道"""
    if not isinstance(ctx.channel, discord.TextChannel): return await ctx.send("Current channel is not a **TextChannel**.", ephemeral=True)
    
    if self.check_guild(ctx.guild.id) and self.check_verify_channel(ctx.guild.id,ctx.channel.id): 
      return await ctx.send("當前頻道已經是**驗證頻道**了!")
    
    data = json.load(open("./json/access.json","r",encoding = "utf-8"))
    exist_name = data[str(ctx.guild.id)]["channel"]
    with open("./json/access.json","w",encoding = "utf-8") as w:
      data[str(ctx.guild.id)]["channel"] = ctx.channel.id
      json.dump(data,w)
    if exist_name:
      await ctx.send(f"已將此伺服器的**驗證頻道**由 <#{exist_name}> 改為 <#{ctx.channel.id}>, 使用`verify settings view`查看設定")
    else:
      await ctx.send(f"已將此伺服器的**驗證頻道**設定為 <#{ctx.channel.id}>, 請使用`verify settings`設定驗證資訊!")
      
  @verify.command(name = "remove", with_app_command=True)
  @commands.has_permissions(administrator = True)
  async def remove(self, ctx:commands.Context):
    """將當前伺服器的驗證頻道取消"""
    if not isinstance(ctx.channel, discord.TextChannel): return await ctx.send("Current channel is not a **TextChannel**.", ephemeral=True)
    
    data = json.load(open("./json/access.json","r",encoding = "utf-8"))

    if str(ctx.guild.id) not in data.keys() or not self.check_has_channel(ctx.guild.id): 
      return await ctx.send("此伺服器並未設定**驗證頻道**!")
    exist_name = "<#" + str(data[str(ctx.guild.id)]["channel"]) + ">"
    data[str(ctx.guild.id)]["channel"] = 0
    w = open("./json/access.json","w",encoding = "utf-8")
    json.dump(data,w)
    return await ctx.send(f"已將此伺服器的**驗證頻道**{exist_name}取消")    
      
  @verify.group(name = "settings", with_app_command=True)
  async def settings(self,ctx:commands.Context):
    if not ctx.invoked_subcommand: return await ctx.send("[Error]Invalid sub command passed", ephemeral=True)

  @settings.command(name = "view", with_app_command=True)
  @commands.has_permissions(administrator = True)
  async def view(self,ctx:commands.Context):
    """檢視驗證頻道的設定"""
    if not self.check_guild(ctx.guild.id) or not self.check_has_channel(ctx.guild.id): return await ctx.send("此伺服器並未設定**驗證頻道**!", ephemeral=True)
    else:
      setting = json.load(open("./json/access.json","r",encoding="utf-8"))[str(ctx.guild.id)]
      channel = "<#" + str(setting["channel"]) + ">"
      question_n = str(len(setting["questions"].keys()))
      fault = setting["fault"]
      if not question_n: question_n = "未設置"
      if setting["role"]: role = "<@&" + str(setting["role"]) + ">"
      else:role = '未設置'
      Embed = discord.Embed(color = discord.Color.blue())
      Embed.add_field(name = f"{ctx.guild} 的當前設置", value = f"驗證頻道: {channel}\n\n驗證問答題數: {question_n}\n\n允許錯題數: {fault}\n\n驗證身分組: {role}")
      await ctx.send(embed = Embed)
    
  @settings.command(name = "setq", with_app_command=True)
  @commands.has_permissions(administrator = True)
  async def setq(self, ctx:commands.Context):
    """設定加入此伺服器的成員必須回答的題目"""
    if not self.check_guild(ctx.guild.id) or not self.check_has_channel(ctx.guild.id): 
      return await ctx.send("此伺服器並未設定**驗證頻道**!", ephemeral=True)
    await ctx.interaction.response.send_modal(QuestionsSetModal(str(ctx.guild.id)))

  @settings.command(name = "setr", with_app_command=True)
  @commands.has_permissions(administrator = True)
  async def setr(self, ctx:commands.Context, role:discord.Role):
    """設定成員回答完成問題後獲得的身分組"""
    if not self.check_guild(ctx.guild.id) or not self.check_has_channel(ctx.guild.id): 
      return await ctx.send("此伺服器並未設定**驗證頻道**!", ephemeral=True)

    data = json.load(open("./json/access.json","r",encoding="utf-8"))
    data[str(ctx.guild.id)]["role"] = role.id
    w = open("./json/access.json","w",encoding="utf-8")
    json.dump(data,w)
    await ctx.send(f"已成功設定獲得身分組({role.mention})")

  def check_guild(self, guild_id):
    data = json.load(open("./json/access.json","r",encoding="utf-8"))
    if str(guild_id) not in data.keys():
      data[str(guild_id)] = {"channel":000000000000000000, "role":0, "fault":0, "questions":{}}
      w = open("./json/access.json","w",encoding="utf-8")
      json.dump(data,w)
      return False
    else: return True

  def check_verify_channel(self, guild_id, channel_id):
    data = json.load(open("./json/access.json","r",encoding="utf-8"))
    return channel_id == data[str(guild_id)]["channel"]
  
  def check_has_channel(self, guild_id):
    data = json.load(open("./json/access.json","r",encoding="utf-8"))
    return data[str(guild_id)]["channel"] and True

async def setup(bot):
  await bot.add_cog(verify(bot))