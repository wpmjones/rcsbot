import nextcord
import coc
import re

from nextcord.ext import commands, tasks
from datetime import datetime, date
from cogs.utils.constants import log_types
from cogs.utils.db import Sql
from cogs.utils.helper import rcs_tags, get_clan
from config import settings, color_pick


class DiscordCheck(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.guild = None
        self.clear_danger.start()
        self.leader_notes.start()
        self.discord_check.start()
        self.no_clan.start()
        bot.loop.create_task(self.cog_init_ready())

    def cog_unload(self):
        self.clear_danger.cancel()
        self.leader_notes.cancel()
        self.discord_check.cancel()
        self.no_clan.cancel()

    async def cog_init_ready(self) -> None:
        """Sets the guild properly"""
        await self.bot.wait_until_ready()
        if not self.guild:
            self.guild = self.bot.get_guild(settings['discord']['rcsguild_id'])

    @tasks.loop(hours=1)
    async def clear_danger(self):
        """Clears the danger-bot channel in preparation for new info"""
        if datetime.utcnow().hour != 16:
            return
        danger_channel = self.guild.get_channel(settings['rcs_channels']['danger_bot'])
        async for message in danger_channel.history():
            await message.delete()

    @clear_danger.before_loop
    async def before_clear_danger(self):
        await self.bot.wait_until_ready()

    @tasks.loop(hours=1)
    async def leader_notes(self):
        """Check the leader-notes channel and see if any of those players are in an RCS clan"""
        if datetime.utcnow().hour != 16:
            return
        danger_channel = self.bot.get_channel(settings['rcs_channels']['danger_bot'])
        notes_channel = self.bot.get_channel(settings['rcs_channels']['leader_notes'])

        messages = ""
        async for message in notes_channel.history(limit=None, oldest_first=True):
            if message.content:
                messages += message.content + " - "
        regex = r"[tT]ag:\s[PYLQGRJCOUV0289]+|#[PYLQGRJOCUV0289]{6,}"
        ban_list = []
        for match in re.finditer(regex, messages):
            if not match.group().startswith("#"):
                new_match = match.group().upper().replace("TAG: ", "#")
            else:
                new_match = match.group().upper()
            if new_match not in ban_list:
                ban_list.append(new_match)
        self.bot.logger.debug(f"ban_list has {len(ban_list)} items")
        for tag in ban_list:
            if len(tag) < 6:
                self.bot.logger.debug(f"Short tag: {tag}")
            try:
                player = await self.bot.coc.get_player(tag)
                if player.clan and player.clan.tag[1:] in rcs_tags():
                    with Sql() as cursor:
                        sql = ("SELECT COUNT(timestamp) AS reported "
                               "FROM rcs_notify "
                               "WHERE memberTag = ? AND clanTag = ?")
                        cursor.execute(sql, player.tag[1:], player.clan.tag[1:])
                        row = cursor.fetchone()
                        reported = row.reported
                        if reported < 3:
                            clan = get_clan(player.clan.tag[1:])
                            await danger_channel.send(f"<@{clan['leaderTag']}>")
                            embed = nextcord.Embed(color=nextcord.Color.dark_red())
                            embed.add_field(name="Leader Note found:",
                                            value=f"{player.name} ({player.tag}) is in {player.clan.name}. Please "
                                                  f"search for `in:leader-notes {player.tag}` for details.")
                            embed.set_footer(text="Reminder: This is not a ban list, simply information that this "
                                                  "member has caused problems in the past.")
                            await danger_channel.send(embed=embed)
                            sql = ("INSERT INTO rcs_notify "
                                   "VALUES (?, ?, ?)")
                            cursor.execute(sql, (datetime.now().strftime('%m-%d-%Y %H:%M:%S'),
                                                 player.clan.tag[1:],
                                                 player.tag[1:]))
            except coc.NotFound:
                pass
            except:
                # really not anything to do here
                # self.bot.logger.exception(f"Other failure on {tag}")
                self.bot.logger.debug(f"Tag {tag} doesn't appear to be valid. Skipping")
        try:
            # Add to task log
            sql = ("INSERT INTO rcs_task_logs (log_type_id, log_date, argument) "
                   "VALUES ($1, $2, $3)")
            await self.bot.pool.execute(sql,
                                        log_types['danger'],
                                        date.today(),
                                        f"{len(ban_list)} tags processed")
        except:
            self.bot.logger.exception("RCS Task Log insert error")

    @leader_notes.before_loop
    async def before_leader_notes(self):
        await self.bot.wait_until_ready()

    @commands.command(name="danger1", hidden=True)
    @commands.is_owner()
    async def danger_check(self, ctx):
        botdev_channel = self.guild.get_channel(settings['rcs_channels']['bot_dev'])
        member_role = self.guild.get_role(settings['rcs_roles']['members'])
        check_name = "pirates"
        report_list = set()
        counter = 0
        for member in self.guild.members:
            counter += 1
            if member_role in member.roles and check_name in member.display_name.lower():
                report_list.add(f"{member.display_name} ({member.id})")
        if report_list:
            content = ""
            for entry in report_list:
                content += f"\u2800\u2800{entry}\n"
            self.bot.logger.info(f"Report list is {len(content)} characters long")
            await self.send_embed(botdev_channel, counter, content)
        else:
            await self.send_embed(botdev_channel, counter, "Nothing Found")

    @tasks.loop(hours=1)
    async def discord_check(self):
        """Check members and notify clan leaders to confirm they are still in the clan"""
        if datetime.utcnow().hour != 16:
            return
        # THIS IS THE BEGINNING OF THE NAME CHECKS
        danger_channel = self.guild.get_channel(settings['rcs_channels']['danger_bot'])
        botdev_channel = self.guild.get_channel(settings['rcs_channels']['bot_dev'])
        member_role = self.guild.get_role(settings['rcs_roles']['members'])
        sql = "SELECT short_name, discord_tag, clan_name FROM rcs_discord_checks ORDER BY clan_name"
        fetch = await self.bot.pool.fetch(sql)
        daily_clans = [{"short_name": row['short_name'], "leader_tag": row['discord_tag'],
                        "clan_name": row['clan_name']} for row in fetch]
        for clan in daily_clans:
            report_list = set()
            short_list = clan['short_name'].split("/")
            for short_name in short_list:
                if short_name != "reddit":
                    regex = r"[|(\[]\W*(reddit |.*\/)?{}".format(short_name)
                else:
                    regex = r"\Wreddit[^\s]|\Wreddit$"
                for member in self.guild.members:
                    if member_role in member.roles \
                            and re.search(regex, member.display_name.lower(), re.IGNORECASE):
                        report_list.add(f"{member.display_name.replace('||', '|')} ({member.id})")
            if report_list:
                await danger_channel.send(f"<@{clan['leader_tag']}> Please check the following list of "
                                          f"members to make sure everyone is still in your clan "
                                          f"(or feeder).")
                clan_header = f"Results for {clan['clan_name']}"
                content = ""
                for entry in report_list:
                    content += f"\u2800\u2800{entry}\n"
                await self.send_embed(danger_channel, clan_header, content)
                # if clan['clan_name'] in ["Ninja Killers", "Faceless Ninjas"]:
                #     requests.post(settings['rcsHooks']['ninjas'])
            else:
                self.bot.logger.info(f"No members for {clan['clan_name']}")
        # Add to task log
        sql = ("INSERT INTO rcs_task_logs (log_type_id, log_date, argument) "
               "VALUES ($1, $2, $3)")
        try:
            await self.bot.pool.execute(sql,
                                        log_types['discord_check'],
                                        date.today(),
                                        f"{len(daily_clans)} clans processed")
        except:
            self.bot.logger.exception("RCS Task Log insert fail")

    @discord_check.before_loop
    async def before_discord_check(self):
        await self.bot.wait_until_ready()

    @tasks.loop(hours=1)
    async def no_clan(self):
        """Check all discord members to see if they have a clan name in their display name"""
        if date.today().weekday() != 2 or datetime.utcnow().hour != 0:
            return
        member_role = self.guild.get_role(settings['rcs_roles']['members'])
        mods_channel = self.guild.get_channel(settings['rcs_channels']['mods'])
        sql = "SELECT short_name, clan_name FROM rcs_clans ORDER BY clan_name"
        fetch = await self.bot.pool.fetch(sql)
        clan_list = []
        for row in fetch:
            clan_list.append(row['clan_name'].lower())
            if "/" in row['short_name']:
                for clan in row['short_name'].split("/"):
                    clan_list.append(clan)
            else:
                clan_list.append(row['short_name'].lower())
            clan_list.append(row['short_name'].lower())
        # Remove duplicates
        clan_list = [*set(clan_list)]
        # Move reddit to the end so it catches other names first
        clan_list.remove("reddit")
        clan_list.append("reddit")
        no_clan_list = []
        for member in self.guild.members:
            if member_role in member.roles:
                test = 0
                for short_name in clan_list:
                    if short_name in member.display_name.lower():
                        test = 1
                        break
                if test == 0:
                    self.bot.logger.info(f"No clan for {member.display_name}")
                    no_clan_list.append(f"{member.mention} did not identify with any clan.")
        if no_clan_list:
            log_message = f"{len(no_clan_list)} members found without a clan"
            content = "**We found some Members without a clan:**\n"
            content += "\n  ".join(no_clan_list)
            await mods_channel.send(content)
        else:
            log_message = "All members have a happy home with a clan in their name."
        # Add to task log
        sql = ("INSERT INTO rcs_task_logs (log_type_id, log_date, argument) "
               "VALUES ($1, $2, $3)")
        try:
            await self.bot.pool.execute(sql,
                                        log_types['no_clan'],
                                        date.today(),
                                        log_message)
        except:
            self.bot.logger.exception("RCS Task Log insert fail")

    @staticmethod
    async def send_embed(channel, header, text):
        """ Sends embed to channel, splitting if necessary """
        if len(text) < 1000:
            embed = nextcord.Embed(color=color_pick(181, 0, 0))
            embed.add_field(name=header, value=text, inline=False)
            embed.set_footer(text="If someone is no longer in your clan, please notify a Chat Mod "
                                  "to have their Member role removed.",
                             icon_url="http://www.mayodev.com/images/dangerbot.png")
            await channel.send(embed=embed)
        else:
            coll = ""
            for line in text.splitlines(keepends=True):
                if len(coll) + len(line) > 1000:
                    embed = nextcord.Embed(color=color_pick(181, 0, 0))
                    embed.add_field(name=header, value=coll, inline=False)
                    await channel.send(embed=embed)
                    header = "Continued..."
                    coll = ""
                coll += line
            embed = nextcord.Embed(color=color_pick(181, 0, 0))
            embed.add_field(name=header, value=coll, inline=False)
            embed.set_footer(text="If someone is no longer in your clan, please notify a Chat Mod "
                                  "to have their Member role removed.",
                             icon_url="http://www.mayodev.com/images/dangerbot.png")
            await channel.send(embed=embed)


def setup(bot):
    bot.add_cog(DiscordCheck(bot))
