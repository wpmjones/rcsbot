import coc
import discord
import praw
import random
import re

from discord.ext import commands, tasks
from cogs.utils.constants import league_badges, log_types
from cogs.utils.db import Sql
from cogs.utils.helper import rcs_tags
from datetime import datetime, date, timedelta, time
from random import randint
from config import settings


class Background(commands.Cog):
    """Cog for background tasks. No real commands here."""
    def __init__(self, bot):
        self.bot = bot
        self.guild = None
        self.media_stats = None

        self.bot.coc.add_events(self.on_clan_war_win_streak_change,
                                self.on_clan_level_change,
                                self.on_clan_war_win_change,
                                )
        self.bot.coc.add_clan_update(rcs_tags(prefix=True))
        self.bot.coc.start_updates("clan")
        bot.loop.create_task(self.cog_init_ready())

    def cog_unload(self):
        self.bot.coc.remove_events(self.on_clan_war_win_streak_change,
                                   self.on_clan_level_change,
                                   self.on_clan_war_win_change,
                                   )

    async def cog_init_ready(self) -> None:
        """Sets the guild properly"""
        await self.bot.wait_until_ready()
        if not self.guild:
            self.guild = self.bot.get_guild(settings['discord']['rcsguild_id'])
            self.media_stats = self.guild.get_channel(settings['rcs_channels']['media_stats'])

    async def on_clan_war_win_streak_change(self, old_streak, new_streak, clan):
        """Watch for changes in war win streak and report to media/stats channel"""
        self.bot.logger.debug("Start war win streak change")
        if new_streak >= 5:
            msg = random.choice(["And the wins keep coming! ",
                                 "We've got another streak! ",
                                 "Impressive numbers! ",
                                 ])
            msg += f"**{clan.name}** has just won another one, bringing their streak to {new_streak}."
            await self.media_stats.send(msg)

    async def on_clan_level_change(self, old_level, new_level, clan):
        """Watch for changes in clan level and report to media/stats channel"""
        self.bot.logger.debug("Start clan level change")
        msg = f"Please help us in congratulating {clan.name} on reaching Level {new_level}."
        await self.media_stats.send(msg)

    async def on_clan_war_win_change(self, old_wins, new_wins, clan):
        """Watch for war wins divisible by 50 and report to media/stats channel"""
        if new_wins % 50 == 0:
            self.bot.logger.debug("Start war win div 50 change")
            prefix = random.choice(["Holy smokes, that is a lot of wins! ",
                                    "Check this out! ",
                                    "Milestone! ",
                                    "Hot diggity dog! ",
                                    "Want to see something cool? "
                                    "And the wins keep coming! "])
            suffix = random.choice(["You are awesome!",
                                    "Keep up the great work!",
                                    "You're making us all proud! ",
                                    "Go win a few more!"])
            msg = f"{prefix}{clan.name} just hit **{new_wins}** wins! {suffix}"
            await self.media_stats.send(msg)

    @tasks.loop(hours=24.0)
    async def clan_checks(self):
        """Check clans for member count, badge, etc."""
        if date.today().weekday() != 2:
            return
        sql = "SELECT MAX(log_date_ AS max_date FROM rcs_task_log WHERE log_type_id = $1"
        row = self.bot.pool.fetchrow(sql, log_types['loc_check'])
        if row and row['max_date'] > date.today() - timedelta(days=7):
            return
        council_chat = self.guild.get_channel(settings['rcs_channels']['council'])
        bot_dev = self.guild.get_channel(settings['rcs_channels']['bot_dev'])
        with Sql(as_dict=True) as cursor:
            cursor.execute("SELECT clanTag, classification FROM rcs_data")
            fetch = cursor.fetchall()
            cursor.execute("SELECT TOP 1 startTime, endTime FROM rcs_events "
                           "WHERE eventType = 11 AND startTime < GETDATE() ORDER BY startTime DESC")
            cwl_fetch = cursor.fetchone()
        if cwl_fetch['endTime'] > datetime.utcnow():
            cwl = True
        else:
            cwl = False
        for row in fetch:
            if row['classification'] != "family":
                clan_desc = "Verified Clan"
                clan_size = 35
            else:
                clan_desc = "Family Clan"
                clan_size = 25
            clan = await self.bot.coc.get_clan(f"#{row['clanTag']}")
            if clan.badge.medium not in league_badges:
                embed = discord.Embed(title=clan.name,
                                      description=f"Clan Level: {clan.level}",
                                      color=discord.Color.red())
                embed.set_thumbnail(url=clan.badge.medium)
                embed.set_footer(text="Incorrect Badge",
                                 icon_url=clan.badge.small)
                await council_chat.send(embed=embed)
                await bot_dev.send(f"{clan.name}\n{clan.badge.medium}\nJust in case...")
            if clan.member_count < clan_size and not cwl:
                embed = discord.Embed(title=clan.name,
                                      description=clan_desc,
                                      color=discord.Color.red())
                embed.add_field(name="Low Membership:", value=f"{clan.member_count} Members")
                embed.add_field(name="In-gameLink", value=f"[Click Here]({clan.share_link})")
                await council_chat.send(embed=embed)
            if clan.type != "inviteOnly":
                embed = discord.Embed(title=clan.name,
                                      description=f"Type: {clan.type}",
                                      color=discord.Color.red())
                embed.set_thumbnail(url=clan.badge.medium)
                embed.set_footer(text="Type not set to Invite Only",
                                 icon_url="https://coc.guide/static/imgs/gear_up.png")
                await council_chat.send(embed=embed)

    @tasks.loop(hours=3.0)
    async def rcs_list(self, ctx):
        """Update database with latest info then update the wiki"""
        now = datetime.utcnow()
        conn = self.bot.pool
        fetch = await conn.fetch("SELECT clan_tag, alt_tag FROM rcs_alts")
        leader_alts = {}
        for row in fetch:
            if row['clan_tag'] not in leader_alts.keys():
                leader_alts[row['clan_tag']] = []
            leader_alts[row['clan_tag']].append(row['alt_tag'])
        family_link = ("[See Below](https://www.reddit.com/r/RedditClanSystem/wiki/official_reddit_clan_system"
                       "#wiki_4._official_family_clans)")
        reddit = praw.Reddit(client_id=settings['reddit_speed']['client'],
                             client_secret=settings['reddit_speed']['secret'],
                             username=settings['reddit_speed']['username'],
                             password=settings['reddit_speed']['password'],
                             user_agent="raspi:com.mayodev.coc_redditclansystem_updater:v0.5 (by /u/TubaKid44)")
        subreddit = "redditclansystem"

        def leader(clan_tag, player_tag):
            return player_tag in leader_alts[clan_tag] if clan_tag in leader_alts else False

        async def update_database():
            sql = ("SELECT clan_tag, leader_name, clan_level, classification, war_wins, win_streak "
                   "FROM rcs_clans ORDER BY clan_name")
            fetch = await conn.fetch(sql)
            leader_changes = ""
            for row in fetch:
                clan = await self.bot.coc.get_clan(row['clan_tag'])
                description = re.sub(r"[^a-zA-Z/.,!\s\d]+", "", clan.description)
                if not clan.public_war_log:
                    clan.war_ties = 0
                    clan.war_losses = 0
                # compare clan leader and report to council chat if different
                clan_leader = clan.get_member(role=coc.Role.leader)
                comparator = (not leader(clan.tag[1:], clan_leader.tag[1:])
                              and row['classification'] != "family"
                              and row['leader_name'] != clan_leader.name)
                if comparator:
                    leader_changes += f"{clan.name}: Leader changed from {row['leader_name']} to {clan_leader.name}\n"
                sql = ("UPDATE rcs_clans "
                       "SET clan_name = $1, clan_level = $2, member_count = $3, war_frequency = $4, clan_type = $5, "
                       "clan_description = $6, clan_location = $7, badge_url = $8, clan_points = $9, "
                       "clan_vs_points = $10, required_trophies = $11, win_streak = $12, war_wins = $13, "
                       "war_ties = $14, war_losses = $15, war_log_public = $16 "
                       "WHERE clan_tag = $17")
                try:
                    await conn.execute(sql, clan.name, clan.level, clan.member_count, clan.war_frequency, clan.type,
                                       description, clan.location.name, clan.badge.url, clan.points,
                                       clan.versus_points, clan.required_trophies, clan.war_win_streak, clan.war_wins,
                                       clan.war_ties, clan.war_losses, clan.public_war_log, clan.tag[1:])
                except:
                    self.bot.logger.exception("SQL fail")
            print(leader_changes)
            if leader_changes and 8 < now.hour < 12:
                embed = discord.Embed(color=discord.Color.dark_red())
                embed.add_field(name="Leader Changes", value=leader_changes)
                embed.add_field(name="Disclaimer", value="These changes may or may not be permanent. "
                                                         "Please investigate as appropriate.")
                embed.set_footer(text="++help alts (for help adjusting leader alts)",
                                 icon_url="https://api-assets.clashofclans.com/badges/200/h8Hj8FDhK2b1PdkwF7fEb"
                                          "TGY5UkT_lntLEOXbiLTujQ.png")
                council_chat = self.bot.get_channel(settings['rcs_channels']['council'])
                await council_chat.send(embed=embed)

        def process_row(row):
            if row['subreddit']:
                sub = f"[Subreddit](https://www.reddit.com{row['subreddit']})"
            else:
                sub = ""
            if row['leader_reddit']:
                leader_reddit = f"[{row['leader_name']}](https://www.reddit.com{row['leader_reddit']})"
            else:
                leader_reddit = row['leader_name']
            if row['social_media']:
                social_media = row['social_media'] + " " + sub
            else:
                social_media = sub
            if row['family_clan'] == "Y":
                family = family_link
            else:
                family = ""
            clan_dot = "![](%%yellowdot%%) "
            if row['member_count'] < 35: clan_dot = "![](%%greendot%%) "
            if row['member_count'] > 45: clan_dot = "![](%%reddot%%) "
            return (f"\n{clan_dot}[{row['clan_name'].replace(' ','&nbsp;')}]"
                    f"(https://link.clashofclans.com/?action=OpenClanProfile&tag={row['clan_tag']}) | "
                    f"[#{row['clan_tag']}](https://www.clashofstats.com/clans/{row['clan_tag']}/members)"
                    f" | {leader_reddit} | {row['member_count']}/50 | {social_media} | "
                    f"{row['notes']} | {family}")

        async def update_wiki_page(wiki_page):
            page = reddit.subreddit(subreddit).wiki[wiki_page]
            content = page.content_md
            sql = ("SELECT clan_name, subreddit, clan_tag, clan_level, leader_name, leader_reddit, member_count, "
                   "war_frequency, social_media, notes, family_clan "
                   "FROM rcs_clans "
                   "WHERE classification = $1 "
                   "ORDER BY member_count, clan_name")
            # Main four categories
            clan_categories = ["comp", "social", "gen", "warFarm"]
            for category in clan_categories:
                fetch = await conn.fetch(sql, category)
                page_content = "Clan Name | Clan Tag | Leader | Members | Social Media | Notes | Family Clan\n"
                page_content += "-|-|-|:-:|-|-|:-:"
                start_marker = f"[](#{category}Start)"
                end_marker = f"[](#{category}End)"
                for row in fetch:
                    page_content += process_row(row)
                start = content.index(start_marker)
                end = content.index(end_marker) + len(end_marker)
                content = content.replace(content[start:end], "{}{}{}".format(start_marker, page_content, end_marker))
            # Family Clans
            start_marker = "[](#feederStart)"
            end_marker = "[](#feederEnd)"
            sql = ("SELECT a.family_clan, a.clan_name, a.clan_tag, a.social_media, a.member_count, "
                   "b.leader_name, b.leader_reddit, a.notes "
                   "FROM rcs_clans a, rcs_clans b "
                   "WHERE a.classification = 'family' AND a.family_clan = b.clan_name "
                   "ORDER BY a.family_clan")
            fetch = await conn.fetch(sql)
            page_content = "Home Clan | Clan Name | Clan Tag | Members | Contact | Notes\n"
            page_content += "-|-|-|:-:|-|-"
            for row in fetch:
                if row['leader_reddit']:
                    leader_reddit = f"[{row['leader_name']}](https://www.reddit.com{row['leader_reddit']})"
                else:
                    leader_reddit = row['leader_name']
                page_content += (f"\n{row['family_clan'].replace(' ','&nbsp;')} | {row['clan_name'].replace(' ','&nbsp;')}"
                                 f" | [{row['clan_tag']}](https://www.clashofstats.com/clans/{row['clan_tag']}/members)"
                                 f" | {row['member_count']}/50 | {leader_reddit} | {row['notes']}")
            start = content.index(start_marker)
            end = content.index(end_marker) + len(end_marker)
            content = content.replace(content[start:end], "{}{}{}".format(start_marker, page_content, end_marker))
            # Push changes to Reddit
            page.edit(content, reason="Updating Clan Tracking Wikipage")

        async def update_records(wiki_page):
            page = reddit.subreddit(subreddit).wiki[wiki_page]
            content = page.content_md
            page_content = "| Clan Name | Wins | Losses | Ties | Total Wars | Win %\n"
            page_content += ":--|:--|:-:|:-:|:-:|:-:|:-:"
            start_marker = "[](#recordStart)"
            end_marker = "[](#recordEnd)"
            sql = ("SELECT clan_name, clan_tag, war_wins, war_losses, war_ties, war_log_public "
                   "FROM rcs_clans "
                   "ORDER BY war_wins DESC")
            fetch = await conn.fetch(sql)
            for i, row in enumerate(fetch):
                total_wars = row['war_wins'] + row['war_losses'] + row['war_ties']
                if row['war_log_public']:
                    win_percent = row['war_wins'] / total_wars * 100
                    win_percent = f"{win_percent:0.2f}"
                else:
                    win_percent = "Private"
                page_content += (f"\n{i+1}. | [{row['clan_name']}](https://link.clashofclans.com/?action="
                                 f"OpenClanProfile&tag={row['clan_tag']}) | {row['war_wins']} | {row['war_losses']} | "
                                 f"{row['war_ties']} | {total_wars} | {win_percent}")
            start = content.index(start_marker)
            end = content.index(end_marker) + len(end_marker)
            content = content.replace(content[start:end], "{}{}{}".format(start_marker, page_content, end_marker))
            page.edit(content, reason="Updating Clan Records")

        print("Updating database")
        # await update_database()
        print("Updating wiki page")
        await update_wiki_page("official_reddit_clan_system")
        print("Updating Records")
        await update_records("clan_records")

    @commands.Cog.listener()
    async def on_message(self, message):
        """Awards random points to members when posting messages"""
        if isinstance(message.channel, discord.DMChannel):
            return
        if message.author.bot or message.guild.id != settings['discord']['rcsguild_id']:
            return
        if settings['rcs_roles']['members'] not in [role.id for role in message.author.roles]:
            return
        conn = self.bot.pool
        row = await conn.fetchrow(f"SELECT * FROM rcs_messages WHERE discord_id = {message.author.id}")
        points = randint(7, 14)
        if row:
            if datetime.now() > row['last_message'] + timedelta(minutes=1):
                await conn.execute(f"UPDATE rcs_messages "
                                   f"SET message_points = {row['message_points']+points}, "
                                   f"last_message = '{datetime.now()}', "
                                   f"message_count = {row['message_count']+1} "
                                   f"WHERE discord_id = {message.author.id}")
            else:
                await conn.execute(f"UPDATE rcs_messages "
                                   f"SET last_message = '{datetime.now()}' "
                                   f"WHERE discord_id = {message.author.id}")
        else:
            await conn.execute(f"INSERT INTO rcs_messages "
                               f"VALUES ({message.author.id}, {points}, '{datetime.now()}', 1)")
        if message.channel.id == 298620147424296970 and "<@&296114507959369739>" in message.content:
            # this is for leader's pinging chat mods in leader-chat
            chat_mods = self.bot.get_channel(settings['rcs_channels']['mods'])
            await chat_mods.send(f"{message.author.display_name} sent:\n{message.content}")


def setup(bot):
    bot.add_cog(Background(bot))
