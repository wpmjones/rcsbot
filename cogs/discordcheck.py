import discord
import coc
import re

from discord.ext import commands, tasks
from datetime import datetime, time, date
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
        bot.loop.create_task(self.cog_init_ready())

    def cog_unload(self):
        self.clear_danger.cancel()
        self.leader_notes.cancel()
        self.discord_check.cancel()

    async def cog_init_ready(self) -> None:
        """Sets the guild properly"""
        await self.bot.wait_until_ready()
        if not self.guild:
            self.guild = self.bot.get_guild(settings['discord']['rcsguild_id'])

    @tasks.loop(time=time(hour=16, minute=20))
    async def clear_danger(self):
        """Clears the danger-bot channel in preparation for new info"""
        danger_channel = self.guild.get_channel(settings['rcs_channels']['danger_bot'])
        async for message in danger_channel.history():
            await message.delete()

    @tasks.loop(time=time(hour=16, minute=25))
    async def leader_notes(self):
        """Check the leader-notes channel and see if any of those players are in an RCS clan"""
        danger_channel = self.bot.get_channel(settings['rcs_channels']['danger_bot'])
        notes_channel = self.bot.get_channel(settings['rcs_channels']['leader_notes'])

        messages = ""
        async for message in notes_channel.history(limit=None, oldest_first=True):
            if message.content:
                messages += message.content + " - "
        regex = r"[tT]ag:\s[PYLQGRJCUV0289]+|#[PYLQGRJCUV0289]{6,}"
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
                               "WHERE memberTag = %s AND clanTag = %s")
                        cursor.execute(sql, (player.tag[1:], player.clan.tag[1:]))
                        row = cursor.fetchone()
                        reported = row[0]
                        if reported < 3:
                            clan = get_clan(player.clan.tag[1:])
                            await danger_channel.send(f"<@{clan['leaderTag']}>")
                            embed = discord.Embed(color=discord.Color.dark_red())
                            embed.add_field(name="Leader Note found:",
                                            value=f"{player.name} ({player.tag}) is in {player.clan.name}. Please "
                                                  f"search for `in:leader-notes {player.tag}` for details.")
                            embed.set_footer(text="Reminder: This is not a ban list, simply information that this "
                                                  "member has caused problems in the past.")
                            await danger_channel.send(embed=embed)
                            sql = ("INSERT INTO rcs_notify "
                                   "VALUES (%s, %s, %s)")
                            cursor.execute(sql, (datetime.now().strftime('%m-%d-%Y %H:%M:%S'),
                                                 player.clan.tag[1:],
                                                 player.tag[1:]))
            except coc.NotFound:
                self.bot.logger.warning(f"Exception on tag: {tag}")
            except:
                self.bot.logger.exception("Other failure")
            # Add to task log
            sql = ("INSERT INTO rcs_task_log (log_type_id, log_date, argument) "
                   "VALUES ($1, $2, $3)")
        try:
            await self.bot.pool.execute(sql,
                                        log_types['danger'],
                                        date.today(),
                                        f"{len(ban_list)} tags processed")
        except:
            self.bot.logger.exception("RCS Task Log insert error")

    @tasks.loop(time=time(hour=16, minute=30))
    async def discord_check(self):
        """Check members and notify clan leaders to confirm they are still in the clan"""
        # THIS IS THE BEGINNING OF THE NAME CHECKS
        danger_channel = self.guild.get_channel(settings['rcs_channels']['danger_bot'])
        botdev_channel = self.guild.get_channel(settings['rcs_channels']['bot_dev'])
        member_role = self.guild.get_role(settings['rcs_roles']['members'])
        with Sql() as cursor:
            cursor.execute("SELECT shortName, discordTag, clanName FROM rcs_vwDiscordClans ORDER BY clanName")
            fetch = cursor.fetchall()
            daily_clans = [{"short_name": row[0], "leader_tag": row[1], "clan_name": row[2]} for row in fetch]
        for clan in daily_clans:
            report_list = []
            short_list = clan['short_name'].split("/")
            for short_name in short_list:
                if short_name != "reddit":
                    regex = r"[|(\[]\W*(reddit |.*\/)?{}".format(short_name)
                else:
                    regex = r"\Wreddit[^\s]|\Wreddit$"
                for member in self.guild.members:
                    if member_role in member.roles \
                            and re.search(regex, member.display_name.lower(), re.IGNORECASE) is not None:
                        report_list.append(member.display_name.replace('||', '|'))
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
                await botdev_channel.send(f"No members for {clan['clan_name']}")
        # Add to task log
        sql = ("INSERT INTO rcs_task_log (log_type_id, log_date, argument) "
               "VALUES ($1, $2, $3)")
        try:
            await self.bot.pool.execute(sql,
                                        log_types['discord_check'],
                                        date.today(),
                                        f"{len(daily_clans)} clans processed")
        except:
            self.bot.logger.exception("RCS Task Log insert fail")

    @tasks.loop(hours=24)
    async def no_clan(self):
        """Check all discord members to see if they have a clan name in their display name"""
        if date.today().weekday() != 0:
            return
        member_role = self.guild.get_role(settings['rcs_roles']['members'])
        mods_channel = self.guild.get_channel(settings['rcs_channels']['mods'])
        with Sql() as cursor:
            cursor.execute("SELECT shortName, clanName FROM rcs_data ORDER BY clanName")
            fetch = cursor.fetchall()
        clan_list = []
        for row in fetch:
            if "/" in row[0]:
                for clan in row[0].split("/"):
                    clan_list.append(clan)
            else:
                clan_list.append(row[0])
        no_clan_list = []
        for member in self.guild.members:
            if member_role in member.roles:
                test = 0
                for short_name in clan_list:
                    if short_name in member.display_name.lower():
                        test = 1
                        break
                if test == 0:
                    no_clan_list.append(f"{member.mention} did not identify with any clan.")
        if no_clan_list:
            log_message = f"{len(no_clan_list)} members found without a clan"
            embed = discord.Embed(color=color_pick(181, 0, 0))
            embed.add_field(name="We found some Members without a clan:",
                            value="\n  ".join(no_clan_list))
            await mods_channel.send(embed=embed)
        else:
            log_message = "All members have a happy home with a clan in their name."
        # Add to task log
        sql = ("INSERT INTO rcs_task_log (log_type_id, log_date, argument) "
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
            embed = discord.Embed(color=color_pick(181, 0, 0))
            embed.add_field(name=header, value=text, inline=False)
            embed.set_footer(text="If someone is no longer in your clan, please notify a Chat Mod "
                                  "to have their Member role removed.",
                             icon_url="http://www.mayodev.com/images/dangerbot.png")
            await channel.send(embed=embed)
        else:
            coll = ""
            for line in text.splitlines(keepends=True):
                if len(coll) + len(line) > 1000:
                    embed = discord.Embed(color=color_pick(181, 0, 0))
                    embed.add_field(name=header, value=coll, inline=False)
                    await channel.send(embed=embed)
                    header = "Continued..."
                    coll = ""
                coll += line
            embed = discord.Embed(color=color_pick(181, 0, 0))
            embed.add_field(name=header, value=coll, inline=False)
            embed.set_footer(text="If someone is no longer in your clan, please notify a Chat Mod "
                                  "to have their Member role removed.",
                             icon_url="http://www.mayodev.com/images/dangerbot.png")
            await channel.send(embed=embed)


def setup(bot):
    bot.add_cog(DiscordCheck(bot))
