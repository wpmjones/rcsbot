import coc
import discord
import asyncio
import re
import requests

from discord.ext import commands
from cogs.utils.checks import is_council, is_mod_or_council, is_leader_or_mod_or_council
from cogs.utils.constants import class_names, class_values
from cogs.utils.converters import ClanConverter, PlayerConverter
from cogs.utils.db import Sql, get_discord_id
from cogs.utils import helper
from config import settings, color_pick
from datetime import datetime


def to_time(seconds):
    d, r = divmod(seconds, 86400)
    h, r = divmod(r, 3600)
    m, s = divmod(r, 60)
    if d > 0:
        return f"{d:.0f}d {h:.0f}h"
    elif h > 0:
        return f"{h:.0f}h {m:.0f}m"
    else:
        return f"{m:.0f}m"


class CouncilCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="council", hidden=True)
    @is_council()
    async def council(self, ctx):
        """Help menu for RCS Council"""
        response = "**RCS Council Help Menu**\n\n"
        response += ("**++magic**\n(Permission: Council only)\n"
                     "Responds with a link to the Council Magic Form\nUsed for:\n"
                     "Leader change\nAdding clans\nRemoving clans\nChanging clan type\nUpdate clan notes\n"
                     "Add a discussion channel\n\n")
        response += ("**++ui  [Discord User] or ++userinfo [Discord User]**\n(Permission: Council or Mods)\n"
                     "Retrieves user information for the specified user\n\n")
        response += ("**++recommend [Discord User] [Recommendation]**\n(Permission: Council only)\n"
                     "Recommends the specified user as a new council member, sending recommendation to #leader-chat "
                     "(no tag).  The post in #leader-chat will include a link to the Google Form so that leaders "
                     "can provide feedback.\n\n")
        response += ("**++inwar**\n(Permission: Council or Mods)\n"
                     "Responds with a list of which RCS clans are currently in prep or war.\n\n")
        response += ("**++ban**\n(Permission: Council or Mods)\n"
                     "Responds with a list of users who have been banned from the RCS Discord Server, who banned "
                     "them and why.\n\n")
        response += ("**++kick**\n(Permission: Council or Mods)\n"
                     "Responds with a list of users who have been kciked from the RCS Discord Server, who kicked "
                     "them and why.\n\n")
        response += ("**++clan notes [clan name or tag]**\n(Permission: Council only)\n"
                     "This command will respond with the current clan notes from the wiki. You then respond with the "
                     "new clan notes and it will update the database.\n\n")
        response += ("**++clan discord [clan name or tag] [new discord invite]**\n(Permission: Council only)\n"
                     "This command will update the database with the new discord invite and, if the current clan "
                     "notes are properly formatted (Discord: [Invite](link)), it will update the notes with the "
                     "new server as well.\n\n")
        response += ("**++leader [clan name or tag]**\n(Permission: Council or Mods)\n"
                     "Responds with information on the clan leader and any alts they may have.\n\n")
        response += ("**++alts list [clan name or tag]**\n(Permission: Council or Mods)\n"
                     "Responds with information on the clan leader and any alts they may have.\n\n")
        response += ("**++alts add [clan name or tag] [new alt name]**\n(Permission: Council or Mods)\n"
                     "Adds the specified alt to the specified clan.\n\n")
        response += ("**++alts remove [clan name or tag] [new alt name]**\n(Permission: Council or Mods)\n"
                     "Removes the specified alt to the specified clan.\n\n")
        response += ("**++warn list [Discord User]**\n(Permission: Council or Mods)\n"
                     "Shows current warnings for the specified user.\n\n")
        response += ("**++warn add [Discord User] [reason]**\n(Permission: Council or Mods)\n"
                     "Adds a warning for the specified user.\n\n")
        response += ("**++warn remove [Warning ID]]**\n(Permission: Council or Mods)\n"
                     "Removes the specified warning.  Warning IDs can be obtained using ++warn list.\n\n")
        response += ("**++dm leaders [message]**\n(Permission: Council only)\n"
                     "Sends the message to all RCS leaders via DM.  If successful, it will respond with a message "
                     "letting you know how many leaders the message was send to.\n\n")
        response += ("**++find [search string]**\n(Permission: Council, Mods, Leaders)\n"
                     "This command will search all users on the RCS Discord Server and, if the search string is in "
                     "their name, respond with their name and whether or not they have the Member role.\n\n")
        response += ("**++tasks all**\n(Permission: Council only)\n"
                     "Sends all active tasks to your DM.\n\n")
        response += ("**++tasks [category]**\n(Permission: Council only)\n"
                     "Responds with active tasks in the specified category (suggestions, council, verification, other, "
                     "action).\n\n")
        response += ("**++tasks add [Discord User] [task]**\n(Permission: Council only)\n"
                     "Creates a new action item for the specified user.\n\n")
        response += ("**++tasks assign [Discord User] [Task ID]**\n(Permission: Council only)\n"
                     "Assigns the specified task to the Discord user provided. Task IDs can be obtained using the "
                     "++tasks [category] command.  Only Suggestions, Other, and Action Items can be assigned.\n\n")
        response += ("**++tasks change [Task ID] [new task]**\n(Permission: Council only)\n"
                     "Change an existing action item.  Only action items can be modified.\n\n")
        response += ("**++tasks update [Task ID] [Optional: new status]**\n(Permission: Council only)\n"
                     "This can only be used on Verification tasks. If you do not provide a new status, it will "
                     "prompt you for the new status.\n\n")
        response += ("**++tasks done [Task ID]**\n(Permission: Council only)\n"
                     "Marks the specified task complete.  Works for all categories.\n\n")
        response += ("**For more information on any of these commands, simply use the ++help feature. For example:** "
                     "`++help clan notes`")
        await ctx.send_text(ctx.channel, response)

    @commands.command(name="cl", hidden=True)
    @commands.is_owner()
    async def create_discord_links(self, ctx):
        url = "http://api.amazingspinach.com/links"
        conn = self.bot.pool
        sql = "SELECT player_tag, discord_id FROM rcs_discord_links"
        fetch = await conn.fetch(sql)
        for row in fetch:
            payload = {"playerTag": row['player_tag'], "discordId": row['discord_id']}
            r = requests.post(url, json=payload)
            if r.status_code == 500:
                continue
            if r.status_code == 400 and "exists" in r.text:
                # player is already linked
                continue
            if r.status_code != 200:
                await ctx.send(f"ERROR: {r.status_code}\n{r.text}")
                break
        await ctx.send("Done")

    @commands.command(name="gl", hidden=True)
    @commands.is_owner()
    async def get_discord_link(self, ctx, player: PlayerConverter = None):
        discord_id = get_discord_id(player.tag)
        if discord_id:
            await ctx.send(f"{player.name} ({player.tag}) is linked to <@{discord_id}> ({discord_id})")
        else:
            await ctx.send(f"No Discord link exists for {player.name} ({player.tag}).")

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

    @commands.command(name="userinfo", aliases=["ui"], hidden=True)
    @is_mod_or_council()
    async def user_info(self, ctx, user: discord.Member):
        """Command to retreive join date and other info for Discord user.

        **Permissions:**
        Chat Mods
        Council"""
        today = datetime.now()
        create_date = user.created_at.strftime("%d %b %Y")
        create_delta = (today - user.created_at).days
        join_date = user.joined_at.strftime("%d %b %Y")
        join_delta = (today - user.joined_at).days
        conn = self.bot.pool
        sql = "SELECT last_message FROM rcs_messages WHERE discord_id = $1"
        row = await conn.fetchrow(sql, user.id)
        last_message = row[0]
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
        embed.add_field(name="Last Message", value=last_message, inline=False)
        embed.add_field(name="Roles", value=", ".join(user_roles), inline=False)
        embed.set_footer(text=f"User ID: {user.id}")
        await ctx.send(embed=embed)

    @commands.command(name="recommend", hidden=True)
    @is_council()
    async def recommend(self, ctx, user: discord.Member, *, desc):
        """Command to recommend new Council member.

        **Permissions:**
        Council

        **Example:**
        ++recommend 178989365953822720 Long description of why we
        feel said individual would make a really good Council member.
        Feel free to write a paragraph, but don't get crazy!
        """
        payload = desc
        url = "https://script.google.com/macros/s/AKfycby6fVhNtzz9hjFT-oAKKF3yqE5gJnwqJPefM50mmOXTymKA5sY/exec"
        async with ctx.session.post(url, data=payload) as r:
            if r.status != 200:
                return await ctx.send("Form did not update successfully.  Call the tuba!")
        form_url = (f"https://docs.google.com/forms/d/e/"
                    f"1FAIpQLSd0JDTqnwFYwg9X45wBwLHXCQcOSjiLJTe5iQ5g5mrUIYbXRQ/viewform?usp=pp_url&entry.14972849="
                    f"{user.display_name}")
        channel = self.bot.get_channel(settings['rcs_channels']['leader_chat'])
        await channel.send(f"The RCS Council supports the addition of {user.display_name} to as a member of Council."
                           f"\n\nPlease complete the following form and provide any necessary feedback.  Thank "
                           f"you!\n\n{form_url}")
        await ctx.send(f"Form udpated and sent to {channel.mention}.")

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
        with Sql() as cursor:
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
        conn = self.bot.pool
        with Sql() as cursor:
            # Check to see if the specified clan has a feeder/family clan
            cursor.execute(f"SELECT clanName, clanTag FROM rcs_data WHERE feeder = '{clan.name}'")
            fetch = cursor.fetchone()
            if fetch is not None:
                self.bot.logger.info(f"Removing family clan for {clan.name}. Issued by {ctx.author} in {ctx.channel}")
                cursor.execute(f"DELETE FROM rcs_data WHERE clanTag = ?", fetch.clanTag)
                await conn.execute("DELETE FROM rcs_clans WHERE clan_tag = $1", fetch.clanTag)
                await ctx.send(f"{fetch.clanName} (feeder for {clan.name}) has been removed.")
            self.bot.logger.info(f"Removing {clan.name}. Issued by {ctx.author} in {ctx.channel}")
            sql = "SELECT leader_reddit, discord_tag FROM rcs_clans WHERE clan_tag = $1"
            fetch = await conn.fetchrow(sql, clan.tag[1:])
            cursor.execute("DELETE FROM rcs_data WHERE clanTag = ?", clan.tag[1:])
            await conn.execute("DELETE FROM rcs_clans WHERE clan_tag = $1", clan.tag[1:])
        # remove leader's roles
        guild = ctx.bot.get_guild(settings['discord']['rcsguild_id'])
        user = guild.get_member(int(fetch['discord_tag']))
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
        # TODO update the wiki immediately
        helper.rcs_tags.clear_cache()
        helper.rcs_names_tags.clear_cache()
        helper.get_clan.clear_cache()
        await ctx.send(f"Please don't forget to remove {fetch['leader_reddit'][22:]} as a mod from META and "
                       f"update the META clan directory.  I've removed the Leaders, RCS Leaders, and Clan "
                       f"Recruiters role from <@{fetch['discord_tag']}>. If they have any other roles, "
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
            tags = helper.rcs_tags(prefix=True)
            in_prep = ""
            in_war = ""
            in_cwl = ""
            async for war in self.bot.coc.get_current_wars(tags):
                try:
                    if not war.is_cwl:
                        if war.state == "preparation":
                            in_prep += (f"{war.clan.name} ({war.clan.tag}) has "
                                        f"{to_time(war.start_time.seconds_until)} until war.\n")
                        if war.state == "inWar":
                            in_war += (f"{war.clan.name} ({war.clan.tag}) has "
                                       f"{to_time(war.end_time.seconds_until)} left in war.\n")
                    if war.is_cwl and war.state == "inWar":
                        in_cwl += (f"{war.clan.name} ({war.clan.tag}) has "
                                   f"{to_time(war.end_time.seconds_until)} left in war.\n")
                except coc.PrivateWarLog:
                    pass
                except Exception as e:
                    self.bot.logger.exception("get war state")
            await msg.delete()
            if in_prep != "":
                await ctx.send_embed(ctx.channel,
                                     "RCS Clan War Status",
                                     "This does not include CWL wars.",
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
                                     discord.Color.dark_blue())
            if all(x == "" for x in [in_prep, in_war, in_cwl]):
                await ctx.send("No clans are in war right now.")

    @commands.command(name="ban", hidden=True)
    @is_mod_or_council()
    async def ban_list(self, ctx):
        """Responds with a list of all members who have been banned from the RCS Discord Server"""
        guild = self.bot.get_guild(settings['discord']['rcsguild_id'])
        content = ""
        async for entry in guild.audit_logs(action=discord.AuditLogAction.ban):
            reason = entry.reason
            if not reason:
                reason = "No reason given"
            content += (f"**{entry.target}** was banned by {entry.user.display_name} on "
                        f"**{entry.created_at.strftime('%Y-%m-%d')}** "
                        f"for:\n{reason}\n\n")
        embed = discord.Embed(title="Members banned from RCS Discord",
                              description=content,
                              color=discord.Color.dark_red())
        if ctx.channel.id in (settings['rcs_channels']['council'],
                              settings['rcs_channels']['council_spam'],
                              settings['rcs_channels']['mods']):
            await ctx.send(embed=embed)
        else:
            channel = self.bot.get_channel(settings['rcs_channels']['mods'])
            await channel.send(embed=embed)
            await ctx.message.delete()
            await ctx.author.send(f"It's really not wise to use the {ctx.command.name} list command in the "
                                  f"{ctx.channel.name} channel.  I have responded in the "
                                  f"<#{settings['rcs_channels']['mods']}> channel instead.")

    @commands.command(name="kick", hidden=True)
    @is_mod_or_council()
    async def kick_list(self, ctx):
        """Responds with a list of all members who have been banned from the RCS Discord Server"""
        guild = self.bot.get_guild(settings['discord']['rcsguild_id'])
        content = ""
        async for entry in guild.audit_logs(action=discord.AuditLogAction.kick):
            reason = entry.reason
            if not reason:
                reason = "No reason given"
            content += (f"**{entry.target}** was kicked by {entry.user.display_name} on "
                        f"**{entry.created_at.strftime('%Y-%m-%d')}** "
                        f"for:\n{reason}\n\n")
        embed = discord.Embed(title="Members kicked from RCS Discord",
                              description=content,
                              color=discord.Color.dark_red())
        if ctx.channel.id in (settings['rcs_channels']['council'],
                              settings['rcs_channels']['council_spam'],
                              settings['rcs_channels']['mods']):
            await ctx.send(embed=embed)
        else:
            channel = self.bot.get_channel(settings['rcs_channels']['mods'])
            await channel.send(embed=embed)
            await ctx.message.delete()
            await ctx.author.send(f"It's really not wise to use the {ctx.command.name} list command in the "
                                  f"{ctx.channel.name} channel.  I have responded in the "
                                  f"<#{settings['rcs_channels']['mods']}> channel instead.")

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
        conn = self.bot.pool
        sql = "SELECT discord_tag, badge_url FROM rcs_clans WHERE clan_tag = $1"
        fetch = await conn.fetchrow(sql, clan.tag[1:])
        discord_id = fetch['discord_tag']
        badge_url = fetch['badge_url']
        sql = "SELECT alt_tag FROM rcs_alts WHERE clan_tag = $1"
        fetch = await conn.fetch(sql, clan.tag[1:])
        if fetch:
            alt_names = ""
            for row in fetch:
                player = await self.bot.coc.get_player(row['alt_tag'])
                alt_names += f"{player.name}\n"
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

    @commands.group(name="clan", invoke_without_command=True, hidden=True)
    @is_council()
    async def clan(self, ctx):
        """[Group] Commands to update clan information for the wiki

        **Permissions:**
        Council
        """

        if ctx.invoked_subcommand is None:
            return await ctx.show_help(ctx.command)

    @clan.command(name="notes")
    @is_council()
    async def clan_notes(self, ctx, clan: ClanConverter = None):
        """Update the notes for the specified clan. This command will respond
        with the current notes, then you will respond with the new notes.
        Responding with `cancel` or just ignoring the bot for 60 seconds
        will stop the command.

        **Example:**
        ++clan notes Tau
        ++clan notes "Reddit Eclipse"
        """
        if not clan:
            return await ctx.send("Please specify the clan name in your command.")

        def check_author(m):
            return m.author == ctx.author and m.channel == ctx.channel

        conn = self.bot.pool
        sql = "SELECT notes FROM rcs_clans WHERE clan_tag = $1"
        fetch = await conn.fetch(sql, clan.tag[1:])
        if fetch is not None:
            old_notes = fetch['notes']
        else:
            return await ctx.send("There was a problem retrieving the notes for this clan. Someone ought to "
                                  "ping that old TubaKid guy and see if he can fix it.")
        try:
            await ctx.send(f"**Current clan notes:**\n{old_notes}\n\nPlease respond with the new clan notes. "
                           f"Remembering that all discord info should appear in the following format:\n"
                           f"**Discord: [Invite](https://discord.gg/invitelink)**")
            response = await ctx.bot.wait_for("message", check=check_author, timeout=60)
        except asyncio.TimeoutError:
            return await ctx.send("Your request has timed out. No changes have been made.")
        if response.content.lower() in ("cancel", "stop", "quit"):
            return await ctx.send(f"Notes update cancelled by {ctx.author.display_name}")
        new_notes = response.content
        with Sql() as cursor:
            sql = "UPDATE rcs_data SET notes = ? WHERE clanTag = ?"
            cursor.execute(sql, (new_notes, clan.tag[1:]))
        psql = "UPDATE rcs_clans SET notes = $1 WHERE clan_tag = $2"
        await conn.execute(sql, new_notes, clan.tag[1:])
        await ctx.send(f"The notes for {clan.name} ({clan.tag}) have been updated in the database. Please allow 3 "
                       f"hours to see the changes reflected in the wiki.")

    @clan.command(name="discord")
    @is_council()
    async def clan_discord(self, ctx, clan: ClanConverter = None, new_discord: str = None):
        """Update the discord server link for the specified clan. This will replace the server link for the ++discord
        command and if there is an existing discord link in the notes section for this clan, it will update that as
        well.

        **Examples:**
        ++clan discord "Reddit Psi" https://discord.gg/newlink
        ++clan discord zen https://discord.gg/newlink
        """
        if not clan:
            return await ctx.send("Please specify the clan name in your command.")
        if not new_discord:
            return await ctx.send("Please provide the new invite link for this Discord server.")
        flag = 0
        conn = self.bot.pool
        sql = "SELECT notes FROM rcs_clans WHERE clan_tag = $1"
        old_notes = await conn.fetchval(sql, clan.tag[1:])
        if old_notes is not None:
            if "Discord: [Invite]" in old_notes:
                start = old_notes.find("Discord: [Invite]")
                end = old_notes.find(")", start) + 1
                old_discord = old_notes[start:end]
                new_notes = old_notes.replace(old_discord, f"Discord: [Invite]({new_discord})")
                with Sql() as cursor:
                    sql = "UPDATE rcs_data SET notes = ? WHERE clanTag = ?"
                    cursor.execute(sql, (new_notes, clan.tag[1:]))
                sql = "UPDATE rcs_clans SET notes = $1 WHERE clan_tag = $2"
                await conn.execute(sql, new_notes, clan.tag[1:])
                flag += 1
        with Sql() as cursor:
            sql = "UPDATE rcs_data SET discordServer = ? WHERE clanTag = ?"
            cursor.execute(sql, (new_discord, clan.tag[1:]))
        sql = "UPDATE rcs_clans SET discord_server = $1 WHERE clan_tag = $2"
        await conn.execute(sql, new_discord, clan.tag[1:])
        flag += 1
        if flag == 1:
            response = (f"The Discord server has been updated for {clan.name}. Please allow up to 3 hours for "
                        f"the change to appear on the wiki.")
        else:
            response = (f"Both the Discord server and the notes section have been updated for {clan.name}. "
                        f"Please allow up to 3 hours for the change to appear on the wiki.")
        await ctx.send(response)

    @clan.command(name="class", aliases=["classify", "classification"])
    @is_council()
    async def clan_class(self, ctx, *, clan: ClanConverter = None):
        """Change the classification for the specified clan.  It will provide options for you.

        **Example:**
        ++clan class Eclipse
        """
        if not clan:
            return await ctx.send("Please specify the clan name in your command.")
        prompt = await ctx.prompt("Please select the new classification:\n"
                                  ":one: Competitive\n"
                                  ":two: Social\n"
                                  ":three: General\n"
                                  ":four: War Farming",
                                  additional_options=4)
        new_class = class_values[prompt]
        with Sql() as cursor:
            sql = "UPDATE rcs_data SET classification = ? WHERE clanTag = ?"
            cursor.execute(sql, (new_class, clan.tag[1:]))
        sql = "UPDATE rcs_clans SET classification = $1 WHERE clan_tag = $2"
        await self.bot.pool.execute(sql, new_class, clan.tag[1:])
        await ctx.send(f"The classification for {clan} is now set to {class_names[prompt]}. Please allow up to "
                       f"3 hours for the changes to appear on the wiki.")

    @commands.group(invoke_without_command=True, hidden=True)
    @is_leader_or_mod_or_council()
    async def alts(self, ctx, *, arg):
        """[Group] Command to handle alt accounts of RCS leaders

        **Permissions:**
        Chat Mods
        Council
        Leaders
        """
        if ctx.invoked_subcommand is not None:
            return
        if arg:
            clan = await ClanConverter().convert(ctx, arg)
            await ctx.invoke(self.leader, clan=clan)

    @alts.command(name="list")
    async def alts_list(self, ctx, *, clan: ClanConverter = None):
        """List alts for the specified clan.

        **Example:**
        ++alts list "Clan Name"
        ++alts list #CLANTAG
        ++alts list ShortName (you can omit the word Reddit)
        """
        if clan:
            await ctx.invoke(self.leader, clan=clan)
        else:
            await ctx.send(f"Terribly sorry, but I can't find that clan!")

    @alts.command(name="add")
    async def alts_add(self, ctx, clan: ClanConverter = None, *, player: PlayerConverter = None):
        """Adds new leader alt for the specified clan
        Quotes are required for clans or players with a space in their name
        Feel free to use the short name (omit the word Reddit) if that is easier
        For best accuracy, using tags is teh best practice

        **Example:**
        ++alts add "Clan Name" alt name
        ++alts add #CVCJR89 #L2URRGV02    (This is the best approach to ensure proper selection.)
        ++alts add ShortName alt name
        """
        if not clan:
            return await ctx.send("Please provide a valid RCS clan.")
        if not player:
            return await ctx.send("Please provide the tag or name of the new alt account.")
        sql = "INSERT INTO rcs_alts (clan_tag, alt_tag) VALUES ($1, $2) "
        await self.bot.pool.execute(sql, clan.tag[1:], player.tag[1:])
        await ctx.send(f"{player.name} ({player.tag}) has been added as an alt account for the leader of {clan.name}.")

    @alts.command(name="remove", aliases=["delete", "del", "rem"])
    async def alts_remove(self, ctx, clan: ClanConverter = None, *, player: PlayerConverter = None):
        """Remove Leader alt for the specified clan
        Quotes are required for clans with a space in their name
        Feel free to use the short name (omit the word Reddit_ if that is easier

        **Exmaple:**
        ++alts remove "Clan Name" alt name
        ++alts delete #CLANTAG alt name
        ++alts del ShortName alt name
        ++alts del "Clan Name" all *(this removes all alts for this clan)*
        """
        if not clan:
            return await ctx.send("Please provide a valid RCS clan.")
        if not player:
            return await ctx.send("Please provide the tag or name of the alt account to be removed or specify all.")
        conn = self.bot.pool
        if player == "all":
            sql = f"DELETE FROM rcs_alts WHERE clan_tag = $1"
            await conn.execute(sql, clan.tag[1:])
            await ctx.send(f"All alt accounts for {clan.name} have been removed.")
        else:
            sql = f"DELETE FROM rcs_alts WHERE clan_tag = $1 AND alt_tag = $2"
            await conn.execute(sql, clan.tag[1:], player.tag[1:])
            await ctx.send(f"{player} has been removed as an alt for the leader of {clan.name}.")

    @commands.group(invoke_without_subcommand=True, hidden=True)
    @is_mod_or_council()
    async def warn(self, ctx):
        """[Group] Commands to handle Discord warnings on the RCS Discord Server

        **Permissions:**
        Council
        Chat Mods
        """
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @warn.command(name="add")
    async def warn_add(self, ctx, member: discord.Member = None, *, reason=None):
        """Adds a warning for the specified user"""
        if not member:
            return await ctx.send("It would appear that you have not provided a valid Discord user. Please try again.")

        def check_author(m):
            return m.author == ctx.author

        if not reason:
            try:
                await ctx.send(f"Can you tell me why we are warning {member.display_name}?")
                response = await ctx.bot.wait_for("message", check=check_author, timeout=45)
                reason = response.content
            except asyncio.TimeoutError:
                return await ctx.send("I don't know why you want to warn this person. Please start over when you are "
                                      "willing to provide a little more information.")
        prompt = await ctx.prompt("Please specify the class for this infraction:\n"
                                  ":one: - Class A (isms, discrimination, links to naughty things, gore, etc. or "
                                  "hostile attack on another member)\n"
                                  ":two: - Class B (Joke or comment in poor taste or offensive to another member, "
                                  "TOS mention, aggresstion to another member)\n"
                                  ":three: - Class C (Spamming, disruptive messages, overuse of profanity or off color "
                                  "remarks/jokes)",
                                  additional_options=3)
        if prompt == 1:
            warning_class = "A"
        elif prompt == 2:
            warning_class = "B"
        elif prompt == 3:
            warning_class = "C"
        else:
            return await ctx.send("You must select a valid class for this infraction. Please try again.")

        conn = self.bot.pool
        sql = ("INSERT INTO rcs_warnings (warned_user_id, warning_class, warning, created_by, created_at) "
               "VALUES ($1, $2, $3, $4, $5)")
        # TODO List role (if guest or member) also include other warnings with dates
        await conn.execute(sql, member.id, warning_class, reason, ctx.author.id, ctx.message.created_at)
        await ctx.message.add_reaction('\u2705')

    @warn.command(name="remove")
    async def warn_remove(self, ctx, warn_id):
        """Removes the specified warning"""
        conn = self.bot.pool
        sql = ("SELECT warned_user_id, warning_class, warning, created_by, created_at FROM rcs_warnings "
               "WHERE warn_id = $1")
        row = await conn.fetchrow(sql, int(warn_id))
        if not row:
            return await ctx.send("There is no warning with that ID.")
        user = self.bot.get_user(row['warned_user_id'])
        warner = self.bot.get_user(row['created_by'])
        prompt = await ctx.prompt(f"Please confirm that this is the warning you would like to remove:\n"
                                  f"Warning ID: {warn_id}\n"
                                  f"Discord Member: {user.display_name}\n"
                                  f"Warning Class: Class {row['warning_class']}\n"
                                  f"Warning: {row['warning']}\n"
                                  f"Warned by: {warner}\n"
                                  f"Created on: {row['created_at'].strftime('%Y-%m-%d')}",
                                  timeout=30)
        if not prompt:
            return await ctx.send("Removal cancelled by user.")
        sql = "DELETE FROM rcs_warnings WHERE warn_id = $1"
        await conn.execute(sql, int(warn_id))
        await ctx.message.add_reaction('\u2705')

    @warn.command(name="list")
    async def warn_list(self, ctx, member: discord.Member = None):
        """Lists current warnings for the specified user"""
        if not member:
            return await ctx.send("It would appear that you have not provided a valid Discord user. Please try again.")
        conn = self.bot.pool
        sql = ("SELECT warn_id, warning_class, warning, created_by, created_at FROM rcs_warnings "
               "WHERE warned_user_id = $1")
        fetch = await conn.fetch(sql, member.id)
        content = ""
        for row in fetch:
            warner = self.bot.get_user(row['created_by'])
            content += (f"Warning ID: {row['warn_id']}\n"
                        f"Warning Class: Class {row['warning_class']}\n"
                        f"Warning: {row['warning']}\n"
                        f"Warned by: {warner}\n"
                        f"Created on: {row['created_at'].strftime('%Y-%m-%d')}\n"
                        f"\n")
        # Remove extra line at the end of content
        content = content[:-2]
        embed = discord.Embed(title=f"Warnings for {member.display_name}",
                              description=content,
                              color=discord.Color.dark_red())
        embed.set_footer(text="To remove a warning, use ++warn remove ##")
        if ctx.channel.id in (settings['rcs_channels']['council'],
                              settings['rcs_channels']['council_spam'],
                              settings['rcs_channels']['mods']):
            await ctx.send(embed=embed)
        else:
            channel = self.bot.get_channel(settings['rcs_channels']['mods'])
            await channel.send(embed=embed)
            await ctx.message.delete()
            await ctx.author.send(f"It's really not wise to use the {ctx.command.name} command in the "
                                  f"{ctx.channel.name} channel.  I have responded in the "
                                  f"<#{settings['rcs_channels']['mods']}> channel instead.")

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
        fetch = await self.bot.pool.fetch("SELECT DISTINCT discord_tag FROM rcs_clans")
        counter = 0
        for row in fetch:
            try:
                member = ctx.guild.get_member(int(row['discord_tag']))
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

    @commands.command(name="find", hidden=True)
    @is_leader_or_mod_or_council()
    async def find(self, ctx, *, arg: str = "help"):
        """Returns any Discord member of the RCS server with the search sting in the name

        **Permissions:**
        Chat Mods
        Council
        Leaders

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
