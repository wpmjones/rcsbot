import discord
import requests
import pathlib

from discord.ext import commands
from cogs.utils import season as coc_season
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
from io import BytesIO
from random import randint
from datetime import datetime
from config import settings


class Eggs(commands.Cog):
    """Cog for easter egg commands (guess away)
    This is also where I try out some new commands, so it's for testing too.
    """
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="avatar", hidden=True)
    async def avatar(self, ctx, user: discord.Member = None):
        """Command to see a larger version of the given member's avatar

        Examples:
        ++avatar @mention
        ++avater 123456789
        ++avatar member#1234
        """
        if not user:
            user = ctx.author
        embed = discord.Embed(color=discord.Color.blue())
        embed.add_field(name=f"{user.name}#{user.discriminator}", value=user.display_name, inline=True)
        embed.add_field(name="Avatar URL", value=user.avatar_url, inline=True)
        embed.set_image(url=user.avatar_url_as(size=128))
        embed.set_footer(text=f"Discord ID: {user.id}",
                         icon_url="https://discordapp.com/assets/2c21aeda16de354ba5334551a883b481.png")
        response = await ctx.send(embed=embed)
        self.bot.messages[ctx.message.id] = response

    @commands.command(name="zag", aliases=["zag-geek", "zaggeek"], hidden=True)
    async def zag(self, ctx):
        """[Easter Egg] Photo of Zag-geek"""
        response = await ctx.send(file=discord.File("/home/tuba/rcsbot/cogs/zag.jpg"))
        self.bot.messages[ctx.message.id] = response

    @commands.command(name="tuba", hidden=True)
    async def tuba(self, ctx):
        """[Easter Egg] Not a photo of TubaKid"""
        response = await ctx.send(file=discord.File("/home/tuba/rcsbot/cogs/tuba.jpg"))
        self.bot.messages[ctx.message.id] = response

    @commands.command(name="password", hidden=True)
    async def password(self, ctx):
        """[Easter Egg] Information on the RCS password"""
        content = ("https://www.reddit.com/r/RedditClansHistory/wiki/the_history_of_the_reddit_clans"
                   "#wiki_please_find_the_password")
        response = await ctx.send(content)
        self.bot.messages[ctx.message.id] = response

    @commands.command(name="cats", aliases=["cat"], hidden=True)
    async def kitty(self, ctx):
        """[Easter Egg] Get a photo of a kitty"""
        url = "https://api.thecatapi.com/v1/images/search"
        headers = {
            "Content-Type": "application/json",
            "x-api-key": settings['api']['catKey']
        }
        r = requests.get(url, headers=headers)
        data = r.json()
        content = data[0]['url']
        response = await ctx.send(content)
        self.bot.messages[ctx.message.id] = response

    @commands.command(name="dogs", aliases=["dog"], hidden=True)
    async def puppy(self, ctx):
        """[Easter Egg] Get a photo of a puppy"""
        url = "https://api.thedogapi.com/v1/images/search"
        headers = {
            "Content-Type": "application/json",
            "x-api-key": settings['api']['dogKey']
        }
        r = requests.get(url, headers=headers)
        data = r.json()
        content = data[0]['url']
        response = await ctx.send(content)
        self.bot.messages[ctx.message.id] = response

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
        response = await ctx.send(file=discord.File(final_buffer, f"results.png"))
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
    bot.add_cog(Eggs(bot))
