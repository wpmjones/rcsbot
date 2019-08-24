import pymssql
import coc
import re
from discord.ext import commands
from config import settings, bot_log

"""Cog for trophy push"""

tag_validator = re.compile("^#?[PYLQGRJCUV0289]+$")


class Games(commands.Cog):
    """Cog for Clan Games"""
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="games_add", aliases=["games+", "ga"])
    async def games_add(self, ctx, player_tag, clan_tag, games_points):
        """Add player who missed the initial pull"""
        player_tag = coc.utils.correct_tag(player_tag)
        clan_tag = coc.utils.correct_tag(clan_tag)
        if not tag_validator.match(player_tag):
            await ctx.send("Please provide a valid player tag.")
        if not tag_validator.match(clan_tag):
            await ctx.send("Please provide a valid clan tag.")
        self.bot.logger.info("Player and clan tags are good.")
        try:
            player = await self.bot.coc_client.get_player(player_tag)
        except coc.NotFound:
            raise commands.BadArgument("That looks like a player tag, but I can't find any accounts with that tag. "
                                       "Any chance it's the wrong tag?")
        self.bot.logger.debug(f"COC info: {player.clan.tag}\nProvided info: {clan_tag}")
        if player.clan.tag == clan_tag:
            conn = pymssql.connect(server=settings['database']['server'],
                                   user=settings['database']['username'],
                                   password=settings['database']['password'],
                                   database=settings['database']['database'])
            conn.autocommit(True)
            cursor = conn.cursor(as_dict=True)
            cursor.execute("SELECT MAX(eventId) FROM rcs_events WHERE eventTypeId = 5")
            row = cursor.fetchone()
            event_id = row['eventId']
            starting_points = player.achievements_dict['Games Champion'].value - games_points
            current_points = player.achievements_dict['Games Champion'].value
            sql = (f"INSERT INTO rcs_clanGames (eventId, playerTag, clanTag, startingPoints, currentPoints) "
                   f"VALUES ({event_id}, {player.tag[1:]}, {player.clan.tag[1:]}, {starting_points}, {current_points})")
            cursor.execute(sql)
            conn.close()
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
        conn = pymssql.connect(server=settings['database']['server'],
                               user=settings['database']['username'],
                               password=settings['database']['password'],
                               database=settings['database']['database'])
        conn.autocommit(True)
        cursor = conn.cursor(as_dict=True)
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
            conn.close()
            content = f"RCS Clan Games\n{'Clan Name':20}{'Clan Total':>12}"
            content += "\n--------------------------------"
            for item in clan_list:
                content += f"\n{item['name']:20}{item['clan_total']:12}"
            await self.send_text(ctx.channel, content, 1)
            bot_log(ctx.command, arg, ctx.author, ctx.guild)
        elif arg in ["average", "avg", "averages"]:
            clan_list = []
            cursor.callproc("rcs_spClanGamesAverage")
            for clan in cursor:
                clan_list.append({"name": clan['clanName'], "clan_average": clan['clanAverage']})
            conn.close()
            content = f"RCS Clan Games\n{'Clan Name':20}{'Clan Average':>12}"
            content += "\n--------------------------------"
            for item in clan_list:
                content += f"\n{item['name']:20}{item['clan_average']:12}"
            await self.send_text(ctx.channel, content, 1)
            bot_log(ctx.command, arg, ctx.author, ctx.guild)
        else:
            clan_tag, clan_name = resolve_clan_tag(arg)
            if clan_tag == "x":
                bot_log(ctx.command, arg, ctx.author, ctx.guild, 1)
                await ctx.send("You have not provided a valid clan name or clan tag.")
                return
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
                           f"AND a.clanTag = '{clan_tag}' "
                           f"ORDER BY points DESC")
            fetched = cursor.fetchall()
            cursor.callproc("rcs_spClanGamesAverage")
            for clan in cursor:
                if clan_name.lower() == clan['clanName'].lower():
                    clan_average = clan['clanAverage']
                    break
            conn.close()
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
            content = "```" + clan_name + " (#" + clan_tag.upper() + ")"
            content += "\n{0:20}{1:>12}".format("Clan Total: ", str(clan_total))
            content += "\n{0:20}{1:>12}".format("Clan Average: ", str(clan_average))
            content += "\n{0:20}{1:>12}".format("name", "Game Points")
            content += "\n--------------------------------"
            for item in member_list:
                content += f"\n{item['name']:20}{item['game_points']:12}"
            content += "```"
            bot_log(ctx.command, arg, ctx.author, ctx.guild)
            await ctx.send(content)

    async def send_text(self, channel, text, block=None):
        """ Sends text to channel, splitting if necessary
        Discord has a 2000 character limit
        """
        if len(text) < 2000:
            if block:
                await channel.send(f"```{text}```")
            else:
                await channel.send(text)
        else:
            coll = ""
            for line in text.splitlines(keepends=True):
                if len(coll) + len(line) > 1994:
                    # if collecting is going to be too long, send  what you have so far
                    if block:
                        await channel.send(f"```{coll}```")
                    else:
                        await channel.send(coll)
                    coll = ""
                coll += line
            if block:
                await channel.send(f"```{coll}```")
            else:
                await channel.send(coll)


def get_clan_name(clan_tag):
    for clan in clans:
        if clan['clanTag'].lower() == clan_tag.lower():
            return clan['clanName']
    return "x"


def get_clan_tag(clan_name):
    for clan in clans:
        if clan['clanName'].lower() == clan_name.lower():
            return clan['clanTag']
    return "x"


def resolve_clan_tag(clan_input):
    if clan_input.startswith("#"):
        clan_tag = clan_input[1:]
        clan_name = get_clan_name(clan_tag)
    else:
        clan_tag = get_clan_tag(clan_input)
        clan_name = clan_input
        if clan_tag == "x":
            clan_name = get_clan_name(clan_input)
            clan_tag = clan_input
            if clan_name == "x":
                return "x", "x"
    return clan_tag, clan_name


mainConn = pymssql.connect(settings['database']['server'],
                           settings['database']['username'], 
                           settings['database']['password'], 
                           settings['database']['database'])
mainCursor = mainConn.cursor(as_dict=True)
mainCursor.execute("SELECT clanName, clanTag FROM rcs_data ORDER BY clanName")
clans = mainCursor.fetchall()
mainConn.close()


def setup(bot):
    bot.add_cog(Games(bot))
