import coc
import discord
import asyncio
from config import settings


class WarStatus:
    def __init__(self, bot):
        self.bot = bot

    async def war_report(self):
        """ For reporting wars to RCS war-updates channel """
        await self.bot.wait_until_ready()
        count = 1
        channel = self.bot.get_channel(settings['oakChannels']['testChat'])
        while not self.bot.is_closed():
            seconds_until_post = 300
            print(f"Sleeping for {seconds_until_post/60} minutes.")
            await asyncio.sleep(seconds_until_post)

            print(f"Counter at {str(count)}")
            await channel.send(f"Counter at {str(count)}")
            count += 1


def setup(bot):
    c = WarStatus(bot)
    bot.add_cog(c)
    bot.loop.create_task(c.war_report())
