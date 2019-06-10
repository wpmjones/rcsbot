import asyncio
import time
import pymssql
import re
import discord
import requests
from datetime import datetime, date
from discord.ext import commands
from config import settings, color_pick


class DiscordCheck(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.flag = 1
        conn = pymssql.connect(settings['database']['server'],
                               settings['database']['username'],
                               settings['database']['password'],
                               settings['database']['database'])
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM rcs_vwDiscordClans ORDER BY clanName")
        fetch = cursor.fetchall()
        self.daily_clans = [{"short_name": row[1], "leader_tag": row[2], "clan_name": row[3]} for row in fetch]
        cursor.execute("SELECT clanName, discordTag FROM rcs_data ORDER BY clanName")
        fetch = cursor.fetchall()
        self.rcs_clans = {}
        for row in fetch:
            self.rcs_clans[row[0]] = row[1]
        self.rcs_clans = [{"clan_name": row[0], "leader_tag": row[1]} for row in fetch]
        cursor.execute("SELECT shortName, clanName FROM rcs_data ORDER BY clanName")
        fetch = cursor.fetchall()
        self.clan_list = []
        for row in fetch:
            if "/" in row[0]:
                for clan in row[0].split("/"):
                    self.clan_list.append(clan)
            else:
                self.clan_list.append(row[0])
        conn.close()
        self.bg_task = self.bot.loop.create_task(self.main())

    async def main(self):
        while self.flag == 1:

            start = time.perf_counter()
            guild = self.bot.get_guild(settings['discord']['rcsGuildId'])
            danger_channel = guild.get_channel(settings['rcsChannels']['dangerBot'])
            async for message in danger_channel.history():
                await message.delete()
            notes_channel = guild.get_channel(settings['rcsChannels']['leaderNotes'])
            member_role = guild.get_role(settings['rcsRoles']['members'])
            # THIS IS THE BEGINNING OF THE LEADER NOTE CHECKS
            message_list = []
            async for message in notes_channel.history(limit=None, oldest_first=True):
                message_list.append(message.content)
            messages = " - ".join(message_list)
            regex = r"[tT]ag:\s[a-zA-Z0-9]+|#[a-zA-Z0-9]{6,}"
            ban_set = set()
            for match in re.finditer(regex, messages):
                if match.group() != "#":
                    ban_set.add(match.group().upper().replace("TAG: ", "#"))
                else:
                    ban_set.add(match.group())
            ban_list = list(ban_set)
            for tag in ban_list:
                if tag == '#UQRJVPJV':
                    continue   # this is a clan, not a player
                try:
                    player = await self.bot.coc_client.get_player(tag)
                    if player.clan and player.clan in self.rcs_clans:
                        conn = pymssql.connect(settings['database']['server'],
                                               settings['database']['username'],
                                               settings['database']['password'],
                                               settings['database']['database'])
                        cursor = conn.cursor(as_dict=True)
                        cursor.execute(f"SELECT COUNT(timestamp) AS reported, clanTag, memberTag "
                                       f"FROM rcs_notify "
                                       f"WHERE memberTag = {player.tag[1:]} AND clanTag = {player.clan.tag[1:]} "
                                       f"GROUP BY clanTag, memberTag")
                        row = cursor.fetchone()
                        reported = row['reported']
                        if reported > 3:
                            embed = discord.Embed(color=discord.Color.dark_red())
                            embed.add_field(name="Leader Note found:",
                                            value=f"<@{self.rcs_clans[player.clan.tag[1:]]['leader_tag']}> "
                                            f"{player.name} ({player.tag}) is in {player.clan.name}. Please "
                                            f"search for `in:leader-notes {player.tag}` for details.")
                            embed.set_footer(text="Reminder: This is not a ban list, simply information that this "
                                                  "member has caused problems in the past.")
                            channel = guild.get_channel(settings['rcsChannels']['dangerBot'])
                            await channel.send(embed=embed)
                            cursor.execute(f"INSERT INTO rcs_notify "
                                           f"VALUES ({datetime.now().strftime('%m-%d-%Y %H:%M:%S')}, "
                                           f"{player.clan.tag[1:]}, {player.tag[1:]})")
                            conn.commit()
                        conn.close()
                except:
                    print("Bad player tag")
            # THIS IS THE BEGINNING OF THE NAME CHECKS
            for clan in self.daily_clans:
                report_list = []
                short_list = clan['short_name'].split("/")
                for short_name in short_list:
                    if short_name != "reddit":
                        regex = r"\W" + short_name + "\W|\W" + short_name + "\Z"
                    else:
                        regex = r"\Wreddit[^\s]"
                    for member in guild.members:
                        if member_role in member.roles \
                                and re.search(regex, member.display_name, re.IGNORECASE) is not None:
                            report_list.append(f"Discord Name: {member.display_name.replace('||', '|')}")
                if report_list:
                    channel = guild.get_channel(settings['rcsChannels']['dangerBot'])
                    clan_header = f"**Results for {clan['clan_name']}**"
                    content = ""
                    for entry in report_list:
                        content += f"  {entry}\n"
                    embed = discord.Embed(color=color_pick(181, 0, 0))
                    embed.add_field(name=clan_header, value=content)
                    embed.set_footer(text="If someone is no longer in your clan, please notify a Chat Mod "
                                          "to have their Member role removed.",
                                     icon_url="http://www.mayodev.com/images/dangerbot.png")
                    await channel.send(f"<@{clan['leader_tag']}> Please check the following list of members to make "
                                       f"sure everyone is still in your clan (or feeder).")
                    await channel.send(embed=embed)
                    if clan['clan_name'] in ["Ninja Killers", "Faceless Ninjas"]:
                        requests.post(settings['rcsWebhooks']['ninjas'])
                else:
                    channel = guild.get_channel(settings['rcsChannels']['botDev'])
                    await channel.send(f"No members for {clan['clan_name']}")
            if date.today().weekday() == 6:
                errors = []
                for member in guild.members:
                    if member_role in member.roles:
                        test = 0
                        for short_name in self.clan_list:
                            if short_name in member.display_name.lower():
                                test = 1
                                continue
                        if test == 0:
                            errors.append(f"{member.mention} did not identify with any clan.")
                if errors:
                    embed = discord.Embed(color=color_pick(181, 0, 0))
                    embed.add_field(name="We found some Members without a clan:",
                                    value="\n  ".join(errors))
                    channel = guild.get_channel(settings['rcsChannels']['mods'])
                    await channel.send(embed=embed)
            elapsed = time.perf_counter() - start
            channel = guild.get_channel(settings['rcsChannels']['botDev'])
            await channel.send(f"I'm going to sleep for {((60*60*24) - elapsed):.2f} seconds. See you tomorrow!")
            await asyncio.sleep((60*60*24) - elapsed)

    @commands.command(name="flip_discord")
    @commands.is_owner()
    async def flip(self, ctx):
        if self.flag == 1:
            self.flag = 0


def setup(bot):
    bot.add_cog(DiscordCheck(bot))
