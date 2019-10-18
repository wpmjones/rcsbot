import traceback
import os
import git
import coc
import sys
import asyncio
import discord

from cogs.utils import context
from cogs.utils.db import RcsDB
from discord.ext import commands
from datetime import datetime
from config import settings
from loguru import logger

enviro = "LIVE"

if enviro == "LIVE":
    token = settings['discord']['rcsbotToken']
    prefix = "++"
    log_level = "INFO"
    coc_names = "vps"
    initial_extensions = ["cogs.general",
                          "cogs.push",
                          "cogs.background",
                          "cogs.discordcheck",
                          "cogs.games",
                          "cogs.newhelp",
                          "cogs.council",
                          "cogs.owner",
                          "cogs.pfp",
                          "cogs.admin",
                          "cogs.draft",
                          "cogs.tasks",
                          "cogs.eggs",
                          ]
elif enviro == "home":
    token = settings['discord']['testToken']
    prefix = ">"
    log_level = "DEBUG"
    coc_names = "ubuntu"
    initial_extensions = ["cogs.general",
                          "cogs.games",
                          "cogs.newhelp",
                          "cogs.council",
                          "cogs.eggs",
                          "cogs.owner",
                          "cogs.admin",
                          "cogs.draft",
                          ]
else:
    token = settings['discord']['testToken']
    prefix = ">"
    log_level = "DEBUG"
    coc_names = "dev"
    initial_extensions = ["cogs.general",
                          "cogs.games",
                          "cogs.discordcheck",
                          "cogs.newhelp",
                          "cogs.council",
                          "cogs.eggs",
                          "cogs.owner",
                          "cogs.admin",
                          "cogs.draft",
                          ]

description = """Multi bot to serve the RCS - by TubaKid

For most commands, you will need to include a clan name or tag.

You can use the clan tag (with or without the hashtag) or you can use the clan name (spelling is kind of important).

There are easter eggs. Feel free to try and find them!"""

coc_client = coc.login(settings['supercell']['user'],
                       settings['supercell']['pass'],
                       client=coc.EventsClient,
                       key_names=coc_names)


class RcsBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=prefix,
                         description=description,
                         case_insensitive=True)
        self.remove_command("help")
        self.coc = coc_client
        self.color = discord.Color.dark_red()
        self.messages = {}

        coc_client.add_events(self.on_event_error)

        for extension in initial_extensions:
            try:
                self.load_extension(extension)
                logger.debug(f"{extension} loaded successfully")
            except Exception as extension:
                logger.error(f"Failed to load extension {extension}.", file=sys.stderr)
                traceback.print_exc()

    @property
    def log_channel(self):
        return self.get_channel(settings['logChannels']['rcs'])

    def send_log(self, message):
        asyncio.ensure_future(self.send_message(message))

    async def send_message(self, message):
        if len(message) < 2000:
            await self.log_channel.send(f"`{message}`")
        else:
            await self.log_channel.send(f"`{message[:1950]}`")

    async def on_message(self, message):
        if message.author.bot:
            return
        await self.process_commands(message)

    async def on_message_delete(self, message):
        if message.id in self.messages:
            del_message = self.messages[message.id]
            await del_message.delete()
            del self.messages[message.id]

    async def process_commands(self, message):
        ctx = await self.get_context(message, cls=context.Context)
        if ctx.command is None:
            return
        async with ctx.acquire():
            await self.invoke(ctx)

    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.NoPrivateMessage):
            await ctx.author.send("This command cannot be used in private messages.")
        elif isinstance(error, commands.DisabledCommand):
            await ctx.author.send("Oops. This command is disabled and cannot be used.")
        elif isinstance(error, commands.CommandInvokeError):
            original = error.original
            if not isinstance(original, discord.HTTPException):
                logger.error(f"In {ctx.command.qualified_name}:", file=sys.stderr)
                traceback.print_tb(original.__traceback__)
                logger.error(f"{original.__class__.__name__}: {original}", file=sys.stderr)
        elif isinstance(error, commands.ArgumentParsingError):
            await ctx.send(error)

    async def on_event_error(self, event_name, *args, **kwargs):
        e = discord.Embed(title="COC Event Error", colour=0xa32952)
        e.add_field(name="Event", value=event_name)
        e.description = f"```py\n{traceback.format_exc()}\n```"
        e.timestamp = datetime.utcnow()

        args_str = ["```py"]
        for index, arg in enumerate(args):
            args_str.append(f"[{index}]: {arg!r}")
        args_str.append("```")
        e.add_field(name="Args", value="\n".join(args_str), inline=False)
        try:
            self.log_channel.send(embed=e)
        except:
            pass

    async def on_error(self, event_method, *args, **kwargs):
        e = discord.Embed(title="Discord Event Error", color=0xa32952)
        e.add_field(name="Event", value=event_method)
        e.description = f"```py\n{traceback.format_exc()}\n```"
        e.timestamp = datetime.utcnow()

        args_str = ["```py"]
        for index, arg in enumerate(args):
            args_str.append(f"[{index}]: {arg!r}")
        args_str.append("```")
        e.add_field(name="Args", value="\n".join(args_str), inline=False)
        try:
            await self.log_channel.send(embed=e)
        except:
            pass

    async def on_ready(self):
        logger.add(self.send_log, level=log_level)
        logger.info("rcs-bot has started")
        activity = discord.Game("Clash of Clans")
        await self.change_presence(status=discord.Status.online, activity=activity)
        logger.info(f'Ready: {self.user} (ID: {self.user.id})')

    async def on_resumed(self):
        logger.info("resumed...")

    async def close(self):
        await super().close()
        await self.coc.close()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        pool = loop.run_until_complete(RcsDB.create_pool())
        bot = RcsBot()
        bot.repo = git.Repo(os.getcwd())
        bot.pool = pool
        bot.logger = logger
        bot.run(token, reconnect=True)
    except:
        traceback.print_exc()
