import schedule
import time
from discord.ext import commands
from config import settings


class WarStatus(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def run_task(self):
        print("begin schedule")
        try:
            schedule.every(5).minutes.do(await self.war_report())
        except:
            print("schedule failed")

        while True:
            schedule.run_pending()
            time.sleep(1)

    async def war_report(self):
        """ For reporting wars to RCS war-updates channel """
        print("Started war_report")
        await self.bot.wait_until_ready()
        channel = self.bot.get_channel(settings['oakChannels']['testChat'])
        clan_list = ["#CVCJR89", "#2UUCUJL"]
        for clan in clan_list:
            print(f"Starting {clan}")
            war = await self.bot.coc_client.get_current_war(clan)
            print(f"{war.clan.name} is currently {war.state}.")
            await channel.send(f"{war.clan.name} is currently {war.state}.")


def setup(bot):
    n = WarStatus(bot)
    bot.add_cog(n)
    bot.loop.create_task(n.run_task())
