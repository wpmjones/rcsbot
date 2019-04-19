import discord
import requests
import pymssql
from discord.ext import commands
from datetime import datetime
from config import settings, emojis

class Eggs:
    """Cog for easter egg commands (guess away)"""
    def __init__(self, bot):
        self.bot = bot

    # TODO improve bot_log

    @commands.command(name="avatar", hidden=True)
    async def avatar(self, ctx, member):
        # convert discord mention to user id only
        if member.startswith("<"):
            discord_id = "".join(member[2:-1])
            if discord_id.startswith("!"):
                discord_id = discord_id[1:]
        else:
            await ctx.send(emojis['other']['redx'] + " I don't believe that's a real Discord user. Please make sure you are using the '@' prefix.")
            return
        guild = ctx.bot.get_guild(settings['discord']['rcsGuildId'])
        is_user, user = is_discord_user(guild, int(discord_id))
        if not is_user:
            await ctx.send(f"{emojis['other']['redx']} User provided **{member}** is not a member of this discord server.")
            return
        embed = discord.Embed(color=discord.Color.blue())
        embed.add_field(name=f"{user.name}#{user.discriminator}\n{user.display_name}", value=user.avatar_url)
        await ctx.send(embed=embed)
        bot_log(ctx.command, ctx.author)

    @commands.command(name="testing", hidden=True)
    async def testing(self, ctx):
        bot_log(ctx.command,ctx.author)
        bk = 33
        aq = 22
        th = 10
        await ctx.send(f"{emojis['th'][th]} {emojis['level'][bk]} {emojis['level'][aq]} {emojis['other']['gap']} {emojis['other']['gap']}TubaToo")

    @commands.command(name="zag", aliases=["zag-geek","zaggeek"], hidden=True)
    async def zag(self, ctx):
        bot_log(ctx.command,ctx.author)
        await ctx.send(file=discord.File("/home/tuba/bot/cogs/zag.jpg"))

    @commands.command(name="tuba", hidden=True)
    async def tuba(self, ctx):
        bot_log(ctx.command,ctx.author)
        await ctx.send(file=discord.File("/home/tuba/bot/cogs/tuba.jpg"))

    @commands.command(name="password", hidden=True)
    async def password(self, ctx):
        content = "https://www.reddit.com/r/RedditClansHistory/wiki/the_history_of_the_reddit_clans#wiki_please_find_the_password"
        bot_log(ctx.command,ctx.author)
        await ctx.send(content)

    @commands.command(name="cats", aliases=["cat"], hidden=True)
    async def kitty(self, ctx):
        url = "https://api.thecatapi.com/v1/images/search"
        headers = {
            "Content-Type": "application/json",
            "x-api-key": settings['api']['catKey']
        }
        r = requests.get(url, headers=headers)
        data = r.json()
        content = data[0]['url']
        bot_log(ctx.command,ctx.author)
        await ctx.send(content)

    @commands.command(name="dogs", aliases=["dog"], hidden=True)
    async def puppy(self, ctx):
        url = "https://api.thedogapi.com/v1/images/search"
        headers = {
            "Content-Type": "application/json",
            "x-api-key": settings['api']['dogKey']
        }
        r = requests.get(url, headers=headers)
        data = r.json()
        content = data[0]['url']
        bot_log(ctx.command,ctx.author)
        await ctx.send(content)

def is_discord_user(guild, discord_id):
    try:
        user = guild.get_member(discord_id)
        if user is None:
            return False, None
        else:
            return True, user
    except:
        return False, None

def bot_log(command, author, errFlag=0):
    msg = str(datetime.now())[:16] + " - "
    if errFlag == 0:
        msg += f"Printing {command}. Requested by {author}."
    else:
        msg += f"ERROR: User provided an incorrect argument for {command}. Requested by {author}."
    print(msg)

def setup(bot):
    bot.add_cog(Eggs(bot))
