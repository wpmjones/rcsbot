import csv

from discord.ext import commands, tasks
from datetime import time, datetime
from dateutil import relativedelta
from cogs.utils.season import get_season_end


class SeasonConfig(commands.Cog, command_attrs=dict(hidden=True)):
    def __init__(self, bot):
        self.bot = bot
        self.start_new_season.start()

    def cog_unload(self):
        self.start_new_season.cancel()

    @staticmethod
    def next_last_monday():
        now = datetime.utcnow()
        day = now + relativedelta.relativedelta(month=now.month + 1,
                                                weekday=relativedelta.MO(-1))
        day.replace(hour=6, minute=0, second=0, microsecond=0)
        return day

    @tasks.loop(time=time(hour=6))
    async def start_new_season(self):
        now = datetime.utcnow()
        next_monday = self.next_last_monday()

        if now.day != next_monday.day:
            return

        await self.new_season()

    async def new_season(self):
        new_start_date = get_season_end()
        with open("/home/tuba/season.csv", "w") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(["start", "end"])
            writer.writerow([new_start_date, self.next_last_monday()])
        return "success"


def setup(bot):
    bot.add_cog(SeasonConfig(bot))
