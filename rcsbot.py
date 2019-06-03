import traceback
import os
import git
import coc
import asyncio
from discord.ext import commands
from config import settings
from rcsdb import RcsDB
from loguru import logger

enviro = "LIVE"

if enviro == "LIVE":
    token = settings['discord']['rcsbotToken']
    prefix = "++"
    log_level = "INFO"
    coc_names = "vps"
else:
    token = settings['discord']['testToken']
    prefix = ">"
    log_level = "DEBUG"
    coc_names = "dev"

logger.add("rcsbot.log", rotation="100MB", level=log_level)
logger.info("Starting bot")

description = """Multi bot to serve the RCS - by TubaKid

For most commands, you will need to include a clan name or tag.

You can use the clan tag (with or without the hashtag) or you can use the clan name (spelling is kind of important).

There are easter eggs. Feel free to try and find them!"""

bot = commands.Bot(command_prefix=prefix, description=description, case_insensitive=True)
bot.remove_command("help")
bot.repo = git.Repo(os.getcwd())


@bot.event
async def on_ready():
    logger.info("-------")
    logger.info(f"Logged in as {bot.user}")
    logger.info("-------")
    channel = bot.get_channel(settings['oakChannels']['testChat'])
    await channel.send("RCS bot has started")


initialExtensions = ["cogs.general",
                     "cogs.background",
                     "cogs.push",
                     "cogs.games",
                     "cogs.newhelp",
                     "cogs.council",
                     "cogs.owner",
                     "cogs.eggs"]

if __name__ == "__main__":
    for extension in initialExtensions:
        try:
            bot.load_extension(extension)
            logger.debug(f"{extension} loaded successfully")
        except Exception as e:
            logger.info(f"Failed to load extension {extension}")
            traceback.print_exc()

bot.db = RcsDB(bot)
loop = asyncio.get_event_loop()
pool = loop.run_until_complete(bot.db.create_pool())
bot.db.pool = pool
bot.logger = logger
bot.coc_client = coc.login(settings['supercell']['user'], settings['supercell']['pass'], key_names=coc_names)
bot.run(token)
