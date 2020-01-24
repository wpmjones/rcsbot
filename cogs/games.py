import coc
import math
import re

from discord.ext import commands
from cogs.utils.checks import is_leader_or_mod_or_council
from cogs.utils.converters import ClanConverter, PlayerConverter
from cogs.utils.db import Sql
from cogs.utils import formats

tag_validator = re.compile("^#?[PYLQGRJCUV0289]+$")


class Games(commands.Cog):
    """Cog for Clan Games"""
    def __init__(self, bot):
        self.bot = bot

    @commands.group(invoke_without_command=True)
    async def games(self, ctx, *, clan: ClanConverter = None):
        """[Group] Commands for clan games"""
        if ctx.invoked_subcommand is not None:
            return

        if not clan:
            await ctx.invoke(self.games_all)
        else:
            await ctx.invoke(self.games_clan, clan=clan)

    @games.command(name="all")
    async def games_all(self, ctx):
        """Returns clan points for all RCS clans"""
        conn = self.bot.pool
        sql = ("SELECT clan_points "
               "FROM rcs_events "
               "WHERE event_type = 5 and start_time < NOW() "
               "ORDER BY start_time DESC")
        clan_points = await conn.fetchval(sql)
        sql = ("SELECT clan_total, clan_name "
               "FROM rcs_clan_games_totals "
               "ORDER BY clan_total DESC")
        fetch = await conn.fetch(sql)
        data = []
        for clan in fetch:
            if clan['clan_total'] >= clan_points:
                data.append([clan['clan_total'], "* " + clan['clan_name']])
            else:
                data.append([clan['clan_total'], clan['clan_name']])
        page_count = math.ceil(len(data) / 25)
        title = "RCS Clan Games Points"
        ctx.icon = "https://cdn.discordapp.com/emojis/639623355770732545.png"
        p = formats.TablePaginator(ctx, data=data, title=title, page_count=page_count)
        await p.paginate()

    @games.command(name="top")
    async def games_top(self, ctx):
        """Show top ten players' games points"""
        await ctx.invoke(self.bot.get_command("top games"))

    @games.command(name="average", aliases=["avg", "averages"])
    async def games_average(self, ctx):
        """Returns the average player points for all RCS clans"""
        conn = self.bot.pool
        sql = ("SELECT clan_avg, clan_name "
               "FROM rcs_clan_games_average "
               "ORDER BY clan_avg DESC")
        fetch = await conn.fetch(sql)
        data = []
        for clan in fetch:
            data.append([clan['clan_avg'], clan['clan_name']])
        page_count = math.ceil(len(data) / 25)
        title = "RCS Clan Games Averages"
        ctx.icon = "https://cdn.discordapp.com/emojis/639623355770732545.png"
        p = formats.TablePaginator(ctx, data=data, title=title, page_count=page_count)
        await p.paginate()

    @games.command(name="clan")
    async def games_clan(self, ctx, *, clan: ClanConverter = None):
        """Returns the individual player points for the specified clan

        Examples:
        `++games clan Team Boom`
        `++games clan #CVCJR89`
        `++games clan Pi`
        """
        async with ctx.typing():
            conn = self.bot.pool
            sql = ("SELECT player_points "
                   "FROM rcs_events "
                   "WHERE event_type = 5 and start_time < NOW() "
                   "ORDER BY start_time DESC")
            player_points = await conn.fetchval(sql)
            sql = ("SELECT player_name, points "
                   "FROM rcs_clan_games_players "
                   "WHERE clan_tag = $1"
                   "ORDER BY points DESC")
            fetch = await conn.fetch(sql, clan.tag[1:])
            clan_total = 0
            clan_size = len(fetch)
            data = []
            for member in fetch:
                if member['points'] >= player_points:
                    clan_total += player_points
                    data.append([member['points'], "* " + member['player_name']])
                else:
                    clan_total += member['points']
                    data.append([member['points'], member['player_name']])
            clan_average = clan_total / clan_size
        page_count = math.ceil(len(data) / 25)
        title = f"{clan.name} Points {clan_total} ({clan_average:.2f} avg)"
        ctx.icon = "https://cdn.discordapp.com/emojis/639623355770732545.png"
        p = formats.TablePaginator(ctx, data=data, title=title, page_count=page_count)
        await p.paginate()

    @games.command(name="add", aliases=["games+", "ga"], hidden=True)
    @is_leader_or_mod_or_council()
    async def games_add(self, ctx, player: PlayerConverter = None, clan: ClanConverter = None, games_points: int = 0):
        """Add player who missed the initial pull

        Examples:
        `++games add TubaKid "Reddit Oak" 2310`
        `++games add #RVP02LU0 #CVCJR89 100`
        `++games add Fredo Tau 3850`
        """
        if not player:
            return await ctx.send("Please provide a valid player tag.")
        if not clan:
            return await ctx.send("Please provide a valid clan tag.")
        if player.clan.tag == clan.tag:
            with Sql(as_dict=True) as cursor:
                cursor.execute("SELECT MAX(eventId) as eventId FROM rcs_events WHERE eventType = 5")
                row = cursor.fetchone()
                event_id = row['eventId']
                try:
                    starting_points = player.achievements_dict['Games Champion'].value - games_points
                    current_points = player.achievements_dict['Games Champion'].value
                except:
                    self.bot.logger.debug("points assignment failed for some reason")
                sql = (f"INSERT INTO rcs_clanGames (eventId, playerTag, clanTag, startingPoints, currentPoints) "
                       f"VALUES (%d, %s, %s, %d,. %d)")
                cursor.execute(sql, (event_id, player.tag[1:], player.clan.tag[1:], starting_points, current_points))
            await ctx.send(f"{player.name} ({player.clan.name}) has been added to the games database.")
        else:
            response = f"{player.name}({player.tag}) is not currently in {clan.name}({clan.tag})."
            await ctx.send(response)


def setup(bot):
    bot.add_cog(Games(bot))
