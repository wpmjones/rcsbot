import discord
import coc

from discord.ext import commands, tasks
from cogs.utils.db import Sql
from cogs.utils import helper
from datetime import datetime, timedelta


class OwnerCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="time", hidden=True)
    async def _time(self, ctx):
        await ctx.send(datetime.utcnow())

    @commands.command(name="clear", hidden=True)
    @commands.is_owner()
    async def clear(self, ctx, msg_count: int = None):
        if msg_count:
            await ctx.channel.purge(limit=msg_count + 1)
        else:
            async for message in ctx.channel.history():
                await message.delete()

    @commands.command(name="emojis", hidden=True)
    async def emoji_list(self, ctx):
        """For listing emojis in RCS emoji servers"""
        server_list = [506645671009583105,
                       506645764512940032,
                       531660501709750282,
                       602130772098416678,
                       629145390687584260,
                       ]
        for _id in server_list:
            guild = self.bot.get_guild(_id)
            emoji_list = list(guild.emojis)
            emoji_list.sort(key=lambda e: e.name)
            report = [f"**{guild.name}** {len(emoji_list)} emojis"]
            for emoji in emoji_list:
                report.append(f"<:{emoji.name}:{emoji.id}> - {emoji.name}:{emoji.id}")
                if len("\n".join(report)) > 1900:
                    await ctx.send("\n".join(report))
                    report = []
            if report:
                await ctx.send("\n".join(report))

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

    @commands.command(name="server", hidden=True)
    @commands.is_owner()
    async def server_list(self, ctx):
        """Displays a list of all guilds on which the bot is installed
        Bot owner only"""
        guild_list = ""
        member_count = 0
        for counter, guild in enumerate(self.bot.guilds):
            guild_list += f"{guild.name} - {guild.id}\n"
            member_count += len(guild.members)
        guild_list += f"**RCS-Bot is installed on {counter} servers!**\n{member_count} users."
        await ctx.send(guild_list)

    @commands.command(name="getroles", hidden=True)
    @commands.is_owner()
    async def getroles(self, ctx, guild_id):
        """Displays all roles for the guild ID specified
        Bot owner only"""
        try:
            guild = self.bot.get_guild(int(guild_id))
            role_list = f"**Roles for {guild.name}**\n"
            for role in guild.roles[1:]:
                role_list += f"{role.name}: {role.id}\n"
            await ctx.send_text(ctx.channel, role_list)
        except:
            self.bot.logger.exception(f"Failed to serve role list")

    @commands.command(name="new_cwl", hidden=True)
    @commands.is_owner()
    async def new_cwl(self, ctx, start_date, cwl_length: int = 9):
        """Command to add new CWL dates to SQL database
        Bot owner only"""
        # TODO Automate this in cwl cog
        with Sql(as_dict=True) as cursor:
            start_day = int(start_date[8:9])
            end_day = str(start_day + cwl_length)
            end_date = start_date[:9] + end_day
            season = start_date[:7]
            cursor.execute("SELECT MAX(eventId) as eventId FROM rcs_events WHERE eventType = 11")
            row = cursor.fetchone()
            event_id = row['eventId'] + 1
            sql = (f"INSERT INTO rcs_events (eventId, eventType, startTime, endTime, season) "
                   f"VALUES (%d, %d, %s, %s, %s)")
            cursor.execute(sql, (event_id, 11, start_date, end_date, season))
        await ctx.send(f"New cwl info added to database.")

    @commands.command(name="cc", hidden=True)
    @commands.is_owner()
    async def clear_cache(self, ctx):
        content = (f"```python\n"
                   f"rcs_names_tags: {helper.rcs_names_tags.cache_info()}\n"
                   f"rcs_tags: {helper.rcs_tags.cache_info()}\n"
                   f"get_clan: {helper.get_clan.cache_info()}```")
        helper.rcs_names_tags.cache_clear()
        helper.rcs_tags.cache_clear()
        helper.get_clan.cache_clear()
        content += "Caches cleared"
        await ctx.send(content)


def setup(bot):
    bot.add_cog(OwnerCog(bot))
