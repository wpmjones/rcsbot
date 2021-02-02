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
        season_start = utils.get_season_start()
        season_end = utils.get_season_end()
        self.bot.logger.info(f"coc has detected a new season\n"
                             f"{season_start}\n"
                             f"{season_end}")
        update_season(season_start, season_end)
        # Add next games
        season_month = season_end.month
        season_year = season_end.year
        try:
            games_start = datetime(season_year, season_month, 22, 8, 0, 0)
            games_end = datetime(season_year, season_month, 28, 8, 0, 0)
            if season_month != 8:
                player_points = 4000
                clan_points = 50000
            else:
                player_points = 5000
                clan_points = 75000
            sql = ("INSERT INTO rcs_events (event_type, start_time, end_time, player_points, clan_points) "
                   "VALUES (1, $1, $2, $3, $4)")
            await self.bot.pool.execute(sql, games_start, games_end, player_points, clan_points)
        except:
            self.bot.logger.exception("Add games failed")
        # add next CWL
        try:
            cwl_start = datetime(season_year, season_month, 1, 3, 0, 0)
            cwl_end = datetime(season_year, season_month, 10, 3, 0, 0)
            if len(str(season_month)) == 1:
                season_month = f"0{str(season_month)}"
            else:
                season_month = str(season_month)
            cwl_season = f"{season_year}-{season_month}"
            sql = ("INSERT INTO rcs_events (event_type, start_time, end_time, season) "
                   "VALUES (2, $1, $2, $3")
            await self.bot.pool.execute(sql, cwl_start, cwl_end, cwl_season)
        except:
            self.bot.logger.exception("Add CWL failed")


def setup(bot):
    bot.add_cog(SeasonConfig(bot))
