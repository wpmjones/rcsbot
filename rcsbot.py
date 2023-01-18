import asyncpg
import nextcord
import traceback
import coc
import sys
import aiohttp
import asyncio

from nextcord.ext import commands
from nextcord.ext.commands import errors
from coc.ext import discordlinks
from cogs.utils import context
from cogs.utils.constants import bot_guilds
from cogs.utils.helper import get_active_wars, rcs_tags
from cogs.utils.error_handler import discord_event_error
from config import settings
from loguru import logger

enviro = settings['enviro']

if enviro == "LIVE":
    token = settings['discord']['rcsbot_token']
    prefix = "++"
    log_level = "INFO"
    coc_names = "galaxy"
    coc_email = settings['supercell']['user']
    coc_pass = settings['supercell']['pass']
    guild_ids = bot_guilds
    initial_extensions = ["cogs.admin",
                          "cogs.background",
                          "cogs.bg_sheets",
                          "cogs.council",
                          "cogs.discordcheck",
                          "cogs.draft",
                          "cogs.eggs",
                          "cogs.games",
                          "cogs.general",
                          "cogs.new_season",
                          "cogs.owner",
                          "cogs.plots",
                          "cogs.push",
                          "cogs.tasks",
                          "cogs.verify",
                          ]
elif enviro == "home":
    token = settings['discord']['test_token']
    prefix = ">"
    log_level = "DEBUG"
    coc_names = "ubuntu"
    coc_email = settings['supercell']['user2']
    coc_pass = settings['supercell']['pass2']
    guild_ids = [settings['discord']['botlogguild_id']]
    initial_extensions = ["cogs.admin",
                          "cogs.council",
                          "cogs.general",
                          "cogs.owner",
                          "cogs.push",
                          ]
else:
    token = settings['discord']['test_token']
    prefix = ">"
    log_level = "DEBUG"
    coc_names = "dev"
    coc_email = settings['supercell']['user2']
    coc_pass = settings['supercell']['pass2']
    guild_ids = [settings['discord']['botlogguild_id']]
    initial_extensions = ["cogs.admin",
                          "cogs.council",
                          "cogs.eggs",
                          "cogs.games",
                          "cogs.general",
                          "cogs.owner",
                          ]

description = """Multi bot to serve the RCS - by TubaKid

For most commands, you will need to include a clan name or tag.

You can use the clan tag (with or without the hashtag) or you can use the clan name (spelling is kind of important).

There are easter eggs. Feel free to try and find them!"""


# class COCClient(coc.EventsClient):
#     async def on_event_error(self, event_name, exception, *args, **kwargs):
#         await clash_event_error(self.bot, event_name, exception, *args, **kwargs)


coc_client = coc.login(coc_email,
                       coc_pass,
                       client=coc.EventsClient,
                       key_count=2,
                       key_names=coc_names,
                       throttle_limit=25,
                       correct_tags=True)

links_client = discordlinks.login(settings['links']['user'],
                                  settings['links']['pass'])

intents = nextcord.Intents.none()
intents.guilds = True
intents.guild_messages = True
intents.guild_reactions = True
intents.members = True
intents.emojis = True
intents.message_content = True


class RcsBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=prefix,
                         description=description,
                         case_insensitive=True,
                         intents=intents,
                         default_guild_ids=guild_ids
                         )
        self.coc = coc_client
        self.links = links_client
        self.logger = logger
        self.color = nextcord.Color.dark_red()
        self.client_id = settings['discord']['rcs_client_id']
        self.messages = {}
        self.categories = {}
        self.active_wars = get_active_wars()
        self.session = None
        self.error_webhook = None
        self.pool = None
        if enviro == "LIVE":
            self.live = True
        else:
            self.live = False
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

    async def on_message(self, message):
        if message.author.bot:
            return
        await self.process_commands(message)

    async def get_context(self, message: nextcord.Message, *, cls=context.Context):
        return await super().get_context(message, cls=cls)

    def get_interaction(self, data, *, cls=context.MyInteraction):
        return super().get_interaction(data, cls=cls)

    async def on_command_error(self, ctx, error):
        if isinstance(error, errors.CommandNotFound):
            return
        elif isinstance(error, errors.TooManyArguments):
            return await ctx.send("You are providing too many arguments!")
        elif isinstance(error, errors.BadArgument):
            return await ctx.send("The library ran into an error attempting to parse your argument.")
        elif isinstance(error, errors.MissingRequiredArgument):
            return await ctx.send("You're missing a required argument.")
        # kinda annoying and useless error.
        elif isinstance(error, nextcord.NotFound) and "Unknown interaction" in str(error):
            return
        elif isinstance(error, errors.MissingRole):
            role = ctx.guild.get_role(int(error.missing_role))  # type: ignore
            return await ctx.send(f'"{role.name}" is required to use this command.')  # type: ignore
        else:
            await ctx.send(f"This command raised an exception: `{type(error)}:{str(error)}`")

    async def on_error(self, event_method, *args, **kwargs):
        return await discord_event_error(self, event_method, *args, **kwargs)

    async def on_ready(self):
        activity = nextcord.Game("Clash of Clans")
        await self.change_presence(status=nextcord.Status.online, activity=activity)
        self.coc.add_clan_updates(*rcs_tags(prefix=True))

    async def after_ready(self):
        await self.wait_until_ready()
        self.session = aiohttp.ClientSession(loop=self.loop)
        logger.add(self.send_log, level=log_level)
        error_webhooks = await self.get_channel(settings['log_channels']['rcs']).webhooks()
        self.error_webhook = error_webhooks[0]
        self.pool = await asyncpg.create_pool(f"{settings['pg']['uri']}/tubadata")
        logger.info("Bot is now ready")


if __name__ == "__main__":
    # loop = asyncio.new_event_loop()
    # asyncio.set_event_loop(loop)
    try:
        # pool = loop.run_until_complete(Table.create_pool(f"{settings['pg']['uri']}/tubadata"))
        bot = RcsBot()
        # bot.pool = pool
        # bot.loop = loop
        bot.run(token, reconnect=True)
    except:
        traceback.print_exc()
