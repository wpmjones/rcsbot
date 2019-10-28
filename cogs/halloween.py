import discord
import random
import asyncio

from discord.ext import commands
from cogs.utils.db import Sql
from cogs.utils.helper import get_emoji_url
from cogs.utils.constants import answers, responses, wrong_answers_resp, testers, halloween_channels, safe_channels
from cogs.utils import challenges
from datetime import datetime
from config import settings


class Halloween(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.title = "🎃 RCS Trick or Treat Adventure 🎃"
        self.color = discord.Color.dark_orange()
        self.event_end = datetime(2019, 11, 1, 3, 00, 00)

    def build_embed(self, data):
        embed = discord.Embed(title=data['title'], description=data['challenge'], color=self.color)
        embed.set_author(name=self.title)
        embed.add_field(name="Players:", value=data['num_players'], inline=True)
        embed.add_field(name="Players Finished:", value=data['num_finished'], inline=True)
        embed.add_field(name="Skips:", value=data['skips'], inline=True)
        if data['image_url']:
            embed.set_image(url=data['image_url'])
        embed.set_footer(text=f"{data['elapsed']} elapsed in your adventure",
                         icon_url="https://cdn.discordapp.com/emojis/629481616091119617.png")
        return embed

    def completion_msg(self, data):
        hours_to_end, mins_to_end, _ = self.get_elapsed(datetime.utcnow(), self.event_end)
        elapsed = f"{data['elapsed'][0]:02}:{data['elapsed'][1]:02}:{data['elapsed'][2]:02}"
        desc = (f"Fantastic job {data['player_name']}!  You have completed the first ever "
                f"🎃 RCS Trick or Treat Adventure 🎃! We hope that there were some treats to go along with "
                f"the tricks we threw at you.  And most of all, we hope you had "
                f"fun!  Once everyone is done (or time runs out), we'll take a look and see who was the fastest "
                f"and announce things in <#298622700849463297>.")
        embed = discord.Embed(title=self.title, description=desc, color=self.color)
        embed.add_field(name="Players:", value=data['num_players'], inline=True)
        embed.add_field(name="Players Finished:", value=data['num_finished'], inline=True)
        embed.add_field(name="Your progress:", value="Finished!", inline=True)
        embed.add_field(name="Completion Time:", value=elapsed, inline=True)
        embed.set_footer(text=f"The event ends in {hours_to_end} hours and {mins_to_end} minutes.",
                         icon_url="https://cdn.discordapp.com/emojis/629481616091119617.png")
        return embed

    @staticmethod
    def get_elapsed(start_time, _now):
        elapsed = _now - start_time
        days_hours = elapsed.days * 24
        hours, rem = divmod(elapsed.seconds, 3600)
        hours = hours + days_hours
        mins, secs = divmod(rem, 60)
        return hours, mins, secs

    @property
    def invite_link(self):
        perms = discord.Permissions.none()
        perms.read_messages = True
        perms.external_emojis = True
        perms.send_messages = True
        perms.manage_channels = True
        perms.manage_messages = True
        perms.embed_links = True
        perms.read_message_history = True
        perms.add_reactions = True
        perms.attach_files = True
        return discord.utils.oauth_url(self.bot.client_id, perms)

    @commands.group(name="halloween", aliases=["h"])
    async def halloween(self, ctx):
        """[Group] Let the halloween fun begin!  Trick or treat!

            Use ++challenge to get the next challenge (on the appropriate Discord server
            Use ++remind in case you've forgotten what challenge you are working on or get stuck
            When answering challenges, you do not need the ++ unless the bot tells you to use it
        """
        if ctx.invoked_subcommand is None:
            return await ctx.send_help(ctx.command)

    @halloween.command(name="channels", aliases=["ch"], hidden=True)
    async def channels(self, ctx):
        with Sql() as cursor:
            sql = "SELECT clan_name, channel_id FROM rcs_halloween_clans ORDER BY challenge"
            cursor.execute(sql)
            fetch = cursor.fetchall()
        content = "```"
        for row in fetch:
            content += f"{row[0]}: <#{row[1]}>\n"
        content += "```"
        await ctx.send(content)

    @halloween.command(name="install", hidden=True)
    @commands.is_owner()
    async def halloween_install(self, ctx):
        with Sql(as_dict=True) as cursor:
            sql = "SELECT discord_id FROM rcs_halloween_clans WHERE channel_id IS NULL"
            cursor.execute(sql)
            fetch = cursor.fetchall()
        for clan in fetch:
            guild = ctx.bot.get_guild(clan['discord_id'])
            if not guild:
                await ctx.send(f"rcs-bot has not been installed on {clan['discord_id']}")
                continue
            found = False
            bypass = False
            for channel in guild.channels:
                if isinstance(channel, discord.TextChannel) and channel.name == "trick-or-treat":
                    found = True
                    perms = channel.permissions_for(guild.me)
                    if perms.send_messages:
                        await ctx.send(f"#trick-or-treat already exists on the {guild.name} server.")
                    else:
                        await ctx.send(f"I found #trick-or-treat on the {guild.name} server, but I don't have "
                                       f"perms to send messages to the channel.")
                        bypass = True
                    break
            if not found:
                try:
                    overwrites = {
                        ctx.me: discord.PermissionOverwrite(read_messages=True, send_messages=True,
                                                            read_message_history=True, embed_links=True,
                                                            manage_messages=True, add_reactions=True,
                                                            external_emojis=True),
                        guild.default_role: discord.PermissionOverwrite(read_messages=False,
                                                                        send_messages=False,
                                                                        read_message_history=False)
                    }
                    reason = "Channel created by RCS-Bot"
                    channel = await guild.create_text_channel(name="trick-or-treat",
                                                              overwrites=overwrites,
                                                              reason=reason)
                    await ctx.send(f"{channel.name} created on the {guild.name} server.")
                except discord.Forbidden:
                    await ctx.send(f"No perms to create a channel in {guild.name}.")
                    continue
                except:
                    await ctx.send(f"Something else went wrong with {guild}")
                    continue
            if not bypass:
                with Sql(as_dict=True) as cursor:
                    sql = "UPDATE rcs_halloween_clans SET channel_id = %d WHERE discord_id = %d"
                    cursor.execute(sql, (channel.id, guild.id))
                await channel.send("🎃 **Halloween is coming** 🎃\n\n"
                                   "The RCS has something mysterious planned for you.  If you would "
                                   "like to participate, type `++halloween join` and we will send you a "
                                   "message when the fun begins!")
                await channel.send(f"{guild.owner.mention} This channel is currently invisible to `@everyone`. "
                                   f"It will be up to you to open it up to your members when you want to. After that, "
                                   f"you can delete this message!  ;)  Thanks!")
                self.bot.logger.info(f"Messages sent to {guild}")

    @halloween.command(name="init", hidden=True)
    async def init(self, ctx):
        title = "Welcome to the 🎃 RCS Trick or Treat Adventure 🎃"
        desc = ("The fun has begun and the spooks are wandering the servers of the RCS looking for treats "
                "and tricks and innocents on which to pick! Play nice and they will take care. Play mean and they "
                "are sure to scare!\n\n"
                "If you are here to play, type `++challenge` and see what's next.  Use `++remind` if you become "
                "vexxed.")
        embed = discord.Embed(title=title, description=desc, color=self.color)
        for channel_id in halloween_channels:
            channel = self.bot.get_channel(channel_id)
            await channel.send(embed=embed)
        # Get SQL players for production
        with Sql() as cursor:
            sql = "SELECT discord_id FROM rcs_halloween_players"
            cursor.execute(sql)
            players = cursor.fetchall()
        init_msg = ("```The time has come, the Walrus said,\n"
                    "  To talk of many things:\n"
                    "Of shoes — and ships — and sealing-wax —\n"
                    "  Of cabbages — and kings —\n"
                    "And why the sea is boiling hot —\n"
                    "  And whether pigs have wings.```\n\n"
                    "So let's do this thing!  Welcome to the 🎃 **RCS Trick or Treat Adventure** 🎃\n\n"
                    "When you are ready to begin this timed event, just type `++halloween start`.  At the time, "
                    "you will be issued your first challenge and the timer will start. The event will end at 10pm "
                    "ET on Nov. 1.  The fastest person (or ghost) to complete the challenges will be in for a "
                    "treat....")
        for player in players:
            if player[0] not in testers:
                user = self.bot.get_user(player[0])
                await user.send(init_msg)
                await asyncio.sleep(3)
                await user.send("...or a trick!!!\n\n"
                                "`NOTE: Unless specifically instructed to do so, do not use ++ when "
                                "answering challenges.`")

    @halloween.command(hidden=True)
    async def bot(self, ctx):
        await ctx.send(self.invite_link)

    @commands.command()
    async def join(self, ctx):
        await ctx.invoke(self.halloween_join)

    @halloween.command(name="join", aliases=["register"])
    async def halloween_join(self, ctx):
        """ - Issue this command to register for the event"""
        async with ctx.typing():
            with Sql() as cursor:
                sql = ("INSERT INTO rcs_halloween_players (discord_id) "
                       "OUTPUT Inserted.discord_id "
                       "SELECT %d "
                       "EXCEPT SELECT discord_id FROM rcs_halloween_players WHERE discord_id = %d")
                cursor.execute(sql, (ctx.author.id, ctx.author.id))
                fetch = cursor.fetchone()
        if not fetch:
            await ctx.send("You're already registered for the event. I'll send you a DM when the event is "
                           "ready to begin!", delete_after=30)
        else:
            await ctx.send("I've registered you for the event.  I'll send you a DM when the event is ready to begin! "
                           "This message will disappear shortly.",
                           delete_after=30)
        await ctx.message.delete(delay=30)

    @halloween.command(name="start")
    async def halloween_start(self, ctx):
        """ - Issue this command to start the event."""
        # REMOVE THIS BEFORE EVENT STARTS!!!
        if ctx.author.id not in testers:
            self.bot.logger.info(f"{ctx.author} just tried to start Halloween!")
            await ctx.message.delete(delay=30)
            return await ctx.send("We haven't started just yet. We'll let you know when it's time to go!",
                                  delete_after=30)
        async with ctx.typing():
            guild = self.bot.get_guild(settings['discord']['rcsGuildId'])
            tot_role = guild.get_role(636646591880626177)
            member = guild.get_member(ctx.author.id)
            await member.add_roles(tot_role)
            with Sql() as cursor:
                # Check to see if they've already started
                sql = "SELECT start_time FROM rcs_halloween_players WHERE discord_id = %d"
                cursor.execute(sql, ctx.author.id)
                fetch = cursor.fetchone()
                if fetch:
                    if fetch[0]:
                        start_time = fetch[0]
                        return await ctx.send(f"You started the event at {start_time} UTC. If you need a reminder "
                                              f"about your next challenge, just type `++halloween remind`.",
                                              delete_after=60)
                # Initiate time and issue the first clue
                start_time = datetime.utcnow()
                cursor.callproc("rcs_halloween_start", (ctx.author.id, start_time))
                sql = "SELECT COUNT(discord_id) FROM rcs_halloween_players WHERE start_time IS NOT NULL"
                cursor.execute(sql)
                fetch = cursor.fetchone()
                num_players = fetch[0]
                sql = "SELECT channel_ID, invite_link FROM rcs_halloween_clans WHERE discord_id = %d"
                cursor.execute(sql, 437848948204634113)
                fetch = cursor.fetchone()
                electrum_channel = fetch[0]
                electrum_invite = fetch[1]
        desc = ("Congratulations! Your time has started and you have officially begun the RCS Trick or Treat "
                "Adventure! You will now be offered 15 challenges to accomplish. You will have 3 skips that you "
                "can use strategically throughout the event. Use them wisely! The member completing the challenges "
                "in the shortest amount of time wins!")
        clue = (f"Head over to the Reddit Electrum Discord server ({electrum_invite}), "
                f"find the <#{electrum_channel}> channel, and type `++challenge` to begin your first challenge.")
        embed = discord.Embed(description=desc, title=self.title, color=self.color)
        embed.add_field(name="Prize Info:",
                        value="Sexy role color, free socks, and maybe some Clash swag",
                        inline=False)
        embed.add_field(name="Clue #1",
                        value=clue,
                        inline=False)
        embed.set_footer(text=f"{num_players} currently participating",
                         icon_url=get_emoji_url(301032036779425812))
        await ctx.send("I'ma slide into your DMs and get you started.  Have fun!", delete_after=15)
        await ctx.message.delete(delay=15)
        await ctx.author.send(embed=embed)

    @halloween.command(name="reset", hidden=True)
    async def halloween_reset(self, ctx, discord_id):
        with Sql() as cursor:
            sql = ("UPDATE rcs_halloween_players "
                   "SET start_time = NULL, finish_time = NULL, skip_count = 0, last_completed = 0 "
                   "WHERE discord_id = %d")
            cursor.execute(sql, discord_id)
            sql = "DELETE FROM rcs_halloween_skips WHERE discord_id = %d"
            cursor.execute(sql, discord_id)
        await ctx.confirm()

    @commands.command(name="challenge")
    async def challenge(self, ctx):
        """Issued to receive the challenge for that server"""
        # REMOVE THIS BEFORE EVENT STARTS!!!
        if ctx.author.id not in testers:
            self.bot.logger.info(f"{ctx.author} just tried to get a challenge!")
            await ctx.message.delete(delay=30)
            return await ctx.send("We haven't started just yet. We'll let you know when it's time to go!",
                                  delete_after=30)
        async with ctx.typing():
            with Sql(as_dict=True) as cursor:
                sql = ("SELECT last_completed + 1 as cur_challenge, finish_time FROM rcs_halloween_players "
                       "WHERE discord_id = %d")
                cursor.execute(sql, ctx.author.id)
                player_info = cursor.fetchone()
                if player_info['cur_challenge'] > 15:
                    await ctx.message.delete(delay=60)
                    return await ctx.send("What?! 15 challenges weren't enough for you? You've completed all the "
                                          "challenges. Sit back and wait for everyone else to catch up!",
                                          delete_after=60)
                sql = "SELECT challenge FROM rcs_halloween_clans WHERE discord_id = %d"
                cursor.execute(sql, ctx.message.guild.id)
                clan = cursor.fetchone()
                if player_info['finish_time']:
                    await ctx.message.delete(delay=60)
                    return await ctx.send("There are no more challenges for you!  You have completed the event.",
                                          delete_after=60)
                if player_info['cur_challenge'] != clan['challenge']:
                    sql = "SELECT clan_name, invite_link FROM rcs_halloween_clans WHERE challenge = %d"
                    cursor.execute(sql, player_info['cur_challenge'])
                    clan = cursor.fetchone()
                    return await ctx.send(f"Looks like you're on the wrong server for this challenge.  Head over to "
                                          f"{clan['clan_name']} (<{clan['invite_link']}>) and try `++challenge` again.",
                                          delete_after=60)
            # Assume player is on the correct server for the current challenge
            data = await self.get_stats(ctx)
            await ctx.message.delete()
            if data["cur_challenge"] == 2:
                return await self.send_challenge_2(ctx)
            func_call = getattr(challenges, f"challenge_{data['cur_challenge']}")
            data['challenge'], data['title'], data['image_url'] = func_call()
            embed = self.build_embed(data)
            await ctx.author.send(embed=embed)

    async def send_challenge_2(self, ctx):
        reactions_1 = ("🔥", "🕵", "🦁", "🌬")
        reactions_2 = ("🇼", "🇨", "🇧", "🇲", "🇬")
        reactions_3 = (
            "🐾", "💤", "👯", "💼", "🐦", "📞", "🗑", "🌡", "🐍", "🌳", "🗞", "📸", "💳", "🗡", "🔋", "🖊",
            "🔫", "📎", "⏱", "🏀"
        )

        def check_1(reaction, user):
            return user == ctx.message.author and str(reaction.emoji) in reactions_1

        def check_2(reaction, user):
            return user == ctx.message.author and str(reaction.emoji) in reactions_2

        def check_3(reaction, user):
            return user == ctx.message.author and str(reaction.emoji) in reactions_3

        msg = await ctx.author.send(embed=challenges.challenge_2a())
        for r in reactions_1:
            await msg.add_reaction(r)

        for i in range(8):
            try:
                reaction, user = await ctx.bot.wait_for("reaction_add", timeout=120, check=check_1)
            except asyncio.TimeoutError:
                await msg.clear_reactions()
                await msg.edit("You have run out of time. When you're ready, just type `++challenge`.")
                return

            if str(reaction.emoji) != reactions_1[2]:
                await ctx.author.send(random.choice([
                    "I'm afraid that was the wrong door.  You're dead.  But a magical "
                    "fairy has come and brought you back to life.  Try again!",
                    "Do you have a death wish?! You're lucky that you have 9 lives! Try again.",
                    "Are you nuts? There was practically a sign on that door that said 'Die "
                    "here' and you went and opened it!  Fortunately, the Healer was nearby "
                    "and you live to try another door.  One more time..."
                ]))
            else:
                break
        else:
            await msg.clear_reactions()
            await msg.edit("You have run out of time. When you're ready, just type `++challenge`.")
            return

        await ctx.author.send(
            "**That's right!  Wise choice.  Those lions all died of starvation and you are safe!**")

        # 2a complete, start 2b
        msg = await ctx.author.send(embed=challenges.challenge_2b())
        for r in reactions_2:
            await msg.add_reaction(r)

        for i in range(8):
            try:
                reaction, user = await ctx.bot.wait_for("reaction_add", timeout=60, check=check_2)
            except asyncio.TimeoutError:
                await msg.clear_reactions()
                await msg.edit("You have run out of time. When you're ready, just type `++challenge`.")
                return

            if str(reaction.emoji) != reactions_2[3]:
                await ctx.author.send(random.choice([
                    "False arrest. They did nothing wrong! Try again!",
                    "Innocent, I say! Innocent! Try again!",
                    "There is no way you can prove that! Pick someone else!",
                    "And you would be wrong. Check the clues and guess again!",
                    "They didn't do it. Try one more time!"
                ]))
            else:
                break
        else:
            await msg.clear_reactions()
            await msg.edit("You have run out of time. When you're ready, just type `++challenge`.")
            return

        await ctx.author.send("**The maid lied about getting the mail. There is no mail delivery on Sunday!**")

        # 2b complete, start 2c
        msg = await ctx.author.send(embed=challenges.challenge_2c())
        for r in reactions_3:
            await msg.add_reaction(r)

        for i in range(12):
            try:
                reaction, user = await ctx.bot.wait_for("reaction_add", timeout=90, check=check_3)
            except asyncio.TimeoutError:
                await msg.clear_reactions()
                await msg.edit("You have run out of time. When you're ready, just type `++challenge`.")
                return

            if str(reaction.emoji) != reactions_3[11]:
                await ctx.author.send("That's an interesting choice.  Also wrong.  Please try again.")
            else:
                break
        else:
            await msg.clear_reactions()
            await msg.edit("You have run out of time. When you're ready, just type `++challenge`.")
            return

        await ctx.author.send("**He's a photographer of course!  Well done!**")
        await ctx.author.send(responses[2])
        with Sql() as cursor:
            sql = "UPDATE rcs_halloween_players SET last_completed = %d WHERE discord_id = %d"
            cursor.execute(sql, (2, ctx.author.id))

    async def get_stats(self, ctx):
        with Sql() as cursor:
            sql = ("SELECT last_completed, skip_count, start_time "
                   "FROM rcs_halloween_players "
                   "WHERE discord_id = %s")
            cursor.execute(sql, ctx.author.id)
            fetch = cursor.fetchone()
            stats = {"last_completed": fetch[0], "skip_count": fetch[1], "start_time": fetch[2]}
            sql = ("SELECT count(discord_id) as num_players, "
                   "(SELECT count(discord_id) FROM rcs_halloween_players WHERE finish_time IS NOT NULL) as done "
                   "FROM rcs_halloween_players")
            cursor.execute(sql)
            fetch = cursor.fetchone()
        hours, mins, secs = self.get_elapsed(stats["start_time"], datetime.utcnow())
        data = {
            "num_players": fetch[0],
            "num_finished": fetch[1],
            "cur_challenge": stats["last_completed"] + 1,
            "skips": f"{stats['skip_count']}/3",
            "elapsed": f"{hours:02}:{mins:02}:{secs:02}"
        }
        return data

    @commands.command(name="remind", aliases=["reminder"])
    async def remind(self, ctx):
        # REMOVE THIS BEFORE EVENT STARTS!!!
        if ctx.author.id not in testers:
            await ctx.message.delete(delay=30)
            return await ctx.send("We haven't started just yet. We'll let you know when it's time to go!",
                                  delete_after=30)
        async with ctx.typing():
            data = await self.get_stats(ctx)
            if data["cur_challenge"] > 15:
                await ctx.message.delete(delay=60)
                return await ctx.send("Can't remind you of anything! You're already done!", delete_after=60)
            if data["cur_challenge"] == 2:
                return await self.send_challenge_2(ctx)
            func_call = getattr(challenges, f"challenge_{data['cur_challenge']}")
            data['challenge'], data['title'], data['image_url'] = func_call()
            embed = self.build_embed(data)
        await ctx.send(f"Sure thing {ctx.author.display_name}!  Here comes a DM with a reminder of where you are.",
                       delete_after=30)
        await ctx.author.send(embed=embed)
        if isinstance(ctx.message.channel, discord.TextChannel):
            try:
                await ctx.message.delete(delay=29)
            except discord.Forbidden:
                self.bot.logger.error(f"Couldn't remove command message on {ctx.message.guild}. Darned perms!")

    @commands.command(name="answer", hidden=True)
    async def answer(self, ctx):
        # REMOVE THIS BEFORE EVENT STARTS!!!
        if ctx.author.id not in testers:
            await ctx.message.delete(delay=30)
            return await ctx.send("We haven't started just yet. We'll let you know when it's time to go!",
                                  delete_after=30)
        with Sql() as cursor:
            sql = "SELECT last_completed FROM rcs_halloween_players WHERE discord_id = %s"
            cursor.execute(sql, ctx.author.id)
            fetch = cursor.fetchone()
            cur_challenge = int(fetch[0]) + 1
            if cur_challenge in (1, 4, 6, 7, 9, 11, 13, 14, 15):
                if cur_challenge == 13 and ctx.message.content.startswith("#"):
                    start = 1
                else:
                    start = 0
                answer = answers[cur_challenge]
                if ctx.message.content.lower()[start:] in answer and cur_challenge != 15:
                    await ctx.author.send(responses[cur_challenge])
                    sql = "UPDATE rcs_halloween_players SET last_completed = %d WHERE discord_id = %d"
                    cursor.execute(sql, (cur_challenge, ctx.author.id))
                elif ctx.message.content.lower() == answer and cur_challenge == 15:
                    guild = self.bot.get_guild(settings['discord']['rcsGuildId'])
                    tot_role = guild.get_role(636646591880626177)
                    party_role = guild.get_role(636646824538669066)
                    member = guild.get_member(ctx.author.id)
                    await member.remove_roles(tot_role)
                    await member.add_roles(party_role)
                    now = datetime.utcnow()
                    sql = ("UPDATE rcs_halloween_players "
                           "SET finish_time = %s, last_completed = 15 "
                           "OUTPUT inserted.start_time "
                           "WHERE discord_id = %d")
                    cursor.execute(sql, (now, ctx.author.id))
                    fetch = cursor.fetchone()
                    start_time = fetch[0]
                    sql = ("SELECT count(discord_id) as num_players, "
                           "(SELECT count(discord_id) FROM rcs_halloween_players WHERE finish_time IS NOT NULL) as done "
                           "FROM rcs_halloween_players")
                    cursor.execute(sql)
                    fetch = cursor.fetchone()
                    embed_data = {
                        "player_name": ctx.author.display_name,
                        "num_players": fetch[0],
                        "num_finished": fetch[1],
                        "elapsed": self.get_elapsed(start_time, now)
                    }
                    embed = self.completion_msg(embed_data)
                    await ctx.author.send(embed=embed)
                    # TODO Send announcement - CHANGE TO 298621931748327426 - give bot perms to SEND
                    news_channel = self.bot.get_channel(628008799663292436)
                    await news_channel.send(f"{ctx.author.display_name} has just completed the "
                                            f"🎃 RCS Trick or Treat Adventure 🎃!")
                else:
                    await ctx.author.send(random.choice(wrong_answers_resp))
            if cur_challenge == 3:
                sql = "SELECT discord_id FROM rcs_halloween_clans WHERE challenge = %d"
                cursor.execute(sql, cur_challenge)
                fetch = cursor.fetchone()
                cur_server = fetch[0]
                if ctx.message.guild.id != cur_server:
                    await ctx.message.delete(delay=30)
                    return await ctx.send("It appears you might be on the wrong server for this challenge. Try "
                                          "`++remind` if you are a bit lost.", delete_after=30)
                if len(ctx.message.attachments) > 0:
                    for attachment in ctx.message.attachments:
                        ext = attachment.filename.split(".")[-1]
                        if ext in ("jpg", "jpeg", "png",  "gif", "tif"):
                            await ctx.author.send(responses[cur_challenge])
                            sql = "UPDATE rcs_halloween_players SET last_completed = %d WHERE discord_id = %d"
                            cursor.execute(sql, (cur_challenge, ctx.author.id))
                            await attachment.save(f"images/3/{ctx.author.display_name}.{ext}")
                        else:
                            await ctx.message.delete(delay=30)
                            return await ctx.send("Nice file, but I don't think that's an image! Try again please!",
                                                  delete_after=30)
                else:
                    await ctx.message.delete(delay=30)
                    return await ctx.send("You need to attach an image for this challenge.",
                                          delete_after=30)
            if cur_challenge == 5:
                clan = await self.bot.coc.get_clan('#2UUCUJL')
                counter = 0
                for p in clan.itermembers:
                    if p.trophies >= 5000:
                        counter += 1
                if ctx.message.content.lower() != str(counter):
                    await ctx.author.send(random.choice(wrong_answers_resp))
                else:
                    await ctx.author.send(responses[cur_challenge])
                    sql = "UPDATE rcs_halloween_players SET last_completed = %d WHERE discord_id = %d"
                    cursor.execute(sql, (cur_challenge, ctx.author.id))
            if cur_challenge == 10:
                cur_channel_id = 443663009743634453
                if ctx.channel.id != cur_channel_id:
                    await ctx.message.delete(delay=30)
                    return await ctx.send("It appears you might be in the wrong channel for this challenge. Try "
                                          "`++remind` if you are a bit lost.", delete_after=30)
                if "231075161556779010" in ctx.message.content:
                    if len(ctx.message.attachments) > 0:
                        for attachment in ctx.message.attachments:
                            ext = attachment.filename.split(".")[-1]
                            if ext in ("jpg", "jpeg", "png", "gif", "tif", "webm"):
                                await ctx.author.send(responses[cur_challenge])
                                sql = "UPDATE rcs_halloween_players SET last_completed = %d WHERE discord_id = %d"
                                cursor.execute(sql, (cur_challenge, ctx.author.id))
                                await attachment.save(f"images/10/{ctx.author.display_name}.{ext}")
                            else:
                                return await ctx.send("Nice file, but I don't think that's an image! Try again please!")
                    else:
                        return await ctx.send("You need to attach an image for this challenge.")

    @commands.command(name="pumpkin")
    async def pumpkin(self, ctx, player: discord.Member):
        if ctx.message.channel.id != 636380378113900544:
            return
        content = ctx.message.content
        guild = ctx.message.guild
        if player.id == ctx.author.id:
            return await ctx.send(f"Nice try but you can't do this one on your own. Recruit someone else to issue "
                                  f"the `++pumpkin {ctx.author.mention}` command for you.")
        with Sql() as cursor:
            sql = "SELECT last_completed + 1 FROM rcs_halloween_players WHERE discord_id = %d"
            cursor.execute(sql, player.id)
            fetch = cursor.fetchone()
            cur_challenge = fetch[0]
        if cur_challenge != 8:
            return await ctx.send(f"I really appreciate your help, but {player.display_name} isn't working on this "
                                  f"challenge right now.")
        embed_msg = (f"Thank you to {ctx.author.display_name} for your help!  {player.display_name}, you have now "
                     f"completed Challenge #8 with Dartaholics!  Check your DMs for your next challenge!")
        embed = discord.Embed(color=self.color)
        embed.add_field(name=f"{player.name}#{player.discriminator}", value=player.display_name, inline=False)
        embed.add_field(name="Challenge Complete!", value=embed_msg, inline=False)
        embed.set_image(url=player.avatar_url_as(size=128))
        embed.set_footer(text=f"Discord ID: {player.id}",
                         icon_url="https://discordapp.com/assets/2c21aeda16de354ba5334551a883b481.png")
        await ctx.send(embed=embed)
        await player.send(responses[8])
        with Sql() as cursor:
            sql = "UPDATE rcs_halloween_players SET last_completed = %d WHERE discord_id = %d"
            cursor.execute(sql, (cur_challenge, player.id))

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if before.guild.id in (602621563770109992, 609516136693760031) and before.nick != after.nick:
            if "🦇" in after.nick:
                await after.send(responses[12])
                with Sql() as cursor:
                    sql = "UPDATE rcs_halloween_players SET last_completed = %d WHERE discord_id = %d"
                    cursor.execute(sql, (12, after.id))

    @commands.command(name="clean_up", hidden=True)
    async def clean_up(self, ctx):
        if ctx.channel.id not in safe_channels:
            content = ctx.message.content
            await ctx.message.delete()
            if content.lower() not in answers.values():
                content = f"**{ctx.author.display_name} said:\n**" + content
                content += ("\n\nWe don't want to clutter up the trick or treat channels. Let's keep the conversation "
                            "here. If you were attempting to answer a question, that wasn't the right answer. "
                            "Maybe give it another shot?")
                return await ctx.author.send(content)
            else:
                content = f"**{ctx.author.display_name} said:\n**" + content
                await ctx.author.send(content)
                await ctx.invoke(self.answer)
        else:
            await ctx.invoke(self.answer)

    @commands.command(name="skip", aliases=["next"])
    async def skip(self, ctx):
        # REMOVE THIS BEFORE EVENT STARTS!!!
        if ctx.author.id not in testers:
            await ctx.message.delete(delay=30)
            return await ctx.send("We haven't started just yet. We'll let you know when it's time to go!",
                                  delete_after=30)
        async with ctx.typing():
            with Sql() as cursor:
                sql = ("UPDATE rcs_halloween_players "
                       "SET last_completed = last_completed + 1, skip_count = skip_count + 1 "
                       "OUTPUT inserted.last_completed, inserted.skip_count "
                       "WHERE discord_id = %s and skip_count < 3")
                cursor.execute(sql, ctx.author.id)
                fetch = cursor.fetchone()
                if not fetch:
                    return await ctx.send("I'm sorry, but you've already used all 3 skips. Gotta finish this one!")
                last_completed = fetch[0]
                skips_left = 3 - fetch[1]
                sql = ("INSERT INTO rcs_halloween_skips (discord_id, challenge) "
                       "VALUES (%d, %d)")
                cursor.execute(sql, (ctx.author.id, last_completed))
                self.bot.logger.info(f"{ctx.author} skipped Challenge #{last_completed}.")
                if last_completed != 15:
                    await ctx.send(f"Challenge #{last_completed} skipped. You have {skips_left} skips left.",
                                   delete_after=60)
                    return await ctx.author.send(responses[last_completed])
                else:
                    # Final challenge skipped
                    now = datetime.utcnow()
                    sql = ("UPDATE rcs_halloween_players "
                           "SET finish_time = %s "
                           "OUTPUT inserted.start_time "
                           "WHERE discord_id = %d")
                    cursor.execute(sql, (now, ctx.author.id))
                    fetch = cursor.fetchone()
                    start_time = fetch[0]
                    sql = ("SELECT count(discord_id) as num_players, "
                           "(SELECT count(discord_id) FROM rcs_halloween_players WHERE finish_time IS NOT NULL) as done "
                           "FROM rcs_halloween_players")
                    cursor.execute(sql)
                    fetch = cursor.fetchone()
                    embed_data = {
                        "player_name": ctx.author.display_name,
                        "num_players": fetch[0],
                        "num_finished": fetch[1],
                        "elapsed": self.get_elapsed(start_time, now)
                    }
                    embed = self.completion_msg(embed_data)
                    await ctx.send(embed=embed)
                    # TODO Send announcement - CHANGE TO 298621931748327426 - give bot perms to SEND
                    news_channel = self.bot.get_channel(628008799663292436)
                    await news_channel.send(f"{ctx.author.display_name} has just completed the "
                                            f"🎃 RCS Trick or Treat Adventure 🎃!")


def setup(bot):
    bot.add_cog(Halloween(bot))
