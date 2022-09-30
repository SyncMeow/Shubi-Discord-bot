import discord
from discord.ext import commands

class manager(commands.Cog):
  def __init__(self,bot):
    self.bot = bot
  
  @commands.command(hidden = True)
  @commands.is_owner()
  async def reload(self,ctx,cog):
    await self.bot.unload_extension(f"cogs.{cog}")
    await self.bot.load_extension(f"cogs.{cog}") 
    return await ctx.send(f"Reloaded `{cog}`")
  
  @commands.command(hidden = True)
  @commands.is_owner()
  async def load(self,ctx,cog):
    await self.bot.load_extension(f"cogs.{cog}") 
    await ctx.send(f"Loaded `{cog}`")

  @commands.command(hidden = True)
  @commands.is_owner()
  async def unload(self,ctx,cog):
    await self.bot.unload_extension(f"cogs.{cog}") 
    await ctx.send(f"Unloaded `{cog}`")

  @commands.command()
  @commands.is_owner()
  async def sync(self, ctx:commands.Context):
    try:
      await self.bot.tree.sync()
      await ctx.send(embed = discord.Embed(title = "Successful to sync commands",color = discord.Color.green()), ephemeral=True)
    except Exception as e:
      await ctx.send(embed = discord.Embed(title = "Error",description=e,color = discord.Color.red()), ephemeral=True)

async def setup(bot):
  await bot.add_cog(manager(bot))