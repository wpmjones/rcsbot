import discord
import math
import pathlib

from discord.ext import commands
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
            sql = "SELECT attack_wins, player_name FROM rcs_members WHERE clan_tag = $1 ORDER BY attack_wins DESC"
            fetch = await self.bot.pool.fetch(sql, clan.tag[1:])
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
            sql = "SELECT defense_wins, player_name FROM rcs_members WHERE clan_tag = $1 ORDER BY defense_wins DESC"
            fetch = await self.bot.pool.fetch(sql, clan.tag[1:])
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
        sql = ("SELECT donations, donations_received, player_name FROM rcs_members WHERE clan_tag = $1 "
               "ORDER BY donations DESC")
        fetch = await self.bot.pool.fetch(sql, clan.tag[1:])
        page_count = math.ceil(len(fetch) / 25)
        title = f"Donations for {clan.name}"
        ctx.icon = "https://cdn.discordapp.com/emojis/301032036779425812.png"
        p = formats.TablePaginator(ctx, data=fetch, title=title, page_count=page_count)
        await p.paginate()

    @commands.command(name="level", aliases=["levels", "lvl", "xp", "exp", "harr"])
    async def levels(self, ctx, *, clan: ClanConverter = None):
        """Exp Level for the whole clan

        **Example:**
        ++xp Reddit Oak
        ++level Oak
        ++lvl #CVCJR89"""
        if not clan:
            return await ctx.send("You have not provided a valid clan name or clan tag.")
        async with ctx.typing():
            sql = "SELECT exp_level, player_name FROM rcs_members WHERE clan_tag = $1 ORDER BY exp_level DESC"
            fetch = await self.bot.pool.fetch(sql, clan.tag[1:])
            page_count = math.ceil(len(fetch) / 25)
            title = f"Exp Levels for {clan.name}"
            ctx.icon = "http://cdn.discordapp.com/emojis/748585659085881444.png"
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
            sql = "SELECT trophies, player_name FROM rcs_members WHERE clan_tag = $1 ORDER BY trophies DESC"
            fetch = await self.bot.pool.fetch(sql, clan.tag[1:])
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
            sql = "SELECT vs_trophies, player_name FROM rcs_members WHERE clan_tag = $1 ORDER BY vs_trophies DESC"
            fetch = await self.bot.pool.fetch(sql, clan.tag[1:])
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
            sql = "SELECT best_trophies, player_name FROM rcs_members WHERE clan_tag = $1 ORDER BY best_trophies DESC"
            fetch = await self.bot.pool.fetch(sql, clan.tag[1:])
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
            sql = "SELECT th_level, player_name FROM rcs_members WHERE clan_tag = $1 ORDER BY th_level DESC"
            fetch = await self.bot.pool.fetch(sql, clan.tag[1:])
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
            sql = "SELECT bh_level, player_name FROM rcs_members WHERE clan_tag = $1 ORDER BY bh_level DESC"
            fetch = await self.bot.pool.fetch(sql, clan.tag[1:])
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
            sql = "SELECT war_stars, player_name FROM rcs_members WHERE clan_tag = $1 ORDER BY war_stars DESC"
            fetch = await self.bot.pool.fetch(sql, clan.tag[1:])
            page_count = math.ceil(len(fetch) / 25)
            title = f"War Stars for {clan.name}"
            ctx.icon = "https://cdn.discordapp.com/emojis/635642870350741514.png"
            p = formats.TablePaginator(ctx, data=fetch, title=title, page_count=page_count)
        await p.paginate()

    async def get_member_list(self, field):
        sql = (f"SELECT {field}, player_name || ' (' || alt_name || ')' as pname FROM rcs_members "
               f"INNER JOIN rcs_clans ON rcs_clans.clan_tag = rcs_members.clan_tag "
               f"ORDER BY {field} DESC LIMIT 10")
        fetch = await self.bot.pool.fetch(sql)
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
            data = await self.get_member_list("attack_wins")
            title = "RCS Top Ten for Attack Wins"
            ctx.icon = "https://cdn.discordapp.com/emojis/635642869750824980.png"
            p = formats.TablePaginator(ctx, data=data, title=title, page_count=1)
        await p.paginate()

    @top.command(name="defenses", aliases=["defences", "def", "defense", "defence", "defends",
                                           "defend", "defensewins", "defencewins"])
    async def top_defenses(self, ctx):
        """Displays top ten defense win totals for all of the RCS"""
        async with ctx.typing():
            data = await self.get_member_list("defense_wins")
            title = "RCS Top Ten for Defense Wins"
            ctx.icon = "https://cdn.discordapp.com/emojis/635642869373468704.png"
            p = formats.TablePaginator(ctx, data=data, title=title, page_count=1)
        await p.paginate()

    @top.command(name="donates", aliases=["donate", "donations", "donation"])
    async def top_donations(self, ctx):
        """Displays top ten donation totals for all of the RCS"""
        async with ctx.typing():
            data = await self.get_member_list("donations")
            title = "RCS Top Ten for Donations"
            ctx.icon = "https://cdn.discordapp.com/emojis/301032036779425812.png"
            p = formats.TablePaginator(ctx, data=data, title=title, page_count=1)
        await p.paginate()

    @top.command(name="level", aliases=["levels", "lvl", "xp", "exp", "harr"])
    async def top_levels(self, ctx):
        """Displays top ten Exp Levels for all of the RCS"""
        async with ctx.typing():
            data = await self.get_member_list("exp_level")
            title = "RCS Top Ten for Exp Level"
            ctx.icon = "https://cdn.discordapp.com/emojis/748585659085881444.png"
            p = formats.TablePaginator(ctx, data=data, title=title, page_count=1)
        await p.paginate()

    @top.command(name="trophies", aliases=["trophy"])
    async def top_trophies(self, ctx):
        """Displays top ten trophy counts for all of the RCS"""
        async with ctx.typing():
            data = await self.get_member_list("trophies")
            title = "RCS Top Ten for Trophies"
            ctx.icon = "https://cdn.discordapp.com/emojis/635642869738111016.png"
            p = formats.TablePaginator(ctx, data=data, title=title, page_count=1)
        await p.paginate()

    @top.command(name="bhtrophies", aliases=["bhtrophy", "bh_trophies"])
    async def top_bh_trophies(self, ctx):
        """Displays top ten vs trophy counts for all of the RCS"""
        async with ctx.typing():
            data = await self.get_member_list("vs_trophies")
            title = "RCS Top Ten for Builder Trophies"
            ctx.icon = "https://cdn.discordapp.com/emojis/635642869738111016.png"
            p = formats.TablePaginator(ctx, data=data, title=title, page_count=1)
        await p.paginate()

    @top.command(name="besttrophies", aliases=["besttrophy", "mosttrophies"])
    async def top_best_trophies(self, ctx):
        """Displays top ten best trophy counts for all of the RCS"""
        async with ctx.typing():
            data = await self.get_member_list("best_trophies")
            title = "RCS Top Ten for Best Trophies"
            ctx.icon = "https://cdn.discordapp.com/emojis/635642869738111016.png"
            p = formats.TablePaginator(ctx, data=data, title=title, page_count=1)
        await p.paginate()

    @top.command(name="warstars", aliases=["stars"])
    async def top_warstars(self, ctx):
        """Displays top ten war star totals for all of the RCS"""
        async with ctx.typing():
            data = await self.get_member_list("war_stars")
            title = "RCS Top Ten for War Stars"
            ctx.icon = "https://cdn.discordapp.com/emojis/635642870350741514.png"
            p = formats.TablePaginator(ctx, data=data, title=title, page_count=1)
        await p.paginate()

    @top.command(name="games")
    async def top_games(self, ctx):
        """Displays top ten clan games points for all of the RCS (current or most recent games)"""
        async with ctx.typing():
            now = datetime.utcnow()
            conn = self.bot.pool
            row = await conn.fetchrow("SELECT MAX(start_time) as start_time, event_id "
                                      "FROM rcs_events WHERE event_type_id = 1 AND start_time < $1 "
                                      "GROUP BY event_id "
                                      "ORDER BY start_time DESC "
                                      "LIMIT 1", now)
            event_id = row['event_id']
            sql = ("SELECT player_tag, (current_points - starting_points) as points "
                   "FROM rcs_clan_games "
                   "WHERE event_id = $1 "
                   "ORDER BY points DESC "
                   "LIMIT 10")
            fetch = await conn.fetch(sql, event_id)
            data = []
            for row in fetch:
                player = await self.bot.coc.get_player(row['player_tag'])
                clan = player.clan.name.replace("Reddit ", "")
                data.append([row['points'], f"{player.name} ({clan})"])
            title = "RCS Top Ten for Clan Games"
            ctx.icon = "https://cdn.discordapp.com/emojis/635642869750824980.png"
            p = formats.TablePaginator(ctx, data=data, title=title, page_count=1)
        await p.paginate()

    @commands.group(name="link", invoke_without_command=True, hidden=True)
    @is_leader_or_mod_or_council()
    async def link(self, ctx, user: discord.User = None, player: PlayerConverter = None):
        """Allows leaders, chat mods or council to link a Discord member to an in-game player tag
        
        **Permissions:**
        RCS Leaders
        Chat Mods
        Council
        
        **Example:**
        ++link @TubaKid #ABC1234
        ++link 051150854571163648 #ABC1234

        **Options:**
        ++link list [clan name/tag]
        ++link check [tag or Discord ID]
        """
        if ctx.invoked_subcommand is not None:
            return

        if not player:
            self.bot.logger.error(f"{ctx.author} provided some bad info for the link command.")
            return await ctx.send("I don't particularly care for that player. Wanna try again?")
        if not user:
            return await ctx.send("That's not a real Discord user. Try again.")
        if player.clan.tag[1:] in rcs_names_tags().values() or player.clan.name.lower().startswith("reddit"):
            try:
                # Add to Mike's Links API database
                await self.bot.links.add_link(player.tag, user.id)
                # Add member role to discord user
                rcs_guild = self.bot.get_guild(settings['discord']['rcsguild_id'])
                member = rcs_guild.get_member(user.id)
                if not member:
                    return await ctx.send(f"{user.display_name} is not a member of the RCS Discord Server "
                                          f"so I couldn't add the Member role.")
                member_role = rcs_guild.get_role(settings['rcs_roles']['members'])
                await member.add_roles(member_role)
                await ctx.confirm()
            except:
                self.bot.logger.exception("Something went wrong while adding a discord link")
                await ctx.send("I'm sorry, but something has gone wrong. I notified the important people and they will "
                               "look into it for you.")
        else:
            await ctx.send(f"I see that {player.name} is in {player.clan} which is not an RCS clan. Try again "
                           f"when {player.name} is in an RCS clan.")

    @link.command(name="check", hidden=True)
    @is_leader_or_mod_or_council()
    async def link_check(self, ctx, tag_or_id):
        if tag_or_id.startswith("#"):
            # player_tag provided
            discord_id = await self.bot.links.get_link(tag_or_id)
            player = await self.bot.coc.get_player(tag_or_id)
            if discord_id:
                content = f"{player.name} ({player.tag}) is linked to <@{discord_id}> ({discord_id})."
            else:
                content = f"No matching Discord ID found for {player.name} ({player.tag})."
        else:
            # assume we have a discord_id
            tags = await self.bot.links.get_linked_players(tag_or_id)
            if tags:
                content = ""
                for tag in tags:
                    player = await self.bot.coc.get_player(tag)
                    content += f"<@{tag_or_id}> ({tag_or_id}) is linked to {player.name} ({player.tag})\n"
            else:
                content = f"No matching tags found for {tag_or_id}."
        return await ctx.send(content)

    @link.command(name="list", hidden=True)
    @is_leader_or_mod_or_council()
    async def link_list(self, ctx, clan: ClanConverter = None):
        """List linked players for the specified clan

        **Permissions:**
        RCS Leaders
        Chat Mods
        Council

        **Example:**
        ++link list Chi
        ++link list #CVCJR89
        ++link list Reddit Snow
        """
        async with ctx.typing():
            if not clan:
                return await ctx.send("You must provide an RCS clan name or tag.")
            tags = [x.tag[1:] for x in clan.members]
            links = await self.bot.links.get_links(*tags)
            linked = not_linked = ""
            for player_tag, discord_id in links:
                player = await self.bot.coc.get_player(player_tag)
                if discord_id:
                    linked += f"<@{discord_id}> is linked to {player.name} ({player.tag})\n"
                else:
                    not_linked += f"{player.name} ({player.tag}) is not currently linked to a Discord account.\n"
        if linked:
            linked = f"**Linked members of {clan.name}**\n" + linked
        if not_linked:
            not_linked = f"**Members of {clan.name} who are not linked**\n" + not_linked
        await ctx.send_text(ctx.channel, linked + not_linked)

    @commands.command(name="unlink", hidden=True)
    @is_leader_or_mod_or_council()
    async def unlink(self, ctx, player: PlayerConverter = None):
        """Unlink player tag from Discord

        **Permissions:**
        RCS Council
        Chat Mods
        Leaders

        **Example:**
        ++unlink #UV8QQ0RV
        """
        if not player:
            self.bot.logger.error(f"{ctx.author} provided some bad info for the link command.")
            return await ctx.send("I don't particularly care for that player. Wanna try again?")
        await self.bot.links.delete_link(player.tag)
        await ctx.confirm()

    @commands.command(name="reddit", aliases=["subreddit"])
    async def reddit(self, ctx, *, clan: ClanConverter = None):
        """Displays a link to specified clan's subreddit"""
        if not clan:
            return await ctx.send("You must provide an RCS clan name or tag.")
        sql = "SELECT subreddit FROM rcs_clans WHERE clan_tag = $1"
        fetch = await self.bot.pool.fetchrow(sql, clan.tag[1:])
        if fetch['subreddit'] != "":
            await ctx.send(fetch['subreddit'])
        else:
            await ctx.send("This clan does not have a subreddit.")

    @commands.command(name="discord")
    async def discord(self, ctx, *, clan: ClanConverter = None):
        """Displays a link to specified clan's Discord server"""
        if not clan:
            return await ctx.send("Here is the link to the RCS Discord Server.  https://discord.gg/X8U9XjD")
        async with ctx.typing():
            sql = "SELECT discord_server FROM rcs_clans WHERE clan_tag = $1"
            fetch = await self.bot.pool.fetchrow(sql, clan.tag[1:])
        if fetch['discord_server']:
            await ctx.send(fetch['discord_server'])
        else:
            await ctx.send("This clan does not have a Discord server.")

    @commands.command(name="cwl")
    async def cwl(self, ctx, *args):
        """Allows for specifying what CWL league your clan is in.

        **Example:**
        ++cwl list - Shows list of RCS clans in their leagues
        ++cwl Reddit Example Master II - assigns your clan to the specified league
        """
        # TODO remove ability to update manually, add clan converter for clan specific request
        conn = self.bot.pool
        # Respond with list
        if args[0] in ["all", "list"]:
            sql = ("SELECT clan_name, clan_tag, cwl_league FROM rcs_clans "
                   "WHERE cwl_league IS NOT NULL "
                   "ORDER BY clan_name")
            clans = await conn.fetch(sql)
            content = ""
            sort_leagues = cwl_league_order[::-1]
            for league in sort_leagues:
                header = f"**{league}:**\n"
                temp = ""
                for clan in clans:
                    if clan['cwl_league'] == league:
                        temp += f"  {clan['clan_name']} (#{clan['clan_tag']})\n"
                if temp:
                    content += header + temp
            return await ctx.send(content)
        # Handle user arguments
        sql = "SELECT clan_name, clan_tag, discord_tag FROM rcs_clans ORDER BY clan_name"
        fetch = await conn.fetch(sql)
        clans = []
        clans_tag = []
        for clan in fetch:
            clans.append(clan['clan_name'].lower())
            clans_tag.append([clan['clan_tag'], clan['clan_name'], clan['discord_tag']])
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
            await conn.execute(f"UPDATE rcs_clans "
                               f"SET cwl_league = '{league}' "
                               f"WHERE clan_tag = '{clan_tag}'")
            await ctx.send("Update complete!")
            if str(ctx.author.id) != str(leader):
                try:
                    leader_spam_chat = self.bot.get_channel(settings["rcs_channels"]["leader_spam"])
                    await leader_spam_chat.send(f"<@{leader}> {clan}'s CWL league has been updated to {league} "
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

    @commands.command(name="season")
    async def season(self, ctx):
        """Responds with information on the current COC season"""
        embed = discord.Embed(title="Season Information", color=discord.Color.green())
        embed.add_field(name="Season Start", value=coc_season.get_season_start())
        embed.add_field(name="Season End", value=coc_season.get_season_end())
        embed.add_field(name="Days Left", value=coc_season.get_days_left())
        embed.set_thumbnail(url="http://www.mayodev.com/images/clock.png")
        response = await ctx.send(embed=embed)
        self.bot.messages[ctx.message.id] = response


def setup(bot):
    bot.add_cog(General(bot))
