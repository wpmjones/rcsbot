import nextcord
import json
import requests
import requests_cache

from nextcord.ext import commands
from config import settings

requests_cache.install_cache("vin_requests")


class Eggs(commands.Cog):
    """Cog for easter egg commands (guess away)
    This is also where I try out some new commands, so it's for testing too.
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="avatar", hidden=True)
    async def avatar(self, ctx, user: nextcord.Member = None):
        """Command to see a larger version of the given member's avatar

        Examples:
        ++avatar @mention
        ++avatar 123456789
        ++avatar member#1234
        """
        if not user:
            user = ctx.author
        embed = nextcord.Embed(color=nextcord.Color.blue())
        embed.add_field(name=f"{user.name}#{user.discriminator}", value=user.display_name, inline=True)
        embed.add_field(name="Avatar URL", value=user.avatar_url, inline=True)
        embed.set_image(url=user.avatar_url_as(size=128))
        embed.set_footer(text=f"Discord ID: {user.id}",
                         icon_url="https://discordapp.com/assets/2c21aeda16de354ba5334551a883b481.png")
        response = await ctx.send(embed=embed)
        self.bot.messages[ctx.message.id] = response

    @commands.command(name="vin", hidden=True)
    async def vin(self, ctx, input_vin):
        """[Easter Egg] Decodes the input VIN and responds with the make/model information"""
        api_url = f"http://api.carmd.com/v3.0/decode?vin={input_vin}"
        headers = {
            "accept": "application/json",
            "authorization": settings['api']['vin_key'],
            "partner-token": settings['api']['vin_token']
        }
        r = requests.get(api_url, headers=headers)
        data = r.json()
        # data = {'message': {'code': 0, 'message': 'ok', 'credentials': 'valid', 'version': 'v3.0.0',
        #                     'endpoint': 'decode', 'counter': 1},
        #         'data': {'year': 2006, 'make': 'HONDA', 'model': 'CIVIC', 'manufacturer': 'HONDA',
        #                  'engine': 'L4, 1.8L; SOHC; 16V', 'trim': 'EX', 'transmission': 'STANDARD'}
        #         }
        made_year = data['data']['year']
        manufacturer = data['data']['manufacturer']
        make = data['data']['make']
        model = data['data']['model']
        engine = data['data']['engine']
        trim = data['data']['trim']
        car_name = f"{made_year} {make} {model}"
        car_info = ""
        if make != manufacturer:
            car_info += f"\nManufactured by: {manufacturer}"
        car_info += f"\nTrim package: {trim}"
        car_info += f"\nEngine: {engine}"
        embed = nextcord.Embed(title=make, color=nextcord.Color.red())
        embed.add_field(name=car_name, value=car_info)
        logos_json = open("static/car_logos.json")
        logos_data = json.load(logos_json)
        if make.lower() in logos_data.keys():
            embed.set_thumbnail(url=logos_data[make.lower()])
        await ctx.send(embed=embed)

    @commands.command(name="zag", aliases=["zag-geek", "zaggeek"], hidden=True)
    async def zag(self, ctx):
        """[Easter Egg] Photo of Zag-geek"""
        response = await ctx.send(file=nextcord.File("/home/tuba/rcsbot/cogs/zag.jpg"))
        self.bot.messages[ctx.message.id] = response

    @commands.command(name="tuba", hidden=True)
    async def tuba(self, ctx):
        """[Easter Egg] Not a photo of TubaKid"""
        response = await ctx.send(file=nextcord.File("/home/tuba/rcsbot/cogs/tuba.jpg"))
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


def setup(bot):
    bot.add_cog(Eggs(bot))
