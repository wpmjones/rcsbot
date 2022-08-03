import coc
import discord
import asyncpraw
import random
import re

from discord.ext import commands, tasks
from cogs.utils.constants import league_badges, log_types
from cogs.utils.db import Sql
from cogs.utils import helper
from datetime import datetime, date, timedelta
from random import randint
from config import settings


class Background(commands.Cog):
    """Cog for background tasks. No real commands here."""
    def __init__(self, bot):
        self.bot = bot
        self.guild = None
        self.media_stats = None
        # coc.py events
        self.bot.coc.add_events(self.on_clan_war_win_streak_change,
                                self.on_clan_level_change,
                                self.on_clan_war_win_change
                                )
        # Discord tasks
        self.clan_checks.start()
        self.rcs_list.start()
        self.update_warlog.start()
        bot.loop.create_task(self.cog_init_ready())

    def cog_unload(self):
        self.bot.coc.remove_events(self.on_clan_war_win_streak_change,
                                   self.on_clan_level_change,
                                   self.on_clan_war_win_change,
                                   )
        self.clan_checks.cancel()
        self.rcs_list.cancel()
        self.update_warlog.cancel()

    async def cog_init_ready(self) -> None:
        """Sets the guild properly"""
        await self.bot.wait_until_ready()
        if not self.guild:
            self.guild = self.bot.get_guild(settings['discord']['rcsguild_id'])
            self.media_stats = self.guild.get_channel(settings['rcs_channels']['media_stats'])

    @coc.ClanEvents.war_win_streak()
    async def on_clan_war_win_streak_change(self, old_clan, new_clan):
        """Watch for changes in war win streak and report to media/stats channel"""
        self.bot.logger.debug("Start war win streak change")
        if new_clan.war_win_streak >= 5:
            msg = random.choice(["And the wins keep coming! ",
                                 "We've got another streak! ",
                                 "Impressive numbers! ",
                                 ])
            msg += f"**{new_clan.name}** has just won another one, bringing their streak to {new_clan.war_win_streak}."
            await self.media_stats.send(msg)

    @coc.ClanEvents.level()
    async def on_clan_level_change(self, old_clan, new_clan):
        """Watch for changes in clan level and report to media/stats channel"""
        self.bot.logger.debug("Start clan level change")
        msg = f"Please help us in congratulating {new_clan.name} on reaching Level {new_clan.level}."
        await self.media_stats.send(msg)

    @coc.ClanEvents.war_wins()
    async def on_clan_war_win_change(self, old_clan, new_clan):
        """Watch for war wins divisible by 50 and report to media/stats channel"""
        if new_clan.war_wins % 50 == 0:
            self.bot.logger.debug("Start war win div 50 change")
            prefix = random.choice(["Holy smokes, that is a lot of wins! ",
                                    "Check this out! ",
                                    "Milestone! ",
                                    "Hot diggity dog! ",
                                    "Want to see something cool? ",
                                    "And the wins keep coming! ",
                                    "Too cool!!!"])
            suffix = random.choice(["You are awesome!",
                                    "Keep up the great work!",
                                    "You're making us all proud!",
                                    "Go win a few more!",
                                    f"Can you get to {new_clan.war_wins + 50}?"])
            msg = f"{prefix}{new_clan.name} just hit **{new_clan.war_wins}** wins! {suffix}"
            await self.media_stats.send(msg)

    # @tasks.loop(hours=1.0)
    # async def new_verification(self):
    #     """Check MS SQL - rcs_verify - for new entries and act accordingly"""
    #     sql = "SELECT clanTag, leaderContact FROM rcs_verify WHERE reported = 0"
    #     with Sql() as cursor:
    #         cursor.execute(sql)
    #         fetch = cursor.fetchall()
    #         if fetch:
    #             clan = await self.bot.coc.get_clan(fetch['clanTag'])
    #             discord_contact = fetch['leaderContact']

    @tasks.loop(hours=24.0)
    async def clan_checks(self):
        """Check clans for member count, badge, etc."""
        conn = self.bot.pool
        print("Starting clan checks")
        if date.today().weekday() != 2:
            return
        sql = "SELECT MAX(log_date) AS max_date FROM rcs_task_logs WHERE log_type_id = $1"
        row = await conn.fetchrow(sql, log_types['loc_check'])
        if row:
            if row['max_date'] > datetime.utcnow() - timedelta(days=7):
                # Skip until 7 days are up
                return
        else:
            self.bot.logger.info("No log found for clan_checks")
        council_chat = self.guild.get_channel(settings['rcs_channels']['council'])
        bot_dev = self.guild.get_channel(settings['rcs_channels']['bot_dev'])
        fetch = await conn.fetch("SELECT clan_tag, classification FROM rcs_clans")
        cwl_fetch = conn.fetchrow("SELECT start_time, end_time FROM rcs_events "
                                  "WHERE event_type = 2 AND start_time < CURRENT_TIMESTAMP "
                                  "ORDER BY start_time DESC "
                                  "LIMIT 1")
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
            clan = await self.bot.coc.get_clan(f"#{row['clan_tag']}")
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
                embed.add_field(name="In-game Link", value=f"[Click Here]({clan.share_link})")
                await council_chat.send(embed=embed)
            if clan.type != "inviteOnly":
                embed = discord.Embed(title=clan.name,
                                      description=f"Type: {clan.type}",
                                      color=discord.Color.red())
                embed.set_thumbnail(url=clan.badge.medium)
                embed.set_footer(text="Type not set to Invite Only",
                                 icon_url="https://coc.guide/static/imgs/gear_up.png")
                await council_chat.send(embed=embed)
        # Update db logs
        sql = "INSERT INTO rcs_task_logs (log_type_id, log_date) VALUES ($1, $2)"
        await conn.execute(sql, log_types['loc_check'], datetime.utcnow())

    @clan_checks.before_loop
    async def before_clan_checks(self):
        await self.bot.wait_until_ready()

    @tasks.loop(hours=3.0)
    async def rcs_list(self):
        """Update database with latest info then update the wiki"""
        print("Starting RCS List")
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
        reddit = asyncpraw.Reddit(client_id=settings['reddit_speed']['client'],
                                  client_secret=settings['reddit_speed']['secret'],
                                  username=settings['reddit_speed']['username'],
                                  password=settings['reddit_speed']['password'],
                                  user_agent="raspi:com.mayodev.coc_redditclansystem_updater:v0.5 (by /u/TubaKid44)")
        subreddit = "redditclansystem"

        def leader(clan_tag, player_tag):
            return player_tag in leader_alts[clan_tag] if clan_tag in leader_alts else False

        async def update_database():
            # Sync changes from SQL to PSQL
            with Sql() as cursor:
                sql = ("SELECT clanleader, socMedia, notes, feeder, classification, subReddit, leaderReddit, "
                       "discordTag, shortName, altName, discordServer, clanTag, clanName FROM rcs_data")
                cursor.execute(sql)
                fetch = cursor.fetchall()
                insert_sql = ("INSERT INTO rcs_clans (leader_name, social_media, notes, family_clan, classification, "
                              "subreddit, leader_reddit, discord_tag, short_name, alt_name, discord_server, clan_tag, "
                              "clan_name) "
                              "VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)")
                update_sql = ("UPDATE rcs_clans "
                              "SET leader_name = $1, social_media = $2, notes = $3, family_clan = $4, "
                              "classification = $5, subreddit = $6, leader_reddit = $7, discord_tag = $8, "
                              "short_name = $9, alt_name = $10, discord_server = $11 "
                              "WHERE clan_tag = $12")
                for row in fetch:
                    sql = "SELECT COUNT(*) AS num_found FROM rcs_clans WHERE clan_tag = $1"
                    found = await conn.fetchval(sql, row[11])
                    if found:
                        # Clan already exists in postgres, update it
                        await conn.execute(update_sql, row[0], row[1], row[2], row[3], row[4], row[5], row[6], int(row[7]),
                                           row[8], row[9], row[10], row[11])
                    else:
                        # Clan does not exist in postgres, insert it
                        await conn.execute(insert_sql, row[0], row[1], row[2], row[3], row[4], row[5], row[6], int(row[7]),
                                           row[8], row[9], row[10], row[11], row[12])
                # Let's try and delete clans that are not listed in MS SQL
                sql = "SELECT clan_tag FROM rcs_clans"
                fetch = await conn.fetch(sql)
                clan_list = [row['clan_tag'] for row in fetch]
                sql = "SELECT clanTag FROM rcs_data"
                cursor.execute(sql)
                sql_clans = cursor.fetchall()
                # After this, clan_list should only contain clans that should be removed
                for row in sql_clans:
                    try:
                        clan_list.remove(row[0])
                    except ValueError:
                        # This will happen when if there is a value in MS SQL that is not in postgresql
                        # Theoretically, this will never happen since we've upserted above
                        pass
                if len(clan_list) > 0:
                    self.bot.logger.info(f"Removing: {clan_list}")
                for tag in clan_list:
                    member_sql = "DELETE FROM rcs_members WHERE clan_tag = $1"
                    clan_sql = "DELETE FROM rcs_clans WHERE clan_tag = $1"
                    await conn.execute(member_sql, tag)
                    await conn.execute(clan_sql, tag)
            print("SQL synced to postgresql")
            # Start the update process
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
                clan_leader = clan.get_member_by(role=coc.Role.leader)
                comparator = (not leader(clan.tag[1:], clan_leader.tag[1:])
                              and row['classification'] != "family"
                              and row['leader_name'] != clan_leader.name)
                if comparator:
                    leader_changes += (f"{clan.name}: Leader changed from {row['leader_name']} to {clan_leader.name}"
                                       f"({clan_leader.tag})\n")
                # Update MS SQL
                sql = ("UPDATE rcs_data "
                       "SET clanName = ?, clanLevel = ?, members = ?, warFreq = ?, clanType = ?, "
                       "clanDescription = ?, clanLocation = ?, clanBadge = ?, clanPoints = ?, "
                       "clanVersusPoints = ?, requiredTrophies = ?, warWinStreak = ?, warWins = ?, warTies = ?, "
                       "warLosses = ?, isWarLogPublic = ? "
                       "WHERE clanTag = ?")
                try:
                    with Sql() as cursor:
                        cursor.execute(sql, clan.name, clan.level, clan.member_count, clan.war_frequency, clan.type,
                                       description, clan.location.name, clan.badge.url, clan.points,
                                       clan.versus_points, clan.required_trophies, clan.war_win_streak,
                                       clan.war_wins, clan.war_ties, clan.war_losses, clan.public_war_log,
                                       clan.tag[1:])
                except:
                    self.bot.logger.exception("MSSQL fail")
                # Update Postgresql
                sql = ("UPDATE rcs_clans "
                       "SET clan_name = $1, clan_level = $2, member_count = $3, war_frequency = $4, clan_type = $5, "
                       "clan_description = $6, clan_location = $7, badge_url = $8, clan_points = $9, "
                       "clan_vs_points = $10, required_trophies = $11, win_streak = $12, war_wins = $13, "
                       "war_ties = $14, war_losses = $15, war_log_public = $16, cwl_league = $17 "
                       "WHERE clan_tag = $18")
                try:
                    cwl_league = clan.war_league.name.replace("League ", "")
                    await conn.execute(sql, clan.name, clan.level, clan.member_count, clan.war_frequency, clan.type,
                                       description, clan.location.name, clan.badge.url, clan.points,
                                       clan.versus_points, clan.required_trophies, clan.war_win_streak, clan.war_wins,
                                       clan.war_ties, clan.war_losses, clan.public_war_log, cwl_league, clan.tag[1:])
                except:
                    self.bot.logger.exception("postgreSQL fail")
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
                sub = f"[Subreddit]({row['subreddit']})"
            else:
                sub = ""
            if row['social_media']:
                social_media = row['social_media'] + " " + sub
            else:
                social_media = sub
            if row['family_clan'] == "Y":
                family = family_link
            else:
                family = ""
            clan_dot = "![](%%yellowdot%%) "
            if row['member_count'] < 35:
                clan_dot = "![](%%greendot%%) "
            if row['member_count'] > 45:
                clan_dot = "![](%%reddot%%) "
            return (f"\n{clan_dot}[{row['clan_name'].replace(' ','&nbsp;')}]"
                    f"(https://link.clashofclans.com/?action=OpenClanProfile&tag={row['clan_tag']}) | "
                    f"[#{row['clan_tag']}](https://www.clashofstats.com/clans/{row['clan_tag']}/members)"
                    f" | {row['leader_name']} | {row['member_count']}/50 | {social_media} | "
                    f"{row['notes']} | {family}")

        async def update_wiki_page(wiki_page):
            sub = await reddit.subreddit(subreddit)
            page = await sub.wiki.get_page("official_reddit_clan_system")
            content = page.content_md
            sql = ("SELECT clan_name, subreddit, clan_tag, clan_level, leader_name, leader_reddit, member_count, "
                   "war_frequency, social_media, notes, family_clan "
                   "FROM rcs_clans "
                   "WHERE classification = $1 "
                   "ORDER BY member_count, clan_name")
            # Main five categories
            clan_categories = ["comp", "social", "clan", "tourney", "warFarm"]
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
            start_marker = "[](#familyStart)"
            end_marker = "[](#familyEnd)"
            sql = ("SELECT a.family_clan, a.clan_name, a.clan_tag, a.social_media, a.member_count, "
                   "b.leader_name, b.leader_reddit, a.notes "
                   "FROM rcs_clans a, rcs_clans b "
                   "WHERE a.classification = 'family' AND a.family_clan = b.clan_name "
                   "ORDER BY a.family_clan")
            fetch = await conn.fetch(sql)
            page_content = "Home Clan | Clan Name | Clan Tag | Members | Contact | Notes\n"
            page_content += "-|-|-|:-:|-|-"
            for row in fetch:
                page_content += (f"\n{row['family_clan'].replace(' ','&nbsp;')} | {row['clan_name'].replace(' ','&nbsp;')}"
                                 f" | [{row['clan_tag']}](https://www.clashofstats.com/clans/{row['clan_tag']}/members)"
                                 f" | {row['member_count']}/50 | {row['leader_name']} | {row['notes']}")
            start = content.index(start_marker)
            end = content.index(end_marker) + len(end_marker)
            content = content.replace(content[start:end], "{}{}{}".format(start_marker, page_content, end_marker))
            # Push changes to Reddit
            await page.edit(content, reason="Updating Clan Tracking Wikipage")

        async def update_records(wiki_page):
            sub = await reddit.subreddit(subreddit)
            page = await sub.wiki.get_page("clan_records")
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
                page_content += (f"\n{i+1}. | [#{row['clan_name']}](https://link.clashofclans.com/?action="
                                 f"OpenClanProfile&tag={row['clan_tag']}) | {row['war_wins']} | {row['war_losses']} | "
                                 f"{row['war_ties']} | {total_wars} | {win_percent}")
            start = content.index(start_marker)
            end = content.index(end_marker) + len(end_marker)
            content = content.replace(content[start:end], "{}{}{}".format(start_marker, page_content, end_marker))
            await page.edit(content, reason="Updating Clan Records")

        self.bot.logger.info("Updating database")
        await update_database()
        self.bot.logger.info("Updating wiki page")
        await update_wiki_page("official_reddit_clan_system")
        self.bot.logger.info("Updating clan records")
        await update_records("clan_records")

    @rcs_list.before_loop
    async def before_rcs_list(self):
        await self.bot.wait_until_ready()

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
                else:
                    # War is not in database, add it (happens if bot is down)
                    if war.end_time.time < datetime.utcnow() - timedelta(days=2):
                        reported = True
                    else:
                        reported = False
                    sql = ("INSERT INTO rcs_wars (clan_name, clan_tag, clan_attacks, clan_destruction, clan_stars,"
                           "opponent_tag, opponent_name, opponent_destruction, opponent_stars,"
                           "end_time, war_state, team_size, reported)"
                           "VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)")
                    await conn.execute(sql, war.clan.name, war.clan.tag[1:], war.clan.attacks_used,
                                       war.clan.destruction, war.clan.stars, war.opponent.tag[1:], war.opponent.name,
                                       war.opponent.destruction, war.opponent.stars,
                                       war.end_time.time, "warEnded", war.team_size, reported)
                    self.bot.logger.info(f"Added war for {war.clan.name} vs {war.opponent.name} ending "
                                         f"{war.end_time.time}.")

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
                                   f"last_message = '{datetime.utcnow()}', "
                                   f"message_count = {row['message_count']+1} "
                                   f"WHERE discord_id = {message.author.id}")
            else:
                await conn.execute(f"UPDATE rcs_messages "
                                   f"SET last_message = '{datetime.utcnow()}' "
                                   f"WHERE discord_id = {message.author.id}")
        else:
            await conn.execute(f"INSERT INTO rcs_messages "
                               f"VALUES ({message.author.id}, {points}, '{datetime.utcnow()}', 1)")
        if message.channel.id == 298620147424296970 and "<@&296114507959369739>" in message.content:
            # this is for leader's pinging chat mods in leader-chat
            chat_mods = self.bot.get_channel(settings['rcs_channels']['mods'])
            await chat_mods.send(f"{message.author.display_name} sent:\n{message.content}")


def setup(bot):
    bot.add_cog(Background(bot))
