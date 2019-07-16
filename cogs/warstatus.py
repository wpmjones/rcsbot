import asyncio
import time
import pymssql
import discord
from datetime import datetime
from discord.ext import commands
from config import settings


class WarStatus(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.flag = 1
        self.bg_task = self.bot.loop.create_task(self.main())

    async def main(self):
        """ For reporting wars to RCS war-updates channel """
        print("Started war_report")
        while self.flag == 1:
            start = time.perf_counter()
            channel = self.bot.get_channel(settings['rcsChannels']['botDev'])
            conn = pymssql.connect(settings['database']['server'],
                                   settings['database']['username'],
                                   settings['database']['password'],
                                   settings['database']['database'],
                                   autocommit=True)
            cursor = conn.cursor(as_dict=True)
            cursor.execute("SELECT clanTag FROM rcs_data ORDER BY clanName")
            rows = cursor.fetchall()
            clan_list = []
            for row in rows:
                clan_list.append(row['clanTag'])
            clan_list = ["#CVCJR89", "#9PL8Y89", "#GPVPR2G", "#8GUY820R"]
            for clan in clan_list:
                self.bot.logger.debug(f"Starting {clan}")
                try:
                    war = await self.bot.coc_client.get_current_war(clan)
                    if war.state == "preparation":
                        sql = (f"SELECT war_id, endTime, warState "
                               f"FROM rcs_wars "
                               f"WHERE clanTag = '{clan[1:]}' "
                               f"AND endTime = '{datetime.strptime(war.end_time.raw_time, '%Y%m%dT%H%M%S.%fZ')}'")
                        print(sql)
                        cursor.execute(sql)
                        if not cursor.fetchone():
                            sql = (f"INSERT INTO rcs_wars "
                                   f"(clanTag, opponentTag, opponentName, clanStars, opponentStars, clanDestruction, "
                                   f"opponentDestruction, teamSize, clanAttacks, opponentAttacks, endTime, warState) "
                                   f"VALUES ('{clan[1:]}', '{war.opponent.tag[1:]}', N'{war.opponent.name}', "
                                   f"0, 0, 0, 0, {war.team_size}, 0, 0, "
                                   f"'{datetime.strptime(war.end_time.raw_time, '%Y%m%dT%H%M%S.%fZ')}', "
                                   f"'preparation')")
                            cursor.execute(sql)
                            self.bot.logger.debug(f"Added new war for {war.clan.name} ({war.clan.tag})")
                    if war.state == "inWar":
                        sql = (f"SELECT war_id, endTime, warState "
                               f"FROM rcs_wars "
                               f"WHERE clanTag = '{clan[1:]}' "
                               f"AND endTime = '{datetime.strptime(war.end_time.raw_time, '%Y%m%dT%H%M%S.%fZ')}'")
                        print(f"60\n{sql}")
                        cursor.execute(sql)
                        fetched = cursor.fetchone()
                        if not fetched:
                            sql = (f"INSERT INTO rcs_wars "
                                   f"(clanTag, opponentTag, opponentName, clanStars, opponentStars, clanDestruction, "
                                   f"opponentDestruction, teamSize, clanAttacks, opponentAttacks, endTime, warState) "
                                   f"VALUES ('{clan[1:]}', '{war.opponent.tag[1:]}', N'{war.opponent.name}', "
                                   f"0, 0, 0, 0, {war.team_size}, 0, 0, "
                                   f"'{datetime.strptime(war.end_time.raw_time, '%Y%m%dT%H%M%S.%fZ')}', "
                                   f"'inWar')")
                            cursor.execute(sql)
                            self.bot.logger.debug(f"Added new war for {war.clan.name} ({war.clan.tag})")
                            sql = (f"SELECT war_id, endTime, warState "
                                   f"FROM rcs_wars "
                                   f"WHERE clanTag = '{clan[1:]}' "
                                   f"AND endTime = '{datetime.strptime(war.end_time.raw_time, '%Y%m%dT%H%M%S.%fZ')}'")
                            print(f"76\n{sql}")
                            cursor.execute(sql)
                            fetched = cursor.fetchone()
                        war_id = fetched['war_id']
                        sql = (f"UPDATE rcs_wars SET "
                               f"clanStars = {war.clan.stars}, "
                               f"opponentStars = {war.opponent.stars}, "
                               f"clanDestruction = {war.clan.destruction}, "
                               f"opponentDestruction = {war.opponent.destruction}, "
                               f"clanAttacks = {war.clan.attacks_used}, "
                               f"opponentAttacks = {war.opponent.attacks_used},"
                               f"warState = 'inWar'"
                               f"WHERE war_id = {war_id}")
                        print(f"89\n{sql}")
                        cursor.execute(sql)
                    await channel.send(f"{war.clan.name} is currently {war.state}.\n"
                                       f"{war.clan.stars}/{war.clan.max_stars}\n"
                                       f"{war.end_time.raw_time}")
                except:
                    self.bot.logger.exception("Fail")
            conn.close()
            elapsed = time.perf_counter() - start
            await asyncio.sleep(600)

    @commands.command(name="flip_wars")
    @commands.is_owner()
    async def flip(self, ctx):
        if self.flag == 1:
            self.flag = 0
            await ctx.send("Flag changed to 0")


def setup(bot):
    bot.add_cog(WarStatus(bot))
