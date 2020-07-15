import discord
import coc

from discord.ext import commands, tasks
from cogs.utils.db import Sql
from cogs.utils import helper
from datetime import datetime
from config import settings


class OwnerCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.update_warlog.start()

    def cog_unload(self):
        self.update_warlog.cancel()

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
        for counter, guild in enumerate(self.bot.guilds):
            guild_list += f"{guild.name} - {guild.id}\n"
        guild_list += f"**RCS-Bot is installed on {counter} servers!**"
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

    @commands.command(name="new_games", hidden=True)
    @commands.is_owner()
    async def new_games(self, ctx, start_date, games_length: int = 6, ind_points: int = 4000, clan_points: int = 50000):
        """Command to add new Clan Games dates to SQL database
        Bot owner only"""
        start_day = int(start_date[8:9])
        end_day = str(start_day + games_length)
        end_date = start_date[:9] + end_day
        with Sql(as_dict=True) as cursor:
            cursor.execute("SELECT MAX(eventId) as eventId FROM rcs_events WHERE eventType = 5")
            row = cursor.fetchone()
            event_id = row['eventId'] + 1
            sql = ("INSERT INTO rcs_events (eventId, eventType, startTime, endTime, playerPoints, clanPoints) "
                   "VALUES (%d, %d, %s, %s, %d, %d)")
            cursor.execute(sql, (event_id, 5, start_date, end_date, ind_points, clan_points))
        sql = ("INSERT INTO rcs_events (event_type, start_time, end_time, player_points, clan_points) "
               "VALUES ($1, $2, $3, $4, $5)")
        await self.bot.pool.execute(sql, 5, datetime.strptime(start_date, "%Y-%m-%d"),
                                    datetime.strptime(end_date, "%Y-%m-%d"), ind_points, clan_points)
        await ctx.send(f"New games info added to database.")

    @commands.command(name="new_cwl", hidden=True)
    @commands.is_owner()
    async def new_cwl(self, ctx, start_date, cwl_length: int = 9):
        """Command to add new CWL dates to SQL database
        Bot owner only"""
        # TODO Update postgres as well
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

    @tasks.loop(hours=1)
    async def update_warlog(self):
        conn = self.bot.pool
        for tag in helper.rcs_tags():
            try:
                war_log = await self.bot.coc.get_warlog(f"#{tag}")
            except coc.PrivateWarLog:
                print(f"{tag} has a private war log.")
                continue
            for war in war_log:
                if war.is_league_entry:
                    # skip all CWL wars
                    continue
                sql = ("SELECT war_id, team_size, end_time::timestamp::date, war_state FROM rcs_wars "
                       "WHERE clan_tag = $1 AND opponent_tag = $2 AND end_time < $3")
                fetch = await conn.fetch(sql, tag, war.opponent.tag[1:], datetime.utcnow())
                if fetch:
                    # Update existing data in the database
                    for row in fetch:
                        if row['end_time'] == war.end_time.time.date() and row['war_state'] != "warEnded":
                            # update database to reflect end of war
                            sql = ("UPDATE rcs_wars SET war_state = 'warEnded', clan_attacks = $1, "
                                   "clan_destruction = $2, clan_stars = $3, "
                                   "opponent_destruction = $4, opponent_stars = $5 WHERE war_id = $6")
                            await conn.execute(sql, war.clan.attacks_used, war.clan.destruction, war.clan.stars,
                                               war.opponent.destruction, war.opponent.stars,
                                               row['war_id'])
                            channel = self.bot.get_channel(settings['log_channels']['test'])
                            await channel.send(f"Updated war for {war.clan.name} vs {war.opponent.name}.")
                else:
                    # War is not in database, add it (happens if bot is down)
                    sql = ("INSERT INTO rcs_wars (clan_tag, clan_attacks, clan_destruction, clan_stars,"
                           "opponent_tag, opponent_name, opponent_destruction, opponent_stars,"
                           "end_time, war_state, team_size, reported)"
                           "VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)")
                    await conn.execute(sql, war.clan.tag[1:], war.clan.attacks_used, war.clan.destruction,
                                       war.clan.stars, war.opponent.tag[1:], war.opponent.name,
                                       war.opponent.destruction, war.opponent.stars,
                                       war.end_time.time, "warEnded", war.team_size, False)
                    self.bot.logger.info(f"Added war for {war.clan.name} vs {war.opponent.name} ending "
                                         f"{war.end_time.time}.")


def setup(bot):
    bot.add_cog(OwnerCog(bot))
