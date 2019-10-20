import pymssql
import coc
import re

from discord.ext import commands
from cogs.utils.converters import ClanConverter
from cogs.utils.db import Sql
from config import settings

tag_validator = re.compile("^#?[PYLQGRJCUV0289]+$")


class Games(commands.Cog):
    """Cog for Clan Games"""
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="games_add", aliases=["games+", "ga"])
    @commands.has_any_role(settings['rcs_roles']['council'],
                           settings['rcs_roles']['chat_mods'],
                           settings['rcs_roles']['leaders'])
    async def games_add(self, ctx, player_tag, clan_tag, games_points: int):
        """Add player who missed the initial pull"""
        player_tag = coc.utils.correct_tag(player_tag)
        clan_tag = coc.utils.correct_tag(clan_tag)
        if not tag_validator.match(player_tag):
            await ctx.send("Please provide a valid player tag.")
        if not tag_validator.match(clan_tag):
            await ctx.send("Please provide a valid clan tag.")
        try:
            player = await self.bot.coc.get_player(player_tag)
        except coc.NotFound:
            raise commands.BadArgument("That looks like a player tag, but I can't find any accounts with that tag. "
                                       "Any chance it's the wrong tag?")
        if player.clan.tag == clan_tag:
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
                       f"VALUES ({event_id}, '{player.tag[1:]}', '{player.clan.tag[1:]}', "
                       f"{starting_points}, {current_points})")
                cursor.execute(sql)
            await ctx.send(f"{player.name} ({player.clan.name}) has been added to the games database.")
        else:
            response = f"{player.name}({player.tag}) is not current in {player.clan.name}({player.clan.tag})."
            await ctx.send(response)

    @commands.command()
    async def games(self, ctx, *, arg: str = 'all'):
        """Clan Games scores (type "++help games" for more information)
          (use "++games all" compare clan totals)
          (use "++games clan name/tag for clan specific scores)
          (use "++games average" to compare clan averages)"""
        with Sql(as_dict=True) as cursor:
            if arg == "all":
                clan_list = []
                cursor.execute("SELECT TOP 1 playerPoints, clanPoints " 
                               "FROM rcs_events " 
                               "WHERE eventType = 5 " 
                               "ORDER BY eventId DESC")
                row = cursor.fetchone()
                clan_points = row['clanPoints']
                cursor.callproc("rcs_spClanGamesTotal")
                for clan in cursor:
                    if clan['clanTotal'] >= clan_points:
                        clan_list.append({"name": clan['clanName'] + " *", "clan_total": clan['clanTotal']})
                    else:
                        clan_list.append({"name": clan['clanName'], "clan_total": clan['clanTotal']})
                content = f"RCS Clan Games\n{'Clan Name':20}{'Clan Total':>12}"
                content += "\n--------------------------------"
                for item in clan_list:
                    content += f"\n{item['name']:20}{item['clan_total']:12}"
                await ctx.send_text(ctx.channel, content, 1)
            elif arg in ["average", "avg", "averages"]:
                clan_list = []
                cursor.callproc("rcs_spClanGamesAverage")
                for clan in cursor:
                    clan_list.append({"name": clan['clanName'], "clan_average": clan['clanAverage']})
                content = f"RCS Clan Games\n{'Clan Name':20}{'Clan Average':>12}"
                content += "\n--------------------------------"
                for item in clan_list:
                    content += f"\n{item['name']:20}{item['clan_average']:12}"
                await ctx.send_text(ctx.channel, content, 1)
            else:
                clan = await ClanConverter().convert(ctx, arg)
                member_list = []
                cursor.execute("SELECT TOP 1 playerPoints, startTime "
                               "FROM rcs_events "
                               "WHERE eventType = 5 "
                               "ORDER BY eventId DESC")
                row = cursor.fetchone()
                player_points = row['playerPoints']
                cursor.execute("CREATE TABLE #rcs_players (playerTag varchar(15), playerName nvarchar(50)) "
                               "INSERT INTO #rcs_players "
                               "SELECT DISTINCT playerTag, playerName FROM rcs_members")
                cursor.execute(f"SELECT b.playerName, CASE WHEN (a.currentPoints - a.startingPoints) > {player_points} "
                               f"THEN {player_points} "
                               f"ELSE (a.currentPoints - a.startingPoints) END AS points "
                               f"FROM rcs_clanGames a LEFT JOIN #rcs_players b ON a.playerTag = b.playerTag "
                               f"WHERE eventId = (SELECT MAX(eventId) FROM rcs_events WHERE eventType = 5) "
                               f"AND a.clanTag = '{clan.tag[1:]}' "
                               f"ORDER BY points DESC")
                fetched = cursor.fetchall()
                cursor.callproc("rcs_spClanGamesAverage")
                for clan in cursor:
                    if clan.name.lower() == clan['clanName'].lower():
                        clan_average = clan['clanAverage']
                        break
                clan_total = 0
                for member in fetched:
                    clan_total += member['points']
                    # Compensate for NULL in fetched due to missing player in rcs_members
                    if not member['playerName']:
                        player = "Missing"
                    else:
                        player = member['playerName']
                    if member['points'] >= player_points:
                        member_list.append({"name": player + " *", "game_points": member['points']})
                    else:
                        member_list.append({"name": player, "game_points": member['points']})
                content = "```" + clan.name + " (" + clan.tag + ")"
                content += "\n{0:20}{1:>12}".format("Clan Total: ", str(clan_total))
                content += "\n{0:20}{1:>12}".format("Clan Average: ", str(clan_average))
                content += "\n{0:20}{1:>12}".format("name", "Game Points")
                content += "\n--------------------------------"
                for item in member_list:
                    content += f"\n{item['name']:20}{item['game_points']:12}"
                content += "```"
                await ctx.send(content)


def setup(bot):
    bot.add_cog(Games(bot))
