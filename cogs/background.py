import asyncpg
from discord.ext import commands
from datetime import datetime, timedelta
from random import randint
from config import settings, bot_log


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
        conn = await asyncpg.connect(user=settings['pg']['user'],
                                     password=settings['pg']['pass'],
                                     host=settings['pg']['host'],
                                     database=settings['pg']['db'])
        row = await conn.fetchrow(f"SELECT * FROM rcs_discord WHERE discord_id = {message.author.id}")
        points = randint(7, 14)
        if row:
            if datetime.now() > row['last_message'] + timedelta(minutes=1):
                print(row['last_message'])
                await conn.execute(f"UPDATE rcs_discord "
                                   f"SET message_points = {row['message_points']+points}, "
                                   f"last_message = {datetime.now()} "
                                   f"WHERE discord_id = {message.author.id}")
        else:
            await conn.execute(f"INSERT INTO rcs_discord "
                               f"VALUES ({message.author.id}, {points}, 0, {datetime.now()})")


def setup(bot):
    bot.add_cog(Background(bot))
