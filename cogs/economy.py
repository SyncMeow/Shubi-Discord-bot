from tkinter import Label
import discord
from discord.ext import commands
from libs import settings
from libs import slot
import aiosqlite
import asyncio
import random

class economy(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
        
  async def setup_db(self):
    self.db = await aiosqlite.connect("bank.db")
    await asyncio.sleep(3)
    async with self.db.cursor() as cursor:
      await cursor.execute("CREATE TABLE IF NOT EXISTS bank(wallet INTEGER, bank INTEGER, maxbank INTEGER, user INTERGER)")
      await cursor.execute("CREATE TABLE IF NOT EXISTS inv(user INTERGER)")
      await cursor.execute("CREATE TABLE IF NOT EXISTS shop(name TEXT, id TEXT, desc TEXT, cost INTEGER)")
    await self.db.commit()
        
  @commands.hybrid_group(name ="economy")
  async def economy(self, ctx):
    return

  @economy.command()
  async def balance(self, ctx:commands.Context, member: discord.Member = None):
    """顯示帳戶資訊, member默認為使用指令者本人"""
    if not member:
      member = ctx.author
    wallet, bank, maxbank = await self.get_balance(member)
    em = discord.Embed(title = f"{member.name} 的帳戶", description=f"👛錢包: :coin: {wallet}\n\n🏦存款: :coin: {bank}", color = discord.Color.brand_red())
    em.set_footer(text = "經濟系統•帳戶資訊", icon_url=settings.avatar)
    await ctx.send(embed = em)

  @economy.command()
  @commands.cooldown(1, 10, commands.BucketType.user)
  async def work(self, ctx:commands.Context):
    """工作賺錢, 每10秒使用一次"""
    await ctx.defer()
    event = random.randint(0,3)
    purpose_list = ["你決定要去挖礦\n","你決定要去冒險\n","你決定要去釣魚\n","你遭遇了突發事件!\n"]
    event_list = [[("你什麼也沒挖到!",0),(":rock:你在坑道挖到了石頭!",10),("🟨你在閃亮的洞窟內挖到了黃金!",100),("💎你在幽暗的窄縫挖到了鑽石!",300)],[("你什麼也沒找到!",0),("🐭你在下水道殺死了一隻很臭的大老鼠!",10),("🐻你在常綠的森林打倒了一隻飢餓的野熊!",70), ("🦍你在巨大的瀑布下好不容易打倒了一隻強大的猩猩!",190), ("🐒你在奇怪的山丘擊敗了一群正在吃香蕉的猴子!",99),("🦄你在彩虹的盡頭千辛萬苦拔下了獨角獸的角!",1500)],[("你什麼也沒釣到!",0),("🐟你在小溪釣到了一隻淡水魚!",10),("🦐你在港口邊釣到了一隻蝦子!",30),("🦀你在海邊釣到了一隻螃蟹!",80),("🦑你在遠洋漁船上捕到了一隻特大魷魚!",240),("🦞你在遠洋漁船上捕到了一隻龍蝦!",500)],[("🐓💥你被一群發狂的雞攻擊!",-10),("🦄⚡你被獨角獸電擊!",-20),("☄💥你被隕石打到!",-50)]]

    purpose = purpose_list[event]
    evt = event_list[event]
    choice = random.choice(evt)   

    res = await self.update_wallet(ctx.author, choice[1])
    if res == 0:
      return await ctx.send("因為找不到你的帳戶, 已經為你自動創建, 請重新使用本指令")
    if event != 3:
      await ctx.send(f"{purpose}{choice[0]}\n賺到了{choice[1]}:coin:")
    else:
      return await ctx.send(f"{purpose}{choice[0]}\n失去了{choice[1]  * -1}:coin:")

  @economy.command()
  @commands.cooldown(1,5,commands.BucketType.user)
  async def withdraw(self, ctx:commands.Context, amount):
    """從銀行帳戶提款, amount輸入 max 提出所有錢"""
    wallet, bank, maxbank = await self.get_balance(ctx.author)
    
    if type(amount) == str and amount.lower() == "max":
      amount = int(bank)
    else:
      try:
        amount = int(amount)
        if amount < 0 :raise ValueError()
        if amount > int(bank): return await ctx.send("你的帳戶沒有這麼多錢!")
      except ValueError:
        return await ctx.send("請輸入正常的金額")

    bank_res = await self.update_bank(ctx.author, -1*amount)
    wallet_res = await self.update_wallet(ctx.author, amount)
    if bank_res == 0 or wallet_res == 0:
      return await ctx.send("因為找不到你的帳戶, 已經為你自動創建, 請重新使用本指令")

    wallet, bank, maxbank = await self.get_balance(ctx.author)
    em = discord.Embed(title = f"{ctx.author.name} 已從銀行領出 {amount}:coin:", description=f"👛錢包: :coin: {wallet}\n\n🏦存款: :coin: {bank}", color = discord.Color.green())
    em.set_footer(text = "經濟系統•帳戶資訊", icon_url=settings.avatar)
    await ctx.send(embed = em)
  
  @economy.command()
  @commands.cooldown(1,5,commands.BucketType.user)
  async def deposit(self, ctx:commands.Context, amount):
    """存錢到銀行帳戶, amount輸入 max 存入所有錢"""
    wallet, bank, maxbank = await self.get_balance(ctx.author)
    
    if type(amount) == str and amount.lower() == "max":
      amount = int(wallet)
    else:
      try:
        amount = int(amount)
        if amount < 0 :raise ValueError()
        if amount > int(wallet): return await ctx.send("你的錢包沒有這麼多錢!")
      except ValueError:
        return await ctx.send("請輸入正常的金額")

    bank_res = await self.update_bank(ctx.author, amount)
    wallet_res = await self.update_wallet(ctx.author, -1*amount)
    if bank_res == 0 or wallet_res == 0:
      return await ctx.send("因為找不到你的帳戶, 已經為你自動創建, 請重新使用本指令")
    elif bank_res == 1:
      return await ctx.send("你的銀行存款已達上限!")

    wallet, bank, maxbank = await self.get_balance(ctx.author)
    em = discord.Embed(title = f"{ctx.author.name} 已存入 {amount}:coin: 到銀行存款", description=f"👛錢包: :coin: {wallet}\n\n🏦存款: :coin: {bank}", color = discord.Color.green())
    em.set_footer(text = "經濟系統•帳戶資訊", icon_url=settings.avatar)
    await ctx.send(embed = em)
    
  @economy.command()
  async def give(self, ctx:commands.Context, member:discord.Member, amount):
    """給某人錢, amount輸入 max 給出錢包所有錢"""
    wallet, bank, maxbank = await self.get_balance(ctx.author)
    async with self.db.cursor() as cursor:
      await cursor.execute("SELECT wallet, bank, maxbank FROM bank WHERE user = ?", (member.id,))
      data = await cursor.fetchone()
      if not data: return await ctx.send(f"{member.name} 並沒有帳戶!")

    if type(amount) == str and amount.lower() == "max":
      amount = int(wallet)
    else:
      try:
        amount = int(amount)
        if amount < 0 :raise ValueError()
        if amount > int(wallet): return await ctx.send("你的錢包沒有這麼多錢!")
      except ValueError:
        return await ctx.send("請輸入正常的金額")

    self_res = await self.update_wallet(ctx.author, -1*amount)
    target_res = await self.update_wallet(member, amount)
    if self_res == 0:
      return await ctx.send("因為找不到你的帳戶, 已經為你自動創建, 請重新使用本指令")

    wallet, bank, maxbank = await self.get_balance(ctx.author)
    tarwallet, tarbank, tarmaxbank = await self.get_balance(member)
    em = discord.Embed(title = f"{ctx.author.name} 匯了 {amount}:coin: 給{member.name}", color = discord.Color.green())
    em.add_field(name = f"{ctx.author.name} 的帳戶",value = f"👛錢包: :coin: {wallet}\n\n🏦存款: :coin: {bank}", inline = False)
    em.add_field(name = f"{member.name} 的帳戶",value = f"👛錢包: :coin: {tarwallet}\n\n🏦存款: :coin: {tarbank}", inline = False)
    em.set_footer(text = "經濟系統•帳戶資訊", icon_url=settings.avatar)
    await ctx.send(embed = em)
  
  @economy.command()
  async def slot(self,ctx:commands.Context):
    """吃角子老虎機, 每次遊玩必須花1000元"""
    wallet, bank, maxbank = await self.get_balance(ctx.author)
    if int(wallet) < 1000:
      return await ctx.send("錢包的錢不足!遊玩一次必須花費 1000 :coin:")
    await self.update_wallet(ctx.author, -1000)
    reward = await slot.start(ctx,1)
    if reward == 0:
      reward = await slot.start(ctx,2)
    await self.update_wallet(ctx.author, reward)
    await ctx.send(f"{ctx.author.name}獲得了 {reward} :coin: !")
  
  @economy.group()
  async def shop(self, ctx:commands.Context):
    pass

  @shop.command()
  @commands.cooldown(1,10,commands.BucketType.user)
  async def show(self, ctx:commands.Context):
    embed = discord.Embed(name = "商店", color = discord.Color.dark_gray())
    async with self.db.cursor() as cursor:
      await cursor.execute("SELECT name, desc, cost FROM shop")
      shop = await cursor.fetchall()
      for item in shop:
        embed.add_field(name = item[0], value = f"{item[1]} \n\n價錢: {item[2]} :coin:", inline = False)
      await ctx.send(embed = embed, view = ShopView(self))

  @commands.command()
  @commands.is_owner()
  async def add_balance(self, ctx:commands.Context, user:discord.Member, amount:int):
    await self.update_wallet(user, amount)
    await ctx.send(f"{user}'s money amount has been changed", delete_after=2)

  @commands.command()
  async def add_inv(self, ctx:commands.Context, name:str):
    await self.update_inv(name)
    await ctx.send(f"New Item Updated", delete_after=2)
  
  @commands.command()
  @commands.is_owner()
  async def add_items(self, ctx:commands.Context, name:str, id:str, desc:str, cost:int):
    await self.update_shop(name, id, desc, cost)
    await ctx.send(f"Item Added", delete_after=2)

  async def create_balance(self, user):
    async with self.db.cursor() as cursor:
      await cursor.execute("INSERT INTO bank VALUES(?, ?, ?, ?)", (0, 100, 999999999, user.id))
    await self.db.commit()
    return
  
  async def create_inv(self, user):
    async with self.db.cursor() as cursor:
      await cursor.execute("INSERT INTO inv VALUES(?, ?, ?, ?)", (0, 0, 0, user.id))
    await self.db.commit()
    return
  
  async def get_balance(self, user):
    async with self.db.cursor() as cursor:
      await cursor.execute("SELECT wallet, bank, maxbank FROM bank WHERE user = ?", (user.id,))
      data = await cursor.fetchone()
      if not data: #if didn't find  create a new one
        await self.create_balance(user)
        return 0, 100, 999999999
      wallet, bank, maxbank = data[0], data[1], data[2]
      return wallet, bank, maxbank

  async def get_inv(self, user):
    async with self.db.cursor() as cursor:
      await cursor.execute("SELECT laptop, phone, fakeid FROM inv WHERE user = ?", (user.id,))
      data = await cursor.fetchone()
      if not data: #if didn't find  create a new one
        await self.create_inv(user)
        return 0, 0, 0
      laptop, phone, fakeid = data[0], data[1], data[2]
      return laptop, phone, fakeid

  async def update_wallet(self, user, amount: int):
    async with self.db.cursor() as cursor:
      await cursor.execute("SELECT wallet FROM bank WHERE user = ?", (user.id,))
      data = await cursor.fetchone()
      if not data: #if didn't find  create a new one
        await self.create_balance(user)
        return 0 #The balance hasn't been created

      change = data[0] + amount
      if change < 0: change = 0
      await cursor.execute("UPDATE bank SET wallet = ? WHERE user = ?", (change, user.id))
    await self.db.commit()
  
  async def update_bank(self, user, amount):
    async with self.db.cursor() as cursor:
      await cursor.execute("SELECT wallet, bank, maxbank FROM bank WHERE user = ?", (user.id,))
      data = await cursor.fetchone()
      if not data: #if didn't find, create a new one
        await self.create_balance(user)
        return 0 #The balance hasn't been created
      capacity = int(data[2] - data[1])
      if amount > capacity:
        await self.update_wallet(user, amount)
        return 1 #less of capacity
      change = data[1] + amount
      if change < 0: change = 0
      await cursor.execute("UPDATE bank SET bank = ? WHERE user = ?", (change, user.id))
    await self.db.commit()
  
  async def update_inv(self, name:str):
    async with self.db.cursor() as cursor:
      await cursor.execute("AFTER TABLE inv ADD ?", (name,))
    await self.db.commit()
    return

  async def update_shop(self, name:str, id:str, desc:str, cost:int):
    async with self.db.cursor() as cursor:
      await cursor.execute("INSERT INTO shop VALUES(?, ?, ?, ?)", (name, id, desc, cost))
    await self.db.commit()
    return

class ShopView(discord.ui.View):
  def __init__(self, cog:economy):
    super().__init__(timeout=120)
    self.cog = cog

  @discord.ui.button(label = "⮞", style=discord.ButtonStyle.blurple, custom_id="right")
  async def right(self, button:discord.ui.Button, interaction:discord.Interaction):
    pass

  @discord.ui.button(label = "⮜", style=discord.ButtonStyle.blurple, custom_id="left")
  async def left(self, button:discord.ui.Button, interaction:discord.Interaction):
    pass

  async def purchase(self, button:discord.ui.Button, interaction:discord.Interaction):
    async with self.cog.db.cursor() as cursor:
      await cursor.execute("SELECT laptop FROM inv WHERE user = ?", (interaction.user.id,))
      item = await cursor.fetchone()
      if item is None:
        await cursor.execute("INSERT INTO inv VALUES (?, ?, ?, ?)", (1, 0, 0, interaction.user.id))
      else:
        await cursor.execute("UPDATE inv SET laptop = ? WHERE user = ?", (item[0]+1, interaction.user.id,))
    await self.cog.db.commit()

async def setup(bot):
  economyBot = economy(bot)
  await economyBot.setup_db()
  await bot.add_cog(economyBot)