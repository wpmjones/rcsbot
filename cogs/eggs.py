import discord
import requests
import season
import traceback
from discord.ext import commands
from datetime import datetime
from config import settings, emojis


class Eggs(commands.Cog):
    """Cog for easter egg commands (guess away)
    This is also where I try out some new commands, so it's for testing too.
    """
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="season", hidden=True)
    async def season(self, ctx, arg: str = ""):
        """Command to show and modify the season information"""
        if arg == "":
            # Return start/stop of current season and days left
            embed = discord.Embed(title="Season Information", color=discord.Color.green())
            embed.add_field(name="Season Start", value=season.get_season_start())
            embed.add_field(name="Season End", value=season.get_season_end())
            embed.add_field(name="Days Left", value=season.get_days_left())
            embed.set_thumbnail(url="http://www.mayodev.com/images/clock.png")
            await ctx.send(embed=embed)
            return
        if not is_council(ctx.author.roles):
            await ctx.send("I'm sorry. I'd love to help, but you're not authorized to make changes to the season.")
            return
        if datetime.now() < datetime.strptime(season.get_season_end(), "%Y-%m-%d"):
            await ctx.send("I would much prefer it if you waited until the season ends to change the dates.")
            return
        try:
            await ctx.send(arg)
            # await ctx.send(datetime.strptime(arg, "%Y-%m-%d"))
            # new_end_date = datetime.strptime(arg, "%Y-%m-%d")
            season.update_season(arg)
        except ValueError as ex:
            # await ctx.send(f"The date you provided is not in the correct format. "
            #                f"{arg} should be in the YYYY-MM-DD format.")
            await ctx.send(log_traceback(ex))
            return
        except Exception as ex:
            await ctx.send(log_traceback(ex))
            return
        await ctx.send(f"File updated.  The new season ends in {season.get_days_left()} days.")

    @commands.command(name="avatar", hidden=True)
    async def avatar(self, ctx, member):
        # convert discord mention to user id only
        if member.startswith("<"):
            discord_id = "".join(member[2:-1])
            if discord_id.startswith("!"):
                discord_id = discord_id[1:]
        else:
            await ctx.send(emojis['other']['redx'] + """ I don't believe that's a real Discord user. Please 
                make sure you are using the '@' prefix.""")
            return
        guild = ctx.bot.get_guild(settings['discord']['rcsGuildId'])
        is_user, user = is_discord_user(guild, int(discord_id))
        if not is_user:
            await ctx.send(f"{emojis['other']['redx']} **{member}** is not a member of this discord server.")
            return
        embed = discord.Embed(color=discord.Color.blue())
        embed.add_field(name=f"{user.name}#{user.discriminator}", value=user.display_name, inline=True)
        embed.add_field(name="Avatar URL", value=user.avatar_url, inline=True)
        embed.set_image(url=user.avatar_url_as(size=128))
        embed.set_footer(text=f"Discord ID: {user.id}",
                         icon_url="https://discordapp.com/assets/2c21aeda16de354ba5334551a883b481.png")
        await ctx.send(embed=embed)
        bot_log(ctx.command, member, ctx.author, ctx.guild)

    @commands.command(name="zag", aliases=["zag-geek", "zaggeek"], hidden=True)
    async def zag(self, ctx):
#        bot_log(ctx.command, "zag Easter egg", ctx.author, ctx.guild)
        await ctx.send(file=discord.File("/home/tuba/rcsbot/cogs/zag.jpg"))

    @commands.command(name="tuba", hidden=True)
    async def tuba(self, ctx):
#        bot_log(ctx.command, "tuba Easter egg", ctx.author, ctx.guild)
        await ctx.send(file=discord.File("/home/tuba/rcsbot/cogs/tuba.jpg"))

    @commands.command(name="password", hidden=True)
    async def password(self, ctx):
        content = """https://www.reddit.com/r/RedditClansHistory/wiki/the_history_of_the_reddit_
            clans#wiki_please_find_the_password"""
#        bot_log(ctx.command, "password Easter egg", ctx.author, ctx.guild)
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
#        bot_log(ctx.command, "cat api", ctx.author, ctx.guild)
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
#        bot_log(ctx.command, "dog api", ctx.author, ctx.guild)
        await ctx.send(content)


def is_council(user_roles):
    for role in user_roles:
        if role.id == settings['rcsRoles']['council']:
            return True
    return False


def is_discord_user(guild, discord_id):
    try:
        user = guild.get_member(discord_id)
        if user is None:
            return False, None
        else:
            return True, user
    except:
        return False, None


def bot_log(command, author, err_flag=0):
    msg = str(datetime.now())[:16] + " - "
    if err_flag == 0:
        msg += f"Printing {command}. Requested by {author}."
    else:
        msg += f"ERROR: User provided an incorrect argument for {command}. Requested by {author}."
    print(msg)


def log_traceback(ex):
    tb_lines = traceback.format_exception(ex.__class__, ex, ex.__traceback__)
    tb_text = "".join(tb_lines)
    return tb_text


def setup(bot):
    bot.add_cog(Eggs(bot))
