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
        self.channel = self.bot.get_channel(settings['rcsChannels']['botDev'])
        self.bg_task = self.bot.loop.create_task(self.main())

    @staticmethod
    def line_num():
        return inspect.currentframe().f_back.f_lineno

    async def _get_war(self, war, cursor):
        sql = (f"SELECT war_id, reported "
               f"FROM rcs_wars "
               f"WHERE clanTag = '{war.clan.tag[1:]}' "
               f"AND endTime = '{datetime.strptime(war.end_time.raw_time, '%Y%m%dT%H%M%S.%fZ')}'")
        cursor.execute(sql)
        return cursor.fetchone()

    async def get_war(self, war, cursor):
        fetched = await self._get_war(war, cursor)
        if fetched:
            return fetched['war_id']

    async def get_war_reported(self, war, cursor):
        fetched = await self._get_war(war, cursor)
        if fetched:
            return fetched.values()

    async def add_war(self, war, cursor):
        sql = (f"INSERT INTO rcs_wars "
               f"(clanTag, opponentTag, opponentName, clanStars, opponentStars, clanDestruction, "
               f"opponentDestruction, teamSize, clanAttacks, opponentAttacks, endTime, warState, reported) "
               f"VALUES ('{war.clan.tag[1:]}', '{war.opponent.tag[1:]}', N'{war.opponent.name}', "
               f"0, 0, 0, 0, {war.team_size}, 0, 0, "
               f"'{datetime.strptime(war.end_time.raw_time, '%Y%m%dT%H%M%S.%fZ')}', "
               f"'{war.state}', 0)")
        cursor.execute(sql)
        self.bot.logger.debug(f"Added new war for {war.clan.name} ({war.clan.tag})")
        return cursor.lastrowid()

    async def update_war(self, war, war_id, cursor):
        if war.state != 'warEnded':
            sql = (f"UPDATE rcs_wars SET "
                   f"clanStars = {war.clan.stars}, "
                   f"opponentStars = {war.opponent.stars}, "
                   f"clanDestruction = {war.clan.destruction}, "
                   f"opponentDestruction = {war.opponent.destruction}, "
                   f"clanAttacks = {war.clan.attacks_used}, "
                   f"opponentAttacks = {war.opponent.attacks_used}, "
                   f"warState = '{war.state}' "
                   f"WHERE war_id = {war_id}")
        else:
            sql = (f"UPDATE rcs_wars SET "
                   f"clanStars = {war.clan.stars}, "
                   f"opponentStars = {war.opponent.stars}, "
                   f"clanDestruction = {war.clan.destruction}, "
                   f"opponentDestruction = {war.opponent.destruction}, "
                   f"clanAttacks = {war.clan.attacks_used}, "
                   f"opponentAttacks = {war.opponent.attacks_used}, "
                   f"reported = 1, "
                   f"warState = '{war.state}' "
                   f"WHERE war_id = {war_id}")
        cursor.execute(sql)
        self.bot.logger.debug(f"Updated war for {war.clan.name} ({war.clan.tag})")

    async def update_attacks(self, attacks, war_id, cursor):
        sql = f"SELECT MAX(attackOrder) AS attackOrder FROM rcs_warattacks WHERE war_id = {war_id}"
        cursor.execute(sql)
        fetched = cursor.fetchone()
        # Because we're asking for MAX, attackOrder is NULL instead of fetched being None
        if isinstance(fetched['attackOrder'], int):
            last_attack = fetched['attackOrder']
        else:
            last_attack = 0
        max_attack = last_attack
        for attack in attacks:
            if attack.order > last_attack:
                sql = (f"INSERT INTO rcs_warattacks "
                       f"(war_id, attackerTag, defenderTag, stars, destruction, attackOrder, "
                       f"attackerTownhall, defenderTownhall, attackerMap, defenderMap) "
                       f"VALUES ({war_id}, '{attack.attacker_tag[1:]}', '{attack.defender_tag[1:]}', "
                       f"{attack.stars}, {attack.destruction}, {attack.order},"
                       f"{attack.attacker.town_hall}, {attack.defender.town_hall}, "
                       f"{attack.attacker.map_position}, {attack. defender.map_position})")
                cursor.execute(sql)
                if attack.order > max_attack:
                    max_attack = attack.order
        self.bot.logger.debug(f"Added attacks through {max_attack} for war_id {war_id}")
        if max_attack > last_attack + 4:
            return 1
        else:
            return 0

    @staticmethod
    def breakdown(members, process=None):
        res = {}
        for member in members:
            th = member.town_hall if member.town_hall > 8 else 8
            if th not in res:
                res[th] = 0
            val = 1 if process is None else process(member)
            res[th] += val
        return "/".join(f"{res.get(th,0)}" for th in range(12, 7, -1))

    @staticmethod
    def member_attacks(member):
        return len(member.attacks)

    @staticmethod
    def member_stars(member):
        best_attack = 0
        for attack in member.defenses:
            if attack.stars > 0:
                best_attack = attack.stars
        return best_attack

    async def send_war_update(self, war_type, war):
        """ Send war update to Discord """
        if war_type == "Reddit v Reddit":
            icon = "http://www.mayodev.com/images/vs.png"
        elif war_type == "Regular" and war.type == "friendly":
            icon = "https://cdnjs.cloudflare.com/ajax/libs/emojione/2.2.7/assets/png/1f91d.png"
        else:
            war_type = ""
            icon = ""
        if war.state == "warEnded":
            clan = await self.bot.coc.get_clan(war.clan.tag)
            if war.status in ["won", "winning"]:
                embed_color = discord.Color.green()
                result = "Victory"
            elif war.status in ["losing", "lost"]:
                embed_color = discord.Color.dark_red()
                result = "Defeat"
            else:
                embed_color = discord.Color.gold()
                result = "Tie"
            footer_text = f"{result} - War Record: {clan.war_wins}-{clan.war_losses}-{clan.war_ties}"
        else:
            embed_color = discord.Color.light_grey()
            hours = war.end_time.seconds_until // 3600
            minutes = (war.end_time.seconds_until % 3600) // 60
            footer_text = f"{hours}:{minutes} to end of war"
        embed = discord.Embed(color=embed_color)
        embed.set_author(name=war_type, icon_url=icon)
        embed.set_footer(text=footer_text, icon_url="https://coc.guide/static/imgs/army/dark-elixir-barrack-6.png")
        embed.add_field(name=war.clan.name,
                        value=f"{war.clan.attacks_used}/{war.team_size*2} attacks\n({war.clan.destruction:0.2f}%)",
                        inline=True)
        embed.add_field(name=f"Size: {war.team_size} vs {war.team_size}",
                        value=f"{war.clan.stars} :star: vs :star: {war.opponent.stars}",
                        inline=True)
        embed.add_field(name=war.clan.name,
                        value=(f"{war.opponent.attacks_used}/{war.team_size * 2} attacks\n"
                               f"({war.opponent.destruction:0.2f}%)"),
                        inline=True)
        embed.add_field(name="Breakdown:",
                        value=f"{self.breakdown(war.clan.members)} vs {self.breakdown(war.opponent.members)}")
        embed.add_field(name="Attacks Left:",
                        value=(f"{self.breakdown(war.clan.members, lambda m: 2 - self.member_attacks(m))} vs "
                               f"{self.breakdown(war.opponent.members, lambda m: 2 - self.member_attacks(m))}"))
        embed.add_field(name="Bases Standing:",
                        value=(f"{self.breakdown(war.clan.members, lambda m: 1 if self.member_stars(m) < 3 else 0)} vs "
                               f"{self.breakdown(war.opponent.members, lambda m: 1 if self.member_stars(m) < 3 else 0)}"))
        await self.channel.send(embed=embed)

    async def main(self):
        """ For reporting wars to RCS war-updates channel """
        print("Started war_report")
        while self.flag == 1:
            start = time.perf_counter()
            conn = pymssql.connect(settings['database']['server'],
                                   settings['database']['username'],
                                   settings['database']['password'],
                                   settings['database']['database'],
                                   autocommit=True)
            cursor = conn.cursor(as_dict=True)
            cursor.execute("SELECT '#' + clanTag AS clanTag FROM rcs_data ORDER BY clanName")
            rows = cursor.fetchall()
            clan_list = []
            for row in rows:
                clan_list.append(row['clanTag'])
            clan_list = ["#CVCJR89", "#9PL8Y89", "#GPVPR2G", "#8GUY820R", "#UPVV99V"]
            for clan in clan_list:
                self.bot.logger.debug(f"Starting {clan}")
                try:
                    war = await self.bot.coc.get_current_war(clan)
                    if war.state == "preparation":
                        war_id = await self.get_war(war, cursor)
                        if not war_id:
                            _ = await self.add_war(war, cursor)
                    if war.state == "inWar":
                        war_id = await self.get_war(war, cursor)
                        if not war_id:
                            war_id = await self.add_war(war, cursor)
                        await self.update_war(war, war_id, cursor)
                        report = await self.update_attacks(war.iterattacks, war_id, cursor)
                        if war.opponent.tag[1:] in clan_list and report == 1:
                            # send in war report after every 5 attacks
                            self.bot.logger.info(f"Reddit v Reddit: {war.clan.name} vs {war.opponent.name}")
                            await self.send_war_update("Reddit v Reddit", war)
                    if war.state == 'warEnded':
                        war_id, reported = await self.get_war_reported(war, cursor)
                        if not war_id:
                            _ = await self.add_war(war, cursor)
                            war_id, reported = await self.get_war_reported(war, cursor)
                        _ = await self.update_attacks(war.iterattacks, war_id, cursor)
                        if reported == 0:
                            # report war to discord here
                            await self.send_war_update("Regular", war)
                            await self.update_war(war, war_id, cursor)
                except:
                    self.bot.logger.exception("Fail")
            conn.close()
            elapsed = time.perf_counter() - start
            await asyncio.sleep((15*60) - elapsed)

    @commands.command(name="flip_wars")
    @commands.is_owner()
    async def flip(self, ctx):
        if self.flag == 1:
            self.flag = 0
            await ctx.send("Flag changed to 0")


def setup(bot):
    bot.add_cog(WarStatus(bot))
