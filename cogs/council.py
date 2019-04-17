import requests, pymssql, re, discord, asyncio
from discord.ext import commands
from config import settings, color_pick
from datetime import datetime

class CouncilCog:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="presence", hidden=True)
    async def presence(self, ctx, *, msg: str = "x"):
        """Command to modify bot presence"""
        if isCouncil(ctx.author.roles):
            if msg.lower() == "default":
                activity = discord.Game("Clash of Clans")
            else:
                activity = discord.Activity(type=discord.ActivityType.watching, name=msg)
            await self.bot.change_presence(status=discord.Status.online, activity=activity)
            print(f"{datetime.now()} - {ctx.author} changed the bot presence to {msg}")
        else:
            await ctx.send("Yeah, I'm going to guess you're not on council and you don't have any business trying "
                           "to use this command!")

    @commands.command(name="userInfo", aliases=["ui"], hidden=True)
    @commands.guild_only()
    async def userInfo(self, ctx, discordId):
        """Command to retreive join date for Discord user."""
        if isRcsGuild(ctx.guild) and (isCouncil(ctx.author.roles) or isChatMod(ctx.author.roles)):
            isUser, user = isDiscordUser(ctx.guild, int(discordId))
            if isUser == False:
                if discordId.startswith("<"):
                    discordId = discordId[2:-1]
                    if discordId.startswith("!"):
                        discordId = discordId[1:]
                else:
                    await ctx.send(":x: That's not a good user.  It should look something like <@!123456789>.")
                    return
                isUser, user = isDiscordUser(ctx.guild, int(discordId))
            if isUser == False:
                await ctx.send(f":x: User specified **{discordId}** is not a member of this discord server.")
                return
            today = datetime.now()
            joinDate = user.joined_at.strftime('%d %b %Y')
            joinDelta = (today - user.joined_at).days
            userRoles = []
            for role in user.roles:
                if role.name != "@everyone":
                    userRoles.append(role.name)
            embed = discord.Embed(title = user.display_name, color = color_pick(255,165,0))
            embed.set_thumbnail(url = user.avatar_url)
            embed.add_field(name = "Joined RCS Server on", value = f"{joinDate}\n({joinDelta} days ago)", inline = True)
            embed.add_field(name = "Message Count", value = "unknown", inline = True)
            embed.add_field(name = "Roles", value = ", ".join(userRoles), inline = False)
            embed.set_footer(text = f"User ID: {user.id}")
            await ctx.send(embed=embed)
        else:
            await ctx.send("Yeah, I'm going to guess you're not on council and you don't have any business trying "
                           "to use this command!")

    @commands.command(name="addClan", aliases=["clanAdd", "newClan"], hidden=True)
    async def addClan(self, ctx, *, clanName: str = "x"):
        """Command to add a new verified clan to the RCS Database."""
        if isRcsGuild(ctx.guild) and isCouncil(ctx.author.roles):
            def checkAuthor(m):
                return m.author == ctx.author
            def checkReaction(reaction, user):
                return user == ctx.message.author and str(reaction.emoji) in [
                    "<:upvote:295295304859910144>",
                    "<:downvote:295295520187088906>",
                    "🇬","🇸","🇨","🇫"]
            def processContent(content):
                if content.lower() in ["stop","cancel","quit"]:
                    botLog(ctx.command,"Process stopped by user",ctx.author,ctx.channel,1)
                    return(content, 1)
                if content.lower() == "none":
                    return("", 0)
                return(content, 0)
            continueFlag = 1
            # Get clan name
            if clanName == "x":
                try:
                    await ctx.send("Please enter the name of the new clan.")
                    response = await ctx.bot.wait_for("message", check=checkAuthor, timeout=10)
                    clanName, cancelFlag = processContent(response.content)
                except asyncio.TimeoutError:
                    return await ctx.send("Seriously, I'm not going to wait that long. Start over!")
            # Confirm clan name
            try:
                sentMsg = await ctx.send(f"I'd like to confirm that you want to create a new clan with the name **{clanName}**. Please upvote is this is correct. Downvote to cancel.")
                await sentMsg.add_reaction("upvote:295295304859910144")
                await sentMsg.add_reaction("downvote:295295520187088906")
                reaction, user = await ctx.bot.wait_for("reaction_add", check=checkReaction, timeout = 10)
            except asyncio.TimeoutError:
                return await ctx.send("You either don't know how to use emoji or you're just slow.  Try again later.")
            if str(reaction.emoji) == "<:downvote:295295520187088906>":
                await sentMsg.clear_reactions()
                await sentMsg.add_reaction("downvote:295295520187088906")
                return await ctx.send("Clan creation cancelled by user.")
            await sentMsg.clear_reactions()
            await sentMsg.add_reaction("upvote:295295304859910144")
            # Get clan tag
            try:
                await ctx.send(f"What is the clan tag for {clanName}?")
                response = await ctx.bot.wait_for("message", check=checkAuthor, timeout=15)
                if response.content.startswith("#"):
                    clanTag, cancelFlag = processContent(response.content[1:])
                else:
                    clanTag, cancelFlag = processContent(response.content)
                if cancelFlag == 1:
                    return await ctx.send("Creating of new clan cancelled by user.")
            except asyncio.TimeoutError:
                return await ctx.send("I don't have all day and I can't add a clan without a tag. Back to one!")
            # Get leader's in game name
            try:
                await ctx.send("Who leads this mighty clan?")
                response = await ctx.bot.wait_for("message", check=checkAuthor, timeout=15)
                leader, cancelFlag = processContent(response.content)
                if cancelFlag == 1:
                    return await ctx.send("Creating of new clan cancelled by user.")
            except asyncio.TimeoutError:
                return await ctx.send("Might I recommend some typing courses for you?  I'm going to rest now. Try again later.")
            # create short name
            try:
                await ctx.send("Please create a short name for this clan. This will be what danger-bot uses to search Discord names. Please/use/slashes/to/include/more/than/one.")
                response = await ctx.bot.wait_for("message", check=checkAuthor, timeout=15)
                shortName, cancelFlag = processContent(response.content)
                if cancelFlag == 1:
                    return await ctx.send("Creating of new clan cancelled by user.")
            except asyncio.TimeoutError:
                await ctx.send("OK slow poke. Here's what I'm going to do. I'm going to create this clan with the stuff I know, but you'll have to add the rest later!\n**Missing info:**\nShort name\nSocial Media\nDescription\nClassification\nSubreddit\nLeader's Reddit Username\nLeader's Discord Tag")
                shortName = socMedia = desc = classificaion = subReddit = leaderReddit = discordTag = ""
                continueFlag = 0
            # Get social media links
            if continueFlag == 1:
                try:
                    await ctx.send("Please include social media links as follows:\n[Twitter](https://twitter.com/RedditZulu)\nType `none` if there aren't any links to add at this time.")
                    response = await ctx.bot.wait_for("message", check=checkAuthor, timeout=45)
                    socMedia, cancelFlag = processContent(response.content)
                    if cancelFlag == 1:
                        return await ctx.send("Creating of new clan cancelled by user.")
                except asyncio.TimeoutError:
                    await ctx.send(f"I'm stopping here.  {clanName} has been added to the database, but you'll need to add the rest at a later time.\n**Missing info:**\nSocial Media\nDescription\nClassification\nSubreddit\nLeader's Reddit Username\nLeader's Discord Tag")
                    socMedia = desc = classificaion = subReddit = leaderReddit = discordTag = ""
                    continueFlag = 0
            # Get Description
            if continueFlag == 1:
                try:
                    await ctx.send("Now I need to know a little bit about the clan.  What notes would you like stored for this clan?")
                    response = await ctx.bot.wait_for("message", check=checkAuthor, timeout=45)
                    desc, cancelFlag = processContent(response.content)
                    if cancelFlag == 1:
                        return await ctx.send("Creating of new clan cancelled by user.")
                except asyncio.TimeoutError:
                    await ctx.send(f"Time's up {ctx.author}. {clanName} has been added to the database, but you'll need to add the rest at a later time.\n**Missing info:**\nDescription\nClassification\nSubreddit\nLeader's Reddit Username\nLeader's Discord Tag")
                    desc = classificaion = subReddit = leaderReddit = discordTag = ""
                    continueFlag = 0
            # Get Classification
            if continueFlag == 1:
                try:
                    sentMsg = await ctx.send(f"Please select the appropriate classification for {clanName}.\n:regional_indicator_g: - General\n:regional_indicator_s: - Social\n:regional_indicator_c: - Competitive\n:regional_indicator_f: - War Farming")
                    await sentMsg.add_reaction("🇬")
                    await sentMsg.add_reaction("🇸")
                    await sentMsg.add_reaction("🇨")
                    await sentMsg.add_reaction("🇫")
                    reaction, user = await ctx.bot.wait_for("reaction_add", check=checkReaction, timeout = 10)
                    await sentMsg.clear_reactions()
                    if str(reaction.emoji) == "🇬":
                        classification = "gen"
                        await sentMsg.add_reaction("🇬")
                    if str(reaction.emoji) == "🇸":
                        classification = "social"
                        await sentMsg.add_reaction("🇸")
                    if str(reaction.emoji) == "🇨":
                        classification = "comp"
                        await sentMsg.add_reaction("🇨")
                    if str(reaction.emoji) == "🇫":
                        classification = "warFarm"
                        await sentMsg.add_reaction("🇫")
                except asyncio.TimeoutError:
                    await ctx.send("Can't keep up?  Sorry about that. I've added {clanName} to the database. You'll need to go back later and add the following.\n**Missing info:**\nClassification\nSubreddit\nLeader's Reddit username\nLeader's Discord Tag")
                    classificaion = subReddit = leaderReddit = discordTag = ""
                    continueFlag = 0
            # Get subreddit
            if continueFlag == 1:
                try:
                    await ctx.send("Please provide the subreddit for this clan (if they are cool enough to have one). (no need to include the /r/)\nIf they are lame and don't have a subreddit, type `none`.")
                    response = await ctx.bot.wait_for("message", check=checkAuthor, timeout=20)
                    subReddit, cancelFlag = processContent(response.content)
                    if cancelFlag == 1:
                        return await ctx.send("Creating of new clan cancelled by user.")
                    if subReddit != "":
                        subReddit = "https://www.reddit.com/r/" + subReddit
                except asyncio.TimeoutError:
                    await ctx.send(f"Ugh! You've run out of time! I'll add {clanName} to the database, but you'll need to add missing stuff later!\n**Missing info:**\nLeader's Reddit Username\nLeader's Discord Tag")
                    subReddit = leaderReddit = discordTag = ""
                    continueFlag = 0
            # Get Reddit Username of leader
            if continueFlag == 1:
                try:
                    await ctx.send(f"Can you please tell me what the reddit username is for {leader}? (No need to include the /u/)")
                    response = await ctx.bot.wait_for("message", check=checkAuthor, timeout=20)
                    leaderReddit, cancelFlag = processContent(response.content)
                    if cancelFlag == 1:
                        return await ctx.send("Creating of new clan cancelled by user.")
                    if leaderReddit != "":
                        leaderReddit = f"https://www.reddit.com/user/{leaderReddit}"
                except asyncio.TimeoutError:
                    await ctx.send(f"I can see we aren't making any progress here. {clanName} is in the database now, but you'll need to do more!\n**Missing info:**\nLeader's reddit username\nLeader's Discord Tag")
                    leaderReddit = discordTag = ""
                    continueFlag = 0
            # Get Leader's Discord Tag
            if continueFlag == 1:
                try:
                    await ctx.send(f"Saving the best for last!  What's this guy/gal's Discord Tag?  You know, the long string of numbers that mean nothing to you, but mean everything to me!")
                    response = await ctx.bot.wait_for("message", check=checkAuthor, timeout=15)
                    discordTag, cancelFlag = processContent(response.content)
                    if cancelFlag == 1:
                        return await ctx.send("Creating of new clan cancelled by user.")
                except asyncio.TimeoutError:
                    await ctx.send(f"You were so close! I'll add {clanName} to the database now, but you'll need to add the **Discord Tag** later.")
                    discordTag = ""
            # Log and inform user
            if discordTag != "":
                print(f"{datetime.now()} - All data collected for {ctx.command}. Adding {clanName} to database now.")
                await ctx.send(f"All data collected!  Adding to database now.\n**Clan name:** {clanName}\n**Clan Tag:** "
                               "#{clanTag}\n**Leader:** {leader}\n**Short Name:** {shortName}\n**Social Media:** {socMedia}\n**Notes:** {desc}"
                               "\n**Classification:** {classification}\n**Subreddit:** {subReddit}\n**Leader's Reddit name:** {leaderReddit}"
                               "\n**Leader's Discord Tag:** {discordTag}")
            # Add info to database
            conn = pymssql.connect(settings['database']['server'], settings['database']['username'], settings['database']['password'], settings['database']['database'], autocommit=True)
            cursor = conn.cursor(as_dict=True)
            cursor.execute(f"""INSERT INTO rcs_data (clanName, clanTag, clanLeader, shortName, socMedia, notes, classification, subReddit, leaderReddit, discordTag)
        VALUES ('{clanName}', '{clanTag}', '{leader}', '{shortName}', '{socMedia}', '{desc}', '{classification}', '{subReddit}', '{leaderReddit}', {discordTag})""")
            await ctx.send(f"{clanName} has been added.  Please allow 3 hours for the clan to appear in wiki.")
            await ctx.send(f"**Next Steps:**\nSend mod invite for META\nUpdate clan directory in META\nAnnounce the new clan in Discord")
            # Add leader roles
            guild = ctx.bot.get_guild(settings['discord']['rcsGuildId'])
            isUser, user = isDiscordUser(guild, int(discordTag))
            if isUser == False:
                await ctx.send(f"{discordTag} does not seem to be a valid tag for {leader} or they are not on the RCS server yet. You will need to add roles manually.")
            else:
                roleObj = guild.get_role(int(settings['rcsRoles']['leaders']))
                await user.add_roles(roleObj, reason = f"Leaders role added by ++addClan command of rcs-bot.")
                roleObj = guild.get_role(int(settings['rcsRoles']['rcsLeaders']))
                await user.add_roles(roleObj, reason = f"RCS Leaders role added by ++addClan command of rcs-bot.")
                roleObj = guild.get_role(int(settings['rcsRoles']['recruiters']))
                await user.add_roles(roleObj, reason = f"Clan Recruiters role added by ++addClan command of rcs-bot.")
            # Send DM to new leader with helpful links
            member = ctx.guild.get_member(int(discordTag))
            await member.send(f"Congratulations on becoming a verified RCS clan!  We have added {clanName} to our database and it will appear on the RCS wiki page within the next 3 hours.  You should now have "
                              "the proper Discord roles and be able to see <#298620147424296970> and a few other new channels."
                              "\n\n<#308300486719700992> is for the reporting of questionable players. It's not necessarily a ban list, "
                              "but a heads up. If someone with a note in that channel joins your clan, you'll receive an alert in <#448918837904146455> letting you."
                              "\n\nThe channels for clan recruitment and events are available to "
                              "you, but if you'd like to add someone else from your clan to help with those items, just let one of the Global Chat Mods know (you can @ tag them)."
                              "\n\nFinally, here is a link to some helpful information. "
                              "It's a lot up front, but this will be a great resource going forward. https://docs.google.com/document/d/16gfd-BgkGk1bdRmyxIt92BA-tl1NcYk7tuR3HpFUJXg/edit?usp=sharing \n\nWelcome to the RCS!")
            botLog(ctx.command,clanName,ctx.author,ctx.channel)
        else:
            print(f"{datetime.now()} - ERROR: {ctx.author} from {ctx.guild} tried to use the ++{ctx.command} command but shouldn't be doing that.")
            await ctx.send("This command can only be performed by Council members on the RCS Discord server. Keep up these antics and I'll tell zig on you!")

    #  @commands.command(name="testdm")
    #  async def testdm(self, ctx, *, arg):
    #    member = ctx.guild.get_member(int(arg))
    #    print(member)
    #    await member.send("This is a test DM from rcs-bot. Please let TubaKid know if you have received it.")

    @commands.command(name="removeClan", aliases=["clanRemove"], hidden=True)
    @commands.guild_only()
    async def removeClan(self, ctx, *, arg: str = "x"):
        """Command to remove a verified clan from the RCS database."""
        if isRcsGuild(ctx.guild) and isCouncil(ctx.author.roles):
            clanTag, clanName = resolveClanTag(arg)
            if clanTag == "x":
                botLog(ctx.command, arg, ctx.author, ctx.guild, 1)
                await ctx.send("You have not provided a valid clan name or clan tag.")
                return
            clanTag, clanName = resolveClanTag(arg)
            if clanTag == "x":
                botLog(ctx.command, arg, ctx.author, ctx.guild, 1)
                await ctx.send("You have not provided a valid clan name or clan tag.")
                return
            conn = pymssql.connect(settings['database']['server'], settings['database']['username'], settings['database']['password'], settings['database']['database'], autocommit=True)
            cursor = conn.cursor(as_dict=True)
            cursor.execute(f"SELECT clanName, clanTag FROM rcs_data WHERE feeder = '{clanName}'")
            fetched = cursor.fetchone()
            if fetched is not None:
                botLog(ctx.command, f"Removing feeder for {clanName}", ctx.author, ctx.channel)
                cursor.execute(f"DELETE FROM rcs_data WHERE clanTag = '{fetched['clanTag']}'")
                await ctx.send(f"{fetched['clanName']} (feeder for {clanName}) has been removed.")
            botLog(ctx.command, f"Removing {clanName}", ctx.author, ctx.channel)
            cursor.execute(f"SELECT leaderReddit, discordTag FROM rcs_data WHERE clanTag = '{clanTag}'")
            fetched = cursor.fetchone()
            cursor.execute(f"DELETE FROM rcs_data WHERE clanTag = '{clanTag}'")
            conn.close()
            # remove leader's roles
            guild = ctx.bot.get_guild(settings['discord']['rcsGuildId'])
            isUser, user = isDiscordUser(guild, int(fetched['discordTag']))
            if isUser == True:
                roleObj = guild.get_role(int(settings['rcsRoles']['leaders']))
                await user.remove_roles(roleObj, reason=f"Leaders role removed by ++removeClan command of rcs-bot.")
                roleObj = guild.get_role(int(settings['rcsRoles']['rcsLeaders']))
                await user.remove_roles(roleObj, reason=f"RCS Leaders role removed by ++removeClan command of rcs-bot.")
                roleObj = guild.get_role(int(settings['rcsRoles']['recruiters']))
                await user.remove_roles(roleObj, reason=f"Clan Recruiters role removed by ++removeClan command of rcs-bot.")
            await ctx.send(f"{clanName} has been removed from the database.  The change will appear on the wiki in the next 3 hours.")
            await ctx.send("<@251150854571163648> Please recycle the bot so we aren't embarassed with old data!")
            await ctx.send(f"Please don't forget to remove {fetched['leaderReddit'][22:]} as a mod from META and update the META clan directory.  I've removed the Leaders, RCS Leaders, and Clan Recruiters role from <@{fetched['discordTag']}>. If they have any other roles, you will need to remove them manually.")
        else:
            print(f"{datetime.now()} - ERROR: {ctx.author} from {ctx.guild} tried to use the ++{ctx.command} command but shouldn't be doing that.")
            await ctx.send("This command can only be performed by Council members on the RCS Discord server. Keep up these antics and I'll tell zig on you!")

    @commands.command(name="leader", hidden=True)
    @commands.guild_only()
    async def leader(self, ctx, *, arg: str = "x"):
        """Command to find the leader for the selected clan.
        Usage: ++leader Reddit Argon"""
        if isRcsGuild(ctx.guild) and isAuthorized(ctx.author.roles):
            clanTag, clanName = resolveClanTag(arg)
            if clanTag == "x":
                botLog(ctx.command, arg, ctx.author, ctx.guild, 1)
                await ctx.send("You have not provided a valid clan name or clan tag.")
                return
            conn = pymssql.connect(settings['database']['server'], settings['database']['username'], settings['database']['password'], settings['database']['database'])
            cursor = conn.cursor(as_dict=True)
            cursor.execute(f"SELECT discordTag FROM rcs_data WHERE clanName = '{clanName}'")
            fetched = cursor.fetchone()
            conn.close()
            if fetched is not None:
                botLog(ctx.command, clanName, ctx.author, ctx.guild)
                await ctx.send(f"The leader of {clanName} is <@{fetched['discordTag']}>")
        else:
            print(f"{datetime.now()} - ERROR: {ctx.author} from {ctx.guild} tried to use the ++leader command but shouldn't be doing that.")
            await ctx.send(f"This command can only be performed by leaders/council on the RCS Discord server. Keep up these antics and I'll tell zig on you!")

    @commands.command(name="find", aliases=["search"], hidden=True)
    async def find(self, ctx, *, arg: str = "help"):
        """Command to to find a search string in Discord user names"""
        # TODO Figure out the None response on some names
        # TODO add regex or option to only search for string in clan name
        if isAuthorized(ctx.author.roles):
            if arg == "help":
                embed = discord.Embed(title="rcs-bot Help File", description="Help for the find/search command", color=color_pick(15,250,15))
                embed.add_field(name="Commands:", value="-----------")
                helpText = "Used to find Discord names with the specified string."
                embed.add_field(name="++find <search string>", value = helpText)
                embed.set_footer(icon_url="https://openclipart.org/image/300px/svg_to_png/122449/1298569779.png", text="rcs-bot proudly maintained by TubaKid.")
                botLog("help", "find", ctx.author, ctx.guild)
                await ctx.send(embed=embed)
                return
            # if not help, code picks up here
            guestRole = "301438407576387584"
            memberRole = "296416358415990785"
            discordServer = str(settings['discord']['rcsGuildId'])

            headers = {"Accept": "application/json", "Authorization": "Bot " + settings['discord']['rcsbotToken']}
            # List first 1000 RCS Discord members
            url = f"https://discordapp.com/api/guilds/{discordServer}/members?limit=1000"
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
                discordName, discordFlag = getDiscordName(item)
                if re.search(regex, discordName, re.IGNORECASE) is not None:
                    reportName = f"@{item['user']['username']}#{item['user']['discriminator']} - <@{item['user']['id']}>" if discordFlag == 1 else f"@{item['nick']} - <@{item['user']['id']}>"
                    if memberRole in item['roles']:
                        reportName += " (Members role)"
                    members.append(reportName)
            if len(members) == 0:
                botLog(ctx.command, arg, ctx.author, ctx.channel)
                await ctx.send("No users with that text in their name.")
                return
            content = f"**{arg} Users**\nDiscord users with {arg} in their name.\n\n**Discord names:**\n"
            content += "\n".join(members)
            botLog(ctx.command, arg, ctx.author, ctx.guild)
            await self.send_text(ctx.channel, content)
        else:
            print(f"{datetime.now()} - ERROR: {ctx.author} from {ctx.guild} tried to use the ++find command but does not have the leader or council role.")
            await ctx.send(f"You have found the secret command!  Unfortunately, you are not an RCS Leader/Council member.  Climb the ladder, then try again!")

    async def send_text(self, channel, text):
        """ Sends text to channel, splitting if necessary """
        if len(text) < 2000:
            await channel.send(text)
        else:
            coll = ""
            for line in text.splitlines(keepends=True):
                if len(coll) + len(line) > 2000:
                    # if collecting is going to be too long, send  what you have so far
                    await channel.send(coll)
                    coll = ""
                coll += line
            await channel.send(coll)

def getDiscordName(item):
    try:
        if "nick" in item and item['nick'] is not None:
            return item['nick'].lower(), 1
        else:
            return item['user']['username'].lower(), 0
    except:
        print(item)

def getClanName(clanTag):
    clanName = ""
    for clan in clans:
        if clan['clanTag'].lower() == clanTag.lower():
            return clan['clanName']
    return "x"

def getClanTag(clanName):
    clanTag = ""
    for clan in clans:
        if clan['clanName'].lower() == clanName.lower():
            return clan['clanTag']
    return "x"

def resolveClanTag(input):
    if input.startswith("#"):
        clanTag = input[1:]
        clanName = getClanName(clanTag)
    else:
        clanTag = getClanTag(input)
        clanName = input
        if clanTag == "x":
            clanName = getClanName(input)
            clanTag = input
            if clanName == "x":
                return "x", "x"
    return clanTag, clanName


def isRcsGuild(guild):
    if str(guild) == "Reddit Clan System":
        return True
    return False


def isAuthorized(userRoles):
    for role in userRoles:
        if role.name in ["Leaders", "Council", "RCS Leaders"]:
            return True
    return False


def isCouncil(userRoles):
    for role in userRoles:
        if role.name == "Council":
            return True
    return False


def isChatMod(userRoles):
    for role in userRoles:
        if role.name == "Global Chat Mods" or "Chat Mods":
            return True
    return False


def isDiscordUser(guild, discordId):
    try:
        user = guild.get_member(discordId)
        if user is None:
            return False, None
        else:
            return True, user
    except:
        return False, None


def botLog(command, request, author, guild, errFlag=0):
    msg = str(datetime.now())[:16] + " - "
    if errFlag == 0:
        msg += f"Printing {command} for {request}. Requested by {author} for {guild}."
    else:
        msg += f"ERROR: User provided an incorrect argument for {command}. Argument provided: {request}. Requested by {author} for {guild}."
    print(msg)


mainConn = pymssql.connect(settings['database']['server'], settings['database']['username'], settings['database']['password'], settings['database']['database'])
mainCursor = mainConn.cursor(as_dict=True)
mainCursor.execute("SELECT clanName, clanTag FROM rcs_data ORDER BY clanName")
clans = mainCursor.fetchall()
mainConn.close()


def setup(bot):
    bot.add_cog(CouncilCog(bot))
