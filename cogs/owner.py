import discord
import season
import traceback
import pymssql
from config import settings
from datetime import datetime
from discord.ext import commands


class OwnerCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="load", hidden=True)
    @commands.is_owner()
    async def load(self, ctx, *, cog: str):
        """Command which loads a module.
        Remember to use dot path. e.g: cogs.owner"""

        try:
            self.bot.load_extension(cog)
        except Exception as e:
            print(f"ERROR: {type(e).__name__} - {e}")
            await ctx.send(f"**`ERROR:`** {type(e).__name__} - {e}")
        else:
            print(f"{cog} successfully loaded")
            await ctx.send("**`SUCCESS`**")

    @commands.command(name="unload", hidden=True)
    @commands.is_owner()
    async def unload(self, ctx, *, cog: str):
        """Command which unloads a module.
        Remember to use dot path. e.g: cogs.owner"""

        try:
            self.bot.unload_extension(cog)
        except Exception as e:
            print(f"ERROR: {type(e).__name__} - {e}")
            await ctx.send(f"**`ERROR:`** {type(e).__name__} - {e}")
        else:
            print(f"{cog} successfully unloaded")
            await ctx.send("**`SUCCESS`**")

    @commands.command(name="reload", hidden=True)
    @commands.is_owner()
    async def reload(self, ctx, *, cog: str):
        """Command which reloads a module.
        Remember to use dot path. e.g: cogs.owner"""

        try:
            self.bot.unload_extension(cog)
            self.bot.load_extension(cog)
        except Exception as e:
            print(f"ERROR: {type(e).__name__} - {e}")
            await ctx.send(f"**`ERROR:`** {type(e).__name__} - {e}")
        else:
            print(f"{cog} reloaded successfully")
            await ctx.send("**`SUCCESS`**")

    @commands.command(name="clear")
    @commands.is_owner()
    async def clear(self, ctx):
        async for message in ctx.channel.history():
            await message.delete()

    @commands.command(name="pull", hidden=True)
    @commands.is_owner()
    async def git_pull(self, ctx):
        """Command to pull latest updates from master branch on GitHub"""
        origin = self.bot.repo.remotes.origin
        try:
            origin.pull()
            print("Code successfully pulled from GitHub")
            await ctx.send("Code successfully pulled from GitHub")
        except Exception as e:
            print(f"ERROR: {type(e).__name__} - {e}")
            await ctx.send(f"**`ERROR:`** {type(e).__name__} - {e}")

    @commands.command(name="emojis")
    @commands.is_owner()
    async def emoji_list(self, ctx):
        server_list = [self.bot.get_guild(506645671009583105),
                       self.bot.get_guild(506645764512940032),
                       self.bot.get_guild(531660501709750282)]
        for guild in server_list:
            content = f"**{guild.name}**\n"
            for emoji in guild.emojis:
                content += f"\n{emoji} - {emoji.name}: {emoji.id}"
            await ctx.send(content)

    @commands.command(name="server")
    @commands.is_owner()
    async def server_list(self, ctx):
        guild_count = len(self.bot.guilds)
        # TODO create embed with guild.name and guild.owner
        for guild in self.bot.guilds:
            await ctx.send(guild.name)

    @commands.command(name="close_db", aliases=["cdb", "cbd"], hidden=True)
    @commands.is_owner()
    async def close_db(self, ctx):
        """Command to close db connection before shutting down bot"""
        if self.bot.db.pool is not None:
            await self.bot.db.pool.close()
            await ctx.send("Database connection closed.")

    @commands.command(name="season", hidden=True)
    @commands.is_owner()
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

    @commands.command(name="new_games", hidden=True)
    @commands.is_owner()
    async def new_games(self, ctx, start_date, games_length: int = 6, ind_points: int = 4000, clan_points: int = 50000):
        """Command to add new Clan Games dates to SQL database"""
        conn = pymssql.connect(settings['database']['server'],
                               settings['database']['username'],
                               settings['database']['password'],
                               settings['database']['database'])
        cursor = conn.cursor(as_dict=True)
        start_day = int(start_date[8:9])
        end_day = str(start_day+games_length)
        end_date = start_date[:9] + end_day
        # TODO add eventId (auto generated?)
        # TODO regex for date OR enter date only
        sql = (f"INSERT INTO rcs_events (eventType, startTime, endTime, playerPoints, clanPoints) "
               f"VALUES (5, '{start_date}', '{end_date}', {ind_points}, {clan_points})")
        cursor.execute(sql)
        conn.commit()
        conn.close()
        await ctx.send(f"New games info added to database.")

    @commands.command()
    @commands.is_owner()
    async def log(self, ctx, num_lines: int = 10):
        with open("rcsbot.log", "r") as f:
            list_start = -1 * num_lines
            await self.send_text(ctx.channel, "\n".join([line for line in f.read().splitlines()[list_start:]]))

    async def send_text(self, channel, text, block=None):
        """ Sends text ot channel, splitting if necessary """
        if len(text) < 2000:
            if block:
                await channel.send(f"```{text}```")
            else:
                await channel.send(text)
        else:
            coll = ""
            for line in text.splitlines(keepends=True):
                if len(coll) + len(line) > 1994:
                    # if collecting is going to be too long, send  what you have so far
                    if block:
                        await channel.send(f"```{coll}```")
                    else:
                        await channel.send(coll)
                    coll = ""
                coll += line
            await channel.send(coll)


def setup(bot):
    bot.add_cog(OwnerCog(bot))
