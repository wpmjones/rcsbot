import discord
import math
import time

from discord.ext import commands
from cogs.utils import formats
from cogs.utils.converters import ClanConverter
from cogs.utils.db import Sql
from cogs.utils.helper import rcs_tags
from datetime import datetime


class Push(commands.Cog):
    """Cog for RCS trophy push"""

    def __init__(self, bot):
        self.bot = bot
        self.title = "2020 Spring Trophy Push"
        self.start_time = datetime(2020, 4, 27, 5, 0)
        self.end_time = datetime(2020, 5, 25, 4, 55)

    @commands.group(name="push", invoke_without_command=True)
    async def push(self, ctx):
        """The main push command for the event and provides information relating to the status of the push."""
        if ctx.invoked_subcommand is not None:
            return

        await ctx.invoke(self.push_info)

    @push.command(name="info")
    async def push_info(self, ctx):
        """Provides current status of the push (start/end time)."""
        now = datetime.utcnow()
        embed = discord.Embed(title=self.title, color=discord.Color.from_rgb(0, 183, 0))
        embed.set_footer(icon_url="https://openclipart.org/image/300px/svg_to_png/122449/1298569779.png",
                         text="For help with this command, type ++help push")
        embed.add_field(name="Start time (UTC):", value=self.start_time.strftime("%d-%b-%Y %H:%M"), inline=True)
        embed.add_field(name="End time (UTC):", value=self.end_time.strftime("%d-%b-%Y %H:%M"), inline=True)
        if now < self.start_time:
            delta = self.start_time - now
            if delta.days > 0:
                start_info = f"Starting in {delta.days} day(s)."
            else:
                hours, _ = divmod(delta.total_seconds(), 3600)
                start_info = f"Starting in {hours:02} hour(s)."
            embed.set_author(name=start_info,
                             icon_url="https://cdn.discordapp.com/emojis/641101630351212567.png")
        elif self.start_time < now < self.end_time:
            delta = self.end_time - now
            if delta.days > 0:
                end_info = f"Ending in {delta.days} day(s)."
            else:
                hours, _ = divmod(delta.total_seconds(), 3600)
                end_info = f"Ending in {hours:02} hour(s)."
            embed.set_author(name=end_info,
                             icon_url="https://cdn.discordapp.com/emojis/641101629881319434.png")
        else:
            # embed.add_field(name="Winning clan:", value="Winning clan")
            # TODO other cool stats here
            embed.set_author(name="Event complete!",
                             icon_url="https://cdn.discordapp.com/emojis/641101630342692884.png")
        await ctx.send(embed=embed)

    @push.command(name="all")
    async def push_all(self, ctx):
        """Returns list of all clans ranked by score (only top 30 trophies contribute to the score)."""
        with Sql() as cursor:
            cursor.execute("SELECT SUM(clanPoints) AS totals, clanName FROM vRCSPush30 "
                           "GROUP BY clanName "
                           "ORDER BY totals DESC")
            fetch = cursor.fetchall()
        page_count = math.ceil(len(fetch) / 20)
        title = "RCS Push Rankings"
        ctx.icon = "https://cdn.discordapp.com/emojis/635642869738111016.png"
        p = formats.TablePaginator(ctx, data=fetch, title=title, page_count=page_count, rows_per_table=20)
        await p.paginate()

    @push.command(name="diff")
    async def push_diff(self, ctx):
        """Returns list of clans ranked by score, showing the differential to the top clan."""
        with Sql() as cursor:
            cursor.execute("SELECT SUM(clanPoints) AS totals, clanName FROM vRCSPush30 "
                           "GROUP BY clanName "
                           "ORDER BY totals DESC")
            fetch = cursor.fetchall()
        top_score = fetch[0][0]
        data = []
        for row in fetch:
            if row[0] == top_score:
                data.append([f"{top_score:.0f}", row[1]])
            else:
                data.append([f"-{top_score - row[0]:.0f}", row[1]])
        page_count = math.ceil(len(fetch) / 20)
        title = "RCS Push Ranking Differentials"
        ctx.icon = "https://cdn.discordapp.com/emojis/635642869738111016.png"
        p = formats.TablePaginator(ctx, data=data, title=title, page_count=page_count, rows_per_table=20)
        await p.paginate()

    @push.command(name="top")
    async def push_top(self, ctx):
        """Returns list of top 10 players for each TH level."""
        # TODO change author icon with TH
        with Sql() as cursor:
            cursor.execute("SELECT currentTrophies, playerName "
                           "FROM rcspush_vwTopTenByTh "
                           "ORDER BY th DESC, currentTrophies DESC")
            fetch = cursor.fetchall()
        ctx.icon = "https://cdn.discordapp.com/emojis/635642869738111016.png"
        p = formats.TopTenPaginator(ctx, data=fetch)
        await p.paginate()

    @push.command(name="th")
    async def push_th(self, ctx, th_level: int):
        """Returns list of top 100 players at the TH specified (there must be a space between th and the number)."""
        if (th_level > 13) or (th_level < 6):
            return await ctx.send("You have not provided a valid town hall level.")
        with Sql() as cursor:
            cursor.execute(f"SELECT TOP 100 currentTrophies, CAST(clanPoints AS DECIMAL(5,2)) as Pts, "
                           f"playerName + ' (' + COALESCE(altName, clanName) + ')' as Name "
                           f"FROM vRCSPush "
                           f"WHERE currentThLevel = {th_level} "
                           f"ORDER BY clanPoints DESC")
            fetch = cursor.fetchall()
        page_count = math.ceil(len(fetch) / 20)
        title = f"RCS Push Top Points for TH{th_level}"
        ctx.icon = "https://cdn.discordapp.com/emojis/635642869738111016.png"
        p = formats.TablePaginator(ctx, data=fetch, title=title, page_count=page_count, rows_per_table=20)
        await p.paginate()

    @push.command(name="th13", hidden=True)
    async def push_th13(self, ctx):
        await ctx.invoke(self.push_th, th_level=13)

    @push.command(name="th12", hidden=True)
    async def push_th12(self, ctx):
        await ctx.invoke(self.push_th, th_level=12)

    @push.command(name="th11", hidden=True)
    async def push_th11(self, ctx):
        await ctx.invoke(self.push_th, th_level=11)

    @push.command(name="th10", hidden=True)
    async def push_th10(self, ctx):
        await ctx.invoke(self.push_th, th_level=10)

    @push.command(name="th9", hidden=True)
    async def push_th9(self, ctx):
        await ctx.invoke(self.push_th, th_level=9)

    @push.command(name="th8", hidden=True)
    async def push_th8(self, ctx):
        await ctx.invoke(self.push_th, th_level=8)

    @push.command(name="th7", hidden=True)
    async def push_th7(self, ctx):
        await ctx.invoke(self.push_th, th_level=7)

    @push.command(name="gain", aliases=["gains", "increase"])
    async def push_gain(self, ctx):
        """Returns top 25 players based on number of trophies gained."""
        with Sql() as cursor:
            cursor.execute("SELECT trophyGain, player FROM rcspush_vwGains ORDER BY trophyGain DESC")
            fetch = cursor.fetchall()
        page_count = math.ceil(len(fetch) / 25)
        title = "RCS Push Top Trophy Gains"
        ctx.icon = "https://cdn.discordapp.com/emojis/635642869738111016.png"
        p = formats.TablePaginator(ctx, data=fetch, title=title, page_count=page_count)
        await p.paginate()

    @push.command(name="clan")
    async def push_clan(self, ctx, clan: ClanConverter = None):
        """Returns a list of players from the specified clan with their push points"""
        if not clan:
            return await ctx.send("Please provide a valid clan name/tag when using this command.")
        print(clan)
        with Sql() as cursor:
            cursor.execute(f"SELECT CAST(clanPoints as decimal(5,2)), "
                           f"playerName + ' (TH' + CAST(currentThLevel as varchar(2)) + ')' "
                           f"FROM vRCSPush "
                           f"WHERE clanName = %s "
                           f"ORDER BY clanPoints DESC",
                           clan.name)
            fetch = cursor.fetchall()
        page_count = math.ceil(len(fetch) / 25)
        title = f"RCS Push - {clan.name} Points"
        ctx.icon = "https://cdn.discordapp.com/emojis/635642869738111016.png"
        p = formats.TablePaginator(ctx, data=fetch, title=title, page_count=page_count)
        await p.paginate()

    @push.command(name="start", hidden=True)
    @commands.is_owner()
    async def push_start(self, ctx):
        msg = await ctx.send("Starting process...")
        # start push
        start = time.perf_counter()
        player_list = []
        async for clan in self.bot.coc.get_clans(rcs_tags()):
            if clan.tag == "#9L2PRL0U":  # Change to in list if more than one clan bails
                continue
            for member in clan.itermembers:
                player_list.append(member.tag)
        team_boom = ['#20PCPRJ8', '#2QG2C9LG8', '#288UUGPGG', '#YQCVUGJU', '#2G0YV209J', '#9P0PPJV8',
                     '#9PYP8VY90', '#982V9288G', '#2Q8GQLU9R', '#22LPCGV8', '#RU9LYLG9', '#28VYCQGRU',
                     '#P2P9QU8C2', '#GVJP200U', '#20CCV90UQ', '#Y9C2909R', '#2UL9UVCC2', '#89QQ9QRJ0',
                     '#8JQGGU2Q0', '#GPUQYRJC', '#R8JVUGVU', '#V8UQ0G0L', '#G82J00P', '#8VQY0GP2',
                     '#88Y0YL98P', '#80LPL9PRP', '#Y0RPYJPC', '#9L9VCYQQ2', '#9P8PCUY8L', '#YY82YY2Y',
                     '#2LQPJVR0', '#2PYQR02GV', '#URLVC082', '#PJ8V0QUU', '#2LJJY8JGQ', '#CYUVGPPQ',
                     '#PY90C2CY', '#L0GYY8V2', '#8L8PLY2Q2', '#LQY0UUV8V', '#2VVQJ9GG2', '#9Y9GCYRJJ',
                     '#8R2QVYYG', '#2VCG8PPVU', '#2UPPC0GUC', '#8LVCUQGRG', '#2LQVURL9L', '#PCR8QGY9',
                     '#2YCV2JRRJ', '#JLPC2GCU']
        player_list.extend(team_boom)
        print(len(player_list))
        players_many = []
        to_insert = []
        async for player in self.bot.coc.get_players(player_list):
            players_many.append((player.tag[1:], player.clan.tag[1:],
                                 player.trophies if player.trophies <= 5000 else 5000,
                                 player.trophies if player.trophies <= 5000 else 5000,
                                 player.best_trophies, player.town_hall, player.name.replace("'", "''"),
                                 player.clan.name))
            to_insert.append({
                "player_tag": player.tag[1:],
                "clan_tag": player.clan.tag[1:],
                "starting_trophies": player.trophies if player.trophies <= 5000 else 5000,
                "current_trophies": player.trophies if player.trophies <= 5000 else 5000,
                "best_trophies": player.best_trophies,
                "starting_th_level": player.town_hall,
                "player_name": player.name.replace("'", "''"),
                "clan_name": player.clan.name
            })
        print("Player list assembled.")
        with Sql() as cursor:
            sql = (f"INSERT INTO rcspush_2020_1 "
                   f"(playerTag, clanTag, startingTrophies, currentTrophies, "
                   f"bestTrophies, startingThLevel, playerName, clanName) "
                   f"VALUES (%s, %s, %d, %d, %d, %d, %s, %s)")
            cursor.executemany(sql, players_many)
            sql = ("UPDATE rcspush_2020_1 SET clanTag = '9L2PRL0U' "
                   "WHERE playerTag IN ('#20PCPRJ8', '#2QG2C9LG8', '#288UUGPGG', '#YQCVUGJU', '#2G0YV209J', "
                   "'#9P0PPJV8', "
                   "'#9PYP8VY90', '#982V9288G', '#2Q8GQLU9R', '#22LPCGV8', '#RU9LYLG9', '#28VYCQGRU', '#P2P9QU8C2', "
                   "'#GVJP200U', '#20CCV90UQ', '#Y9C2909R', '#2UL9UVCC2', '#89QQ9QRJ0', '#8JQGGU2Q0', '#GPUQYRJC', "
                   "'#R8JVUGVU', '#V8UQ0G0L', '#G82J00P', '#8VQY0GP2', '#88Y0YL98P', '#80LPL9PRP', '#Y0RPYJPC', "
                   "'#9L9VCYQQ2', '#9P8PCUY8L', '#YY82YY2Y', '#2LQPJVR0', '#2PYQR02GV', '#URLVC082', '#PJ8V0QUU', "
                   "'#2LJJY8JGQ', '#CYUVGPPQ', '#PY90C2CY', '#L0GYY8V2', '#8L8PLY2Q2', '#LQY0UUV8V', '#2VVQJ9GG2', "
                   "'#9Y9GCYRJJ', '#8R2QVYYG', '#2VCG8PPVU', '#2UPPC0GUC', '#8LVCUQGRG', '#2LQVURL9L', '#PCR8QGY9', "
                   "'#2YCV2JRRJ', '#JLPC2GCU')")
            cursor.execute(sql)
        conn = self.bot.pool
        sql = ("INSERT INTO rcspush_2020_1 (player_tag, clan_tag, starting_trophies, current_trophies, best_trophies, "
               "starting_th_level, player_name, clan_name) "
               "SELECT x.player_tag, x.clan_tag, x.starting_trophies, x.current_trophies, x.best_trophies, "
               "x.starting_th_level, x.player_name, x.clan_name "
               "FROM jsonb_to_recordset($1::jsonb) as x (player_tag TEXT, clan_tag TEXT, starting_trophies INTEGER, "
               "current_trophies INTEGER, best_trophies INTEGER, starting_th_level INTEGER, player_name TEXT, "
               "clan_name TEXT)")
        await conn.execute(sql, to_insert)
        await msg.delete()
        await ctx.send(f"{len(player_list)} members added. Elapsed time: "
                       f"{(time.perf_counter() - start) / 60:.2f} minutes")


def setup(bot):
    bot.add_cog(Push(bot))
