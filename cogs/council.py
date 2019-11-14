
import discord
import coc
import asyncio
import re

from discord.ext import commands
from cogs.utils.checks import is_council, is_mod_or_council, is_leader_or_mod_or_council
from cogs.utils.converters import ClanConverter
from cogs.utils.db import Sql
from cogs.utils import helper
from config import settings, color_pick
from datetime import datetime


class CouncilCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="form", aliases=["magic"], hidden=True)
    @is_council()
    async def magic_form(self, ctx):
        """Displays a link to the Council Magic Form

        **Permissions:**
        Council

        **Notes:**
        If the command is executed anywhere other than #council-chat or #council-bot-spam, the output will be
        redirected to #council-bot-spam."""
        link = "https://docs.google.com/forms/d/e/1FAIpQLScnSCYr2-qA7OHxrf-z0BZFjDr8aRvvHzIM6bIMTLVtlO16GA/viewform"
        if ctx.channel.id in (settings['rcs_channels']['council'], settings['rcs_channels']['council_spam']):
            await ctx.send(link)
        else:
            await ctx.send("I think I'll respond in the private council channel.")
            channel = self.bot.get_channel(settings['rcs_channels']['council_spam'])
            await channel.send(link)

    # @commands.command(name="userinfo", aliases=["ui"], hidden=True)
    # @is_mod_or_council()
    # async def user_info(self, ctx, user: discord.Member):
    #     """Command to retreive join date and other info for Discord user.
    #
    #     **Permissions:**
    #     Chat Mods
    #     Council"""
    #     today = datetime.now()
    #     create_date = user.created_at.strftime("%d %b %Y")
    #     create_delta = (today - user.created_at).days
    #     join_date = user.joined_at.strftime("%d %b %Y")
    #     join_delta = (today - user.joined_at).days
    #     conn = self.bot.pool
    #     sql = "SELECT MAX(last_message) FROM rcs_discord WHERE discord_id = $1"
    #     row = conn.fetchrow(sql, user.id)
    #     last_message = row[0]
    #     user_roles = []
    #     for role in user.roles:
    #         if role.name != "@everyone":
    #             user_roles.append(role.name)
    #     embed = discord.Embed(title=user.display_name,
    #                           description=f"{user.name}#{user.discriminator}",
    #                           color=color_pick(255, 165, 0))
    #     embed.set_thumbnail(url=user.avatar_url)
    #     embed.add_field(name="Joined RCS Server on", value=f"{join_date}\n({join_delta} days ago)", inline=True)
    #     embed.add_field(name="Discord Creation Date", value=f"{create_date}\n({create_delta} days ago)", inline=True)
    #     embed.add_field(name="Last Message", value=last_message, inline=False)
    #     embed.add_field(name="Roles", value=", ".join(user_roles), inline=False)
    #     embed.set_footer(text=f"User ID: {user.id}")
    #     await ctx.send(embed=embed)

    @commands.command(name="addClan", aliases=["clanAdd", "newClan", "add_clan", "new_clan"], hidden=True)
    @is_council()
    async def add_clan(self, ctx, *, clan_tag: str = "x"):
        """Interactive command to add a new verified clan to the RCS Database.

        **Permissions:**
        Council

        **Notes:**
        Make sure you have the following information before beginning:
        Clan Tag
        Short Names (possibilities for use in Discord nicknames)
        Social Media links
        Clan notes (how the clan wants to be described on the wiki)
        Classification
        Subreddit link (optional)
        Leader's Reddit Username
        Leader's Discord Tag
        """
        def check_author(m):
            return m.author == ctx.author

        def process_content(content):
            if content.lower() in ["stop", "cancel", "quit"]:
                self.bot.logger.info(f"Process stopped by user ({ctx.command}, {ctx.author})")
                return content, 1
            if content.lower() == "none":
                return "", 0
            return content, 0

        short_name = soc_media = desc = classification = subreddit = leader_reddit = discord_tag = ""

        continue_flag = 1
        # Get clan tag
        if clan_tag == "x":
            try:
                await ctx.send("Please enter the tag of the new clan.")
                response = await ctx.bot.wait_for("message", check=check_author, timeout=30)
                clan_name, cancel_flag = process_content(response.content)
            except asyncio.TimeoutError:
                return await ctx.send("Seriously, I'm not going to wait that long. Start over!")
        # Confirm clan name
        try:
            clan = ctx.coc.get_clan(clan_tag)
        except coc.NotFound:
            raise commands.BadArgument(f"{clan_tag} is not a valid clan tag.")
        confirm = await ctx.prompt(f"I'd like to confirm that you want to create a new clan with "
                                   f"the name **{clan.name}**.")
        if not confirm:
            return await ctx.send("Clan creation cancelled by user.")
        # Get leader's in game name
        leader = clan.get_member(role="leader")
        # create short name
        try:
            await ctx.send("Please create a short name for this clan. This will be what danger-bot "
                           "uses to search Discord names. Please/use/slashes/to/include/more/than/one.")
            response = await ctx.bot.wait_for("message", check=check_author, timeout=30)
            short_name, cancel_flag = process_content(response.content)
            if cancel_flag == 1:
                return await ctx.send("Creating of new clan cancelled by user.")
        except asyncio.TimeoutError:
            await ctx.send("OK slow poke. Here's what I'm going to do. I'm going to create this clan "
                           "with the stuff I know, but you'll have to add the rest later!\n**Missing "
                           "info:**\nShort name\nSocial Media\nDescription\nClassification\nSubreddit\n"
                           "Leader's Reddit Username\nLeader's Discord Tag")
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
                await ctx.send(f"I'm stopping here.  {clan.name} has been added to the database, but you'll "
                               "need to add the rest at a later time.\n**Missing info:**\nSocial Media\n"
                               "Description\nClassification\nSubreddit\nLeader's Reddit Username\n"
                               "Leader's Discord Tag")
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
                await ctx.send(f"Time's up {ctx.author}. {clan.name} has been added to the database, but "
                               "you'll need to add the rest at a later time.\n**Missing info:**\n"
                               "Description\nClassification\nSubreddit\nLeader's Reddit Username\n"
                               "Leader's Discord Tag")
                continue_flag = 0
        # Get Classification
        if continue_flag == 1:
            prompt = await ctx.prompt(f"Please select the appropriate classification for {clan.name}.\n"
                                      f":one: - General\n"
                                      f":two: - Social\n"
                                      f":three: - Competitive\n"
                                      f":four: - War Farming",
                                      additional_options=4)
            if prompt == 1:
                classification = "gen"
            elif prompt == 2:
                classification = "social"
            elif prompt == 3:
                classification = "comp"
            elif prompt == 4:
                classification = "warFarm"
            else:
                await ctx.send(f"Can't keep up?  Sorry about that. I've added {clan.name} to the database. "
                               f"You'll need to go back later and add the following.\n**Missing info:**\n"
                               f"Classification\nSubreddit\nLeader's Reddit username\nLeader's Discord Tag")
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
                await ctx.send(f"Ugh! You've run out of time! I'll add {clan.name} to the database, but you'll "
                               "need to add missing stuff later!\n**Missing info:**\nLeader's Reddit Username\n"
                               "Leader's Discord Tag")
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
                await ctx.send(f"I can see we aren't making any progress here. {clan.name} is in the database "
                               "now, but you'll need to do more!\n**Missing info:**\nLeader's reddit username\n"
                               "Leader's Discord Tag")
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
                await ctx.send(f"You were so close! I'll add {clan.name} to the database now, but you'll "
                               "need to add the **Discord Tag** later.")
        # Log and inform user
        if discord_tag != "":
            print(f"{datetime.now()} - All data collected for {ctx.command}. Adding {clan.name} to database now.")
            await ctx.send(f"All data collected!  Adding to database now.\n**Clan name:** {clan.name}\n"
                           f"**Clan Tag:** #{clan_tag}\n**Leader:** {leader}\n**Short Name:** {short_name}\n"
                           f"**Social Media:** {soc_media}\n**Notes:** {desc}\n**Classification:** "
                           f"{classification}\n**Subreddit:** {subreddit}\n**Leader's Reddit name:** "
                           f"{leader_reddit}\n**Leader's Discord Tag:** {discord_tag}")
        # Add info to database
        with Sql(as_dict=True) as cursor:
            cursor.execute(f"INSERT INTO rcs_data (clanName, clanTag, clanLeader, shortName, socMedia, "
                           f"notes, classification, subReddit, leaderReddit, discordTag)"
                           f"VALUES ('{clan.name}', '{clan_tag}', '{leader}', '{short_name}', '{soc_media}', "
                           f"'{desc}', '{classification}', '{subreddit}', '{leader_reddit}', {discord_tag})")
        await ctx.send(f"{clan.name} has been added.  Please allow 3 hours for the clan to appear in wiki.")
        # force wiki and cache update
        await ctx.send(f"**Next Steps:**\nSend mod invite for META\nUpdate clan directory in META\n"
                       f"Announce the new clan in Discord")
        # Add leader roles
        guild = ctx.bot.get_guild(settings['discord']['rcsguild_id'])
        user = guild.get_member(int(discord_tag))
        if not user:
            await ctx.send(f"{discord_tag} does not seem to be a valid tag for {leader} or they are not on "
                           "the RCS server yet. You will need to add roles manually.")
        else:
            role_obj = guild.get_role(int(settings['rcs_roles']['leaders']))
            await user.add_roles(role_obj, reason=f"Leaders role added by ++addClan command of rcs-bot.")
            role_obj = guild.get_role(int(settings['rcs_roles']['rcs_leaders']))
            await user.add_roles(role_obj, reason=f"RCS Leaders role added by ++addClan command of rcs-bot.")
            role_obj = guild.get_role(int(settings['rcs_roles']['recruiters']))
            await user.add_roles(role_obj, reason=f"Clan Recruiters role added by ++addClan command of rcs-bot.")
        # Send DM to new leader with helpful links
        member = ctx.guild.get_member(int(discord_tag))
        await member.send(f"Congratulations on becoming a verified RCS clan!  We have added {clan.name} "
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
        self.bot.logger.info(f"{ctx.command} issued by {ctx.author} for {clan.name} (Channel: {ctx.channel})")

    @commands.command(name="removeClan", aliases=["clanRemove", "remove_clan"], hidden=True)
    @is_council()
    async def remove_clan(self, ctx, *, clan: ClanConverter = None):
        """Interactive command to remove a verified clan from the RCS database.

        **Permissions:**
        Council"""
        if not clan:
            return await ctx.send("You have not provided a valid clan name or clan tag.")
        with Sql(as_dict=True) as cursor:
            cursor.execute(f"SELECT clanName, clanTag FROM rcs_data WHERE feeder = '{clan.name}'")
            fetch = cursor.fetchone()
            if fetch is not None:
                self.bot.logger.info(f"Removing family clan for {clan.name}. Issued by {ctx.author} in {ctx.channel}")
                cursor.execute(f"DELETE FROM rcs_data WHERE clanTag = '{fetch['clanTag']}'")
                await ctx.send(f"{fetch['clanName']} (feeder for {clan.name}) has been removed.")
            self.bot.logger.info(f"Removing {clan.name}. Issued by {ctx.author} in {ctx.channel}")
            cursor.execute(f"SELECT leaderReddit, discordTag FROM rcs_data WHERE clanTag = '{clan.tag}'")
            fetch = cursor.fetchone()
            cursor.execute(f"DELETE FROM rcs_data WHERE clanTag = '{clan.tag}'")
        # remove leader's roles
        guild = ctx.bot.get_guild(settings['discord']['rcsguild_id'])
        user = guild.get_member(int(fetch['discordTag']))
        if user:
            role_obj = guild.get_role(int(settings['rcs_roles']['leaders']))
            await user.remove_roles(role_obj,
                                    reason=f"Leaders role removed by ++removeClan command of rcs-bot.")
            role_obj = guild.get_role(int(settings['rcs_roles']['rcs_leaders']))
            await user.remove_roles(role_obj,
                                    reason=f"RCS Leaders role removed by ++removeClan command of rcs-bot.")
            role_obj = guild.get_role(int(settings['rcs_roles']['recruiters']))
            await user.remove_roles(role_obj,
                                    reason=f"Clan Recruiters role removed by ++removeClan command of rcs-bot.")
        await ctx.send(f"{clan.name} has been removed from the database.  The change will appear on the wiki "
                       "in the next 3 hours.")
        # TODO update the wiki
        helper.rcs_names_tags.clear_cache()
        helper.get_clan.clear_cache()
        await ctx.send("<@251150854571163648> Please recycle the bot so we aren't embarassed with old data!")
        await ctx.send(f"Please don't forget to remove {fetch['leaderReddit'][22:]} as a mod from META and "
                       f"update the META clan directory.  I've removed the Leaders, RCS Leaders, and Clan "
                       f"Recruiters role from <@{fetch['discordTag']}>. If they have any other roles, "
                       f"you will need to remove them manually.")

    @commands.command(name="in_war", aliases=["inwar"], hidden=True)
    @is_mod_or_council()
    async def in_war(self, ctx):
        """Displays the current war status of RCS clans (prep and in war only)
        This command takes a minute to gather all its information

        **Permissions:**
        Chat Mods
        Council"""
        async with ctx.typing():
            msg = await ctx.send("Loading...")
            with Sql(as_dict=True) as cursor:
                cursor.execute("SELECT '#' + clanTag AS tag, isWarLogPublic FROM rcs_data "
                               "WHERE classification <> 'feeder' ORDER BY clanName")
                clans = cursor.fetchall()
            tags = [clan['tag'] for clan in clans if clan['isWarLogPublic'] == 1]
            in_prep = ""
            in_war = ""
            in_cwl = ""
            async for war in self.bot.coc.get_current_wars(tags):
                try:
                    if war.state == "preparation":
                        in_prep += (f"{war.clan.name} ({war.clan.tag}) has "
                                    f"{war.start_time.seconds_until // 3600:.0f} hours until war.\n")
                    if war.state == "inWar":
                        if war.type == "cwl":
                            in_cwl += (f"{war.clan.name} ({war.clan.tag}) has "
                                       f"{war.end_time.seconds_until // 3600:.0f} hours left in war.\n")
                        else:
                            in_war += (f"{war.clan.name} ({war.clan.tag}) has "
                                       f"{war.end_time.seconds_until // 3600:.0f} hours left in war.\n")
                except Exception as e:
                    self.bot.logger.exception("get war state")
            await msg.delete()
            await ctx.send_embed(ctx.channel,
                                 "RCS Clan War Status",
                                 "This includes CWL wars.",
                                 in_prep,
                                 discord.Color.dark_gold())
            if in_war != "":
                await ctx.send_embed(ctx.channel,
                                     "RCS Clan War Status",
                                     "This does not include CWL wars.",
                                     in_war,
                                     discord.Color.dark_red())
            if in_cwl != "":
                await ctx.send_embed(ctx.channel,
                                     "RCS CWL War Status",
                                     "These are CWL wars.",
                                     in_cwl,
                                     discord.Color.dark_red())

    @commands.command(name="leader", hidden=True)
    @is_mod_or_council()
    async def leader(self, ctx, *, clan: ClanConverter = None):
        """Command to find the leader for the selected clan.

        **Permissions:**
        Chat Mods
        Council

        **Example:**
        ++leader Reddit Tau
        """
        if not clan:
            return await ctx.send("You have not provided a valid clan name or clan tag.")
        with Sql(as_dict=True) as cursor:
            cursor.execute(f"SELECT discordTag, clanBadge FROM rcs_data WHERE clanName = '{clan.name}'")
            fetch = cursor.fetchone()
            discord_id = fetch['discordTag']
            badge_url = fetch['clanBadge']
            cursor.execute(f"SELECT altName FROM rcs_alts WHERE clanTag = '{clan.tag[1:]}' ORDER BY altName")
            fetch = cursor.fetchall()
        if fetch:
            alt_names = ""
            for row in fetch:
                alt_names += f"{row['altName']}\n"
        else:
            alt_names = "No alts for this leader"
        embed = discord.Embed(title=f"Leader Information for {clan.name}",
                              color=color_pick(240, 240, 240))
        embed.set_thumbnail(url=badge_url)
        embed.add_field(name="Leader name:",
                        value=f"<@{discord_id}>",
                        inline=False)
        embed.add_field(name="Alt accounts:",
                        value=alt_names,
                        inline=False)
        await ctx.send(embed=embed)

    @commands.group(invoke_without_command=True, hidden=True)
    @is_leader_or_mod_or_council()
    async def alts(self, ctx):
        """[Group] Command to handle alt accounts of RCS leaders

        **Permissions:**
        Chat Mods
        Council
        Leaders
        """
        if ctx.invoked_subcommand is None:
            return await ctx.show_help(ctx.command)

    @alts.command(name="list")
    async def alts_list(self, ctx, *, clan: ClanConverter = None):
        """List alts for the specified clan.

        **Example:**
        ++alts list Clan Name
        ++alts list #CLANTAG
        ++alts list ShortName (you can omit the word Reddit)
        """
        if clan:
            await ctx.invoke(self.leader, clan=clan)
        else:
            await ctx.send(f"Terribly sorry, but I can't find that clan!")

    @alts.command(name="add")
    async def alts_add(self, ctx, clan: ClanConverter = None, *, new_alt: str = None):
        """Adds new leader alt for the specified clan
        Quotes are required for clans with a space in their name
        Feel free to use the short name (omit the word Reddit) if that is easier

        **Example:**
        ++alts add "Clan Name" alt name
        ++alts add #CLANTAG alt name
        ++alts add ShortName alt name
        """
        if not new_alt:
            return await ctx.send("Please provide the name of the new alt account.")
        with Sql() as cursor:
            sql = (f"INSERT INTO rcs_alts "
                   f"SELECT {clan[0].tag[1:]}, {new_alt} "
                   f"EXCEPT "
                   f"SELECT clanTag, altName FROM rcs_alts WHERE clanTag = {clan[0].tag[1:]} AND altName = {new_alt}")
            cursor.execute(sql)
        await ctx.send(f"{new_alt} has been added as an alt account for the leader of {clan[0].name}.")

    @alts.command(name="remove", aliases=["delete", "del", "rem"])
    async def alts_remove(self, ctx, clan: ClanConverter = None, *, alt: str = None):
        """Remove Leader alt for the specified clan
        Quotes are required for clans with a space in their name
        Feel free to use the short name (omit the word Reddit_ if that is easier

        **Exmaple:**
        ++alts remove "Clan Name" alt name
        ++alts delete #CLANTAG alt name
        ++alts del ShortName alt name
        ++alts del "Clan Name" all *(this removes all alts for this clan)*
        """
        if not alt:
            return await ctx.send("Please provide the name of the alt account to be removed or specify all.")
        with Sql() as cursor:
            if alt == "all":
                sql = f"DELETE FROM rcs_alts WHERE clanTag = {clan[0].tag[1:]}"
                cursor.execute(sql)
                await ctx.send(f"All alt accounts for {clan[0].name} have been removed.")
            else:
                sql = f"DELETE FROM rcs_alts WHERE clanTag = {clan[0].tag[1:]} AND altName = {alt}"
                cursor.execute(sql)
                await ctx.send(f"{alt} has been removed as an alt for the leader of {clan[0].name}.")

    @commands.group(invoke_without_subcommand=True, hidden=True)
    @is_council()
    async def dm(self, ctx):
        """[Group] Commands to send DMs to various roles in the RCS Discord Server

        **Permissions:**
        Council"""
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @dm.command(name="leaders", aliases=["leader", "rcsleaders"])
    async def dm_leaders(self, ctx, *, message):
        """Sends message as a DM to all RCS leaders

        **Example:**
        ++dm leaders Here is a free DM to all leaders

        **Notes:**
        It takes a minute to complete this command.
        When the command is complete, it will let
        you know how many people received a DM.
        """
        if not message:
            return await ctx.send("I'm not going to send a blank message you goofball!")
        msg = await ctx.send("One moment while I track down these leaders...")
        with Sql(as_dict=True) as cursor:
            cursor.execute("SELECT DISTINCT discordTag FROM rcs_data")
            rows = cursor.fetchall()
        counter = 0
        for row in rows:
            try:
                member = ctx.guild.get_member(int(row['discordTag']))
                await member.send(message)
                counter += 1
            except:
                self.bot.logger.exception("DM send attempt")
        # Send same message to TubaKid so he knows what's going on
        member = ctx.guild.get_member(251150854571163648)
        await member.send(f"**The following has been sent to all RCS leaders by {ctx.author}**\n\n{message}")
        await msg.edit(f"Message sent to {counter} RCS leaders.")

    @dm.command(name="ayedj", aliases=["dj", "djs"])
    async def dm_djs(self, ctx, *, message):
        """Sends message as a DM to all RCS DJs

        **Example:**
        ++dm djs Here is a free DM to all music DJs

        **Notes:**
        It takes a minute to complete this command.
        When the command is complete, it will let
        you know how many people received a DM.
        """
        if not message:
            return await ctx.send("I don't think the DJs will be impressed with a blank message!")
        msg = await ctx.send("One moment while I spin the turntables...")
        dj_role = ctx.guild.get_role(settings['rcs_roles']['djs'])
        counter = 0
        for member in dj_role.members:
            try:
                await member.send(message)
                counter += 1
            except:
                self.bot.logger.exception("DM send attempt")
        # Send same message to TubaKid so he knows what's going on
        member = ctx.guild.get_member(251150854571163648)
        await member.send(f"**The following has been sent to all RCS DJs by {ctx.author}**\n\n{message}")
        await msg.edit(f"Message sent to {counter} RCS DJs.")

    @commands.command(name="find", aliases=["search"], hidden=True)
    @is_mod_or_council()
    async def find(self, ctx, *, arg: str = "help"):
        """Returns any Discord member of the RCS server with the search sting in the name

        **Permissions:**
        Chat Mods
        Council

        **Example:**
        ++find speed
        """
        guild = ctx.bot.get_guild(settings['discord']['rcsguild_id'])
        member_role = guild.get_role(settings['rcs_roles']['members'])
        members = guild.members
        regex = r"{}".format(arg)
        report = []
        for member in members:
            if isinstance(member, str):
                print(member)
            discord_name = f"{member.name}|{member.display_name}"
            if re.search(regex, discord_name, re.IGNORECASE) is not None:
                report_name = f"{member.display_name} - {member.mention}"
                if member_role in member.roles:
                    report_name += " (Members role)"
                report.append(report_name)
        if len(report) == 0:
            await ctx.send("No users with that text in their name.")
            return
        content = f"**{arg} Users**\nDiscord users with {arg} in their name.\n\n**Discord names:**\n"
        content += "\n".join(report)
        await ctx.send_text(ctx.channel, content)


def setup(bot):
    bot.add_cog(CouncilCog(bot))
