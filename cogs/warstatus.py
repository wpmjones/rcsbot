import coc
import discord
import asyncio
from config import settings


class WarStatus:
    def __init__(self, bot):
        self.bot = bot
        self.bot.loop.create_task(await self.war_report())

    async def war_report(self):
        count = 1
        channel = self.get_channel(settings['oakChannels']['testChat'])
        while True:
            seconds_until_post = 300
            print(f"Sleeping for {seconds_until_post/60} minutes.")
            await asyncio.sleep(seconds_until_post)

            print(f"Counter at {str(count)}")
            await channel.send(f"Counter at {str(count)}")
            count += 1


def setup(bot):
    bot.add_cog(WarStatus(bot))

