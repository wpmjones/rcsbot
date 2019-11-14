import discord
import traceback
import os
import git
import coc
import sys
import aiohttp
import asyncio

from discord.ext import commands
from cogs.utils import context, category
from cogs.utils.db import Psql
from cogs.utils.helper import rcs_names_tags, get_active_wars
from datetime import datetime
from config import settings
from loguru import logger

enviro = "LIVE"

if enviro == "LIVE":
    token = settings['discord']['rcsbot_token']
    prefix = "++"
    log_level = "INFO"
    coc_names = "vps"
    initial_extensions = ["cogs.admin",
                          "cogs.council",
                          "cogs.eggs",
                          "cogs.games",
                          "cogs.general",
                          "cogs.newhelp",
                          "cogs.owner",
                          "cogs.push",
                          "cogs.tasks",
                          ]
elif enviro == "home":
    token = settings['discord']['test_token']
    prefix = ">"
    log_level = "DEBUG"
    coc_names = "ubuntu"
    initial_extensions = ["cogs.admin",
                          "cogs.council",
                          "cogs.eggs",
                          "cogs.games",
                          "cogs.general",
                          "cogs.newhelp",
                          "cogs.owner",
                          "cogs.push",
                          "cogs.tasks",
                          "cogs.warstatus",
                          ]
else:
    token = settings['discord']['test_token']
    prefix = ">"
    log_level = "DEBUG"
    coc_names = "dev"
    initial_extensions = ["cogs.admin",
                          "cogs.council",
                          "cogs.eggs",
                          "cogs.games",
                          "cogs.general",
                          "cogs.newhelp",
                          "cogs.owner",
                          "cogs.push",
                          "cogs.tasks",
                          ]

description = """Multi bot to serve the RCS - by TubaKid

For most commands, you will need to include a clan name or tag.

You can use the clan tag (with or without the hashtag) or you can use the clan name (spelling is kind of important).

There are easter eggs. Feel free to try and find them!"""

coc_client = coc.login(settings['supercell']['user'],
                       settings['supercell']['pass'],
                       client=coc.EventsClient,
                       key_names=coc_names,
                       correct_tags=True)


class RcsBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=prefix,
                         description=description,
                         case_insensitive=True)
        self.remove_command("help")
        self.coc = coc_client
        self.logger = logger
        self.rcs_names_tags = rcs_names_tags()
        self.color = discord.Color.dark_red()
        self.client_id = settings['discord']['rcs_client_id']
        self.messages = {}
        self.categories = {}
        self.active_wars = get_active_wars()
        self.session = aiohttp.ClientSession(loop=self.loop)

        coc_client.add_events(self.on_event_error)

        for extension in initial_extensions:
            try:
                self.load_extension(extension)
                self.logger.debug(f"{extension} loaded successfully")
            except Exception as extension:
                self.logger.error(f"Failed to load extension {extension}.", file=sys.stderr)
                traceback.print_exc()

    @property
    def log_channel(self):
        return self.get_channel(settings['log_channels']['rcs'])

    async def send_message(self, message):
        if len(message) < 2000:
            await self.log_channel.send(f"`{message}`")
        else:
            await self.log_channel.send(f"`{message[:1950]}`")

    def send_log(self, message):
        asyncio.ensure_future(self.send_message(message))

    def get_category(self, name) -> category.Category:
        return self.categories.get(name)

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
                self.logger.error(f"In {ctx.command.qualified_name}:", file=sys.stderr)
                traceback.print_tb(original.__traceback__)
                self.logger.error(f"{original.__class__.__name__}: {original}", file=sys.stderr)
        elif isinstance(error, commands.ArgumentParsingError):
            await ctx.send(error)

    async def on_event_error(self, event_name, *args, **kwargs):
        embed = discord.Embed(title="COC Event Error", colour=0xa32952)
        embed.add_field(name="Event", value=event_name)
        embed.description = f"```py\n{traceback.format_exc()}\n```"
        embed.timestamp = datetime.utcnow()

        args_str = ["```py"]
        for index, arg in enumerate(args):
            args_str.append(f"[{index}]: {arg!r}")
        args_str.append("```")
        embed.add_field(name="Args", value="\n".join(args_str), inline=False)
        try:
            event_channel = self.get_channel(settings['log_channels']['events'])
            await event_channel.send(embed=embed)
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
        logger.info("rcs-bot has started")
        activity = discord.Game("Clash of Clans")
        await self.change_presence(status=discord.Status.online, activity=activity)
        self.logger.info(f'Ready: {self.user} (ID: {self.user.id})')

    async def close(self):
        await super().close()
        await self.coc.close()

    async def after_ready(self):
        await bot.wait_until_ready()
        logger.add(self.send_log, level=log_level)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        # pool = loop.run_until_complete(Psql.create_pool())
        bot = RcsBot()
        bot.repo = git.Repo(os.getcwd())
        # bot.pool = pool
        bot.loop = loop
        bot.run(token, reconnect=True)
    except:
        traceback.print_exc()