import asyncpg
from loguru import logger
from discord.ext import commands
from datetime import datetime, timedelta
from random import randint
from config import settings

# logger.add("general.log", rotation="100MB",
#            format="{time:YYYY-MM-DD HH:mm:ss} {level} {message}", level="INFO")


class Background(commands.Cog):
    """Cog for background tasks. No real commands here."""
    def __init__(self, bot):
        self.bot = bot

    def is_rcs(ctx):
        return ctx.guild.id == int(settings['discord']['rcsGuildId'])

    @commands.Cog.listener()
    @commands.check(is_rcs)
    async def on_message(self, message):
        if message.author == self.bot.user:
            return
        if settings['rcsRoles']['members'] not in message.author.roles:
            return
        logger.debug("User has member role.")
        conn = await asyncpg.connect(user=settings['pg']['user'],
                                     password=settings['pg']['pass'],
                                     host=settings['pg']['host'],
                                     database=settings['pg']['db'])
        logger.debug("Postgresql connection established.")
        row = await conn.fetchrow(f"SELECT * FROM rcs_discord WHERE discord_id = {message.author.id}")
        logger.debug(row)
        points = randint(7, 14)
        if row:
            if datetime.now() > row['last_message'] + timedelta(minutes=1):
                await conn.execute(f"UPDATE rcs_discord "
                                   f"SET message_points = {row['message_points']+points}, "
                                   f"last_message = '{datetime.now()}' "
                                   f"WHERE discord_id = {message.author.id}")
                logger.info("{} receives {} for their message", message.author.display_name, points)
            else:
                logger.debug("User posted within the last minute. No points awarded.")
        else:
            await conn.execute(f"INSERT INTO rcs_discord "
                               f"VALUES ({message.author.id}, {points}, 0, '{datetime.now()}')")
            logger.info("Added {} to the rcs_discord table for message tracking", message.author.display_name)


def setup(bot):
    bot.add_cog(Background(bot))
