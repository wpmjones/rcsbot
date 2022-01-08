import asyncio
import coc
import nextcord

from nextcord.ext import commands
from datetime import datetime, timedelta
from config import settings


class Miniwar(commands.Cog):
    """Cog for Miniwar bot commands"""
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="miniwar")
    async def miniwar(self, ctx):
        """
        Command to initiate a new miniwar

        **Permissions:**
        Leaders

        **Example:**
        ++miniwar

        **Other info:**
        The bot will respond and prompt the user for necessary info for the miniwar
        """
        def check_author(m):
            return m.author == ctx.author

        # ask for clan one
        try:
            await ctx.send("Please provide the clan tag for the first clan")
            response = await ctx.bot.wait_for("message", check=check_author, timeout=30)
        except asyncio.TimeoutError:
            return await ctx.send("Time's up! Try again some other time.")
        # confirm clan one
        try:
            clan1 = await ctx.coc.get_clan(response.content)
            await ctx.send(f"Clan #1: {clan1.name}")
        except coc.NotFound:
            raise commands.BadArgument(f"{response.content} is not a valid clan tag. I'm sorry but you'll have to "
                                       f"start over once you find the correct clan tag.")
        # ask for clan two
        try:
            await ctx.send("Please provide the clan tag for the second clan")
            response = await ctx.bot.wait_for("message", check=check_author, timeout=30)
        except asyncio.TimeoutError:
            return await ctx.send("Time's up! Try again some other time.")
        # confirm clan two
        try:
            clan2 = await ctx.coc.get_clan(response.content)
            await ctx.send(f"Clan #2: {clan2.name}")
        except coc.NotFound:
            raise commands.BadArgument(f"{response.content} is not a valid clan tag. I'm sorry but you'll have to "
                                       f"start over once you find the correct clan tag.")
        # ask for start time
        try:
            await ctx.send("How long until you'd like to start this miniwar? (minutes or hours)")
            response = await ctx.bot.wait_for("message", check=check_author, timeout=30)
            if int(response.content) < 12:
                time_til_start = int(response.content) * 60
            else:
                time_til_start = int(response.content)
        except asyncio.TimeoutError:
            return await ctx.send("You're time has expired. Chat with you later!")
        # ask for prep length
        prompt = await ctx.prompt("How long will the prep time be?\n"
                                  ":one: - 15 minutes\n"
                                  ":two: - 30 minutes\n"
                                  ":three: - 1 hour\n"
                                  ":four: - 2 hours",
                                  additional_options=4)
        if prompt == 1:
            prep_length = 15
        elif prompt == 2:
            prep_length = 30
        elif prompt == 3:
            prep_length = 60
        elif prompt == 4:
            prep_length = 120
        else:
            return await ctx.send("I got a little bored waiting for a response. Please start over.")
        # ask for war length
        prompt = await ctx.prompt("How long will the battle time be?\n"
                                  ":one: - 15 minutes\n"
                                  ":two: - 30 minutes\n"
                                  ":three: - 1 hour\n"
                                  ":four: - 2 hours\n"
                                  ":five: - 4 hours",
                                  additional_options=5)
        if prompt == 1:
            war_length = 15
        elif prompt == 2:
            war_length = 30
        elif prompt == 3:
            war_length = 60
        elif prompt == 4:
            war_length = 120
        elif prompt == 5:
            war_length = 240
        else:
            return await ctx.send("I got a little bored waiting for a response. Please start over.")
        # confirm info and store to db
        match_time = datetime.utcnow() + timedelta(minutes=time_til_start)
        end_time = match_time + timedelta(minutes=prep_length + war_length)
        if prep_length >= 60:
            prep_time = f"{prep_length / 60:.0f} hour(s)"
        else:
            prep_time = f"{prep_length} minutes"
        if war_length >= 60:
            war_time = f"{war_length / 60:.0f} hour(s)"
        else:
            war_time = f"{war_length} minutes"
        match_info = (f"**Miniwar:** {clan1.name} vs. {clan2.name}\n"
                      f"Match to occur at {match_time} UTC\n"
                      f"Prep Length: {prep_time}\n"
                      f"War Length: {war_time}")
        confirm = await ctx.prompt(f"{match_info}\n\nIs the above information correct?")
        if not confirm:
            return await ctx.send("Sorry. It's probably my fault.  It's always my fault.  Run `++miniwar` again and "
                                  "I'll try to do better this time.")
        # DB Insert happens here
        sql = ("INSERT INTO rcs_miniwar (organizer_discord_id, clan_tag_1, clan_tag_2, "
               "start_time, end_time prep_length, war_length)"
               "VALUES ($1, $2, $3, $4, $5, $6, $7)")
        await self.bot.pool.execute(sql, ctx.author.id, clan1.tag, clan2.tag, match_time, end_time,
                                    prep_length, war_length)
        # Create channels, roles, perms, announce in global


def setup(bot):
    bot.add_cog(Miniwar(bot))
