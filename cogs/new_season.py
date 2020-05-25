import csv

from discord.ext import commands, tasks
from datetime import time, date
from dateutil import relativedelta


class SeasonConfig(commands.Cog, command_attrs=dict(hidden=True)):
    def __init__(self, bot):
        self.bot = bot
        self.start_new_season.start()

    def cog_unload(self):
        self.start_new_season.cancel()

    @staticmethod
    def next_last_monday():
        now = date.today()
        print(now.month + 1)
        day = now + relativedelta.relativedelta(month=now.month + 1,
                                                weekday=relativedelta.MO(1))
        return day

    @tasks.loop(time=time(hour=6))
    async def start_new_season(self):
        now = date.today()
        next_monday = self.next_last_monday()
        if now != next_monday:
            return
        await self.new_season()

    async def new_season(self):
        with open("/home/tuba/season.csv", "w") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(["start", "end"])
            writer.writerow([date.today(), self.next_last_monday()])
        return "success"


def setup(bot):
    bot.add_cog(SeasonConfig(bot))
