import discord
import requests
import pymssql
from discord.ext import commands
from datetime import datetime
from config import settings, emojis

class Eggs:
  '''Cog for easter egg commands (guess away)'''
  def __init__(self, bot):
    self.bot = bot

  @commands.command(name=server)
  async def server_list(self, ctx):
    list_names = []
    for guild in self.bot.guilds:
      list_names.append(guild.name)
      await ctx.send(list_names)

  @commands.command(name='colors', aliases=['colours','color','colour'], hidden=True)
  async def colors(self, ctx):
    botLog(ctx.command,ctx.author)
    content = "The following commands give you the respective colour:\n"
    content += "\n**!holipink**"
    content += "\n**!holired**"
    content += "\n**!holiorange**"
    content += "\n**!holiyellow**"
    content += "\n**!holigreen**"
    content += "\n**!holiteal**"
    content += "\n**!holiblue**"
    content += "\n**!holipurple**"
    await ctx.send(content)

  @commands.command(name='dmtest', hidden=True)
  async def dmtest(self, ctx):
    botLog(ctx.command,ctx.author)
    await ctx.author.send(ctx.channel)

  @commands.command(name='testing', hidden=True)
  async def testing(self, ctx):
    botLog(ctx.command,ctx.author)
    bk = 33
    aq = 22
    th = 10
    await ctx.send('{} {} {} {} {}TubaToo'.format(emojis['th'][th], emojis['level'][bk], emojis['level'][aq], emojis['other']['gap'], emojis['other']['gap']))

  @commands.command(name='zag', aliases=['zag-geek','zaggeek'], hidden=True)
  async def zag(self, ctx):
    botLog(ctx.command,ctx.author)
    await ctx.send(file=discord.File('/home/tuba/bot/cogs/zag.jpg'))

  @commands.command(name='tuba', hidden=True)
  async def tuba(self, ctx):
    botLog(ctx.command,ctx.author)
    await ctx.send(file=discord.File('/home/tuba/bot/cogs/tuba.jpg'))

  @commands.command(name='password', hidden=True)
  async def password(self, ctx):
    content = 'https://www.reddit.com/r/RedditClansHistory/wiki/the_history_of_the_reddit_clans#wiki_please_find_the_password'
    botLog(ctx.command,ctx.author)
    await ctx.send(content)

  @commands.command(name='cats', aliases=['cat'], hidden=True)
  async def kitty(self, ctx):
    url = 'https://api.thecatapi.com/v1/images/search'
    headers = {
      'Content-Type': 'application/json',
      'x-api-key': settings['api']['catKey']
    }
    r = requests.get(url, headers=headers)
    data = r.json()
    content = data[0]['url']
    botLog(ctx.command,ctx.author)
    await ctx.send(content)

  @commands.command(name='dogs', aliases=['dog'], hidden=True)
  async def puppy(self, ctx):
    url = 'https://api.thedogapi.com/v1/images/search'
    headers = {
      'Content-Type': 'application/json',
      'x-api-key': settings['api']['dogKey']
    }
    r = requests.get(url, headers=headers)
    data = r.json()
    content = data[0]['url']
    botLog(ctx.command,ctx.author)
    await ctx.send(content)

def botLog(command, author, errFlag=0):
  msg = str(datetime.now())[:16] + ' - '
  if errFlag == 0:
    msg += 'Printing {}. Requested by {}.'.format(command, author)
  else:
    msg += 'ERROR: User provided an incorrect argument for {}. Requested by {}.'.format(command, author)
  print(msg)

def setup(bot):
  bot.add_cog(Eggs(bot))
