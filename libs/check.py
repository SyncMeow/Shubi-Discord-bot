import discord
from discord.ext import commands
import json

def predicate(ctx:commands.Context):
  with open('setting.json', 'r', encoding='utf8') as jfile:
    jdata = json.load(jfile)
  return ctx.message.author.id == jdata['Owner_id'] or ctx.message.author.id in jdata['Valid_User']

def valid_user():
	return commands.check(predicate)