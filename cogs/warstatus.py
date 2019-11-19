import discord
import coc

from discord.ext import commands
from cogs.utils.converters import ClanConverter
from cogs.utils.helper import rcs_tags
from cogs.utils.images import get_random_image
from cogs.utils.db import Sql
from io import BytesIO
from config import settings


class WarStatus(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.test_channel = self.bot.get_channel(settings['log_channels']['test'])
        self.war_channel = self.bot.get_channel(settings['rcs_channels']['war_updates'])

        self.bot.coc.add_events(self.on_war_state_change,
                                )
        self.bot.coc.add_war_update(rcs_tags(prefix=True))
        self.bot.coc.start_updates("war")

    def cog_unload(self):
        self.bot.coc.remove_events(self.on_war_state_change,
                                   )

    @commands.command(name="back")
    async def backlog(self, ctx):
        for tag in rcs_tags(prefix=True):
            print(f"Processing war logs for {tag}")
            try:
                war_log = await self.bot.coc.get_warlog(tag, cache=False, update_cache=False)
            except coc.PrivateWarLog:
                continue
            with Sql() as cursor:
                for war in war_log:
                    if isinstance(war, coc.LeagueWarLogEntry):
                        # Ignore CWL wars
                        continue
                    oppo_name = war.opponent.name.replace("'", "''")
                    sql = ("INSERT INTO rcs_wars (clanTag, clanStars, clanDestruction, clanAttacks, "
                           "opponentTag, opponentName, opponentStars, opponentDestruction, opponentAttacks, "
                           "teamSize, warState, endTime, reported, warType) "
                           "(SELECT %s, %d, %d, %d, %s, N'{}', %d, %d, %d, %d, %s, %s, 1, 'random'"
                           "WHERE NOT EXISTS "
                           "(SELECT war_id FROM rcs_wars WHERE clanTag = %s and endTime = %s))".format(oppo_name))
                    cursor.execute(sql, (war.clan.tag[1:], war.clan.stars, war.clan.destruction, war.clan.attacks_used,
                                         war.opponent.tag[1:], war.opponent.stars, war.opponent.destruction,
                                         war.opponent.attacks_used, war.team_size, "warEnded", war.end_time.time,
                                         war.clan.tag[1:], war.end_time.time))
        print("All Done")

    @commands.command(name="warstats")
    async def war_stats(self, ctx, clan: ClanConverter = None):
        if not clan:
            return await ctx.send("Please provide a valid RCS clan name or tag.")
        async with ctx.typing():
            with Sql(as_dict=True) as cursor:
                sql = ("SELECT TOP 1 clanStars, clanDestruction, clanAttacks, "
                       "opponentTag, opponentName, opponentStars, opponentDesctruction, opponentAttacks, "
                       "teamSize, endTime, warType "
                       "FROM rcs_wars "
                       "WHERE clanTag = %s AND warType = 'random' "
                       "ORDER BY endTime DESC")
                cursor.execute(sql, clan.tag[1:])
                last_war = cursor.fetchone()
                sql = ("SELECT SUM(clanStars) as stars, SUM(teamSize) as size, SUM(clanDestruction) as destruct, "
                       "COUNT(war_id) as num_wars "
                       "FROM rcs_wars "
                       "WHERE clanTag = %s and warType = 'random'")
                cursor.execute(sql, clan.tag[1:])
                war_stats = cursor.fetchone()
            # do stuff with data

    @commands.command(name="img")
    async def report_war(self, ctx):
        """Send war report to #rcs-war-updates"""
        img = await get_random_image()

        buffer = BytesIO()
        img.save(buffer, "png")
        buffer.seek(0)
        await ctx.send(file=discord.File(buffer, "results.png"))

    async def add_war(self, war):
        with Sql() as cursor:
            sql = ("INSERT INTO rcs_wars (clanTag, opponentTag, opponentName, teamSize, warState, endTime, warType) "
                   "(SELECT %s, %s, N'{}', %d, %s, %s, %s "
                   "WHERE NOT EXISTS "
                   "(SELECT war_id FROM rcs_wars WHERE clanTag = %s AND endTime = %s))".format(war.opponent.name))
            cursor.execute(sql, (war.clan.tag[1:], war.opponent.tag[1:], war.team_size,
                                 war.state, war.end_time.time, war.clan.tag[1:], war.end_time.time, war.type))
            try:
                self.bot.active_wars[war.clan.tag] = cursor.lastrowid()
            except TypeError:
                sql = "SELECT war_id FROM rcs_wars WHERE clanTag = %s AND endTime = %s"
                cursor.execute(sql, (war.clan.tag[1:], war.end_time.time))
                fetch = cursor.fetchone()
                self.bot.active_wars[war.clan.tag] = fetch[0]
                print("War is already in database. Updating active_wars")

    async def on_war_state_change(self, current_state, war):
        if isinstance(war, coc.LeagueWar):
            # I don't want to do anything with CWL wars
            return
        self.bot.logger.debug(f"Working on {war.clan.name} ({war.clan.tag})")
        if current_state == "preparation":
            await self.add_war(war)
            self.bot.logger.info(f"New war added to database for {war.clan.name} "
                                 f"(war_id: {self.bot.active_wars[war.clan.tag]}).")
        if current_state == "inWar":
            if war.clan.tag not in self.bot.active_wars.keys():
                await self.add_war(war)
            with Sql() as cursor:
                sql = ("UPDATE rcs_wars "
                       "SET warState = 'inWar' "
                       "WHERE war_id = %d")
                cursor.execute(sql, self.bot.active_wars[war.clan.tag])
            self.bot.logger.info(f"War database updated for {war.clan.name} at the start of war. "
                                 f"(war_id: {self.bot.active_wars[war.clan.tag]})")
        if current_state == "warEnded":
            if war.clan.tag not in self.bot.active_wars.keys():
                await self.add_war(war)
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
                                     self.bot.active_wars[war.clan.tag]))
            self.bot.logger.info(f"War database updated for {war.clan.name} at the end of war. "
                                 f"(war_id: {self.bot.active_wars[war.clan.tag]})")
            try:
                del self.bot.active_wars[war.clan.tag]
            except KeyError:
                self.bot.logger.error(f"Could not remove active war from dict. Clan tag: {war.clan.tag}")


def setup(bot):
    bot.add_cog(WarStatus(bot))
