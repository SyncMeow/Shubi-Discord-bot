import discord
from discord.ext import commands
import random
import asyncio

async def start(ctx:commands.Context,times:int):
  msg = await ctx.send(f"{ctx.author.name} 花費了 1000 :coin: 遊玩一次吃角子老虎機")
  symbols = ["🍎","🍋","🍌","🍐","🍓","🍒","🍇","🔔",":seven:","🔄"]
  for i in range(30):
    img1 = random.choice(symbols)
    img2 = random.choice(symbols)
    img3 = random.choice(symbols)
    em = discord.Embed(title = f" ▁▁▁▁▁▁▁▁▁▁▁▁\n|  {img1}  |  {img2}  |  {img3}  |\n▔▔▔▔▔▔▔", color = discord.Color.dark_gold())
    await msg.edit(embed = em)
    await asyncio.sleep(0.05)

  reward = 0
  chance = random.randint(1,100)
  if chance in range(1,71):
    symbols = ["🍎","🍋","🍌","🍐","🍓","🍒","🍇","🔔"]
    imgs = []
    for i in range(3):
      img = random.choice(symbols)
      symbols.remove(img)
      imgs.append(img)
    reward = random.randint(1,8) * 100
  elif chance in range(71,96):
    symbols = ["🍎","🍋","🍌","🍐","🍓","🍒","🍇","🔔"]
    imgs = []
    for i in range(2):
      img = random.choice(symbols)
      symbols.remove(img)
      imgs.append(img)
    imgs.append(imgs[0])
    random.shuffle(imgs)
    reward = random.randint(12,21) * 100
  elif chance in range(96,101):
    t = random.randint(0,9) if times == 1 else random.randint(1,10)
    if t == 0:
      imgs = ["🔄","🔄","🔄"]
      await ctx.send("再來一次!")
      await asyncio.sleep(1)
      return 0
    elif t == 1:
      imgs = [":seven:",":seven:",":seven:"]
      reward = 7777
    else:
      img = random.choice(["🍎","🍋","🍌","🍐","🍓","🍒","🍇","🔔"])
      imgs = [img,img,img]
      reward = random.randint(30,35) * 100
  
  em = discord.Embed(title = f" ▁▁▁▁▁▁▁▁▁▁▁▁\n|  {imgs[0]}  |  {imgs[1]}  |  {imgs[2]}  |\n▔▔▔▔▔▔▔", color = discord.Color.gold())
  await msg.edit(embed = em) 
  await asyncio.sleep(0.8)
  return reward