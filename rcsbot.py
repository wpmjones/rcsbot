import discord
import traceback
import coc
import sys
import aiohttp
import asyncio

from discord.ext import commands
from coc.ext import discordlinks
from cogs.utils import context, category
from cogs.utils.db import Table
from cogs.utils.error_handler import clash_event_error
from cogs.utils.helper import get_active_wars, rcs_tags
from datetime import datetime
from config import settings
from loguru import logger

enviro = "LIVE"

if enviro == "LIVE":
    token = settings['discord']['rcsbot_token']
    prefix = "++"
    log_level = "INFO"
    coc_names = "galaxy"
    coc_email = settings['supercell']['user']
    coc_pass = settings['supercell']['pass']
    initial_extensions = ["cogs.admin",
                          "cogs.archive",
                          "cogs.background",
                          "cogs.council",
                          "cogs.discordcheck",
                          "cogs.draft",
                          "cogs.eggs",
                          "cogs.games",
                          "cogs.general",
                          "cogs.newhelp",
                          "cogs.new_season",
                          "cogs.owner",
                          "cogs.plots",
                          "cogs.tasks",
                          ]
elif enviro == "home":
    token = settings['discord']['test_token']
    prefix = ">"
    log_level = "DEBUG"
    coc_names = "ubuntu"
    coc_email = settings['supercell']['user2']
    coc_pass = settings['supercell']['pass2']
    initial_extensions = ["cogs.admin",
                          "cogs.council",
                          "cogs.general",
                          "cogs.newhelp",
                          "cogs.owner",
                          "cogs.plots",
                          ]
else:
    token = settings['discord']['test_token']
    prefix = ">"
    log_level = "DEBUG"
    coc_names = "dev"
    coc_email = settings['supercell']['user2']
    coc_pass = settings['supercell']['pass2']
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


class COCClient(coc.EventsClient):
    async def on_event_error(self, event_name, exception, *args, **kwargs):
        await clash_event_error(self.bot, event_name, exception, *args, **kwargs)


coc_client = coc.login(coc_email,
                       coc_pass,
                       client=COCClient,
                       key_count=2,
                       key_names=coc_names,
                       throttle_limit=25,
                       correct_tags=True)

links_client = discordlinks.login(settings['links']['user'],
                                  settings['links']['pass'])

intents = discord.Intents.default()
intents.members = True


class RcsBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=prefix,
                         description=description,
                         case_insensitive=True,
                         intents=intents,
                         )
        self.remove_command("help")
        self.coc = coc_client
        self.links = links_client
        self.logger = logger
        self.color = discord.Color.dark_red()
        self.client_id = settings['discord']['rcs_client_id']
        self.messages = {}
        self.categories = {}
        self.active_wars = get_active_wars()
        self.session = aiohttp.ClientSession(loop=self.loop)
        self.loop.create_task(self.after_ready())

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
        else:
            await ctx.send(error)

    async def on_error(self, event_method, *args, **kwargs):
        e = discord.Embed(title="Discord Event Error", color=0xa32952)
        e.add_field(name="Event", value=event_method)
        e.description = f"```py\n{traceback.format_exc()}\n```"
        e.timestamp = datetime.utcnow()

        args_str = ["```py\n"]
        for index, arg in enumerate(args):
            args_str.append(f"[{index}]: {arg!r}")
        args_str.append("```")
        e.add_field(name="Args", value="\n".join(args_str), inline=False)
        try:
            await self.log_channel.send(embed=e)
        except:
            pass

    async def on_ready(self):
        activity = discord.Game("Clash of Clans")
        await self.change_presence(status=discord.Status.online, activity=activity)
        self.coc.add_clan_updates(*rcs_tags(prefix=True))

    async def close(self):
        await super().close()
        await self.coc.close()

    async def after_ready(self):
        await self.wait_until_ready()
        logger.add(self.send_log, level=log_level)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        pool = loop.run_until_complete(Table.create_pool(f"{settings['pg']['uri']}/tubadata"))
        bot = RcsBot()
        bot.pool = pool
        bot.loop = loop
        bot.run(token, reconnect=True)
    except:
        traceback.print_exc()
