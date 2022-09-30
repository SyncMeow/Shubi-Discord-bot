import discord
from discord.ext import commands

class fakeuser(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.webhook_cache = {}#channel_id:webhook  

    @commands.hybrid_command(name = "fake", with_app_command=True)
    @commands.is_owner()
    async def fake(self, ctx:commands.Context, target:discord.Member, msg:str):
        await self.fake_user_msg(ctx,target,msg)
    
    @commands.hybrid_command(name = "fakeuser", with_app_command=True)
    @commands.cooldown(1,5,commands.BucketType.user)
    async def fakeuser(self, ctx:commands.Context, target:discord.Member, msg:str):
        """偽裝成某人說話"""
        if ctx.author.id not in [721289329191682071, 850305162282270732, 596645933119438849, 275210585455722496, 869654532584513578, 863356824748687390]:
            return
        await self.fake_user_msg(ctx,target,msg)
    
    async def fake_user_msg(self, ctx:commands.Context, target:discord.Member, msg:str):
        channel = ctx.channel
        webhook = None
        if channel.id not in self.webhook_cache.keys():
            webhook_list = await channel.webhooks()
            for w in webhook_list:
                if w.name == "FakeUser":
                    webhook = w
                    self.webhook_cache[channel.id] = webhook
            
            if not webhook:
                webhook = await channel.create_webhook(name = "FakeUser", avatar =await self.bot.user.display_avatar.read())
        else:
            webhook = self.webhook_cache[channel.id] 
        await ctx.send("成功發送訊息", ephemeral=True)
        await webhook.send(content = msg, username = target.display_name, avatar_url=target.avatar.url)
    
async def setup(bot):
    await bot.add_cog(fakeuser(bot))    