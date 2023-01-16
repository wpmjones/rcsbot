import nextcord
import math
import pathlib

from nextcord import SlashOption
from nextcord.ext import commands, menus
from cogs.utils.converters import ClanConverter
from cogs.utils.constants import cwl_league_order
from cogs.utils.emoji_lookup import nums
from cogs.utils.helper import rcs_tags
from cogs.utils.page_sources import MainEmbedPageSource, MainFieldPageSource
from cogs.utils import season as coc_season
from PIL import Image, ImageFont, ImageDraw
from io import BytesIO
from random import randint
from config import settings

GUILD_IDS = [settings['discord']['rcsguild_id'], settings['discord']['botlogguild_id']]


class General(commands.Cog):
    """Cog for General bot commands"""
    def __init__(self, bot):
        self.bot = bot
        # TODO move non game related commands elsewhere

    @nextcord.slash_command(name="attacks", description="Attack wins for the specified clan")
    async def attacks(self, interaction, clan: ClanConverter = SlashOption(name="clan", required=True)):
        """Attack wins for the whole clan"""
        sql = ("SELECT ROW_NUMBER () OVER (ORDER BY attack_wins DESC) as row_num, attack_wins, player_name "
               "FROM rcs_members WHERE clan_tag = $1")
        fetch = await self.bot.pool.fetch(sql, clan.tag[1:])
        data = []
        for row in fetch:
            formatted = f"{nums[row[0]]}`⠀{row[1]:\u00A0>4}⠀` `⠀{row[2]:\u00A0>22.22}⠀`"
            data.append(formatted)
        pages = menus.ButtonMenuPages(source=MainEmbedPageSource(data, f"Attack Wins for {clan.name}", 25),
                                      clear_buttons_after=True)
        await pages.start(interaction=interaction)

    @nextcord.slash_command(name="defenses", description="Defense wins for the specified clan")
    async def defenses(self, interaction, clan: ClanConverter = SlashOption(name="clan", required=True)):
        """Defense wins for the whole clan"""
        sql = ("SELECT ROW_NUMBER () OVER (ORDER BY defense_wins DESC) as row_num, defense_wins, player_name "
               "FROM rcs_members WHERE clan_tag = $1")
        fetch = await self.bot.pool.fetch(sql, clan.tag[1:])
        data = []
        for row in fetch:
            formatted = f"{nums[row[0]]}`⠀{row[1]:\u00A0>4}⠀` `⠀{row[2]:\u00A0>22.22}⠀`"
            data.append(formatted)
        pages = menus.ButtonMenuPages(source=MainEmbedPageSource(data, f"Defense Wins for {clan.name}", 25),
                                      clear_buttons_after=True)
        await pages.start(interaction=interaction)

    @nextcord.slash_command(name="donations", description="Donations for the specified clan")
    async def donations(self, interaction, clan: ClanConverter = SlashOption(name="clan", required=True)):
        """Donations for the whole clan"""
        sql = ("SELECT ROW_NUMBER () OVER (ORDER BY donations DESC) as row_num, donations, "
               "donations_received, player_name FROM rcs_members WHERE clan_tag = $1")
        fetch = await self.bot.pool.fetch(sql, clan.tag[1:])
        data = []
        for row in fetch:
            formatted = f"{nums[row[0]]}`⠀{row[1]:\u00A0>4}⠀` `⠀{row[2]:\u00A0>4}⠀` `⠀{row[3]:\u00A0>18.18}⠀`"
            data.append(formatted)
        pages = menus.ButtonMenuPages(source=MainEmbedPageSource(data, f"Donations for {clan.name}", 25),
                                      clear_buttons_after=True)
        await pages.start(interaction=interaction)

    @nextcord.slash_command(name="level", description="XP levels for the specified clan")
    async def levels(self, interaction, clan: ClanConverter = SlashOption(name="clan", required=True)):
        """Exp Level for the whole clan"""
        sql = ("SELECT ROW_NUMBER () OVER (ORDER BY exp_level DESC) as row_num, exp_level, player_name "
               "FROM rcs_members WHERE clan_tag = $1")
        fetch = await self.bot.pool.fetch(sql, clan.tag[1:])
        data = []
        for row in fetch:
            formatted = f"{nums[row[0]]}`⠀{row[1]:\u00A0>4}⠀` `⠀{row[2]:\u00A0>22.22}⠀`"
            data.append(formatted)
        pages = menus.ButtonMenuPages(source=MainEmbedPageSource(data, f"XP Levels for {clan.name}", 25),
                                      clear_buttons_after=True)
        await pages.start(interaction=interaction)

    @nextcord.slash_command(name="trophies", description="Trophy counts for the specified clan")
    async def trophies(self, interaction, clan: ClanConverter = SlashOption(name="clan", required=True)):
        """Trophy count for the whole clan"""
        sql = ("SELECT ROW_NUMBER () OVER (ORDER BY trophies DESC) as row_num, trophies, player_name "
               "FROM rcs_members WHERE clan_tag = $1")
        fetch = await self.bot.pool.fetch(sql, clan.tag[1:])
        data = []
        for row in fetch:
            formatted = f"{nums[row[0]]}`⠀{row[1]:\u00A0>4}⠀` `⠀{row[2]:\u00A0>22.22}⠀`"
            data.append(formatted)
        pages = menus.ButtonMenuPages(source=MainEmbedPageSource(data, f"Trophy Counts for {clan.name}", 25),
                                      clear_buttons_after=True)
        await pages.start(interaction=interaction)

    @nextcord.slash_command(name="bhtrophies", description="Builder Trophies for the specified clan")
    async def bh_trophies(self, interaction, clan: ClanConverter = SlashOption(name="clan", required=True)):
        """Trophy count for the whole clan"""
        sql = ("SELECT ROW_NUMBER () OVER (ORDER BY vs_trophies DESC) as row_num, vs_trophies, player_name "
               "FROM rcs_members WHERE clan_tag = $1")
        fetch = await self.bot.pool.fetch(sql, clan.tag[1:])
        data = []
        for row in fetch:
            formatted = f"{nums[row[0]]}`⠀{row[1]:\u00A0>4}⠀` `⠀{row[2]:\u00A0>22.22}⠀`"
            data.append(formatted)
        pages = menus.ButtonMenuPages(source=MainEmbedPageSource(data, f"Builder Trophies for {clan.name}", 25),
                                      clear_buttons_after=True)
        await pages.start(interaction=interaction)

    @nextcord.slash_command(name="besttrophies", description="Best trophy counts for the specified clan")
    async def besttrophies(self, interaction, clan: ClanConverter = SlashOption(name="clan", required=True)):
        """Best trophy count for the whole clan"""
        sql = ("SELECT ROW_NUMBER () OVER (ORDER BY best_trophies DESC) as row_num, best_trophies, player_name "
               "FROM rcs_members WHERE clan_tag = $1")
        fetch = await self.bot.pool.fetch(sql, clan.tag[1:])
        data = []
        for row in fetch:
            formatted = f"{nums[row[0]]}`⠀{row[1]:\u00A0>4}⠀` `⠀{row[2]:\u00A0>22.22}⠀`"
            data.append(formatted)
        pages = menus.ButtonMenuPages(source=MainEmbedPageSource(data, f"Best Trophy Counts for {clan.name}", 25),
                                      clear_buttons_after=True)
        await pages.start(interaction=interaction)

    @nextcord.slash_command(name="townhalls", description="Clan Members by Town Hall Level")
    async def townhalls(self, interaction, clan: ClanConverter = SlashOption(name="clan", required=True)):
        """List of clan members by town hall level"""
        sql = ("SELECT ROW_NUMBER () OVER (ORDER BY th_level DESC, player_name) as row_num, th_level, player_name "
               "FROM rcs_members WHERE clan_tag = $1")
        fetch = await self.bot.pool.fetch(sql, clan.tag[1:])
        data = []
        for row in fetch:
            formatted = f"{nums[row[0]]}`⠀{row[1]:\u00A0>4}⠀` `⠀{row[2]:\u00A0>22.22}⠀`"
            data.append(formatted)
        pages = menus.ButtonMenuPages(source=MainEmbedPageSource(data, f"TH Levels for {clan.name}", 25),
                                      clear_buttons_after=True)
        await pages.start(interaction=interaction)

    @nextcord.slash_command(name="builderhalls", description="Clan Members by Builder Hall Level")
    async def builderhalls(self, interaction, clan: ClanConverter = SlashOption(name="clan", required=True)):
        """List of clan members by builder hall level"""
        sql = ("SELECT ROW_NUMBER () OVER (ORDER BY bh_level DESC, player_name) as row_num, bh_level, player_name "
               "FROM rcs_members WHERE clan_tag = $1")
        fetch = await self.bot.pool.fetch(sql, clan.tag[1:])
        data = []
        for row in fetch:
            formatted = f"{nums[row[0]]}`⠀{row[1]:\u00A0>4}⠀` `⠀{row[2]:\u00A0>22.22}⠀`"
            data.append(formatted)
        pages = menus.ButtonMenuPages(source=MainEmbedPageSource(data, f"BH Levels for {clan.name}", 25),
                                      clear_buttons_after=True)
        await pages.start(interaction=interaction)

    @nextcord.slash_command(name="warstars", description="War stars for the specified clan")
    async def warstars(self, interaction, clan: ClanConverter = SlashOption(name="clan", required=True)):
        """List of clan members by war stars earned"""
        sql = ("SELECT ROW_NUMBER () OVER (ORDER BY war_stars DESC, player_name) as row_num, war_stars, player_name "
               "FROM rcs_members WHERE clan_tag = $1")
        fetch = await self.bot.pool.fetch(sql, clan.tag[1:])
        data = []
        for row in fetch:
            formatted = f"{nums[row[0]]}`⠀{row[1]:\u00A0>4}⠀` `⠀{row[2]:\u00A0>22.22}⠀`"
            data.append(formatted)
        pages = menus.ButtonMenuPages(source=MainEmbedPageSource(data, f"War Stars for {clan.name}", 25),
                                      clear_buttons_after=True)
        await pages.start(interaction=interaction)

    async def get_member_list(self, field):
        sql = (f"SELECT ROW_NUMBER () OVER (ORDER BY {field} DESC, player_name) as row_num, {field}, "
               f"player_name || ' (' || alt_name || ')' as pname FROM rcs_members "
               f"INNER JOIN rcs_clans ON rcs_clans.clan_tag = rcs_members.clan_tag "
               f"ORDER BY {field} DESC LIMIT 10")
        fetch = await self.bot.pool.fetch(sql)
        return fetch

    @nextcord.slash_command(name="top", description="Slash group for top commands")
    async def top(self, interaction):
        """This is the slash group and will never be called"""
        pass

    @top.subcommand(name="attacks", description="Top ten attack win totals for the RCS")
    async def top_attacks(self, interaction):
        """Displays top ten attack win totals for all of the RCS"""
        fetch = await self.get_member_list("attack_wins")
        title = "RCS Top Ten for Attack Wins"
        data = []
        for row in fetch:
            formatted = f"{nums[row[0]]}`⠀{row[1]:\u00A0>4}⠀` `⠀{row[2]:\u00A0>22.22}⠀`"
            data.append(formatted)
        pages = menus.ButtonMenuPages(source=MainEmbedPageSource(data, title, 10),
                                      clear_buttons_after=True)
        await pages.start(interaction=interaction)

    @top.subcommand(name="defenses", description="Top ten defense win totals for the RCS")
    async def top_defenses(self, interaction):
        """Displays top ten defense win totals for all of the RCS"""
        fetch = await self.get_member_list("defense_wins")
        title = "RCS Top Ten for Defense Wins"
        data = []
        for row in fetch:
            formatted = f"{nums[row[0]]}`⠀{row[1]:\u00A0>4}⠀` `⠀{row[2]:\u00A0>22.22}⠀`"
            data.append(formatted)
        pages = menus.ButtonMenuPages(source=MainEmbedPageSource(data, title, 10),
                                      clear_buttons_after=True)
        await pages.start(interaction=interaction)

    @top.subcommand(name="donates", description="Top ten donation counts for the RCS")
    async def top_donations(self, interaction):
        """Displays top ten donation totals for all of the RCS"""
        fetch = await self.get_member_list("donations")
        title = "RCS Top Ten for Donations"
        data = []
        for row in fetch:
            formatted = f"{nums[row[0]]}`⠀{row[1]:\u00A0>4}⠀` `⠀{row[2]:\u00A0>22.22}⠀`"
            data.append(formatted)
        pages = menus.ButtonMenuPages(source=MainEmbedPageSource(data, title, 10),
                                      clear_buttons_after=True)
        await pages.start(interaction=interaction)

    @top.subcommand(name="level", description="Top ten XP levels for the RCS")
    async def top_levels(self, interaction):
        """Displays top ten Exp Levels for all of the RCS"""
        fetch = await self.get_member_list("exp_level")
        title = "RCS Top Ten for Exp Level"
        data = []
        for row in fetch:
            formatted = f"{nums[row[0]]}`⠀{row[1]:\u00A0>4}⠀` `⠀{row[2]:\u00A0>22.22}⠀`"
            data.append(formatted)
        pages = menus.ButtonMenuPages(source=MainEmbedPageSource(data, title, 10),
                                      clear_buttons_after=True)
        await pages.start(interaction=interaction)

    @top.subcommand(name="trophies", description="Top ten trophy counts for the RCS")
    async def top_trophies(self, interaction):
        """Displays top ten trophy counts for all of the RCS"""
        fetch = await self.get_member_list("trophies")
        title = "RCS Top Ten for Trophies"
        data = []
        for row in fetch:
            formatted = f"{nums[row[0]]}`⠀{row[1]:\u00A0>4}⠀` `⠀{row[2]:\u00A0>22.22}⠀`"
            data.append(formatted)
        pages = menus.ButtonMenuPages(source=MainEmbedPageSource(data, title, 10),
                                      clear_buttons_after=True)
        await pages.start(interaction=interaction)

    @top.subcommand(name="bhtrophies", description="Top ten BH trophies for the RCS")
    async def top_bh_trophies(self, interaction):
        """Displays top ten vs trophy counts for all of the RCS"""
        fetch = await self.get_member_list("vs_trophies")
        title = "RCS Top Ten for Builder Trophies"
        data = []
        for row in fetch:
            formatted = f"{nums[row[0]]}`⠀{row[1]:\u00A0>4}⠀` `⠀{row[2]:\u00A0>22.22}⠀`"
            data.append(formatted)
        pages = menus.ButtonMenuPages(source=MainEmbedPageSource(data, title, 10),
                                      clear_buttons_after=True)
        await pages.start(interaction=interaction)

    @top.subcommand(name="besttrophies", description="Top ten best trophies for the RCS")
    async def top_best_trophies(self, interaction):
        """Displays top ten best trophy counts for all of the RCS"""
        fetch = await self.get_member_list("best_trophies")
        title = "RCS Top Ten for Best Trophies"
        data = []
        for row in fetch:
            formatted = f"{nums[row[0]]}`⠀{row[1]:\u00A0>4}⠀` `⠀{row[2]:\u00A0>22.22}⠀`"
            data.append(formatted)
        pages = menus.ButtonMenuPages(source=MainEmbedPageSource(data, title, 10),
                                      clear_buttons_after=True)
        await pages.start(interaction=interaction)

    @top.subcommand(name="warstars", description="Top ten war stars for the RCS")
    async def top_warstars(self, interaction):
        """Displays top ten war star totals for all of the RCS"""
        fetch = await self.get_member_list("war_stars")
        title = "RCS Top Ten for War Stars"
        data = []
        for row in fetch:
            formatted = f"{nums[row[0]]}`⠀{row[1]:\u00A0>4}⠀` `⠀{row[2]:\u00A0>22.22}⠀`"
            data.append(formatted)
        pages = menus.ButtonMenuPages(source=MainEmbedPageSource(data, title, 10),
                                      clear_buttons_after=True)
        await pages.start(interaction=interaction)

    @nextcord.slash_command(name="reddit", description="Displays the subreddit for the specified clan")
    async def reddit(self, interaction, clan: ClanConverter = SlashOption(name="clan", required=True)):
        """Displays a link to specified clan's subreddit"""
        sql = "SELECT subreddit FROM rcs_clans WHERE clan_tag = $1"
        fetch = await self.bot.pool.fetchrow(sql, clan.tag[1:])
        if fetch['subreddit'] != "":
            await interaction.response.send_message(fetch['subreddit'])
        else:
            await interaction.response.send_message("This clan does not have a subreddit.")

    @nextcord.slash_command(name="discord", description="Displays the link to the clan's Discord server")
    async def discord(self, interaction, clan: ClanConverter = SlashOption(name="clan", required=True)):
        """Displays a link to specified clan's Discord server"""
        sql = "SELECT discord_server FROM rcs_clans WHERE clan_tag = $1"
        fetch = await self.bot.pool.fetchrow(sql, clan.tag[1:])
        if fetch['discord_server']:
            await interaction.response.send_message(fetch['discord_server'])
        else:
            await interaction.response.send_message("This clan does not have a Discord server.")

    @nextcord.slash_command(name="cwl", description="Lists CWL leagues for all RCS clans")
    async def cwl(self, interaction):
        """List CWL leagues of all RCS clans"""
        await interaction.response.defer()
        sort_leagues = cwl_league_order[::-1]
        cwl_clans = {}
        data = []
        for league in sort_leagues:
            cwl_clans[league] = []
        for tag in rcs_tags():
            clan = await self.bot.coc.get_clan(tag)
            league = clan.war_league.name.replace("League ", "")
            cwl_clans[league].append(f"{clan.name} ({clan.tag})")
        for league in sort_leagues:
            content = ""
            for clan in cwl_clans[league]:
                content += f"{clan}\n"
            if content:
                data.append((league, content))
        pages = menus.ButtonMenuPages(source=MainFieldPageSource(data, "RCS CWL Leagues", 3),
                                      clear_buttons_after=True)
        await pages.start(interaction=interaction)

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
        response = await ctx.send(file=nextcord.File(final_buffer, "results.png"))
        # Currently DISABLED - Remove comment to auto-delete response with command
        # self.bot.messages[ctx.message.id] = response

    @nextcord.slash_command(name="season", description="Responds with information on the current COC season")
    async def season(self, ctx):
        """Responds with information on the current COC season"""
        embed = nextcord.Embed(title="Season Information", color=nextcord.Color.green())
        embed.add_field(name="Season Start", value=coc_season.get_season_start())
        embed.add_field(name="Season End", value=coc_season.get_season_end())
        embed.add_field(name="Days Left", value=coc_season.get_days_left())
        embed.set_thumbnail(url="http://www.mayodev.com/images/clock.png")
        response = await ctx.send(embed=embed)

    @nextcord.slash_command(name="get_clan", description="Responds with general information on the specified clan")
    async def get_clan(self, interaction, clan: ClanConverter = SlashOption(name="clan", required=True)):
        """Responds with general information on the specified clan"""
        embed = nextcord.Embed(title=clan.name, color=nextcord.Color.dark_red(), description=clan.description)
        embed.set_thumbnail(url=clan.badge.url)
        embed.add_field(name="Clan Tag", value=clan.tag)
        embed.add_field(name="Clan Level", value=clan.level)
        embed.add_field(name="War Log", value="Public" if clan.public_war_log else "Private")
        embed.set_footer(text=f"War Record: {clan.war_wins}-{clan.war_losses}-{clan.war_ties}")
        await interaction.response.send_message(embed=embed)


def setup(bot):
    bot.add_cog(General(bot))
