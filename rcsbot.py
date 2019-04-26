import sys
import traceback
import os
import git
from discord.ext import commands
from config import settings
import logging
from datetime import datetime

logging.basicConfig(filename="rcsbot.log",
                    filemode="a",
                    level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info("Starting bot")

description = """Multi bot to serve the RCS - by TubaKid

For most commands, you will need to include a clan name or tag.

You can use the clan tag (with or without the hashtag) or you can use the clan name (spelling is kind of important).

There are easter eggs. Feel free to try and find them!"""

bot = commands.Bot(command_prefix="++", description=description, case_insensitive=True)
bot.remove_command("help")
bot.repo = git.Repo(os.getcwd())


@bot.event
async def on_ready():
    logger.info("-------")
    logger.info(f"Logged in as {bot.user}")
    logger.info("-------")


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
        except Exception as e:
            logger.info(f"Failed to load extension {extension}")
            traceback.print_exc()

bot.run(settings['discord']['rcsbotToken'])
