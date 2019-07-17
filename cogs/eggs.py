import discord
import requests
import season
import traceback
import pymssql
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
            season.update_season(arg)
        except ValueError as ex:
            await ctx.send(log_traceback(ex))
            return
        except Exception as ex:
            await ctx.send(log_traceback(ex))
            return
        await ctx.send(f"File updated.  The new season ends in {season.get_days_left()} days.")

    @commands.command(name="avatar", hidden=True)
    async def avatar(self, ctx, user: discord.Member):
        # convert discord mention to user id only
        if user:
            embed = discord.Embed(color=discord.Color.blue())
            embed.add_field(name=f"{user.name}#{user.discriminator}", value=user.display_name, inline=True)
            embed.add_field(name="Avatar URL", value=user.avatar_url, inline=True)
            embed.set_image(url=user.avatar_url_as(size=128))
            embed.set_footer(text=f"Discord ID: {user.id}",
                             icon_url="https://discordapp.com/assets/2c21aeda16de354ba5334551a883b481.png")
            await ctx.send(embed=embed)
            self.bot.logger.info(ctx.command, f"avatar for {user.id}", ctx.author)
        else:
            await ctx.send(emojis['other']['redx'] + """ I don't believe that's a real Discord user. Please 
                make sure you are using the '@' prefix or give me an ID or something I can work with.""")

    @commands.command(name="zag", aliases=["zag-geek", "zaggeek"], hidden=True)
    async def zag(self, ctx):
        await ctx.send(file=discord.File("/home/tuba/rcsbot/cogs/zag.jpg"))

    @commands.command(name="tuba", hidden=True)
    async def tuba(self, ctx):
        await ctx.send(file=discord.File("/home/tuba/rcsbot/cogs/tuba.jpg"))

    @commands.command(name="password", hidden=True)
    async def password(self, ctx):
        content = ("https://www.reddit.com/r/RedditClansHistory/wiki/the_history_of_the_reddit_clans"
                   "#wiki_please_find_the_password")
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
        await ctx.send(content)

    @commands.command(name="in_war", aliases=["inwar"], hidden=True)
    @commands.has_any_role("Admin1", "Leaders", "Council")
    async def in_war(self, ctx):
        sent_msg = await ctx.send("Retrieving clan war status...")
        conn = pymssql.connect(settings['database']['server'],
                               settings['database']['username'],
                               settings['database']['password'],
                               settings['database']['database'])
        cursor = conn.cursor(as_dict=True)
        cursor.execute("SELECT '#' + clanTag AS tag, isWarLogPublic FROM rcs_data "
                       "WHERE classification <> 'feeder' ORDER BY clanName")
        clans = cursor.fetchall()
        conn.close()
        tags = [clan['tag'] for clan in clans if clan['isWarLogPublic'] == 1]
        in_prep = ""
        in_war = ""
        # async for war in self.bot.coc_client.get_current_wars(tags):
        for tag in tags:
            print(tag)
            try:
                war = await self.bot.coc_client.get_clan_war(tag)
                if war.state == "preparation":
                    in_prep += f"{war.clan.name} ({tag}) has {war.start_time.seconds_until // 3600:.0f} hours until war.\n"
                if war.state == "inWar":
                    in_war += f"{war.clan.name} ({tag}) has {war.end_time.seconds_until // 3600:.0f} hours left in war.\n"
            except Exception as e:
                self.bot.logger.exception("get war state")
        await sent_msg.delete()
        embed = discord.Embed(title="RCS Clan War Status", color=discord.Color.dark_gold())
        embed.add_field(name="Clans in prep day",
                        value=in_prep,
                        inline=False)
        embed.set_footer(text="This does not include CWL wars.")
        await ctx.send(embed=embed)
        embed = discord.Embed(title="RCS Clan War Status", color=discord.Color.dark_red())
        embed.add_field(name="Clans in war",
                        value=in_war,
                        inline=False)
        embed.set_footer(text="This does not include CWL wars.")
        await ctx.send(embed=embed)


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


def log_traceback(ex):
    tb_lines = traceback.format_exception(ex.__class__, ex, ex.__traceback__)
    tb_text = "".join(tb_lines)
    return tb_text


def setup(bot):
    bot.add_cog(Eggs(bot))
