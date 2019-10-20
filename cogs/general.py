import discord
import math

from discord.ext import commands
from cogs.utils.db import Sql
from cogs.utils.converters import PlayerConverter, ClanConverter
from cogs.utils.constants import cwl_league_names, cwl_league_order
from cogs.utils import formats
from config import settings, emojis


class General(commands.Cog):
    """Cog for General bot commands"""
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="attacks", aliases=["att", "attack", "attackwin", "attackwins"])
    async def attacks(self, ctx, *, clan: ClanConverter = None):
        """Attack wins for the whole clan"""
        if not clan:
            return await ctx.send("You have not provided a valid clan name or clan tag.")
        async with ctx.typing():
            # with Sql() as cursor:
            #     cursor.execute("SELECT attackWins, playerName FROM rcs_members WHERE clanTag = %s "
            #                    "AND timestamp = (SELECT TOP 1 timestamp from rcs_members WHERE clanTag = %s "
            #                    "ORDER BY timestamp DESC) ORDER BY attackWins DESC", (clan.tag[1:], clan.tag[1:]))
            #     fetch = cursor.fetchall()
            sql = "SELECT attack_wins, player_name FROM rcs_members WHERE player_name = 'Royal' LIMIT 25"
            fetch = await ctx.db.fetch(sql)
            page_count = math.ceil(len(fetch) / 20)
            title = f"{clan.name} ({clan.tag})"
            ctx.config.render = 1
            p = formats.BoardPaginator(ctx, data=fetch, title=title, page_count=page_count)
        await p.paginate()

    @commands.command(name="defenses", aliases=["defences", "def", "defense", "defence", "defends",
                                                "defend", "defensewins", "defencewins"])
    async def defenses(self, ctx, *, clan: ClanConverter = None):
        """Defense wins for the whole clan"""
        if not clan:
            return await ctx.send("You have not provided a valid clan name or clan tag.")
        with Sql(as_dict=True) as cursor:
            member_list = []
            cursor.execute(f"SELECT playerName, defenceWins, timestamp FROM rcs_members WHERE clanTag = '{clan.tag[1:]}' "
                           f"AND timestamp = (SELECT TOP 1 timestamp from rcs_members WHERE clanTag = '{clan.tag[1:]}' "
                           f"ORDER BY timestamp DESC) ORDER BY defenceWins DESC")
            fetched = cursor.fetchall()
        for member in fetched:
            member_list.append({"name": member['playerName'], "defenses": member['defenceWins']})
        content = f"{clan.name} ({clan.tag})\n{'Name':20}{'Defense Wins':>12}"
        content += "\n--------------------------------"
        for item in member_list:
            content += f"\n{item['name']:20}{item['defenses']:12}"
        await ctx.send_text(ctx.channel, content, 1)

    @commands.command(name="donations", aliases=["donate", "donates", "donation"])
    async def donations(self, ctx, *, clan: ClanConverter = None):
        """Donations for the whole clan"""
        if not clan:
            return await ctx.send("You have not provided a valid clan name or clan tag.")
        with Sql(as_dict=True) as cursor:
            member_list = []
            cursor.execute(f"SELECT playerName, donations, donationsReceived, timestamp FROM rcs_members "
                           f"WHERE clanTag = '{clan.tag[1:]}' AND timestamp = (SELECT TOP 1 timestamp from rcs_members "
                           f"WHERE clanTag = '{clan.tag[1:]}' ORDER BY timestamp DESC) ORDER BY donations DESC")
            fetched = cursor.fetchall()
        for member in fetched:
            member_list.append({"name": member['playerName'], "donations": member['donations'],
                                "received": member['donationsReceived']})
        content = f"{clan.name} ({clan.tag})\n{'Name':10}{'Donations/Received':>20}"
        content += "\n------------------------------"
        for item in member_list:
            content += f"\n{item['name']:19}{str(item['donations']):>11}/{str(item['received'])}"
        await ctx.send_text(ctx.channel, content, 1)

    @commands.command(name="trophies", aliases=["trophy"])
    async def trophies(self, ctx, *, clan: ClanConverter = None):
        """Trophy count for the whole clan"""
        if not clan:
            return await ctx.send("You have not provided a valid clan name or clan tag.")
        with Sql(as_dict=True) as cursor:
            member_list = []
            cursor.execute(f"SELECT playerName, trophies, timestamp FROM rcs_members WHERE clanTag = '{clan.tag[1:]}' "
                           f"AND timestamp = (SELECT TOP 1 timestamp from rcs_members WHERE clanTag = '{clan.tag[1:]}' "
                           f"ORDER BY timestamp DESC) ORDER BY trophies DESC")
            fetched = cursor.fetchall()
        for member in fetched:
            member_list.append({"name": member['playerName'], "trophies": member['trophies']})
        content = f"{clan.name} ({clan.tag})\n{'Name':20}{'Trophies':>10}"
        content += "\n------------------------------"
        for item in member_list:
            content += f"\n{item['name']:20}{str(item['trophies']):>10}"
        await ctx.send_text(ctx.channel, content, 1)

    @commands.command(name="bhtrophies", aliases=["bhtrophy", "bh_trophies"])
    async def bh_trophies(self, ctx, *, clan: ClanConverter = None):
        """Trophy count for the whole clan"""
        if not clan:
            return await ctx.send("You have not provided a valid clan name or clan tag.")
        with Sql(as_dict=True) as cursor:
            member_list = []
            cursor.execute(f"SELECT playerName, vsTrophies, timestamp FROM rcs_members WHERE clanTag = '{clan.tag[1:]}' "
                           f"AND timestamp = (SELECT TOP 1 timestamp from rcs_members WHERE clanTag = '{clan.tag[1:]}' "
                           f"ORDER BY timestamp DESC) ORDER BY vsTrophies DESC")
            fetched = cursor.fetchall()
        for member in fetched:
            member_list.append({"name": member['playerName'], "trophies": member['vsTrophies']})
        content = f"{clan.name} ({clan.tag})\n{'Name':20}{'BH Trophies':>10}"
        content += "\n------------------------------"
        for item in member_list:
            content += f"\n{item['name']:20}{str(item['trophies']):>10}"
        await ctx.send_text(ctx.channel, content, 1)

    @commands.command(name="besttrophies", aliases=["besttrophy", "mosttrophies"])
    async def besttrophies(self, ctx, *, clan: ClanConverter = None):
        """Best trophy count for the whole clan"""
        if not clan:
            return await ctx.send("You have not provided a valid clan name or clan tag.")
        with Sql(as_dict=True) as cursor:
            member_list = []
            cursor.execute(f"SELECT playerName, bestTrophies, timestamp FROM rcs_members WHERE clanTag = '{clan.tag[1:]}' "
                           f"AND timestamp = (SELECT TOP 1 timestamp from rcs_members WHERE clanTag = '{clan.tag[1:]}' "
                           f"ORDER BY timestamp DESC) ORDER BY bestTrophies DESC")
            fetched = cursor.fetchall()
        for member in fetched:
            member_list.append({"name": member['playerName'], "bestTrophies": member['bestTrophies']})
        content = f"{clan.name} ({clan.tag})\n{'Name':10}{'Best Trophies':>20}"
        content += "\n------------------------------"
        for item in member_list:
            content += f"\n{item['name']:20}{str(item['bestTrophies']):>10}"
        await ctx.send_text(ctx.channel, content, 1)

    @commands.command(name="townhalls", aliases=["townhall", "th"])
    async def townhalls(self, ctx, *, clan: ClanConverter = None):
        """List of clan members by town hall level"""
        if not clan:
            return await ctx.send("You have not provided a valid clan name or clan tag.")
        with Sql(as_dict=True) as cursor:
            member_list = []
            cursor.execute(f"SELECT playerName, thLevel, timestamp FROM rcs_members WHERE clanTag = '{clan.tag[1:]}' "
                           f"AND timestamp = (SELECT TOP 1 timestamp from rcs_members WHERE clanTag = '{clan.tag[1:]}' "
                           f"ORDER BY timestamp DESC) ORDER BY thLevel DESC, playerName")
            fetched = cursor.fetchall()
        gap = emojis['other']['gap']
        for member in fetched:
            th = member['thLevel']
            member_list.append({"name": member['playerName'], "thLevel": emojis['th'][th]})
        await ctx.send(f"**{clan.name}** ({clan.tag})")
        content = ""
        for item in member_list:
            content += f"\n{item['thLevel']} {gap}{item['name']}"
        await ctx.send_text(ctx.channel, content)

    @commands.command(name="builderhalls", aliases=["builderhall", "bh"])
    async def builderhalls(self, ctx, *, clan: ClanConverter = None):
        """List of clan members by builder hall level"""
        if not clan:
            return await ctx.send("You have not provided a valid clan name or clan tag.")
        with Sql(as_dict=True) as cursor:
            member_list = []
            cursor.execute(f"SELECT playerName, builderHallLevel, timestamp FROM rcs_members WHERE clanTag = '{clan.tag[1:]}' "
                           f"AND timestamp = (SELECT TOP 1 timestamp from rcs_members WHERE clanTag = '{clan.tag[1:]}' "
                           f"ORDER BY timestamp DESC) ORDER BY builderHallLevel DESC, playerName")
            fetched = cursor.fetchall()
        gap = emojis['other']['gap']
        for member in fetched:
            bh = member['builderHallLevel']
            member_list.append({"name": member['playerName'], "bhLevel": emojis['th'][bh]})
        await ctx.send(f"**{clan.name}** ({clan.tag})")
        content = ""
        for item in member_list:
            content += f"\n{item['bhLevel']} {gap}{item['name']}"
        await ctx.send_text(ctx.channel, content)

    @commands.command(name="warstars", aliases=["stars"])
    async def warstars(self, ctx, *, clan: ClanConverter = None):
        """List of clan members by war stars earned"""
        if not clan:
            return await ctx.send("You have not provided a valid clan name or clan tag.")
        with Sql(as_dict=True) as cursor:
            member_list = []
            cursor.execute(f"SELECT playerName, warStars, timestamp FROM rcs_members WHERE clanTag = '{clan.tag[1:]}' "
                           f"AND timestamp = (SELECT TOP 1 timestamp from rcs_members WHERE clanTag = '{clan.tag[1:]}' "
                           f"ORDER BY timestamp DESC) ORDER BY warStars DESC")
            fetched = cursor.fetchall()
        for member in fetched:
            member_list.append({"name": member['playerName'], "warStars": member['warStars']})
        content = f"{clan.name} ({clan.tag})\n{'Name':10}{'War Stars':>20}"
        content += "\n------------------------------"
        for item in member_list:
            content += f"\n{item['name']:20}{str(item['warStars']):>10}"
        await ctx.send_text(ctx.channel, content, 1)

    @commands.command(name="top")
    async def top(self, ctx, category: str = "x"):
        """Lists top ten (type "++help top" for more information)
        (warstars, attacks, defenses, trophies, bhtrophies, donations, games)"""
        categories = {
            "warstars": "warStars",
            "attacks": "attackWins",
            "defenses": "defenceWins",
            "defences": "defenceWins",
            "trophies": "trophies",
            "bhtrophies": "vsTrophies",
            "bh_trophies": "vsTrophies",
            "donations": "donations",
            "games": "games"
        }
        if category not in categories:
            return await ctx.send("You need to provide a valid category.\n"
                                  "(warstars, attacks, defenses, trophies, bhtrophies, donations, games)")
        with Sql(as_dict=True) as cursor:
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
                await ctx.send_text(ctx.channel, content, 1)
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
                await ctx.send_text(ctx.channel, content, 1)

    @commands.command(name="link")
    @commands.has_any_role(settings['rcs_roles']['council'],
                           settings['rcs_roles']['chat_mods'],
                           settings['rcs_roles']['leaders'])
    async def link(self, ctx, member: discord.Member, player_tag):
        try:
            player = await PlayerConverter().convert(ctx, player_tag)
        except:
            self.bot.logger.error(f"{ctx.author} provided {player_tag} for the link command.")
            # TODO Provide some random fun here
            return await ctx.send("I don't particularly care for that player tag. Wanna try again?")
        if player.clan.tag[1:] in self.bot.rcs_clans.values():
            try:
                await self.bot.db.link_user(player.tag[1:], member.id)
                emoji = "\u2705"
                member_role = ctx.guild.get_role(settings['rcs_roles']['members'])
                await member.add_roles(member_role)
                await ctx.message.add_reaction(emoji)
            except:
                self.bot.logger.exception("Something went wrong while adding a discord link")
                await ctx.send("I'm sorry, but something has gone wrong. I notified the important people and they will "
                               "look into it for you.")
        else:
            await ctx.send(f"I see that {player.name} is in {player.clan} which is not an RCS clan. Try again "
                           f"when {player.name} is in an RCS clan.")

    @commands.command(name="reddit", aliases=["subreddit"])
    async def reddit(self, ctx, *, clan: ClanConverter = None):
        """Return link to specified clan's subreddit"""
        if not clan:
            return await ctx.send("You must provide an RCS clan name or tag.")
        with Sql(as_dict=True) as cursor:
            cursor.execute(f"SELECT subReddit FROM rcs_data WHERE clanTag = '{clan.tag[1:]}'")
            fetched = cursor.fetchone()
        if fetched['subReddit'] != "":
            await ctx.send(fetched['subReddit'])
        else:
            await ctx.send("This clan does not have a subreddit.")

    @commands.command(name="discord")
    async def discord(self, ctx, *, clan: ClanConverter = None):
        """Return link to specified clan's Discord server"""
        if not clan:
            return await ctx.send("You must provide an RCS clan name or tag.")
        with Sql(as_dict=True) as cursor:
            cursor.execute(f"SELECT discordServer FROM rcs_data WHERE clanTag = '{clan.tag[1:]}'")
            fetched = cursor.fetchone()
        if fetched['discordServer'] != "":
            await ctx.send(fetched['discordServer'])
        else:
            await ctx.send("This clan does not have a Discord server.")

    @commands.command(name="cwl")
    async def cwl(self, ctx, *args):
        # Respond with list
        if args[0] in ["all", "list"]:
            with Sql(as_dict=True) as cursor:
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
        with Sql(as_dict=True) as cursor:
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
                return await ctx.send("Please provide a clan name and CWL league in that order. "
                                      "`++cwl Reddit Example Bronze II`")
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
                await ctx.send("Update complete!")
                if str(ctx.author.id) != str(leader):
                    try:
                        leader_chat = self.bot.get_channel(settings["rcs_channels"]["leader_chat"])
                        await leader_chat.send(f"<@{leader}> {clan}'s CWL league has been updated to {league} "
                                               f"by {ctx.author.mention}.")
                        await ctx.send("Update complete!")
                    except:
                        self.bot.logger.exception("Failed to send to Leader Chat")
            else:
                return await ctx.send("Please provide a clan name and CWL league in that order. "
                                      "`++cwl Reddit Example Bronze ii`")


def setup(bot):
    bot.add_cog(General(bot))
