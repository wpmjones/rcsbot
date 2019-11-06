import discord
import math
import time

from discord.ext import commands
from cogs.utils import formats
from cogs.utils.converters import ClanConverter
from cogs.utils.db import Sql
from cogs.utils.helper import rcs_clans
from datetime import datetime
from config import settings


class Push(commands.Cog):
    """Cog for RCS trophy push"""
    def __init__(self, bot):
        self.bot = bot
        self.title = "2019 RCS Turkey Day Trophy Push"
        self.start_time = datetime(2019, 11, 15, 5, 0)
        self.end_time = datetime(2019, 11, 24, 5, 0)

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
        embed = discord.Embed(title=self.title, color=discord.Color.from_rgb(155, 103, 60))
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
            embed.add_field(name="Winning clan:", value="Winning clan")
            # TODO other cool stats here
            embed.set_author(name="Event complete!",
                             icon_url="https://cdn.discordapp.com/emojis/641101630342692884.png")
        await ctx.send(embed=embed)

    @push.command(name="all")
    async def push_all(self, ctx):
        """Returns list of all clans ranked by score (only top 30 trophies contribute to the score."""
        with Sql(as_dict=True) as cursor:
            cursor.execute("SELECT SUM(clanPoints) AS totals, clanName FROM rcspush_vwClanPointsTop30 "
                           "GROUP BY clanName "
                           "ORDER BY totals DESC")
            fetch = cursor.fetchall()
        page_count = math.ceil(len(fetch) / 20)
        title = "RCS Push Rankings"
        ctx.icon = "https://cdn.discordapp.com/emojis/635642869738111016.png"
        p = formats.TablePaginator(ctx, data=fetch, title=title, page_count=page_count)
        await p.paginate()

    @push.command(name="diff")
    async def push_diff(self, ctx):
        """Returns list of clans ranked by score, showing the differential to the top clan."""
        with Sql() as cursor:
            cursor.execute("SELECT SUM(clanPoints) AS totals, clanName FROM rcspush_vwClanPointsTop30 "
                           "GROUP BY clanName "
                           "ORDER BY totals DESC")
            fetch = cursor.fetchall()
        top_score = fetch[0][0]
        data = []
        for row in fetch:
            data.append([top_score - row[0], row[1]])
        page_count = math.ceil(len(fetch) / 20)
        title = "RCS Push Ranking Differentials"
        ctx.icon = "https://cdn.discordapp.com/emojis/635642869738111016.png"
        p = formats.TablePaginator(ctx, data=data, title=title, page_count=page_count)
        await p.paginate()

    @push.command(name="top")
    async def push_top(self, ctx):
        """Returns list of top 10 players for each TH level."""
        th_list = [12, 11, 10, 9, 8, 7]
        # TODO decide what data you want to show here
        # TODO UNION top tens and paginate on TH level
        with Sql(as_dict=True) as cursor:
            cursor.execute(f"SELECT TOP 10 playerName, clanName, clanPoints, currentTrophies "
                           f"FROM rcspush_vwClanPoints "
                           f"WHERE thLevel = {level} "
                           f"ORDER BY clanPoints DESC")
            fetch = cursor.fetchall()
        msg_list = []
        for row in fetch:
            if row['clanName'][:6] == "Reddit":
                clan_name = row['clanName'][7:]
            else:
                clan_name = row['clanName']
            msg_list.append({"name": f"{row['playerName']} ({clan_name})",
                             "points": f"{str(row['clanPoints'])[:5]} ({str(row['currentTrophies'])})"})
            content = f"```RCS Trophy Push - Top TH{str(level)}"
            content += "\n{0:25}{1:>17}".format("Player Name (clan)", "Points (Trophies)")
            content += "\n------------------------------------------"
            for item in msg_list:
                content += "\n{0:30}{1:>12}".format(item['name'], item['points'])
            content += "```"
        await ctx.send(content)

    @push.command(name="th")
    async def push_th(self, ctx, th_level):
        if (th_level > 12) or (th_level < 6):
            return await ctx.send("You have not provided a valid town hall level.")
        with Sql(as_dict=True) as cursor:
            cursor.execute(f"SELECT TOP 80 playerName, clanName, clanPoints, currentTrophies "
                           f"FROM rcspush_vwClanPoints "
                           f"WHERE thLevel = {th_level} "
                           f"ORDER BY clanPoints DESC")
            fetched = cursor.fetchall()
        # TODO Decide what data you want to show here
        msg_list = []
        for row in fetched:
            if row['clanName'][:7] == 'Reddit ':
                clan_name = row['clanName'][7:]
            else:
                clan_name = row['clanName']
            msg_list.append({"name": f"{row['playerName']} ({clan_name})",
                             "points": f"{str(row['clanPoints'])[:5]} ({str(row['currentTrophies'])})"})
        content = "RCS Trophy Push - {0:4}".format(arg.upper())
        content += "\n{0:25}{1:>17}".format("Player (Clan)", "Points (Trophies)")
        content += "\n------------------------------------------"
        for item in msg_list:
            content += "\n{0:30}{1:>12}".format(item['name'], item['points'])

    @push.command(name="gain", aliases=["gains", "increase"])
    async def push_gain(self, ctx):
        """Returns top 25 players based on number of trophies gained."""
        with Sql(as_dict=True) as cursor:
            cursor.execute("SELECT trophyGain, player FROM rcspush_vwGains ORDER BY trophyGain DESC")
            fetch = cursor.fetchall()
        page_count = math.ceil(len(fetch) / 25)
        title = "RCS Push Top Trophy Gains"
        ctx.icon = "https://cdn.discordapp.com/emojis/635642869738111016.png"
        p = formats.TablePaginator(ctx, data=fetch, title=title, page_count=page_count)
        await p.paginate()

    @push.command(name="clan")
    async def push_clan(self, ctx, clan: ClanConverter = None):
        if not clan:
            return await ctx.send("Please provide a valid clan name/tag when using this command.")
        with Sql(as_dict=True) as cursor:
            cursor.execute(f"SELECT clanPoints, playerName + ' TH(' + thLevel + ')' as playerName "
                           f"FROM rcspush_vwClanPoints "
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
        await ctx.send("Starting process...")
        # start push
        start = time.perf_counter()
        for clan in rcs_clans():
            if clan == "Reddit Tau":  # Change to in list if more than one clan bails
                continue
            clan_tag = rcs_clans()[clan]
            self.bot.logger.info(f"Starting {clan_tag}")
            coc_clan = await self.bot.coc.get_clan(f"#{clan_tag}")
            with Sql() as cursor:
                async for player in coc_clan.get_detailed_members():
                    pname = player.name.replace("'", "''")
                    sql = (f"INSERT INTO rcspush_2019_2 "
                           f"(playerTag, clanTag, startingTrophies, currentTrophies, "
                           f"bestTrophies, startingThLevel, playerName, clanName) "
                           f"VALUES (%s, %s, %d, %d, %d, %d, N'{pname}', %s)")
                    cursor.execute(sql,
                                   (player.tag[1:], clan_tag, player.trophies, player.trophies,
                                    player.best_trophies, player.town_hall, clan))
        await ctx.send(f"All members added. Elapsed time: {(time.perf_counter() - start)/60:.2f} minutes")


def setup(bot):
    bot.add_cog(Push(bot))
