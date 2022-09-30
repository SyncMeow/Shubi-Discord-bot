import discord
from discord.ext import commands
from libs import settings
import json

class HelpCommand(commands.Cog):
  def __init__(self,bot):
    self.bot = bot

  @commands.Cog.listener()
  async def on_message(self,message):
    if message.author == self.bot.user:
      return

    if message.content == "s$help":
      await self.help(message)
      
  async def help(self,msg):
    with open("./json/help_command.json","r",encoding = "utf-8") as r:
      data = json.load(r)
  
    #generate pages
    pages = []
    i = 0
    for category in data.keys():
      i += 1
      page = discord.Embed(title = category,description = f"`page {i}/{len(data.keys())}`",color = discord.Color.orange())
      for command in data[category].keys():
        if command == "info":
          page.add_field(name = "關於本系列指令",value = f"```{data[category][command]}```",inline = False)
          continue
        page.add_field(name = command,value = f"```{data[category][command]}```",inline = False)
      page.set_footer(text = "Provided by Shubi#4470", icon_url=settings.avatar)
      pages.append(page)
  
    n_pages = len(data.keys())
    cur_page = 1

    message = await msg.channel.send(embed = pages[cur_page - 1])
    await message.add_reaction("◀")
    await message.add_reaction("▶") 
    await message.add_reaction("❌") 
    def check(reaction:discord.Reaction,user):
      return user == msg.author and True
      
    while (True):
      try:
        reaction, user = await self.bot.wait_for("reaction_add",check = check)
        if str(reaction.emoji) == "◀":
          if cur_page > 1:
            cur_page -= 1
            await message.edit(embed = pages[cur_page - 1])
          await message.remove_reaction(reaction,user)
        elif str(reaction.emoji) == "▶":
          if cur_page < n_pages:
            cur_page += 1
            await message.edit(embed = pages[cur_page - 1])
          await message.remove_reaction(reaction,user)
        elif str(reaction.emoji) == "❌":
          await message.delete()
          return
        else:
          await message.remove_reaction(reaction,user)
      except:
        return


async def setup(bot):
  await bot.add_cog(HelpCommand(bot))