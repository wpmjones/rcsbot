import asyncio
import time
import pymssql
import discord
import inspect
from datetime import datetime
from discord.ext import commands
from config import settings


class WarStatus(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.flag = 1
        self.bg_task = self.bot.loop.create_task(self.main())

    @staticmethod
    def line_num():
        return inspect.currentframe().f_back.f_lineno

    async def get_war(self, war, cursor):
        sql = (f"SELECT war_id, endTime, warState "
               f"FROM rcs_wars "
               f"WHERE clanTag = '{war.clan.tag[1:]}' "
               f"AND endTime = '{datetime.strptime(war.end_time.raw_time, '%Y%m%dT%H%M%S.%fZ')}'")
        print(f"{self.line_num()} - {sql}")
        cursor.execute(sql)
        fetched = cursor.fetchone()
        if not fetched:
            return None
        else:
            return fetched['war_id']

    async def add_war(self, war, cursor):
        sql = (f"INSERT INTO rcs_wars "
               f"(clanTag, opponentTag, opponentName, clanStars, opponentStars, clanDestruction, "
               f"opponentDestruction, teamSize, clanAttacks, opponentAttacks, endTime, warState) "
               f"VALUES ('{war.clan.tag[1:]}', '{war.opponent.tag[1:]}', N'{war.opponent.name}', "
               f"0, 0, 0, 0, {war.team_size}, 0, 0, "
               f"'{datetime.strptime(war.end_time.raw_time, '%Y%m%dT%H%M%S.%fZ')}', "
               f"'preparation')")
        print(f"{self.line_num()} - {sql}")
        cursor.execute(sql)
        self.bot.logger.debug(f"Added new war for {war.clan.name} ({war.clan.tag})")
        return cursor.lastrowid()

    async def update_war(self, war, war_id, cursor):
        sql = (f"UPDATE rcs_wars SET "
               f"clanStars = {war.clan.stars}, "
               f"opponentStars = {war.opponent.stars}, "
               f"clanDestruction = {war.clan.destruction}, "
               f"opponentDestruction = {war.opponent.destruction}, "
               f"clanAttacks = {war.clan.attacks_used}, "
               f"opponentAttacks = {war.opponent.attacks_used}, "
               f"warState = '{war.state}' "
               f"WHERE war_id = {war_id}")
        print(f"{self.line_num()} - {sql}")
        cursor.execute(sql)
        self.bot.logger.debug(f"Updated war for {war.clan.name} ({war.clan.tag})")

    async def update_attacks(self, attacks, war_id, cursor):
        sql = f"SELECT MAX(attackOrder) AS attackOrder FROM rcs_warattacks WHERE war_id = {war_id}"
        print(f"{self.line_num()} - {sql}")
        cursor.execute(sql)
        fetched = cursor.fetchone()
        if isinstance(fetched['attackOrder'], int):
            last_attack = fetched['attackOrder']
        else:
            last_attack = 0
        max_attack = last_attack
        print(f"Last Attack: {last_attack}")
        for attack in attacks:
            print(f" - {attack.order}")
            if attack.order > last_attack:
                sql = (f"INSERT INTO rcs_warattacks "
                       f"(war_id, attackerTag, defenderTag, stars, destruction, attackOrder) "
                       f"VALUES ({war_id}, '{attack.attacker_tag[1:]}', '{attack.defender_tag[1:]}', "
                       f"{attack.stars}, {attack.destruction}, {attack.order})")
                print(f"{self.line_num()} - {sql}")
                cursor.execute(sql)
                if attack.order > max_attack:
                    max_attack = attack.order
        self.bot.logger.debug(f"Added attacks through {max_attack} for war_id {war_id}")

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
                        war_id = await self.get_war(war, cursor)
                        if not war_id:
                            war_id = await self.add_war(war, cursor)
                    if war.state == "inWar":
                        war_id = await self.get_war(war, cursor)
                        if not war_id:
                            war_id = await self.add_war(war, cursor)
                        await self.update_war(war, war_id, cursor)
                        await self.update_attacks(war.iterattacks, war_id, cursor)
                    if war.state == 'warEnded':
                        war_id = await self.get_war(war, cursor)
                        if not war_id:
                            war_id = await self.add_war(war, cursor)
                        await self.update_war(war, war_id, cursor)
                        await self.update_attacks(war.iterattacks, war_id, cursor)
                        # TODO update rcs_warstatus
                        # report war to discord here
                        await channel.send(f"{war.clan.name} {war.status}\n"
                                           f"{war.clan.stars} to {war.opponent.stars}")
                except:
                    self.bot.logger.exception("Fail")
            await channel.send("End of list")
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
