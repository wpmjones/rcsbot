import pymssql
import re
import discord
import requests
from datetime import datetime, date
from discord.ext import commands, tasks
from config import settings, color_pick


class DiscordCheck(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.main.start()

    def cog_unload(self):
        self.main.cancel()

    @tasks.loop(hours=24)
    async def main(self):
        guild = self.bot.get_guild(settings['discord']['rcsGuildId'])
        danger_channel = guild.get_channel(settings['rcsChannels']['dangerBot'])
        botdev_channel = guild.get_channel(settings['rcsChannels']['botDev'])
        notes_channel = guild.get_channel(settings['rcsChannels']['leaderNotes'])
        mods_channel = guild.get_channel(settings['rcsChannels']['mods'])
        member_role = guild.get_role(settings['rcsRoles']['members'])
        conn = pymssql.connect(settings['database']['server'],
                               settings['database']['username'],
                               settings['database']['password'],
                               settings['database']['database'])
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM rcs_vwDiscordClans ORDER BY clanName")
        fetch = cursor.fetchall()
        daily_clans = [{"short_name": row[1], "leader_tag": row[2], "clan_name": row[3]} for row in fetch]
        cursor.execute("SELECT clanName, discordTag FROM rcs_data ORDER BY clanName")
        fetch = cursor.fetchall()
        rcs_clans = {}
        for row in fetch:
            rcs_clans[row[0]] = row[1]
        rcs_clans = [{"clan_name": row[0], "leader_tag": row[1]} for row in fetch]
        cursor.execute("SELECT shortName, clanName FROM rcs_data ORDER BY clanName")
        fetch = cursor.fetchall()
        clan_list = []
        for row in fetch:
            if "/" in row[0]:
                for clan in row[0].split("/"):
                    clan_list.append(clan)
            else:
                clan_list.append(row[0])
        self.bot.logger.debug("About the clear messages")
        async for message in danger_channel.history():
            await message.delete()
        self.bot.logger.debug("Messages cleared")
        # THIS IS THE BEGINNING OF THE LEADER NOTE CHECKS
        message_list = []
        async for message in notes_channel.history(limit=None, oldest_first=True):
            message_list.append(message.content)
        self.bot.logger.debug("Messages pulled from Leader Notes")
        messages = " - ".join(message_list)
        regex = r"[tT]ag:\s[a-zA-Z0-9]+|#[a-zA-Z0-9]{6,}"
        ban_set = set()
        for match in re.finditer(regex, messages):
            if match.group() != "#":
                ban_set.add(match.group().upper().replace("TAG: ", "#"))
            else:
                ban_set.add(match.group())
        ban_list = list(ban_set)
        self.bot.logger.debug("Starting to loop through ban_list")
        for tag in ban_list:
            try:
                player = await self.bot.coc.get_player(tag)
                if player.clan and player.clan in rcs_clans:
                    cursor.execute(f"SELECT COUNT(timestamp) AS reported, clanTag, memberTag "
                                   f"FROM rcs_notify "
                                   f"WHERE memberTag = {player.tag[1:]} AND clanTag = {player.clan.tag[1:]} "
                                   f"GROUP BY clanTag, memberTag")
                    row = cursor.fetchone()
                    reported = row[0]
                    if reported > 3:
                        embed = discord.Embed(color=discord.Color.dark_red())
                        embed.add_field(name="Leader Note found:",
                                        value=f"<@{rcs_clans[player.clan.tag[1:]]['leader_tag']}> "
                                        f"{player.name} ({player.tag}) is in {player.clan.name}. Please "
                                        f"search for `in:leader-notes {player.tag}` for details.")
                        embed.set_footer(text="Reminder: This is not a ban list, simply information that this "
                                              "member has caused problems in the past.")
                        await danger_channel.send(embed=embed)
                        cursor.execute(f"INSERT INTO rcs_notify "
                                       f"VALUES ({datetime.now().strftime('%m-%d-%Y %H:%M:%S')}, "
                                       f"{player.clan.tag[1:]}, {player.tag[1:]})")
                        conn.commit()
                    conn.close()
            except:
                self.bot.logger.warning(f"Exception on tag: {tag}")
        # THIS IS THE BEGINNING OF THE NAME CHECKS
        self.bot.logger.debug("Beginning of daily clan check")
        for clan in daily_clans:
            self.bot.logger.debug(f"Checking {clan['clan_name']}")
            report_list = []
            short_list = clan['short_name'].split("/")
            for short_name in short_list:
                if short_name != "reddit":
                    regex = r"\W" + short_name + "\W|\W" + short_name + "\Z"
                else:
                    regex = r"\Wreddit[^\s]"
                self.bot.logger.debug("Looping through Discord members.")
                for member in guild.members:
                    if member_role in member.roles \
                            and re.search(regex, member.display_name, re.IGNORECASE) is not None:
                        report_list.append(member.display_name.replace('||', '|'))
            self.bot.logger.debug(f"Reviewed all members for {clan['clan_name']}")
            if report_list:
                await danger_channel.send(f"<@{clan['leader_tag']}> Please check the following list of "
                                          f"members to make sure everyone is still in your clan "
                                          f"(or feeder).")
                clan_header = f"Results for {clan['clan_name']}"
                content = ""
                for entry in report_list:
                    content += f"\u2800\u2800{entry}\n"
                await self.send_embed(danger_channel, clan_header, content)
                if clan['clan_name'] in ["Ninja Killers", "Faceless Ninjas"]:
                    requests.post(settings['rcsWebhooks']['ninjas'])
            else:
                await botdev_channel.send(f"No members for {clan['clan_name']}")
        # THIS SECTION CHECKS FOR MEMBERS WITHOUT ANY CLAN AFFILIATION
        if date.today().weekday() == 4:
            errors = []
            for member in guild.members:
                if member_role in member.roles:
                    test = 0
                    for short_name in clan_list:
                        if short_name in member.display_name.lower():
                            test = 1
                            continue
                    if test == 0:
                        errors.append(f"{member.mention} did not identify with any clan.")
                        self.bot.logger.info(f"{member.mention} did not identify with any clan.")
            self.bot.logger.debug(errors)
            if errors:
                embed = discord.Embed(color=color_pick(181, 0, 0))
                embed.add_field(name="We found some Members without a clan:",
                                value="\n  ".join(errors))
                await mods_channel.send(embed=embed)
        conn.close()

    @main.before_loop
    async def before_main(self):
        await self.bot.wait_until_ready()

    async def send_embed(self, channel, header, text):
        """ Sends embed to channel, splitting if necessary """
        self.bot.logger.debug(f"Content is {len(text)} characters long.")
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
