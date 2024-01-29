from xml.dom import NotFoundErr
import discord
from discord.ext import commands

class server_observe(commands.Cog):
  def __init__(self, bot:discord.Client) -> None:
    self.bot = bot
  
  async def get_all_channel(self, guild_id):
    guild = self.bot.get_guild(guild_id)
    categories = {}
    for c in guild.channels:
      if c.category.name not in categories.keys():
        categories[c.category.name] = (c.category, c)
    return categories

  async def get_channel_history(self, channel_id, limit:int):
    channel = self.bot.get_channel(channel_id)
    if not isinstance(channel, discord.TextChannel) or not channel:
      return
    
    return [msg for msg in channel.history(limit = limit)]

async def setup(bot):
  await bot.add_cog(server_observe(bot))