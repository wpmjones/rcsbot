import coc

from nextcord.ext import commands
from datetime import datetime


class SeasonConfig(commands.Cog, command_attrs=dict(hidden=True)):
    def __init__(self, bot):
        self.bot = bot
        self.bot.coc.add_events(self.coc_new_season)

    def cog_unload(self):
        self.bot.coc.remove_events(self.coc_new_season)

    @coc.ClientEvents.new_season_start()
    async def coc_new_season(self):
        """Just testing new_season_start"""
        season_start = coc.utils.get_season_start()
        season_end = coc.utils.get_season_end()
        self.bot.logger.info(f"coc has detected a new season\n"
                             f"{season_start}\n"
                             f"{season_end}")
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
                   "VALUES ($1, $2, $3, $4, $5)")
            await self.bot.pool.execute(sql, 1, games_start, games_end, player_points, clan_points)
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
                   "VALUES ($1, $2, $3, $4")
            await self.bot.pool.execute(sql, 2, cwl_start, cwl_end, cwl_season)
        except:
            self.bot.logger.exception("Add CWL failed")
        self.bot.logger.info("New season process complete.")


def setup(bot):
    bot.add_cog(SeasonConfig(bot))
