import discord
from discord.ext import commands
from discord import app_commands
from libs.settings import avatar
from datetime import datetime, timedelta
import traceback

class error(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        self.ignored = [commands.errors.CommandNotFound, commands.errors.NotOwner, commands.errors.NoPrivateMessage]
        bot.tree.on_error = self.on_app_command_error

    @commands.Cog.listener()
    async def on_command_error(self, ctx:commands.Context, error):
        if type(error) in self.ignored:
            return

        if isinstance(error, commands.errors.CommandInvokeError):
            error = error.original

        if isinstance(error, commands.errors.MissingPermissions):
            permissions = ", ".join(error.missing_permissions)
            warning = f"你必須擁有 **{permissions}** 權限以執行此指令"
            embed = self.warning_embed(warning)
            return await ctx.send(embed = embed, ephemeral =True)
        
        if isinstance(error, commands.errors.MissingRequiredArgument):
            warning = f"請輸入參數 **{error.param}**"
            embed = self.warning_embed(warning)
            return await ctx.send(embed = embed, ephemeral =True)
        
        if isinstance(error, commands.errors.CommandOnCooldown):
            embed = self.cooldown_embed(error)
            return await ctx.send(embed = embed, ephemeral =True)

        error = "".join(traceback.format_exception(error))
        print(error)
        embed = self.warning_embed(error)
        return await ctx.send(embed = embed, ephemeral =True)

    async def on_app_command_error(self, interaction:discord.Interaction, error):
        if type(error) in self.ignored:
            return
        
        if isinstance(error, app_commands.errors.MissingPermissions):
            permissions = ", ".join(error.missing_permissions)
            warning = f"你必須擁有 **{permissions}** 權限以執行此指令"
            embed = self.warning_embed(warning)
            return await interaction.response.send_message(embed = embed, ephemeral=True)
        
        if isinstance(error, app_commands.errors.CommandOnCooldown):
            embed = self.cooldown_embed(error)
            return await interaction.response.send_message(embed = embed, ephemeral=True)
        
        error = "".join(traceback.format_exception(error))
        print(error)
        embed = self.warning_embed(error)
        return await interaction.response.send_message(embed = embed, ephemeral=True)
    
    def warning_embed(self, warning:str) -> discord.Embed:
        Embed = discord.Embed(title = "發生錯誤", description=warning, color = discord.Color.red(),timestamp=datetime.utcnow())
        Embed.set_footer(text = "例外事件崁入式訊息", icon_url = avatar)
        return Embed
    
    def cooldown_embed(self, error):
        wait = timedelta(seconds=int(error.retry_after))
        Embed = discord.Embed(title = "請求已被限制", description=f"此指令冷卻中 請等待**{wait}**", color = discord.Color.red())
        Embed.set_footer(text = "速率限制崁入式訊息", icon_url = avatar)
        return Embed

async def setup(bot):
    await bot.add_cog(error(bot))