import discord
import requests
import traceback
import pymssql
import season as coc_season
from datetime import datetime
from discord.ext import commands
from config import settings, emojis, color_pick


class Eggs(commands.Cog):
    """Cog for easter egg commands (guess away)
    This is also where I try out some new commands, so it's for testing too.
    """
    def __init__(self, bot):
        self.bot = bot

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
        await self.send_embed(ctx.channel,
                              "RCS Clan War Status",
                              "This does not include CWL wars.",
                              in_prep,
                              discord.Color.dark_gold())
        await self.send_embed(ctx.channel,
                              "RCS Clan War Status",
                              "This does not include CWL wars.",
                              in_war,
                              discord.Color.dark_red())

    @commands.group(invoke_without_subcommands=True)
    async def season(self, ctx):
        """Group of commands to deal with the current COC season"""
        if ctx.invoked_subcommand is None:
            desc = "All commands must begin with a ++"
            embed = discord.Embed(title="rcs-bot Help File", description=desc, color=color_pick(15, 250, 15))
            embed.add_field(name="Commands:", value="-----------", inline=False)
            help_text = "Responds with the information on the current COC season."
            embed.add_field(name="++season info", value=help_text)
            embed.set_footer(icon_url="https://openclipart.org/image/300px/svg_to_png/122449/1298569779.png",
                             text="rcs-bot proudly maintained by TubaKid.")
            return await ctx.send(embed=embed)

    @season.command(name="change")
    @commands.is_owner()
    async def change(self, ctx, arg: str = ""):
        """Command to modify the season information"""
        if datetime.now() < datetime.strptime(coc_season.get_season_end(), "%Y-%m-%d"):
            return await ctx.send("I would much prefer it if you waited until the season ends to change the dates.")
        try:
            coc_season.update_season(arg)
        except ValueError as ex:
            return await ctx.send(log_traceback(ex))
        except Exception as ex:
            return await ctx.send(log_traceback(ex))
        await ctx.send(f"File updated.  The new season ends in {coc_season.get_days_left()} days.")

    @season.command(name="info")
    async def season_info(self, ctx):
        """Command to display the season information"""
        embed = discord.Embed(title="Season Information", color=discord.Color.green())
        embed.add_field(name="Season Start", value=coc_season.get_season_start())
        embed.add_field(name="Season End", value=coc_season.get_season_end())
        embed.add_field(name="Days Left", value=coc_season.get_days_left())
        embed.set_thumbnail(url="http://www.mayodev.com/images/clock.png")
        return await ctx.send(embed=embed)

    async def send_embed(self, channel, header, footer, text, embed_color):
        """ Sends embed to channel, splitting if necessary """
        self.bot.logger.debug(f"Content is {len(text)} characters long.")
        if len(text) < 1000:
            embed = discord.Embed(color=embed_color)
            embed.add_field(name=header, value=text, inline=False)
            embed.set_footer(text=footer)
            await channel.send(embed=embed)
        else:
            coll = ""
            for line in text.splitlines(keepends=True):
                if len(coll) + len(line) > 1000:
                    embed = discord.Embed(color=embed_color)
                    embed.add_field(name=header, value=coll, inline=False)
                    await channel.send(embed=embed)
                    header = "Continued..."
                    coll = ""
                coll += line
            embed = discord.Embed(color=embed_color)
            embed.add_field(name=header, value=coll, inline=False)
            embed.set_footer(text=footer)
            await channel.send(embed=embed)


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
