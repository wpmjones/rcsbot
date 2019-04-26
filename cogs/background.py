import asyncpg
from discord.ext import commands
from random import randint
from config import settings, bot_log


class Background:
    """Cog for background tasks. No real commands here."""
    def __init__(self, bot):
        self.bot = bot

    def is_rcs(ctx):
        return ctx.guild.id == int(settings['discord']['rcsGuildId'])

    @commands.Cog.listener()
    @commands.check(is_rcs)
    async def on_message(self, message):
        conn = await asyncpg.connect(user=settings['pg']['user'],
                                     password=settings['pg']['pass'],
                                     host="localhost",
                                     database=settings['pg']['db'])
        row = await conn.fetch(f"SELECT * FROM rcs_discord WHERE discord_id = {message.author.id}")
        points = randint(0, 15)
        if row:
            await conn.execute(f"UPDATE rcs_discord "
                               f"SET message_xp = {row['message_xp']+points} "
                               f"WHERE discord_id = {message.author.id}")
        else:
            await conn.execute(f"INSERT INTO rcs_discord "
                               f"VALUES ({message.author.id}, points, 0)")


def setup(bot):
    bot.add_cog(Background(bot))
