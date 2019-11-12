import coc

from discord.ext import commands
from cogs.utils.helper import rcs_tags
from cogs.utils.db import Sql
from config import settings


class WarStatus(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.test_channel = self.bot.get_channel(settings['log_channels']['test'])
        self.war_channel = self.bot.get_channel(settings['rcs_channels']['war_updates'])

        self.active_wars = self.get_active_wars()

        self.bot.coc.add_events(self.on_war_state_change,
                                )
        self.bot.coc.add_war_update(rcs_tags(prefix=True))
        self.bot.coc.start_updates("war")

    def cog_unload(self):
        self.bot.coc.remove_events(self.on_war_state_change,
                                   )

    @staticmethod
    def get_active_wars():
        with Sql(as_dict=True) as cursor:
            sql = "SELECT '#' + clanTag as tag, war_id FROM rcs_wars WHERE warState <> 'warEnded'"
            cursor.execute(sql)
            fetch = cursor.fetchall()
        wars = {}
        for row in fetch:
            wars[row['tag']] = row['war_id']
        return wars

    # TODO Create command to pull old war logs into DB

    async def report_war(self, war):
        """Send war report to #rcs-war-updates"""
        # TODO Use PIL to create image of war report

        return None

    async def on_war_state_change(self, current_state, war):
        if isinstance(war, coc.LeagueWar):
            # I don't want to do anything with CWL wars
            return
        if current_state == "preparation":
            # TODO move add_war elsewhere, use it with inwar/warended if war not in table
            with Sql() as cursor:
                sql = ("INSERT INTO rcs_wars (clanTag, opponentTag, opponentName, teamSize, warState, endTime) "
                       "VALUES ('{}', '{}', N'{}', {}, '{}', '{}')")
                cursor.execute(sql, (war.clan.tag, war.opponent.tag, war.opponent.name, war.team_size,
                                     war.state, war.end_time.time))
                self.active_wars[war.clan.tag] = cursor.lastrowid()
            self.bot.logger.info(f"New war added to database for {war.clan.name} "
                                 f"(war_id: {self.active_wars[war.clan.tag]}).")
        if current_state == "inWar":
            with Sql() as cursor:
                sql = ("UPDATE rcs_wars "
                       "SET warState = 'inWar' "
                       "WHERE war_id = %d")
                cursor.execute(sql, self.active_wars[war.clan.tag])
            self.bot.logger.info(f"War database updated for {war.clan.name} at the start of war. "
                                 f"(war_id: {self.active_wars[war.clan.tag]})")
        if current_state == "warEnded":
            await self.report_war(war)
            with Sql() as cursor:
                sql = ("UPDATE rcs_wars "
                       "SET clanStars = %d, "
                       "clanDestruction = %d, "
                       "clanAttacks = %d, "
                       "opponentStars = %d, "
                       "opponentDestruction = %d, "
                       "opponentAttacks = %d, "
                       "warState = 'warEnded', "
                       "reported = 1) "
                       "WHERE war_id = %d")
                cursor.execute(sql, (war.clan.stars, war.clan.destruction, war.clan.attacks_used,
                                     war.opponent.stars, war.opponent.destruction, war.opponent.attacks_used,
                                     self.active_wars[war.clan.tag]))
            self.bot.logger.info(f"War database updated for {war.clan.name} at the end of war. "
                                 f"(war_id: {self.active_wars[war.clan.tag]})")
            try:
                del self.active_wars[war.clan.tag]
            except KeyError:
                self.bot.logger.error(f"Could not remove active war from dict. Clan tag: {war.clan.tag}")


def setup(bot):
    bot.add_cog(WarStatus(bot))
