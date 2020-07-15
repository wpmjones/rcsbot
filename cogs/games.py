import math
import re

from discord.ext import commands, tasks
from cogs.utils.checks import is_leader_or_mod_or_council
from cogs.utils.converters import ClanConverter, PlayerConverter
from cogs.utils.helper import rcs_tags
from cogs.utils import formats
from datetime import datetime, timedelta

tag_validator = re.compile("^#?[PYLQGRJCUV0289]+$")


class Games(commands.Cog):
    """Cog for Clan Games"""
    def __init__(self, bot):
        self.bot = bot
        self.start_games.start()
        self.update_games.start()

    def cog_unload(self):
        self.start_games.cancel()
        self.update_games.cancel()

    async def get_last_games(self):
        """Get games ID from rcs_events for the most recent clan games"""
        sql = ("SELECT event_id, MAX(end_time) as end_time " 
               "FROM rcs_events "
               "WHERE event_type_id = 1 AND end_time < current_timestamp "
               "GROUP BY event_id "
               "ORDER BY end_time DESC "
               "LIMIT 1")
        row = await self.bot.pool.fetchrow(sql)
        return row['event_id'], row['end_time']

    async def get_current_games(self):
        """Get games ID from RCS-events for the current clan games, if active (else None)"""
        sql = ("SELECT event_id, player_points, clan_points  "
               "FROM rcs_events "
               "WHERE event_type_id = 1 AND current_timestamp BETWEEN start_time AND end_time")
        row = await self.bot.pool.fetchrow(sql)
        if row:
            return {"games_id": row['event_id'],
                    "player_points": row['player_points'],
                    "clan_points": row['clan_points']}
        else:
            return None

    async def get_next_games(self):
        """Get games ID from rcs_events for the next clan games, if available (else None)"""
        sql = ("SELECT event_id, MIN(start_time) as start_time "
               "FROM rcs_events "
               "WHERE event_type_id = 1 AND start_time > current_timestamp "
               "GROUP BY event_id")
        row = await self.bot.pool.fetchrow(sql)
        if row:
            return row['event_id'], row['start_time']
        else:
            return None

    async def closest_games(self):
        """Get the most recent or next games, depending on which is closest"""
        last_games_id, _last = await self.get_last_games()
        next_games_id, _next = await self.get_next_games()
        now = datetime.utcnow()
        time_to_last = now - _last
        time_to_next = _next - now
        if time_to_next > time_to_last:
            # deal with last games
            return "last", last_games_id
        else:
            # deal with next games
            return "next", next_games_id

    @tasks.loop(minutes=10)
    async def start_games(self, ctx):
        """Task to pull initial Games data for the new clan games"""
        now = datetime.utcnow()
        conn = self.bot.pool
        games_id = await self.get_next_games()
        print(f"start_games:\n  Games ID: {games_id}")
        if games_id:
            sql = "SELECT start_time FROM rcs_events WHERE event_id = $1"
            start_time = await conn.fetchval(sql, games_id)
            print(f"start_games:\n  Start Time: {start_time}")
            if start_time - now < timedelta(minutes=10):
                to_insert = []
                async for clan in self.bot.coc.get_clans(rcs_tags(prefix=True)):
                    counter = 1
                    async for member in clan.get_detailed_members():
                        to_insert.append((counter,
                                          games_id,
                                          member.tag[1:],
                                          clan.tag[1:],
                                          member.get_achievement("Games Champion").value,
                                          member.get_achievement("Games Champion").value
                                          ))
                        counter += 1
                sql = ("INSERT INTO rcs_clan_games (event_id, player_tag, clan_tag, starting_points, current_points) "
                       "SELECT x.event_id, x.player_tag, x.clan_tag, x.starting_points, x.current_points "
                       "FROM unnest($1::rcs_clan_games[]) as x")
                await conn.execute(sql, to_insert)

    @start_games.before_loop
    async def before_start_games(self):
        await self.bot.wait_until_ready()

    @tasks.loop(minutes=12)
    async def update_games(self):
        """Task to pull API data for clan games"""
        conn = self.bot.pool
        games = await self.get_current_games()
        if games:
            sql = "SELECT points_id, player_tag FROM rcs_clan_games WHERE event_id = $1"
            players = await conn.fetch(sql, games['games_id'])
            sql = "UPDATE rcs_clan_games SET current_points = $1 WHERE points_id = $2"
            for row in players:
                player = await self.bot.coc.get_player(row['player_tag'])
                await conn.execute(sql, player.get_achievement("Games Champion").value, row['points_id'])

    @update_games.before_loop
    async def before_update_games(self):
        await self.bot.wait_until_ready()

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
        games = await self.get_current_games()
        if games:
            sql = ("SELECT SUM(current_points - starting_points) AS clan_total, clan_name "
                   "FROM rcs_clan_games "
                   "WHERE event_id = $1 "
                   "ORDER BY clan_total DESC")
            fetch = await conn.fetch(sql, games['games_id'])
            data = []
            for clan in fetch:
                prefix = "* " if clan['clan_total'] >= games['clan_points'] else ""
                data.append([clan['clan_total'], prefix + clan['clan_name']])
            page_count = math.ceil(len(data) / 25)
            title = "RCS Clan Games Points"
            ctx.icon = "https://cdn.discordapp.com/emojis/639623355770732545.png"
            p = formats.TablePaginator(ctx, data=data, title=title, page_count=page_count)
            await p.paginate()
        else:
            closest, games_id = await self.closest_games()
            if closest == "next":
                sql = "SELECT start_time FROM rcs_events WHERE event_id = $1"
                next_start = await conn.fetchval(sql, games_id)
                # TODO Next line will need formatting
                return await ctx.send(f"Clan Games are not currently active. Next games starts at {next_start}")
            else:
                sql = ("SELECT SUM(current_points - starting_points) AS clan_total, clan_name "
                       "FROM rcs_clan_games "
                       "WHERE event_id = $1 "
                       "ORDER BY clan_total DESC")
                fetch = await conn.fetch(sql, games_id)
                data = []
                for clan in fetch:
                    prefix = "* " if clan['clan_total'] >= games['clan_points'] else ""
                    data.append([clan['clan_total'], prefix + clan['clan_name']])
                page_count = math.ceil(len(data) / 25)
                title = "Last Clan Games Points"
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
                   "WHERE event_type_id = 1 and start_time < NOW() "
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

        **Examples:**
        `++games add TubaKid "Reddit Oak" 2310`
        `++games add #RVP02LU0 #CVCJR89 100`
        `++games add Fredo Tau 3850`
        """
        if not player:
            return await ctx.send("Please provide a valid player tag.")
        if not clan:
            return await ctx.send("Please provide a valid clan tag.")
        if player.clan.tag == clan.tag:
            conn = self.bot.pool
            row = await conn.fetchrow("SELECT MAX(event_id) as event_id FROM rcs_events WHERE event_type_id = 1 "
                                      "AND start_time < $1", datetime.utcnow())
            event_id = row['event_id']
            try:
                starting_points = player.get_achievement("Games Champion").value - games_points
                current_points = player.get_achievement("Games Champion").value
            except:
                self.bot.logger.debug("points assignment failed for some reason")
            sql = (f"INSERT INTO rcs_clan_games (event_id, player_tag, clan_tag, starting_points, current_points) "
                   f"VALUES ($1, $2, $3, $4, $5)")
            await conn.execute(sql, event_id, player.tag[1:], player.clan.tag[1:], starting_points, current_points)
            await ctx.send(f"{player.name} ({player.clan.name}) has been added to the games database.")
        else:
            response = f"{player.name}({player.tag}) is not currently in {clan.name}({clan.tag})."
            await ctx.send(response)

    @games.command(name="correct", hidden=True)
    @is_leader_or_mod_or_council()
    async def games_correct(self, ctx, player: PlayerConverter = None, games_points: int = 0):
        """Update a score for a player whose achievement is out of whack

        **Example:**
        ++games correct #RVP02LU0 3580
        """
        if not player:
            return await ctx.send("Please provide a valid player tag.")
        conn = self.bot.pool
        row = await conn.fetchrow("SELECT MAX(event_id) as event_id FROM rcs_events "
                                  "WHERE event_type_id = 1 AND start_time < $1",
                                  datetime.utcnow())
        event_id = row['event_id']
        starting_points = player.get_achievement("Games Champion").value - games_points
        sql = ("UPDATE rcs_clan_games "
               "SET starting_points = $1 "
               "WHERE event_id = $2 AND player_tag = $3")
        await conn.execute(sql, starting_points, event_id, player.tag[1:])
        await ctx.send(f"Points for {player.name} have been updated to {games_points}.")


def setup(bot):
    bot.add_cog(Games(bot))
