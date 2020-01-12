import discord
import math
import pathlib

from discord.ext import commands
from cogs.utils.db import Sql, Psql
from cogs.utils.checks import is_leader_or_mod_or_council
from cogs.utils.converters import PlayerConverter, ClanConverter
from cogs.utils.constants import cwl_league_names, cwl_league_order
from cogs.utils.helper import rcs_names_tags
from cogs.utils import formats
from cogs.utils import season as coc_season
from PIL import Image, ImageFont, ImageDraw
from io import BytesIO
from random import randint
from datetime import datetime
from config import settings


class General(commands.Cog):
    """Cog for General bot commands"""
    def __init__(self, bot):
        self.bot = bot
        # TODO Add command for ++clan to show all clan info
        # TODO move non game related commands elsewhere

    @commands.command(name="attacks", aliases=["att", "attack", "attackwin", "attackwins"])
    async def attacks(self, ctx, *, clan: ClanConverter = None):
        """Attack wins for the whole clan

        **Example:**
        ++attacks Reddit Example
        """
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
        """Defense wins for the whole clan

        **Example:**
        ++def Reddit Example
        """
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

    @commands.command(name="donations", aliases=["don", "dons", "donate", "donates", "donation"])
    async def donations(self, ctx, *, clan: ClanConverter = None):
        """Donations for the whole clan

        **Example:**
        ++don Reddit Example
        """
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
        """Trophy count for the whole clan

        **Example:**
        ++trophies Reddit Example
        """
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
        """Trophy count for the whole clan

        **Example:**
        ++bhtrophies Reddit Example
        """
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
        """Best trophy count for the whole clan

        **Example:**
        ++besttrophies Reddit Example
        """
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
        """List of clan members by town hall level

        **Example:**
        ++th Reddit Example
        """
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
        """List of clan members by builder hall level

        **Example:**
        ++bh Reddit Example
        """
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
        """List of clan members by war stars earned

        **Example:**
        ++stars Reddit Example
        """
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
        """[Group] Lists top ten
        (warstars, attacks, defenses, trophies, bhtrophies, donations, games)
        """
        if ctx.invoked_subcommand is None:
            return await ctx.send_help(ctx.command)

    @top.command(name="attacks", aliases=["att", "attack", "attackwin", "attackwins"])
    async def top_attacks(self, ctx):
        """Displays top ten attack win totals for all of the RCS"""
        async with ctx.typing():
            data = self.get_member_list("attackWins")
            title = "RCS Top Ten for Attack Wins"
            ctx.icon = "https://cdn.discordapp.com/emojis/635642869750824980.png"
            p = formats.TablePaginator(ctx, data=data, title=title, page_count=1)
        await p.paginate()

    @top.command(name="defenses", aliases=["defences", "def", "defense", "defence", "defends",
                                           "defend", "defensewins", "defencewins"])
    async def top_defenses(self, ctx):
        """Displays top ten defense win totals for all of the RCS"""
        async with ctx.typing():
            data = self.get_member_list("defenceWins")
            title = "RCS Top Ten for Defense Wins"
            ctx.icon = "https://cdn.discordapp.com/emojis/635642869373468704.png"
            p = formats.TablePaginator(ctx, data=data, title=title, page_count=1)
        await p.paginate()

    @top.command(name="donates", aliases=["donate", "donations", "donation"])
    async def top_donations(self, ctx):
        """Displays top ten donation totals for all of the RCS"""
        async with ctx.typing():
            data = self.get_member_list("donations")
            title = "RCS Top Ten for Donations"
            ctx.icon = "https://cdn.discordapp.com/emojis/301032036779425812.png"
            p = formats.TablePaginator(ctx, data=data, title=title, page_count=1)
        await p.paginate()

    @top.command(name="trophies", aliases=["trophy"])
    async def top_trophies(self, ctx):
        """Displays top ten trophy counts for all of the RCS"""
        async with ctx.typing():
            data = self.get_member_list("trophies")
            title = "RCS Top Ten for Trophies"
            ctx.icon = "https://cdn.discordapp.com/emojis/635642869738111016.png"
            p = formats.TablePaginator(ctx, data=data, title=title, page_count=1)
        await p.paginate()

    @top.command(name="bhtrophies", aliases=["bhtrophy", "bh_trophies"])
    async def top_bh_trophies(self, ctx):
        """Displays top ten vs trophy counts for all of the RCS"""
        async with ctx.typing():
            data = self.get_member_list("vsTrophies")
            title = "RCS Top Ten for Builder Trophies"
            ctx.icon = "https://cdn.discordapp.com/emojis/635642869738111016.png"
            p = formats.TablePaginator(ctx, data=data, title=title, page_count=1)
        await p.paginate()

    @top.command(name="besttrophies", aliases=["besttrophy", "mosttrophies"])
    async def top_best_trophies(self, ctx):
        """Displays top ten best trophy counts for all of the RCS"""
        async with ctx.typing():
            data = self.get_member_list("bestTrophies")
            title = "RCS Top Ten for Best Trophies"
            ctx.icon = "https://cdn.discordapp.com/emojis/635642869738111016.png"
            p = formats.TablePaginator(ctx, data=data, title=title, page_count=1)
        await p.paginate()

    @top.command(name="warstars", aliases=["stars"])
    async def top_warstars(self, ctx):
        """Displays top ten war star totals for all of the RCS"""
        async with ctx.typing():
            data = self.get_member_list("warStars")
            title = "RCS Top Ten for War Stars"
            ctx.icon = "https://cdn.discordapp.com/emojis/635642870350741514.png"
            p = formats.TablePaginator(ctx, data=data, title=title, page_count=1)
        await p.paginate()

    @top.command(name="games")
    async def top_games(self, ctx):
        """Displays top ten clan games points for all of the RCS (current or most recent games)"""
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

    @commands.group(name="link", invoke_without_command=True, hidden=True)
    @is_leader_or_mod_or_council()
    async def link(self, ctx, member: discord.Member = None, player: PlayerConverter = None):
        """Allows leaders, chat mods or council to link a Discord member to an in-game player tag
        
        **Permissions:**
        RCS Leaders
        Chat Mods
        Council
        
        **Example:**
        ++link @TubaKid #ABC1234
        ++link 051150854571163648 #ABC1234
        """
        if ctx.invoked_subcommand is not None:
            return

        if not player:
            self.bot.logger.error(f"{ctx.author} provided some bad info for the link command.")
            return await ctx.send("I don't particularly care for that player. Wanna try again?")
        if not member:
            return await ctx.send("That's not a real Discord user. Try again.")
        if player.clan.tag[1:] in rcs_names_tags().values():
            try:
                await Psql(self.bot).link_user(player.tag[1:], member.id)
                emoji = "\u2705"
                rcs_guild = self.bot.get_guild(settings['discord']['rcsguild_id'])
                member_role = rcs_guild.get_role(settings['rcs_roles']['members'])
                await member.add_roles(member_role)
                await ctx.message.add_reaction(emoji)
            except:
                self.bot.logger.exception("Something went wrong while adding a discord link")
                await ctx.send("I'm sorry, but something has gone wrong. I notified the important people and they will "
                               "look into it for you.")
        else:
            await ctx.send(f"I see that {player.name} is in {player.clan} which is not an RCS clan. Try again "
                           f"when {player.name} is in an RCS clan.")

    @link.command(name="list", hidden=True)
    @is_leader_or_mod_or_council()
    async def list(self, ctx, clan: ClanConverter = None):
        """List linked players for the spcified clan

        **Permissions:**
        RCS Leaders
        Chat Mods
        Council

        **Example:**
        ++link list Chi
        ++link list #CVCJR89
        ++link list Reddit Snow
        """
        if not clan:
            return await ctx.send("You must provide an RCS clan name or tag.")
        tags = [x.tag[1:] for x in clan.itermembers]
        sql = "SELECT discord_id, player_tag FROM rcs_discord_links WHERE player_tag = any($1::TEXT[])"
        fetch = await self.bot.pool.fetch(sql, tags)
        if not fetch:
            return await ctx.send(f"No linked players found for {clan.name}.")
        response = ""
        for row in fetch:
            player = await self.bot.coc.get_player(row['player_tag'])
            response += f"<@{row['discord_id']}> is linked to {player.name} ({player.tag})\n"
        await ctx.send_text(ctx.channel, response)

    @commands.command(name="reddit", aliases=["subreddit"])
    async def reddit(self, ctx, *, clan: ClanConverter = None):
        """Displays a link to specified clan's subreddit"""
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
        """Displays a link to specified clan's Discord server"""
        if not clan:
            return await ctx.send("You must provide an RCS clan name or tag.")
        async with ctx.typing():
            with Sql(as_dict=True) as cursor:
                cursor.execute(f"SELECT discordServer FROM rcs_data WHERE clanTag = '{clan.tag[1:]}'")
                fetch = cursor.fetchone()
        if fetch['discordServer']:
            await ctx.send(fetch['discordServer'])
        else:
            await ctx.send("This clan does not have a Discord server.")

    @commands.command(name="cwl")
    async def cwl(self, ctx, *args):
        """Allows for specifying what CWL league your clan is in.

        **Example:**
        ++cwl list - Shows list of RCS clans in their leagues
        ++cwl Reddit Example Master II - assigns your clan to the specified league
        """
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
            fetch = cursor.fetchall()
            clans = []
            clans_tag = []
            for clan in fetch:
                clans.append(clan["clanName"].lower())
                clans_tag.append([clan["clanTag"], clan["clanName"], clan["discordTag"]])
            leagues = cwl_league_names
            league_num = "I"
            if args[-1].lower() in ["3", "iii", "three"]:
                league_num = "III"
            if args[-1].lower() in ["2", "ii", "two"]:
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

    @commands.command(name="roll")
    async def roll(self, ctx, *args):
        """Roll a set number of dice providing random results

        **Parameters**
        Max number on die (one whole number per die)

        **Format**
        `++roll integer [integer] [integer]...`

        **Example**
        `++roll 6 6' for two "traditional" dice
        `++roll 4 6 8 10 12 20` if you're a D&D fan
        `++roll 25` if you just need a random number 1-25
        """
        if not args:
            return await ctx.send_help(ctx.command)

        def get_die(num):
            path = pathlib.Path(f"static/{num}.png")
            if path.exists() and path.is_file():
                image = Image.open(f"static/{num}.png")
            else:
                image = Image.open("static/die-blank.png")
                draw = ImageDraw.Draw(image)
                black = (0, 0, 0)
                font_size = 54
                font = ImageFont.truetype("static/sc-magic.ttf", font_size)
                text_width, text_height = draw.textsize(num, font)
                # handle different height/width numbers
                while text_width > 57 or text_height > 57:
                    font_size -= 5
                    font = ImageFont.truetype("static/sc-magic.ttf", font_size)
                    text_width, text_height = draw.textsize(num, font)
                if text_width / text_height > 1.2:
                    offset = 1
                else:
                    offset = 4
                position = ((64 - text_width) / 2, (64 - text_height) / 2 - offset)
                draw.text(position, num, black, font=font)
                image.save(f"static/{num}.png")
            return image

        dice = []
        final_width = 0
        for die in args:
            answer = str(randint(1, int(die)))
            dice.append(get_die(answer))
            # die is 64 wide plus 4 for padding
            final_width += 64 + 4
        final_image = Image.new("RGBA", (final_width, 64), (255, 0, 0, 0))
        current_pos = 0
        for image in dice:
            final_image.paste(image, (current_pos, 0))
            current_pos += 64 + 4
        final_buffer = BytesIO()
        final_image.save(final_buffer, "png")
        final_buffer.seek(0)
        response = await ctx.send(file=discord.File(final_buffer, "results.png"))
        # Currently DISABLED - Remove comment to auto-delete response with command
        # self.bot.messages[ctx.message.id] = response

    @commands.group(invoke_without_subcommands=True)
    async def season(self, ctx):
        """Group of commands to deal with the current COC season"""
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(title="Season Information", color=discord.Color.green())
            embed.add_field(name="Season Start", value=coc_season.get_season_start())
            embed.add_field(name="Season End", value=coc_season.get_season_end())
            embed.add_field(name="Days Left", value=coc_season.get_days_left())
            embed.set_thumbnail(url="http://www.mayodev.com/images/clock.png")
            response = await ctx.send(embed=embed)
            self.bot.messages[ctx.message.id] = response

    @season.command(name="change", hidden=True)
    @commands.is_owner()
    async def change(self, ctx, arg: str = ""):
        """Command to modify the season information"""
        if datetime.now() < datetime.strptime(coc_season.get_season_end(), "%Y-%m-%d"):
            return await ctx.send("I would much prefer it if you waited until the season ends to change the dates.")
        try:
            coc_season.update_season(arg)
        except:
            self.bot.logger.exception("season change")
            return
        response = await ctx.send(f"File updated.  The new season ends in {coc_season.get_days_left()} days.")
        self.bot.messages[ctx.message.id] = response

    @season.command(name="info")
    async def season_info(self, ctx):
        """Command to display the season information"""
        embed = discord.Embed(title="Season Information", color=discord.Color.green())
        embed.add_field(name="Season Start", value=coc_season.get_season_start())
        embed.add_field(name="Season End", value=coc_season.get_season_end())
        embed.add_field(name="Days Left", value=coc_season.get_days_left())
        embed.set_thumbnail(url="http://www.mayodev.com/images/clock.png")
        response = await ctx.send(embed=embed)
        self.bot.messages[ctx.message.id] = response


def setup(bot):
    bot.add_cog(General(bot))
