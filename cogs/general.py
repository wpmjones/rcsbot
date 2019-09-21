import pymssql
import discord
from cogs.utils.converters import PlayerConverter
from cogs.utils.constants import cwl_league_names, cwl_league_order
from loguru import logger
from discord.ext import commands
from config import settings, emojis

logger.add("general.log", rotation="100MB",
           format="{time:YYYY-MM-DD HH:mm:ss} {level} {message}", level="INFO")
info_string = "Printing {} for {}. Requested by {} for {}."
error_string = "User provided an incorrect argument for {}. Argument provided: {}. Requested by {} for {}."


class General(commands.Cog):
    """Cog for General bot commands"""
    def __init__(self, bot):
        self.bot = bot
        conn = pymssql.connect(settings['database']['server'],
                               settings['database']['username'],
                               settings['database']['password'],
                               settings['database']['database'])
        cursor = conn.cursor(as_dict=True)
        cursor.execute("SELECT clanName, clanTag FROM rcs_data ORDER BY clanName")
        self.clans = cursor.fetchall()
        conn.close()

    @commands.command(name="attacks", aliases=["att", "attack", "attackwin", "attackwins"])
    async def attacks(self, ctx, *, arg: str = "x"):
        """Attack wins for the whole clan"""
        conn = pymssql.connect(server=settings['database']['server'],
                               user=settings['database']['username'],
                               password=settings['database']['password'],
                               database=settings['database']['database'])
        cursor = conn.cursor(as_dict=True)
        clan_tag, clan_name = self.resolve_clan_tag(arg)
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
        clan_tag, clan_name = self.resolve_clan_tag(arg)
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
        clan_tag, clan_name = self.resolve_clan_tag(arg)
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
        clan_tag, clan_name = self.resolve_clan_tag(arg)
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

    @commands.command(name="bhtrophies", aliases=["bhtrophy", "bh_trophies"])
    async def bh_trophies(self, ctx, *, arg: str = "x"):
        """Trophy count for the whole clan"""
        conn = pymssql.connect(settings['database']['server'],
                               settings['database']['username'],
                               settings['database']['password'],
                               settings['database']['database'])
        cursor = conn.cursor(as_dict=True)
        clan_tag, clan_name = self.resolve_clan_tag(arg)
        if clan_tag == "x":
            logger.error(error_string, ctx.command, arg, ctx.author, ctx.guild)
            await ctx.send("You have not provided a valid clan name or clan tag.")
            return
        member_list = []
        cursor.execute(f"SELECT playerName, vsTrophies, timestamp FROM rcs_members WHERE clanTag = '{clan_tag}' "
                       f"AND timestamp = (SELECT TOP 1 timestamp from rcs_members WHERE clanTag = '{clan_tag}' "
                       f"ORDER BY timestamp DESC) ORDER BY trophies DESC")
        fetched = cursor.fetchall()
        conn.close()
        for member in fetched:
            member_list.append({"name": member['playerName'], "trophies": member['vsTrophies']})
        content = f"{clan_name} (#{clan_tag.upper()})\n{'Name':20}{'BH Trophies':>10}"
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
        clan_tag, clan_name = self.resolve_clan_tag(arg)
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
        clan_tag, clan_name = self.resolve_clan_tag(arg)
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
        clan_tag, clan_name = self.resolve_clan_tag(arg)
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
        clan_tag, clan_name = self.resolve_clan_tag(arg)
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

    @commands.command(name="link")
    @commands.has_any_role(settings['rcsRoles']['council'],
                           settings['rcsRoles']['chatMods'],
                           settings['rcsRoles']['leaders'])
    async def link(self, ctx, member: discord.Member, player_tag):
        try:
            player = await PlayerConverter().convert(ctx, player_tag)
        except:
            self.bot.logger.error(f"{ctx.author} provided {player_tag} for the link command.")
            # TODO Provide some random fun here
            return await ctx.send("I don't particularly care for that player tag. Wanna try again?")
        print(player.name)
        if player.clan.tag[1:] in [clan['clanTag'] for clan in self.clans]:
            try:
                await self.bot.db.link_user(player.tag[1:], member.id)
                emoji = "\u2705"
                member_role = ctx.guild.get_role(settings['rcsRoles']['members'])
                await member.add_roles(member_role)
                await ctx.message.add_reaction(emoji)
            except:
                self.bot.logger.exception("Something went wrong while adding a discord link")
                await ctx.send("I'm sorry, but something has gone wrong. I notified the important people and they will "
                               "look into it for you.")
        else:
            await ctx.send(f"I see that {player.name} is in {player.clan} which is not an RCS clan. Try again "
                           f"when you are in an RCS clan.")

    @commands.command(name="reddit", aliases=["subreddit"])
    async def reddit(self, ctx, *, arg: str = "x"):
        """Return link to specified clan's subreddit"""
        if arg == "x":
            logger.error(error_string, ctx.command, "clan missing", ctx.author, ctx.guild)
            await ctx.send("You must provide a clan name or tag.")
            return
        clan_tag, clan_name = self.resolve_clan_tag(arg)
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

    @commands.command(name="discord")
    async def discord(self, ctx, *, arg: str = "x"):
        """Return link to specified clan's Discord server"""
        if arg == "x":
            logger.error(error_string, ctx.command, "clan missing", ctx.author, ctx.guild)
            await ctx.send("You must provide a clan name or tag.")
            return
        clan_tag, clan_name = self.resolve_clan_tag(arg)
        if clan_tag == "x":
            logger.error(error_string, ctx.command, arg, ctx.author, ctx.guild)
            await ctx.send("You have not provided a valid clan name or clan tag.")
            return
        conn = pymssql.connect(settings['database']['server'],
                               settings['database']['username'],
                               settings['database']['password'],
                               settings['database']['database'])
        cursor = conn.cursor(as_dict=True)
        cursor.execute(f"SELECT discordServer FROM rcs_data WHERE clanTag = '{clan_tag}'")
        fetched = cursor.fetchone()
        logger.info(info_string, ctx.command, arg, ctx.author, ctx.guild)
        if fetched['discordServer'] != "":
            await ctx.send(fetched['discordServer'])
        else:
            await ctx.send("This clan does not have a Discord server.")

    @commands.command(name="cwl")
    async def cwl(self, ctx, *args):
        conn = pymssql.connect(server=settings['database']['server'],
                               user=settings['database']['username'],
                               password=settings['database']['password'],
                               database=settings['database']['database'])
        cursor = conn.cursor(as_dict=True)
        # Respond with list
        if args[0] in ["all", "list"]:
            cursor.execute("SELECT clanName, clanTag, cwlLeague FROM rcs_data "
                           "WHERE cwlLeague IS NOT NULL "
                           "ORDER BY clanName")
            clans = cursor.fetchall()
            content = ""
            for league in cwl_league_order:
                header = f"**{league}:**\n"
                temp = ""
                for clan in clans:
                    if clan['cwlLeague'] == league:
                        temp += f"  {clan['clanName']} (#{clan['clanTag']})\n"
                if temp:
                    content += header + temp
            return await ctx.send(content)
        # Handle user arguments
        cursor.execute("SELECT clanName, clanTag, discordTag FROM rcs_data ORDER BY clanName")
        fetched = cursor.fetchall()
        clans = []
        clans_tag = []
        for clan in fetched:
            clans.append(clan["clanName"].lower())
            clans_tag.append([clan["clanTag"], clan["clanName"], clan["discordTag"]])
        leagues = cwl_league_names
        league_num = "I"
        if args[-1].lower() in ["3", "iii", "three"]:
            league_num = "III"
        if args[-1] in ["2", "ii", "two"]:
            league_num = "II"
        if len(args) == 4:
            clan = f"{args[0]} {args[1]}"
            league = f"{args[2]} {league_num}"
        elif len(args) == 3:
            clan = f"{args[0]}"
            league = f"{args[1]} {league_num}"
        elif len(args) == 5:
            clan = f"{args[0]} {args[1]} {args[2]}"
            league = f"{args[3]} {league_num}"
        else:
            await ctx.send("Please provide a clan name and CWL league in that order. `++cwl Reddit Example Bronze II`")
            return
        self.bot.logger.debug(f"{ctx.command} for {ctx.author}\n{args}\n{clan}\n{league}")
        if clan.lower() in clans and league.lower() in leagues:
            if args[-2].lower() in ["master", "masters"]:
                league = f"Master {league_num}"
            elif args[-2].lower() in ["champ", "champs", "champion", "champions"]:
                league = f"Champion {league_num}"
            else:
                league = f"{args[-2].title()} {league_num}"
            for clan_tuple in clans_tag:
                if clan.lower() == clan_tuple[1].lower():
                    clan = clan_tuple[1]
                    clan_tag = clan_tuple[0]
                    leader = clan_tuple[2]
                    break
            cursor.execute(f"UPDATE rcs_data "
                           f"SET cwlLeague = '{league}' "
                           f"WHERE clanTag = '{clan_tag}'")
            conn.commit()
            conn.close()
            logger.debug(f"Context ID: {ctx.author.id}\nLeader Tag: {leader}")
            if str(ctx.author.id) == str(leader):
                await ctx.send("Update complete!")
            else:
                try:
                    leader_chat = self.bot.get_channel(settings["rcsChannels"]["leaderChat"])
                    await leader_chat.send(f"<@{leader}> {clan}'s CWL league has been updated to {league} "
                                           f"by {ctx.author.mention}.")
                    await ctx.send("Update complete!")
                except:
                    logger.exception("Failed to send to Leader Chat")

        else:
            await ctx.send("Please provide a clan name and CWL league in that order. `++cwl Reddit Example Bronze ii`")
            return

    @staticmethod
    async def send_text(channel, text, block=None):
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

    def get_clan_name(self, clan_tag):
        for clan in self.clans:
            if clan['clanTag'].lower() == clan_tag.lower():
                return clan['clanName']
        return "x"

    def get_clan_tag(self, clan_name):
        for clan in self.clans:
            if clan['clanName'].lower() == clan_name.lower():
                return clan['clanTag']
        return "x"

    def resolve_clan_tag(self, clan_input):
        if clan_input.startswith("#"):
            clan_tag = clan_input[1:]
            clan_name = self.get_clan_name(clan_tag)
        else:
            clan_tag = self.get_clan_tag(clan_input)
            clan_name = clan_input
            if clan_tag == "x":
                clan_name = self.get_clan_name(clan_input)
                clan_tag = clan_input
                if clan_name == "x":
                    return "x", "x"
        return clan_tag, clan_name


def setup(bot):
    bot.add_cog(General(bot))
