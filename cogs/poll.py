import discord
from discord import app_commands
from discord.ext import commands
from libs.poll_class import PollCreateModal

poll_activity = {}

class poll(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
    
    @app_commands.command()
    @app_commands.guild_only()
    async def poll(self, interaction: discord.Interaction):
        """建立一場投票"""
        guild = interaction.guild
        channel = interaction.channel
        author = interaction.user

        await interaction.response.send_modal(PollCreateModal(guild = guild,channel = channel, author = author))

async def setup(bot):
    await bot.add_cog(poll(bot))