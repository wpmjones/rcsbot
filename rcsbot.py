import discord, requests, pymssql, sys, traceback
from discord.ext import commands
from config import settings
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info('Starting bot')

description = '''Multi bot to serve the RCS - by TubaKid

For most commands, you will need to include a clan name or tag.

You can use the clan tag (with or without the hashtag) or you can use the clan name (spelling is kind of important).

There are easter eggs. Feel free to try and find them!'''

bot = commands.Bot(command_prefix='++', description=description, case_insensitive=True)
bot.remove_command('help')

@bot.event
async def on_ready():
  print('-------')
  print('Logged in as {0.user}'.format(bot))
  print('-------')

initialExtensions = ['cogs.general','cogs.push', 'cogs.games', 'cogs.cwl', 'cogs.newhelp', 'cogs.council', 'cogs.owner', 'cogs.eggs']

if __name__ == '__main__':
  for extension in initialExtensions:
    try:
      bot.load_extension(extension)
    except Exception as e:
      print('Failed to load extension {}'.format(extension), file=sys.stderr)
      traceback.print_exc()

bot.run(settings['discord']['rcsbotToken'])
