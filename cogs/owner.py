import discord
import psutil

from discord.ext import commands
from cogs.utils.db import Sql
from cogs.utils import helper
from datetime import datetime


class OwnerCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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

    @commands.command(name="presence", hidden=True)
    @commands.is_owner()
    async def presence(self, ctx, *, msg: str = "default"):
        """Command to modify bot presence"""
        if msg.lower() == "default":
            activity = discord.Game("Clash of Clans")
        else:
            activity = discord.Activity(type=discord.ActivityType.watching, name=msg)
        await self.bot.change_presence(status=discord.Status.online, activity=activity)
        print(f"{datetime.now()} - {ctx.author} changed the bot presence to {msg}")

    @commands.command(name="emojis")
    @commands.is_owner()
    async def emoji_list(self, ctx):
        def get_key(item):
            return item.name

        server_list = [self.bot.get_guild(506645671009583105),
                       self.bot.get_guild(506645764512940032),
                       self.bot.get_guild(531660501709750282),
                       self.bot.get_guild(602130772098416678),
                       self.bot.get_guild(629145390687584260)]
        for guild in server_list:
            content = ""
            for index, emoji in enumerate(sorted(guild.emojis, key=get_key)):
                content += f"\n{emoji} - {emoji.name}:{emoji.id}"
            content = f"**{guild.name}** {index} emoji" + content
            await ctx.send_text(ctx.channel, content)

    @commands.command(name="server")
    @commands.is_owner()
    async def server_list(self, ctx):
        guild_list = []
        for guild in self.bot.guilds:
            guild_list.extend(f"{guild.name} - {guild.id}")
        await ctx.send("\n".join(guild_list))

    @commands.command(name="getroles", hidden=True)
    @commands.is_owner()
    async def getroles(self, ctx, guild_id):
        try:
            guild = self.bot.get_guild(int(guild_id))
            role_list = f"**Roles for {guild.name}**\n"
            for role in guild.roles[1:]:
                role_list += f"{role.name}: {role.id}\n"
            await ctx.send_text(ctx.channel, role_list)
        except:
            self.bot.logger.exception(f"Failed to serve role list")

    @commands.command(name="new_games", hidden=True)
    @commands.is_owner()
    async def new_games(self, ctx, start_date, games_length: int = 6, ind_points: int = 4000, clan_points: int = 50000):
        """Command to add new Clan Games dates to SQL database"""
        with Sql(as_dict=True) as cursor:
            start_day = int(start_date[8:9])
            end_day = str(start_day+games_length)
            end_date = start_date[:9] + end_day
            cursor.execute("SELECT MAX(eventId) as eventId FROM rcs_events WHERE eventType = 5")
            row = cursor.fetchone()
            event_id = row['eventId'] + 1
            sql = (f"INSERT INTO rcs_events (eventId, eventType, startTime, endTime, playerPoints, clanPoints) "
                   f"VALUES ({event_id}, 5, '{start_date}', '{end_date}', {ind_points}, {clan_points})")
            cursor.execute(sql)
        await ctx.send(f"New games info added to database.")

    @commands.command(name="cc", hidden=True)
    @commands.is_owner()
    async def clear_cache(self, ctx):
        content = (f"```python\n"
                   f"rcs_clans: {helper.rcs_clans.cache_info()}\n"
                   f"get_clan: {helper.get_clan.cache_info()}```")
        helper.rcs_clans.cache_clear()
        helper.get_clan.cache_clear()
        content += "Caches cleared"
        await ctx.send(content)

    @commands.command(hidden=True)
    @commands.is_owner()
    async def process(self, ctx):
        memory_usage = self.process.memory_full_info().uss / 1024 ** 2
        cpu_usage = self.process.cpu_percent() / psutil.cpu_count()
        await ctx.send(f'{memory_usage:.2f} MiB\n{cpu_usage:.2f}% CPU')


def setup(bot):
    bot.add_cog(OwnerCog(bot))
