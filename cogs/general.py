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
            with Sql() as cursor:
                cursor.execute("SELECT attackWins, playerName FROM rcs_members WHERE clanTag = %s "
                               "AND timestamp = (SELECT TOP 1 timestamp from rcs_members WHERE clanTag = %s "
                               "ORDER BY timestamp DESC) ORDER BY attackWins DESC", (clan.tag[1:], clan.tag[1:]))
                fetch = cursor.fetchall()
            page_count = math.ceil(len(fetch) / 25)
            title = f"Attack Wins for {clan.name}"
            ctx.icon = "https://cdn.discordapp.com/emojis/635642869750824980.png"
            p = formats.TablePaginator(ctx, data=fetch, title=title, page_count=page_count)
        await p.paginate()

    @commands.command(name="defenses", aliases=["defences", "def", "defense", "defence", "defends",
                                                "defend", "defensewins", "defencewins"])
    async def defenses(self, ctx, *, clan: ClanConverter = None):
        """Defense wins for the whole clan"""
        if not clan:
            return await ctx.send("You have not provided a valid clan name or clan tag.")
        async with ctx.typing():
            with Sql() as cursor:
                cursor.execute("SELECT defenceWins, playerName FROM rcs_members WHERE clanTag = %s "
                               "AND timestamp = (SELECT TOP 1 timestamp from rcs_members WHERE clanTag = %s "
                               "ORDER BY timestamp DESC) ORDER BY defenceWins DESC", (clan.tag[1:], clan.tag[1:]))
                fetch = cursor.fetchall()
            page_count = math.ceil(len(fetch) / 25)
            title = f"Defense Wins for {clan.name}"
            ctx.icon = "https://cdn.discordapp.com/emojis/635642869373468704.png"
            p = formats.TablePaginator(ctx, data=fetch, title=title, page_count=page_count)
        await p.paginate()

    @commands.command(name="donations", aliases=["donate", "donates", "donation"])
    async def donations(self, ctx, *, clan: ClanConverter = None):
        """Donations for the whole clan"""
        if not clan:
            return await ctx.send("You have not provided a valid clan name or clan tag.")
        with Sql() as cursor:
            cursor.execute(f"SELECT donations, donationsReceived, playerName FROM rcs_members "
                           f"WHERE clanTag = %s AND timestamp = (SELECT TOP 1 timestamp from rcs_members "
                           f"WHERE clanTag = %s ORDER BY timestamp DESC) ORDER BY donations DESC",
                           (clan.tag[1:], clan.tag[1:]))
            fetch = cursor.fetchall()
            page_count = math.ceil(len(fetch) / 25)
            title = f"Donations for {clan.name}"
            ctx.icon = "https://cdn.discordapp.com/emojis/301032036779425812.png"
            p = formats.TablePaginator(ctx, data=fetch, title=title, page_count=page_count)
        await p.paginate()

    @commands.command(name="trophies", aliases=["trophy"])
    async def trophies(self, ctx, *, clan: ClanConverter = None):
        """Trophy count for the whole clan"""
        if not clan:
            return await ctx.send("You have not provided a valid clan name or clan tag.")
        async with ctx.typing():
            with Sql() as cursor:
                cursor.execute("SELECT trophies, playerName FROM rcs_members WHERE clanTag = %s "
                               "AND timestamp = (SELECT TOP 1 timestamp from rcs_members WHERE clanTag = %s "
                               "ORDER BY timestamp DESC) ORDER BY trophies DESC", (clan.tag[1:], clan.tag[1:]))
                fetch = cursor.fetchall()
            page_count = math.ceil(len(fetch) / 25)
            title = f"Trophies for {clan.name}"
            ctx.icon = "https://cdn.discordapp.com/emojis/635642869738111016.png"
            p = formats.TablePaginator(ctx, data=fetch, title=title, page_count=page_count)
        await p.paginate()

    @commands.command(name="bhtrophies", aliases=["bhtrophy", "bh_trophies"])
    async def bh_trophies(self, ctx, *, clan: ClanConverter = None):
        """Trophy count for the whole clan"""
        if not clan:
            return await ctx.send("You have not provided a valid clan name or clan tag.")
        async with ctx.typing():
            with Sql() as cursor:
                cursor.execute("SELECT vsTrophies, playerName FROM rcs_members WHERE clanTag = %s "
                               "AND timestamp = (SELECT TOP 1 timestamp from rcs_members WHERE clanTag = %s "
                               "ORDER BY timestamp DESC) ORDER BY vsTrophies DESC", (clan.tag[1:], clan.tag[1:]))
                fetch = cursor.fetchall()
            page_count = math.ceil(len(fetch) / 25)
            title = f"Builder Trophies for {clan.name}"
            ctx.icon = "https://cdn.discordapp.com/emojis/635642869738111016.png"
            p = formats.TablePaginator(ctx, data=fetch, title=title, page_count=page_count)
        await p.paginate()

    @commands.command(name="besttrophies", aliases=["besttrophy", "mosttrophies"])
    async def besttrophies(self, ctx, *, clan: ClanConverter = None):
        """Best trophy count for the whole clan"""
        if not clan:
            return await ctx.send("You have not provided a valid clan name or clan tag.")
        async with ctx.typing():
            with Sql() as cursor:
                cursor.execute("SELECT bestTrophies, playerName FROM rcs_members WHERE clanTag = %s "
                               "AND timestamp = (SELECT TOP 1 timestamp from rcs_members WHERE clanTag = %s "
                               "ORDER BY timestamp DESC) ORDER BY bestTrophies DESC", (clan.tag[1:], clan.tag[1:]))
                fetch = cursor.fetchall()
            page_count = math.ceil(len(fetch) / 25)
            title = f"Best Trophies for {clan.name}"
            ctx.icon = "https://cdn.discordapp.com/emojis/635642869738111016.png"
            p = formats.TablePaginator(ctx, data=fetch, title=title, page_count=page_count)
        await p.paginate()

    @commands.command(name="townhalls", aliases=["townhall", "th"])
    async def townhalls(self, ctx, *, clan: ClanConverter = None):
        """List of clan members by town hall level"""
        if not clan:
            return await ctx.send("You have not provided a valid clan name or clan tag.")
        async with ctx.typing():
            with Sql() as cursor:
                member_list = []
                cursor.execute(f"SELECT thLevel, playerName FROM rcs_members WHERE clanTag = %s "
                               f"AND timestamp = (SELECT TOP 1 timestamp from rcs_members WHERE clanTag = %s "
                               f"ORDER BY timestamp DESC) ORDER BY thLevel DESC, trophies DESC",
                               (clan.tag[1:], clan.tag[1:]))
                fetch = cursor.fetchall()
            page_count = math.ceil(len(fetch) / 25)
            title = f"Town Halls for {clan.name}"
            ctx.icon = "https://cdn.discordapp.com/emojis/513119024188489738.png"
            p = formats.TablePaginator(ctx, data=fetch, title=title, page_count=page_count)
        await p.paginate()

    @commands.command(name="builderhalls", aliases=["builderhall", "bh"])
    async def builderhalls(self, ctx, *, clan: ClanConverter = None):
        """List of clan members by builder hall level"""
        if not clan:
            return await ctx.send("You have not provided a valid clan name or clan tag.")
        async with ctx.typing():
            with Sql() as cursor:
                member_list = []
                cursor.execute(f"SELECT builderHallLevel, playerName FROM rcs_members WHERE clanTag = %s "
                               f"AND timestamp = (SELECT TOP 1 timestamp from rcs_members WHERE clanTag = %s "
                               f"ORDER BY timestamp DESC) ORDER BY builderHallLevel DESC, vsTrophies DESC",
                               (clan.tag[1:], clan.tag[1:]))
                fetch = cursor.fetchall()
            page_count = math.ceil(len(fetch) / 25)
            title = f"Builder Halls for {clan.name}"
            ctx.icon = "https://cdn.discordapp.com/emojis/513119024188489738.png"
            p = formats.TablePaginator(ctx, data=fetch, title=title, page_count=page_count)
        await p.paginate()

    @commands.command(name="warstars", aliases=["stars"])
    async def warstars(self, ctx, *, clan: ClanConverter = None):
        """List of clan members by war stars earned"""
        if not clan:
            return await ctx.send("You have not provided a valid clan name or clan tag.")
        async with ctx.typing():
            with Sql() as cursor:
                cursor.execute(f"SELECT warStars, playerName FROM rcs_members WHERE clanTag = %s "
                               f"AND timestamp = (SELECT TOP 1 timestamp from rcs_members WHERE clanTag = %s "
                               f"ORDER BY timestamp DESC) ORDER BY warStars DESC", (clan.tag[1:], clan.tag[1:]))
                fetch = cursor.fetchall()
            page_count = math.ceil(len(fetch) / 25)
            title = f"War Stars for {clan.name}"
            ctx.icon = "https://cdn.discordapp.com/emojis/635642870350741514.png"
            p = formats.TablePaginator(ctx, data=fetch, title=title, page_count=page_count)
        await p.paginate()

    @staticmethod
    def get_member_list(field):
        with Sql() as cursor:
            cursor.execute(f"SELECT TOP 10 {field}, playerName + ' (' + altName + ')' as pname FROM rcs_members "
                           f"INNER JOIN rcs_data ON rcs_data.clanTag = rcs_members.clanTag "
                           f"AND timestamp = (SELECT MAX(timestamp) FROM rcs_members WHERE timestamp < "
                           f"(SELECT MAX(timestamp) FROM rcs_members)) ORDER BY {field} DESC")
            fetch = cursor.fetchall()
        return fetch

    @commands.group()
    async def top(self, ctx):
        """[Group] Lists top ten (type "++help top" for more information)
        (warstars, attacks, defenses, trophies, bhtrophies, donations, games)"""
        if ctx.invoked_subcommand is None:
            return await ctx.send_help(ctx.command)

    @top.command(name="attacks", aliases=["att", "attack", "attackwin", "attackwins"])
    async def top_attacks(self, ctx):
        async with ctx.typing():
            data = self.get_member_list("attackWins")
            title = "RCS Top Ten for Attack Wins"
            ctx.icon = "https://cdn.discordapp.com/emojis/635642869750824980.png"
            p = formats.TablePaginator(ctx, data=data, title=title, page_count=1)
        await p.paginate()

    @top.command(name="defenses", aliases=["defences", "def", "defense", "defence", "defends",
                                           "defend", "defensewins", "defencewins"])
    async def top_defenses(self, ctx):
        async with ctx.typing():
            data = self.get_member_list("defenceWins")
            title = "RCS Top Ten for Defense Wins"
            ctx.icon = "https://cdn.discordapp.com/emojis/635642869373468704.png"
            p = formats.TablePaginator(ctx, data=data, title=title, page_count=1)
        await p.paginate()

    @top.command(name="donations", aliases=["donate", "donates", "donation"])
    async def top_donations(self, ctx):
        async with ctx.typing():
            data = self.get_member_list("donations")
            title = "RCS Top Ten for Donations"
            ctx.icon = "https://cdn.discordapp.com/emojis/301032036779425812.png"
            p = formats.TablePaginator(ctx, data=data, title=title, page_count=1)
        await p.paginate()

    @top.command(name="trophies", aliases=["trophy"])
    async def top_trophies(self, ctx):
        async with ctx.typing():
            data = self.get_member_list("trophies")
            title = "RCS Top Ten for Trophies"
            ctx.icon = "https://cdn.discordapp.com/emojis/635642869738111016.png"
            p = formats.TablePaginator(ctx, data=data, title=title, page_count=1)
        await p.paginate()

    @top.command(name="bhtrophies", aliases=["bhtrophy", "bh_trophies"])
    async def top_bh_trophies(self, ctx):
        async with ctx.typing():
            data = self.get_member_list("vsTrophies")
            title = "RCS Top Ten for Builder Trophies"
            ctx.icon = "https://cdn.discordapp.com/emojis/635642869738111016.png"
            p = formats.TablePaginator(ctx, data=data, title=title, page_count=1)
        await p.paginate()

    @top.command(name="besttrophies", aliases=["besttrophy", "mosttrophies"])
    async def top_best_trophies(self, ctx):
        async with ctx.typing():
            data = self.get_member_list("bestTrophies")
            title = "RCS Top Ten for Best Trophies"
            ctx.icon = "https://cdn.discordapp.com/emojis/635642869738111016.png"
            p = formats.TablePaginator(ctx, data=data, title=title, page_count=1)
        await p.paginate()

    @top.command(name="warstars", aliases=["stars"])
    async def top_warstars(self, ctx):
        async with ctx.typing():
            data = self.get_member_list("warStars")
            title = "RCS Top Ten for War Stars"
            ctx.icon = "https://cdn.discordapp.com/emojis/635642870350741514.png"
            p = formats.TablePaginator(ctx, data=data, title=title, page_count=1)
        await p.paginate()

    @top.command(name="games")
    async def top_games(self, ctx):
        async with ctx.typing():
            with Sql() as cursor:
                temp_table = ("CREATE TABLE #rcs_players (playerTag varchar(15), playerName nvarchar(50)) "
                              "INSERT INTO #rcs_players "
                              "SELECT DISTINCT playerTag, playerName FROM rcs_members")
                cursor.execute(temp_table)
                cursor.execute("SELECT TOP 10 (a.currentPoints - a.startingPoints) as points, "
                               "b.playerName + ' (' + c.altName + ')' as pname "
                               "FROM rcs_clanGames a "
                               "INNER JOIN #rcs_players b ON b.playerTag = a.playerTag "
                               "INNER JOIN rcs_data c ON c.clanTag = a.clanTag "
                               "WHERE eventId = (SELECT MAX(eventId) FROM rcs_events WHERE eventType = 5) "
                               "ORDER BY points DESC")
                fetch = cursor.fetchall()
            title = "RCS Top Ten for Clan Games"
            ctx.icon = "https://cdn.discordapp.com/emojis/635642869750824980.png"
            p = formats.TablePaginator(ctx, data=fetch, title=title, page_count=1)
        await p.paginate()

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
