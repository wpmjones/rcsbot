import requests
import pymssql
import re
import discord
import asyncio
from discord.ext import commands
from cogs.utils.helper import correct_tag
from config import settings, color_pick
from datetime import datetime


class CouncilCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="form", aliases=["magic"], hidden=True)
    async def magic_form(self, ctx):
        if is_council(ctx.author.roles):
            if ctx.channel.id == settings['rcsChannels']['council']:
                await ctx.send("https://docs.google.com/forms/d/e/1FAIpQLScnSCYr2-"
                               "qA7OHxrf-z0BZFjDr8aRvvHzIM6bIMTLVtlO16GA/viewform")
            else:
                await ctx.send("I think I'll respond in the private council channel.")
                channel = self.bot.get_channel(settings['rcsChannels']['council'])
                await channel.send("https://docs.google.com/forms/d/e/1FAIpQLScnSCYr2-"
                                   "qA7OHxrf-z0BZFjDr8aRvvHzIM6bIMTLVtlO16GA/viewform")
        else:
            await ctx.send("Nice try slick, but this one ain't for you.")

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

    @commands.command(name="rolelist")
    @commands.is_owner()
    async def role_list(self, ctx):
        for guild in self.bot.guilds:
            role_list = f"**Roles for {guild.name}**\n"
            for role in guild.roles[1:]:
                role_list += f"{role.name}: {role.id}\n"
            await ctx.send(role_list)

    @commands.command(name="myroles")
    @commands.is_owner()
    async def my_roles(self, ctx):
        for guild in self.bot.guilds:
            try:
                member = guild.get_member(366778328448892928)
                role_list = ""
                for role in member.roles:
                    if role.name != "@everyone":
                        role_list += f"{role.name}: {role.id}\n"
                await ctx.send(f"**On the {guild.name} server, {member.name} has:**\n{role_list}")
            except:
                await ctx.send(f"**Member has no roles on {guild.name}.**")

    @commands.command(name="userInfo", aliases=["ui"], hidden=True)
    @commands.has_any_role(settings['rcsRoles']['council'], settings['rcsRoles']['chatMods'])
    async def user_info(self, ctx, user: discord.Member):
        """Command to retreive join date for Discord user."""
        today = datetime.now()
        create_date = user.created_at.strftime("%d %b %Y")
        create_delta = (today - user.created_at).days
        join_date = user.joined_at.strftime("%d %b %Y")
        join_delta = (today - user.joined_at).days
        user_roles = []
        for role in user.roles:
            if role.name != "@everyone":
                user_roles.append(role.name)
        embed = discord.Embed(title=user.display_name,
                              description=f"{user.name}#{user.discriminator}",
                              color=color_pick(255, 165, 0))
        embed.set_thumbnail(url=user.avatar_url)
        embed.add_field(name="Joined RCS Server on", value=f"{join_date}\n({join_delta} days ago)", inline=True)
        embed.add_field(name="Discord Creation Date", value=f"{create_date}\n({create_delta} days ago)", inline=True)
        embed.add_field(name="Roles", value=", ".join(user_roles), inline=False)
        embed.set_footer(text=f"User ID: {user.id}")
        await ctx.send(embed=embed)

    @commands.command(name="addClan", aliases=["clanAdd", "newClan"], hidden=True)
    async def add_clan(self, ctx, *, clan_name: str = "x"):
        """Command to add a new verified clan to the RCS Database."""
        if is_council(ctx.author.roles):
            def check_author(m):
                return m.author == ctx.author
            
            def check_reaction(reaction, user):
                return user == ctx.message.author and str(reaction.emoji) in [
                    "<:upvote:295295304859910144>",
                    "<:downvote:295295520187088906>",
                    "🇬", "🇸", "🇨", "🇫"]
            
            def process_content(content):
                if content.lower() in ["stop", "cancel", "quit"]:
                    self.bot.logger.info(f"Process stopped by user ({ctx.command}, {ctx.author})")
                    return content, 1
                if content.lower() == "none":
                    return "", 0
                return content, 0
            continue_flag = 1
            # Get clan name
            if clan_name == "x":
                try:
                    await ctx.send("Please enter the name of the new clan.")
                    response = await ctx.bot.wait_for("message", check=check_author, timeout=10)
                    clan_name, cancel_flag = process_content(response.content)
                except asyncio.TimeoutError:
                    return await ctx.send("Seriously, I'm not going to wait that long. Start over!")
            # Confirm clan name
            try:
                sent_msg = await ctx.send(f"I'd like to confirm that you want to create a new clan with "
                                          "the name **{clan_name}**. Please upvote is this is correct. "
                                          "Downvote to cancel.")
                await sent_msg.add_reaction("upvote:295295304859910144")
                await sent_msg.add_reaction("downvote:295295520187088906")
                reaction, user = await ctx.bot.wait_for("reaction_add", check=check_reaction, timeout=10)
            except asyncio.TimeoutError:
                return await ctx.send("You either don't know how to use emoji or you're just slow.  Try again later.")
            if str(reaction.emoji) == "<:downvote:295295520187088906>":
                await sent_msg.clear_reactions()
                await sent_msg.add_reaction("downvote:295295520187088906")
                return await ctx.send("Clan creation cancelled by user.")
            await sent_msg.clear_reactions()
            await sent_msg.add_reaction("upvote:295295304859910144")
            # Get clan tag
            try:
                await ctx.send(f"What is the clan tag for {clan_name}?")
                response = await ctx.bot.wait_for("message", check=check_author, timeout=15)
                if response.content.startswith("#"):
                    clan_tag, cancel_flag = process_content(response.content[1:])
                else:
                    clan_tag, cancel_flag = process_content(response.content)
                if cancel_flag == 1:
                    return await ctx.send("Creating of new clan cancelled by user.")
            except asyncio.TimeoutError:
                return await ctx.send("I don't have all day and I can't add a clan without a tag. Back to one!")
            # Get leader's in game name
            try:
                await ctx.send("Who leads this mighty clan?")
                response = await ctx.bot.wait_for("message", check=check_author, timeout=15)
                leader, cancel_flag = process_content(response.content)
                if cancel_flag == 1:
                    return await ctx.send("Creating of new clan cancelled by user.")
            except asyncio.TimeoutError:
                return await ctx.send("Might I recommend some typing courses for you? "
                                      "I'm going to rest now. Try again later.")
            # create short name
            try:
                await ctx.send("Please create a short name for this clan. This will be what danger-bot "
                               "uses to search Discord names. Please/use/slashes/to/include/more/than/one.")
                response = await ctx.bot.wait_for("message", check=check_author, timeout=15)
                short_name, cancel_flag = process_content(response.content)
                if cancel_flag == 1:
                    return await ctx.send("Creating of new clan cancelled by user.")
            except asyncio.TimeoutError:
                await ctx.send("OK slow poke. Here's what I'm going to do. I'm going to create this clan "
                               "with the stuff I know, but you'll have to add the rest later!\n**Missing "
                               "info:**\nShort name\nSocial Media\nDescription\nClassification\nSubreddit\n"
                               "Leader's Reddit Username\nLeader's Discord Tag")
                short_name = soc_media = desc = classification = subreddit = leader_reddit = discord_tag = ""
                continue_flag = 0
            # Get social media links
            if continue_flag == 1:
                try:
                    await ctx.send("Please include social media links as follows:\n[Twitter](https://twitter.com/"
                                   "RedditZulu)\nType `none` if there aren't any links to add at this time.")
                    response = await ctx.bot.wait_for("message", check=check_author, timeout=45)
                    soc_media, cancel_flag = process_content(response.content)
                    if cancel_flag == 1:
                        return await ctx.send("Creating of new clan cancelled by user.")
                except asyncio.TimeoutError:
                    await ctx.send(f"I'm stopping here.  {clan_name} has been added to the database, but you'll "
                                   "need to add the rest at a later time.\n**Missing info:**\nSocial Media\n"
                                   "Description\nClassification\nSubreddit\nLeader's Reddit Username\n"
                                   "Leader's Discord Tag")
                    soc_media = desc = classification = subreddit = leader_reddit = discord_tag = ""
                    continue_flag = 0
            # Get Description
            if continue_flag == 1:
                try:
                    await ctx.send("Now I need to know a little bit about the clan.  What notes would you like "
                                   "stored for this clan?")
                    response = await ctx.bot.wait_for("message", check=check_author, timeout=45)
                    desc, cancel_flag = process_content(response.content)
                    if cancel_flag == 1:
                        return await ctx.send("Creating of new clan cancelled by user.")
                except asyncio.TimeoutError:
                    await ctx.send(f"Time's up {ctx.author}. {clan_name} has been added to the database, but "
                                   "you'll need to add the rest at a later time.\n**Missing info:**\n"
                                   "Description\nClassification\nSubreddit\nLeader's Reddit Username\n"
                                   "Leader's Discord Tag")
                    desc = classification = subreddit = leader_reddit = discord_tag = ""
                    continue_flag = 0
            # Get Classification
            if continue_flag == 1:
                try:
                    sent_msg = await ctx.send(f"Please select the appropriate classification for {clan_name}.\n"
                                              ":regional_indicator_g: - General\n:regional_indicator_s: - Social"
                                              "\n:regional_indicator_c: - Competitive\n:regional_indicator_f: - "
                                              "War Farming")
                    await sent_msg.add_reaction("🇬")
                    await sent_msg.add_reaction("🇸")
                    await sent_msg.add_reaction("🇨")
                    await sent_msg.add_reaction("🇫")
                    reaction, user = await ctx.bot.wait_for("reaction_add", check=check_reaction, timeout=10)
                    await sent_msg.clear_reactions()
                    if str(reaction.emoji) == "🇬":
                        classification = "gen"
                        await sent_msg.add_reaction("🇬")
                    if str(reaction.emoji) == "🇸":
                        classification = "social"
                        await sent_msg.add_reaction("🇸")
                    if str(reaction.emoji) == "🇨":
                        classification = "comp"
                        await sent_msg.add_reaction("🇨")
                    if str(reaction.emoji) == "🇫":
                        classification = "warFarm"
                        await sent_msg.add_reaction("🇫")
                except asyncio.TimeoutError:
                    await ctx.send("Can't keep up?  Sorry about that. I've added {clan_name} to the database. "
                                   "You'll need to go back later and add the following.\n**Missing info:**\n"
                                   "Classification\nSubreddit\nLeader's Reddit username\nLeader's Discord Tag")
                    classification = subreddit = leader_reddit = discord_tag = ""
                    continue_flag = 0
            # Get subreddit
            if continue_flag == 1:
                try:
                    await ctx.send("Please provide the subreddit for this clan (if they are cool enough to have one). "
                                   "(no need to include the /r/)\nIf they are lame and don't have a subreddit, "
                                   "type `none`.")
                    response = await ctx.bot.wait_for("message", check=check_author, timeout=20)
                    subreddit, cancel_flag = process_content(response.content)
                    if cancel_flag == 1:
                        return await ctx.send("Creating of new clan cancelled by user.")
                    if subreddit != "":
                        subreddit = f"https://www.reddit.com/r/{subreddit}"
                except asyncio.TimeoutError:
                    await ctx.send(f"Ugh! You've run out of time! I'll add {clan_name} to the database, but you'll "
                                   "need to add missing stuff later!\n**Missing info:**\nLeader's Reddit Username\n"
                                   "Leader's Discord Tag")
                    subreddit = leader_reddit = discord_tag = ""
                    continue_flag = 0
            # Get Reddit Username of leader
            if continue_flag == 1:
                try:
                    await ctx.send(f"Can you please tell me what the reddit username is for {leader}? (No need "
                                   "to include the /u/)")
                    response = await ctx.bot.wait_for("message", check=check_author, timeout=20)
                    leader_reddit, cancel_flag = process_content(response.content)
                    if cancel_flag == 1:
                        return await ctx.send("Creating of new clan cancelled by user.")
                    if leader_reddit != "":
                        leader_reddit = f"https://www.reddit.com/user/{leader_reddit}"
                except asyncio.TimeoutError:
                    await ctx.send(f"I can see we aren't making any progress here. {clan_name} is in the database "
                                   "now, but you'll need to do more!\n**Missing info:**\nLeader's reddit username\n"
                                   "Leader's Discord Tag")
                    leader_reddit = discord_tag = ""
                    continue_flag = 0
            # Get Leader's Discord Tag
            if continue_flag == 1:
                try:
                    await ctx.send(f"Saving the best for last!  What's this guy/gal's Discord Tag?  You know, the "
                                   "long string of numbers that mean nothing to you, but mean everything to me!")
                    response = await ctx.bot.wait_for("message", check=check_author, timeout=15)
                    discord_tag, cancel_flag = process_content(response.content)
                    if cancel_flag == 1:
                        return await ctx.send("Creating of new clan cancelled by user.")
                except asyncio.TimeoutError:
                    await ctx.send(f"You were so close! I'll add {clan_name} to the database now, but you'll "
                                   "need to add the **Discord Tag** later.")
                    discord_tag = ""
            # Log and inform user
            if discord_tag != "":
                print(f"{datetime.now()} - All data collected for {ctx.command}. Adding {clan_name} to database now.")
                await ctx.send(f"All data collected!  Adding to database now.\n**Clan name:** {clan_name}\n"
                               "**Clan Tag:** #{clan_tag}\n**Leader:** {leader}\n**Short Name:** {short_name}\n"
                               "**Social Media:** {soc_media}\n**Notes:** {desc}\n**Classification:** "
                               "{classification}\n**Subreddit:** {subreddit}\n**Leader's Reddit name:** "
                               "{leader_reddit}\n**Leader's Discord Tag:** {discord_tag}")
            # Add info to database
            conn = pymssql.connect(settings['database']['server'],
                                   settings['database']['username'],
                                   settings['database']['password'],
                                   settings['database']['database'],
                                   autocommit=True)
            cursor = conn.cursor(as_dict=True)
            cursor.execute(f"""INSERT INTO rcs_data (clanName, clanTag, clanLeader, shortName, socMedia, 
                           notes, classification, subReddit, leaderReddit, discordTag)
                           VALUES ('{clan_name}', '{clan_tag}', '{leader}', '{short_name}', '{soc_media}', 
                           '{desc}', '{classification}', '{subreddit}', '{leader_reddit}', {discord_tag})""")
            await ctx.send(f"{clan_name} has been added.  Please allow 3 hours for the clan to appear in wiki.")
            await ctx.send(f"**Next Steps:**\nSend mod invite for META\nUpdate clan directory in META\n"
                           "Announce the new clan in Discord")
            # Add leader roles
            guild = ctx.bot.get_guild(settings['discord']['rcsGuildId'])
            is_user, user = is_discord_user(guild, int(discord_tag))
            if not is_user:
                await ctx.send(f"{discord_tag} does not seem to be a valid tag for {leader} or they are not on "
                               "the RCS server yet. You will need to add roles manually.")
            else:
                role_obj = guild.get_role(int(settings['rcsRoles']['leaders']))
                await user.add_roles(role_obj, reason=f"Leaders role added by ++addClan command of rcs-bot.")
                role_obj = guild.get_role(int(settings['rcsRoles']['rcsLeaders']))
                await user.add_roles(role_obj, reason=f"RCS Leaders role added by ++addClan command of rcs-bot.")
                role_obj = guild.get_role(int(settings['rcsRoles']['recruiters']))
                await user.add_roles(role_obj, reason=f"Clan Recruiters role added by ++addClan command of rcs-bot.")
            # Send DM to new leader with helpful links
            member = ctx.guild.get_member(int(discord_tag))
            await member.send(f"Congratulations on becoming a verified RCS clan!  We have added {clan_name} "
                              "to our database and it will appear on the RCS wiki page within the next 3 hours.  "
                              "You should now have the proper Discord roles and be able to see <#298620147424296970> "
                              "and a few other new channels."
                              "\n\n<#308300486719700992> is for the reporting of questionable players. It's not "
                              "necessarily a ban list, but a heads up. If someone with a note in that channel "
                              "joins your clan, you'll receive an alert in <#448918837904146455> letting you."
                              "\n\nThe channels for clan recruitment and events are available to "
                              "you, but if you'd like to add someone else from your clan to help with those "
                              "items, just let one of the Global Chat Mods know (you can @ tag them)."
                              "\n\nFinally, here is a link to some helpful information. "
                              "It's a lot up front, but this will be a great resource going forward. "
                              "https://docs.google.com/document/d/16gfd-BgkGk1bdRmyxIt92BA-tl1NcYk7tuR3HpFUJXg/"
                              "edit?usp=sharing\n\nWelcome to the RCS!")
            self.bot.logger.info(f"{ctx.command} issued by {ctx.author} for {clan_name} (Channel: {ctx.channel})")
        else:
            print(f"{datetime.now()} - ERROR: {ctx.author} from {ctx.guild} tried to use the ++{ctx.command} "
                  "command but shouldn't be doing that.")
            await ctx.send("This command can only be performed by Council members on the RCS Discord server. "
                           "Keep up these antics and I'll tell zig on you!")

    #  @commands.command(name="testdm")
    #  async def testdm(self, ctx, *, arg):
    #    member = ctx.guild.get_member(int(arg))
    #    print(member)
    #    await member.send("This is a test DM from rcs-bot. Please let TubaKid know if you have received it.")

    @commands.command(name="removeClan", aliases=["clanRemove"], hidden=True)
    async def remove_clan(self, ctx, *, arg: str = "x"):
        """Command to remove a verified clan from the RCS database."""
        if is_council(ctx.author.roles):
            clan_tag, clan_name = resolve_clan_tag(arg)
            if clan_tag == "x":
                self.bot.logger.error(f"{arg} did not resolve to a valid clan for the {ctx.command} command. Issued "
                                      f"by {ctx.author} in {ctx.channel}")
                return await ctx.send("You have not provided a valid clan name or clan tag.")
            conn = pymssql.connect(settings['database']['server'], 
                                   settings['database']['username'], 
                                   settings['database']['password'], 
                                   settings['database']['database'], 
                                   autocommit=True)
            cursor = conn.cursor(as_dict=True)
            cursor.execute(f"SELECT clanName, clanTag FROM rcs_data WHERE feeder = '{clan_name}'")
            fetched = cursor.fetchone()
            if fetched is not None:
                self.bot.logger.info(f"Removing family clan for {clan_name}. Issued by {ctx.author} in {ctx.channel}")
                cursor.execute(f"DELETE FROM rcs_data WHERE clanTag = '{fetched['clanTag']}'")
                await ctx.send(f"{fetched['clanName']} (feeder for {clan_name}) has been removed.")
            self.bot.logger.info(f"Removing {clan_name}. Issued by {ctx.author} in {ctx.channel}")
            cursor.execute(f"SELECT leaderReddit, discordTag FROM rcs_data WHERE clanTag = '{clan_tag}'")
            fetched = cursor.fetchone()
            cursor.execute(f"DELETE FROM rcs_data WHERE clanTag = '{clan_tag}'")
            conn.close()
            # remove leader's roles
            guild = ctx.bot.get_guild(settings['discord']['rcsGuildId'])
            is_user, user = is_discord_user(guild, int(fetched['discordTag']))
            if is_user:
                role_obj = guild.get_role(int(settings['rcsRoles']['leaders']))
                await user.remove_roles(role_obj, 
                                        reason=f"Leaders role removed by ++removeClan command of rcs-bot.")
                role_obj = guild.get_role(int(settings['rcsRoles']['rcsLeaders']))
                await user.remove_roles(role_obj, 
                                        reason=f"RCS Leaders role removed by ++removeClan command of rcs-bot.")
                role_obj = guild.get_role(int(settings['rcsRoles']['recruiters']))
                await user.remove_roles(role_obj, 
                                        reason=f"Clan Recruiters role removed by ++removeClan command of rcs-bot.")
            await ctx.send(f"{clan_name} has been removed from the database.  The change will appear on the wiki "
                           "in the next 3 hours.")
            await ctx.send("<@251150854571163648> Please recycle the bot so we aren't embarassed with old data!")
            await ctx.send(f"Please don't forget to remove {fetched['leaderReddit'][22:]} as a mod from META and "
                           f"update the META clan directory.  I've removed the Leaders, RCS Leaders, and Clan "
                           f"Recruiters role from <@{fetched['discordTag']}>. If they have any other roles, "
                           f"you will need to remove them manually.")
        else:
            print(f"{datetime.now()} - ERROR: {ctx.author} from {ctx.guild} tried to use the ++{ctx.command} "
                  "command but shouldn't be doing that.")
            await ctx.send("This command can only be performed by Council members on the RCS Discord server. "
                           "Keep up these antics and I'll tell zig on you!")

    @commands.command(name="leader", hidden=True)
    async def leader(self, ctx, *, arg: str = "x"):
        """Command to find the leader for the selected clan.
        Usage: ++leader Reddit Argon"""
        if is_authorized(ctx.author.roles):
            clan_tag, clan_name = resolve_clan_tag(arg)
            if clan_tag == "x":
                self.bot.logger.error(f"{arg} did not resolve to a valid clan for the {ctx.command} command. Issued "
                                      f"by {ctx.author} in {ctx.channel}")
                await ctx.send("You have not provided a valid clan name or clan tag.")
                return
            conn = pymssql.connect(settings['database']['server'], 
                                   settings['database']['username'], 
                                   settings['database']['password'], 
                                   settings['database']['database'])
            cursor = conn.cursor(as_dict=True)
            cursor.execute(f"SELECT discordTag FROM rcs_data WHERE clanName = '{clan_name}'")
            fetched = cursor.fetchone()
            conn.close()
            if fetched is not None:
                await ctx.send(f"The leader of {clan_name} is <@{fetched['discordTag']}>")
        else:
            self.bot.logger.error(f"{ctx.author} from {ctx.guild} tried to use the ++leader command "
                                  f"but shouldn't be doing that.")
            await ctx.send("This command can only be performed by leaders/council on the RCS Discord server. "
                           "Keep up these antics and I'll tell zig on you!")

    @commands.command(name="leader_dm", aliases=["dmleaders", "dm_leaders"], hidden=True)
    @commands.has_role(settings['rcsRoles']['council'])
    async def leader_dm(self, ctx, *, message):
        """Sends message as a DM to all RCS leaders"""
        if not message:
            await ctx.send("I'm not going to send a blank message you goofball!")
            return
        msg = await ctx.send("One moment while I track down these leaders...")
        conn = pymssql.connect(settings['database']['server'],
                               settings['database']['username'],
                               settings['database']['password'],
                               settings['database']['database'])
        cursor = conn.cursor(as_dict=True)
        cursor.execute("SELECT DISTINCT discordTag FROM rcs_data")
        rows = cursor.fetchall()
        conn.close()
        counter = 0
        for row in rows:
            try:
                member = ctx.guild.get_member(int(row['discordTag']))
                await member.send(message)
                counter += 1
            except:
                self.bot.logger.exception("DM send attempt")
        member = ctx.guild.get_member(251150854571163648)
        await member.send(f"**The following has been sent to all RCS leaders by {ctx.author}**\n\n{message}")
        await msg.edit(f"Message sent to {counter} RCS leaders.")

    @commands.command(name="find", aliases=["search"], hidden=True)
    async def find(self, ctx, *, arg: str = "help"):
        """Command to to find a search string in Discord user names"""
        # TODO Figure out the None response on some names
        # TODO add regex or option to only search for string in clan name
        if is_authorized(ctx.author.roles) or 440585276042248192 in ctx.author.roles:
            if arg == "help":
                embed = discord.Embed(title="rcs-bot Help File", 
                                      description="Help for the find/search command", 
                                      color=color_pick(15, 250, 15))
                embed.add_field(name="Commands:", value="-----------")
                help_text = "Used to find Discord names with the specified string."
                embed.add_field(name="++find <search string>", value=help_text)
                embed.set_footer(icon_url="https://openclipart.org/image/300px/svg_to_png/122449/1298569779.png", 
                                 text="rcs-bot proudly maintained by TubaKid.")
                await ctx.send(embed=embed)
                return
            # if not help, code picks up here
            member_role = "296416358415990785"
            guild = str(settings['discord']['rcsGuildId'])

            headers = {"Accept": "application/json", "Authorization": "Bot " + settings['discord']['rcsbotToken']}
            # List first 1000 RCS Discord members
            url = f"https://discordapp.com/api/guilds/{guild}/members?limit=1000"
            r = requests.get(url, headers=headers)
            data1 = r.json()
            # List second 1000 RCS Discord members
            url += "&after=" + data1[999]['user']['id']
            r = requests.get(url, headers=headers)
            data2 = r.json()
            data = data1 + data2

            regex = r"{}".format(arg)
            members = []
            for item in data:
                discord_name, discord_flag = get_discord_name(item)
                if re.search(regex, discord_name, re.IGNORECASE) is not None:
                    report_name = f"""@{item['user']['username']}#{item['user']['discriminator']} - 
                        <@{item['user']['id']}>""" if discord_flag == 1 \
                        else f"@{item['nick']} - <@{item['user']['id']}>"
                    if member_role in item['roles']:
                        report_name += " (Members role)"
                    members.append(report_name)
            if len(members) == 0:
                await ctx.send("No users with that text in their name.")
                return
            content = f"**{arg} Users**\nDiscord users with {arg} in their name.\n\n**Discord names:**\n"
            content += "\n".join(members)
            await self.send_text(ctx.channel, content)
        else:
            print(f"{datetime.now()} - ERROR: {ctx.author} from {ctx.guild} tried to use the ++find command "
                  "but does not have the leader or council role.")
            await ctx.send(f"You have found the secret command!  Unfortunately, you are not an RCS "
                           "Leader/Council member.  Climb the ladder, then try again!")

    async def send_text(self, channel, text, block=None):
        """ Sends text to channel, splitting if necessary
        Discord has a 2000 character limit
        """
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


def get_discord_name(item):
    try:
        if "nick" in item and item['nick'] is not None:
            return item['nick'].lower(), 1
        else:
            return item['user']['username'].lower(), 0
    except:
        print(item)


def get_clan_name(clan_tag):
    if clan_tag.startswith("#"):
        clan_tag = clan_tag[1:]
    for clan in clans:
        if clan['clanTag'].lower() == clan_tag.lower():
            return clan['clanName']
    return "x"


def get_clan_tag(clan_name):
    for clan in clans:
        if clan['clanName'].lower() == clan_name.lower():
            return clan['clanTag']
    return "x"


def resolve_clan_tag(clan_input):
    tag_validator = re.compile("^#?[PYLQGRJCUV0289]+$")
    tag = correct_tag(clan_input)
    name = clan_input.strip()
    if tag_validator.match(tag):
        return tag, get_clan_name(tag)
    else:
        return get_clan_tag(name), name


def is_authorized(user_roles):
    for role in user_roles:
        if role.id in [settings['rcsRoles']['leaders'],
                       settings['rcsRoles']['rcsLeaders'],
                       settings['rcsRoles']['council'],
                       ]:
            return True
    return False


def is_council(user_roles):
    for role in user_roles:
        if role.id == settings['rcsRoles']['council']:
            return True
    return False


def is_chat_mod(user_roles):
    for role in user_roles:
        if role.id == settings['rcsRoles']['chatMods']:
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


mainConn = pymssql.connect(settings['database']['server'], 
                           settings['database']['username'], 
                           settings['database']['password'], 
                           settings['database']['database'])
mainCursor = mainConn.cursor(as_dict=True)
mainCursor.execute("SELECT clanName, clanTag FROM rcs_data ORDER BY clanName")
clans = mainCursor.fetchall()
mainConn.close()


def setup(bot):
    bot.add_cog(CouncilCog(bot))
