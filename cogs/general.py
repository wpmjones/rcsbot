import pymssql
from loguru import logger
from discord.ext import commands
from config import settings, emojis

logger.add("general.log", rotation="100MB",
           format="{time:YYYY-MM-DD HH:mm:ss} {level} {message}", level="DEBUG")
info_string = "Printing {} for {}. Requested by {} for {}."
error_string = "User provided an incorrect argument for {}. Argument provided: {}. Requested by {} for {}."


class General(commands.Cog):
    """Cog for General bot commands"""
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="attacks", aliases=["att", "attack", "attackwin", "attackwins"])
    async def attacks(self, ctx, *, arg: str = "x"):
        """Attack wins for the whole clan"""
        conn = pymssql.connect(server=settings['database']['server'],
                               user=settings['database']['username'],
                               password=settings['database']['password'],
                               database=settings['database']['database'])
        cursor = conn.cursor(as_dict=True)
        clan_tag, clan_name = resolve_clan_tag(arg)
        if clan_tag == "x":
            logger.error(error_string, ctx.command, arg, ctx.author, ctx.guild)
            await ctx.send("You have not provided a valid clan name or clan tag.")
            return
        member_list = []
        cursor.execute(f"SELECT playerName, attackWins, timestamp FROM rcs_members WHERE clanTag = '{clan_tag}' "
                       f"AND timestamp = (SELECT TOP 1 timestamp from rcs_members WHERE clanTag = '{clan_tag}' " 
                       f"ORDER BY timestamp DESC) ORDER BY attackWins DESC")
        fetched = cursor.fetchall()
        conn.close()
        for member in fetched:
            member_list.append({"name": member['playerName'], "attacks": member['attackWins']})
        content = f"{clan_name} (#{clan_tag.upper()})\n{'Name':<20}{'Attack Wins':>12}"
        content += "\n--------------------------------"
        for item in member_list:
            content += f"\n{item['name']:20}{item['attacks']:12}"
        await self.send_text(ctx.channel, content, 1)
        logger.info(info_string, ctx.command, arg, ctx.author, ctx.guild)

    @commands.command(name="defenses", aliases=["defences", "def", "defense", "defence", "defends",
                                                "defend", "defensewins", "defencewins"])
    async def defenses(self, ctx, *, arg: str = "x"):
        """Defense wins for the whole clan"""
        conn = pymssql.connect(settings['database']['server'],
                               settings['database']['username'],
                               settings['database']['password'],
                               settings['database']['database'])
        cursor = conn.cursor(as_dict=True)
        clan_tag, clan_name = resolve_clan_tag(arg)
        if clan_tag == "x":
            logger.error(error_string, ctx.command, arg, ctx.author, ctx.guild)
            await ctx.send("You have not provided a valid clan name or clan tag.")
            return
        member_list = []
        cursor.execute(f"SELECT playerName, defenceWins, timestamp FROM rcs_members WHERE clanTag = '{clan_tag}' "
                       f"AND timestamp = (SELECT TOP 1 timestamp from rcs_members WHERE clanTag = '{clan_tag}' "
                       f"ORDER BY timestamp DESC) ORDER BY defenceWins DESC")
        fetched = cursor.fetchall()
        conn.close()
        for member in fetched:
            member_list.append({"name": member['playerName'], "defenses": member['defenceWins']})
        content = f"{clan_name} (#{clan_tag.upper()})\n{'Name':20}{'Defense Wins':>12}"
        content += "\n--------------------------------"
        for item in member_list:
            content += f"\n{item['name']:20}{item['defenses']:12}"
        await self.send_text(ctx.channel, content, 1)
        logger.info(info_string, ctx.command, arg, ctx.author, ctx.guild)

    @commands.command(name="donations", aliases=["donate", "donates", "donation"])
    async def donations(self, ctx, *, arg: str = "x"):
        """Donations for the whole clan"""
        conn = pymssql.connect(settings['database']['server'],
                               settings['database']['username'],
                               settings['database']['password'],
                               settings['database']['database'])
        cursor = conn.cursor(as_dict=True)
        clan_tag, clan_name = resolve_clan_tag(arg)
        if clan_tag == "x":
            logger.error(error_string, ctx.command, arg, ctx.author, ctx.guild)
            await ctx.send("You have not provided a valid clan name or clan tag.")
            return
        member_list = []
        cursor.execute(f"SELECT playerName, donations, donationsReceived, timestamp FROM rcs_members "
                       f"WHERE clanTag = '{clan_tag}' AND timestamp = (SELECT TOP 1 timestamp from rcs_members "
                       f"WHERE clanTag = '{clan_tag}' ORDER BY timestamp DESC) ORDER BY donations DESC")
        fetched = cursor.fetchall()
        conn.close()
        for member in fetched:
            member_list.append({"name": member['playerName'], "donations": member['donations'],
                                "received": member['donationsReceived']})
        content = f"{clan_name} (#{clan_tag.upper()})\n{'Name':10}{'Donations/Received':>20}"
        content += "\n------------------------------"
        for item in member_list:
            content += f"\n{item['name']:19}{str(item['donations']):>11}/{str(item['received'])}"
        await self.send_text(ctx.channel, content, 1)
        logger.info(info_string, ctx.command, arg, ctx.author, ctx.guild)

    @commands.command(name="trophies", aliases=["trophy"])
    async def trophies(self, ctx, *, arg: str = "x"):
        """Trophy count for the whole clan"""
        conn = pymssql.connect(settings['database']['server'],
                               settings['database']['username'],
                               settings['database']['password'],
                               settings['database']['database'])
        cursor = conn.cursor(as_dict=True)
        clan_tag, clan_name = resolve_clan_tag(arg)
        if clan_tag == "x":
            logger.error(error_string, ctx.command, arg, ctx.author, ctx.guild)
            await ctx.send("You have not provided a valid clan name or clan tag.")
            return
        member_list = []
        cursor.execute(f"SELECT playerName, trophies, timestamp FROM rcs_members WHERE clanTag = '{clan_tag}' "
                       f"AND timestamp = (SELECT TOP 1 timestamp from rcs_members WHERE clanTag = '{clan_tag}' "
                       f"ORDER BY timestamp DESC) ORDER BY trophies DESC")
        fetched = cursor.fetchall()
        conn.close()
        for member in fetched:
            member_list.append({"name": member['playerName'], "trophies": member['trophies']})
        content = f"{clan_name} (#{clan_tag.upper()})\n{'Name':20}{'Trophies':>10}"
        content += "\n------------------------------"
        for item in member_list:
            content += f"\n{item['name']:20}{str(item['trophies']):>10}"
        await self.send_text(ctx.channel, content, 1)
        logger.info(info_string, ctx.command, arg, ctx.author, ctx.guild)

    @commands.command(name="besttrophies", aliases=["besttrophy", "mosttrophies"])
    async def besttrophies(self, ctx, *, arg: str = "x"):
        """Best trophy count for the whole clan"""
        conn = pymssql.connect(settings['database']['server'], 
                               settings['database']['username'], 
                               settings['database']['password'], 
                               settings['database']['database'])
        cursor = conn.cursor(as_dict=True)
        clan_tag, clan_name = resolve_clan_tag(arg)
        if clan_tag == "x":
            logger.error(error_string, ctx.command, arg, ctx.author, ctx.guild)
            await ctx.send("You have not provided a valid clan name or clan tag.")
            return
        member_list = []
        cursor.execute(f"SELECT playerName, bestTrophies, timestamp FROM rcs_members WHERE clanTag = '{clan_tag}' "
                       f"AND timestamp = (SELECT TOP 1 timestamp from rcs_members WHERE clanTag = '{clan_tag}' "
                       f"ORDER BY timestamp DESC) ORDER BY bestTrophies DESC")
        fetched = cursor.fetchall()
        conn.close()
        for member in fetched:
            member_list.append({"name": member['playerName'], "bestTrophies": member['bestTrophies']})
        content = f"{clan_name} (#{clan_tag.upper()})\n{'Name':10}{'Best Trophies':>20}"
        content += "\n------------------------------"
        for item in member_list:
            content += f"\n{item['name']:20}{str(item['bestTrophies']):>10}"
        await self.send_text(ctx.channel, content, 1)
        logger.info(info_string, ctx.command, arg, ctx.author, ctx.guild)

    @commands.command(name="townhalls", aliases=["townhall", "th"])
    async def townhalls(self, ctx, *, arg: str = "x"):
        """List of clan members by town hall level"""
        conn = pymssql.connect(settings['database']['server'], 
                               settings['database']['username'], 
                               settings['database']['password'], 
                               settings['database']['database'])
        cursor = conn.cursor(as_dict=True)
        clan_tag, clan_name = resolve_clan_tag(arg)
        if clan_tag == "x":
            logger.error(error_string, ctx.command, arg, ctx.author, ctx.guild)
            await ctx.send("You have not provided a valid clan name or clan tag.")
            return
        member_list = []
        cursor.execute(f"SELECT playerName, thLevel, timestamp FROM rcs_members WHERE clanTag = '{clan_tag}' "
                       f"AND timestamp = (SELECT TOP 1 timestamp from rcs_members WHERE clanTag = '{clan_tag}' "
                       f"ORDER BY timestamp DESC) ORDER BY thLevel DESC, playerName")
        fetched = cursor.fetchall()
        conn.close()
        gap = emojis['other']['gap']
        for member in fetched:
            th = member['thLevel']
            member_list.append({"name": member['playerName'], "thLevel": emojis['th'][th]})
        await ctx.send(f"**{clan_name}** (#{clan_tag.upper()})")
        content = ""
        for item in member_list:
            content += f"\n{item['thLevel']} {gap}{item['name']}"
        await self.send_text(ctx.channel, content)
        logger.info(info_string, ctx.command, arg, ctx.author, ctx.guild)

    @commands.command(name="builderhalls", aliases=["builderhall", "bh"])
    async def builderhalls(self, ctx, *, arg: str = "x"):
        """List of clan members by builder hall level"""
        conn = pymssql.connect(settings['database']['server'], 
                               settings['database']['username'], 
                               settings['database']['password'], 
                               settings['database']['database'])
        cursor = conn.cursor(as_dict=True)
        clan_tag, clan_name = resolve_clan_tag(arg)
        if clan_tag == "x":
            logger.error(error_string, ctx.command, arg, ctx.author, ctx.guild)
            await ctx.send("You have not provided a valid clan name or clan tag.")
            return
        member_list = []
        cursor.execute(f"SELECT playerName, builderHallLevel, timestamp FROM rcs_members WHERE clanTag = '{clan_tag}' "
                       f"AND timestamp = (SELECT TOP 1 timestamp from rcs_members WHERE clanTag = '{clan_tag}' "
                       f"ORDER BY timestamp DESC) ORDER BY builderHallLevel DESC, playerName")
        fetched = cursor.fetchall()
        conn.close()
        gap = emojis['other']['gap']
        for member in fetched:
            bh = member['builderHallLevel']
            member_list.append({"name": member['playerName'], "bhLevel": emojis['th'][bh]})
        await ctx.send(f"**{clan_name}** (#{clan_tag.upper()})")
        content = ""
        for item in member_list:
            content += f"\n{item['bhLevel']} {gap}{item['name']}"
        await self.send_text(ctx.channel, content)
        logger.info(info_string, ctx.command, arg, ctx.author, ctx.guild)

    @commands.command(name="warstars", aliases=["stars"])
    async def warstars(self, ctx, *, arg: str = "x"):
        """List of clan members by war stars earned"""
        conn = pymssql.connect(settings['database']['server'], 
                               settings['database']['username'], 
                               settings['database']['password'], 
                               settings['database']['database'])
        cursor = conn.cursor(as_dict=True)
        clan_tag, clan_name = resolve_clan_tag(arg)
        if clan_tag == "x":
            logger.error(error_string, ctx.command, arg, ctx.author, ctx.guild)
            await ctx.send("You have not provided a valid clan name or clan tag.")
            return
        member_list = []
        cursor.execute(f"SELECT playerName, warStars, timestamp FROM rcs_members WHERE clanTag = '{clan_tag}' "
                       f"AND timestamp = (SELECT TOP 1 timestamp from rcs_members WHERE clanTag = '{clan_tag}' "
                       f"ORDER BY timestamp DESC) ORDER BY warStars DESC")
        fetched = cursor.fetchall()
        conn.close()
        for member in fetched:
            member_list.append({"name": member['playerName'], "warStars": member['warStars']})
        content = f"{clan_name} (#{clan_tag.upper()})\n{'Name':10}{'War Stars':>20}"
        content += "\n------------------------------"
        for item in member_list:
            content += f"\n{item['name']:20}{str(item['warStars']):>10}"
        await self.send_text(ctx.channel, content, 1)
        logger.info(info_string, ctx.command, arg, ctx.author, ctx.guild)

    @commands.command(name="top")
    async def top(self, ctx, category: str = "x"):
        """Lists top ten (type "++help top" for more information)
        (warstars, attacks, defenses, trophies, donations)"""
        categories = {
            "warstars": "warStars",
            "attacks": "attackWins",
            "defenses": "defenceWins",
            "defences": "defenceWins",
            "trophies": "trophies",
            "donations": "donations",
            "games": "games"
        }
        conn = pymssql.connect(settings['database']['server'], 
                               settings['database']['username'], 
                               settings['database']['password'], 
                               settings['database']['database'])
        cursor = conn.cursor(as_dict=True)
        if category not in categories:
            logger.error(error_string, ctx.command, category, ctx.author, ctx.guild)
            await ctx.send("You need to provide a valid category.\n(warstars, attacks, defenses, trophies, donations)")
            return
        if category != "games":
            field = categories[category]
            member_list = []
            cursor.execute(f"SELECT TOP 10 playerName, clanName, {field} FROM rcs_members "
                           f"INNER JOIN rcs_data ON rcs_data.clanTag = rcs_members.clanTag "
                           f"AND timestamp = (SELECT MAX(timestamp) FROM rcs_members WHERE timestamp < "
                           f"(SELECT MAX(timestamp) FROM rcs_members)) ORDER BY {field} DESC")
            fetched = cursor.fetchall()
            for member in fetched:
                member_list.append({"name": member['playerName'], "clan": member['clanName'], "amount": member[field]})
            content = "RCS Top Ten for: " + category
            content += "\n----------------------------------------"
            for item in member_list:
                content += f"\n{item['name'] + ' (' + item['clan'] + ')':33}{str(item['amount']):>7}"
            await self.send_text(ctx.channel, content, 1)
            logger.info(info_string, ctx.command, category, ctx.author, ctx.guild)
        else:
            member_list = []
            temp_table = ("CREATE TABLE #rcs_players (playerTag varchar(15), playerName nvarchar(50)) "
                          "INSERT INTO #rcs_players "
                          "SELECT DISTINCT playerTag, playerName FROM rcs_members")
            cursor.execute(temp_table)
            cursor.execute("SELECT TOP 10 b.playerName, c.clanName, (a.currentPoints - a.startingPoints) as points "
                           "FROM rcs_clanGames a "
                           "INNER JOIN #rcs_players b ON b.playerTag = a.playerTag "
                           "INNER JOIN rcs_data c ON c.clanTag = a.clanTag "
                           "WHERE eventId = (SELECT MAX(eventId) FROM rcs_events WHERE eventType = 5) "
                           "ORDER BY points DESC")
            fetched = cursor.fetchall()
            for member in fetched:
                member_list.append({"name": f"{member['playerName']} ({member['clanName']})",
                                    "points": member['points']})
            content = "RCS Top Ten for: Clan Games"
            content += "\n----------------------------------------"
            for item in member_list:
                content += f"\n{item['name']:33}{str(item['points']):>7}"
            await self.send_text(ctx.channel, content, 1)
            logger.info(info_string, ctx.command, category, ctx.author, ctx.guild)
            
    @commands.command(name="reddit", aliases=["subreddit"])
    async def reddit(self, ctx, *, arg: str = "x"):
        """Return link to specified clan's subreddit"""
        if arg == "x":
            logger.error(error_string, ctx.command, "clan missing", ctx.author, ctx.guild)
            await ctx.send("You must provide a clan name or tag.")
            return
        clan_tag, clan_name = resolve_clan_tag(arg)
        if clan_tag == "x":
            logger.error(error_string, ctx.command, arg, ctx.author, ctx.guild)
            await ctx.send("You have not provided a valid clan name or clan tag.")
            return
        conn = pymssql.connect(settings['database']['server'], 
                               settings['database']['username'], 
                               settings['database']['password'], 
                               settings['database']['database'])
        cursor = conn.cursor(as_dict=True)
        cursor.execute(f"SELECT subReddit FROM rcs_data WHERE clanTag = '{clan_tag}'")
        fetched = cursor.fetchone()
        logger.info(info_string, ctx.command, arg, ctx.author, ctx.guild)
        if fetched['subReddit'] != "":
            await ctx.send(fetched['subReddit'])
        else:
            await ctx.send("This clan does not have a subreddit.")

    async def send_text(self, channel, text, block=None):
        """ Sends text to channel, splitting if necessary """
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
    bot.add_cog(General(bot))
