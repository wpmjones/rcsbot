import coc

from discord.ext import commands, tasks
from cogs.utils.season import get_season_end, update_season
from coc import utils
from datetime import date, datetime
from dateutil.relativedelta import relativedelta, MO


class SeasonConfig(commands.Cog, command_attrs=dict(hidden=True)):
    def __init__(self, bot):
        self.bot = bot
        # self.start_new_season.start()
        self.bot.coc.add_events(self.coc_new_season)

    def cog_unload(self):
        # self.start_new_season.cancel()
        self.bot.coc.remove_events(self.coc_new_season)

    @staticmethod
    def next_last_monday():
        now = date.today()
        if now.month >= 11:
            new_month = now.month - 10
            new_year = now.year + 1
        else:
            new_month = now.month + 2
            new_year = now.year
        day = now + relativedelta(year=new_year, month=new_month, day=1, weekday=MO(-1))
        return day

    # @tasks.loop(minutes=15.0)
    # async def start_new_season(self):
    #     now = datetime.utcnow()
    #     season_end = get_season_end()
    #     end = datetime(year=int(season_end[:4]), month=int(season_end[5:7]), day=int(season_end[-2:]), hour=5)
    #     self.bot.logger.debug(f"\nCurrent time: {now}\nSeason end: {season_end}\nend: {end}\n"
    #                           f"Next Monday: {self.next_last_monday()}")
    #     if now > end:
    #         update_season(self.next_last_monday())

    @coc.ClientEvents.new_season_start()
    async def coc_new_season(self):
        """Just testing new_season_start"""
        self.bot.logger.info(f"coc has detected a new season\n"
                             f"{utils.get_season_start()}\n"
                             f"{utils.get_season_end()}")
        update_season(utils.get_season_start(), utils.get_season_end())


def setup(bot):
    bot.add_cog(SeasonConfig(bot))
