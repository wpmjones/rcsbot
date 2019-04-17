import coc
import discord
import asyncio
from discord.ext import commands
from config import settings


class warStatus:
    def __init__(self, bot):
        self.bot = bot

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

    self.bot.loop.create_task(war_report())


def setup(bot):
    bot.add_cog(warStatus(bot))

