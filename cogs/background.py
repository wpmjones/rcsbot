import discord
import random

from discord.ext import commands, tasks
from cogs.utils.constants import league_badges
from cogs.utils.db import Sql
from cogs.utils.helper import rcs_tags
from datetime import datetime, date, timedelta, time
from random import randint
from config import settings


class Background(commands.Cog):
    """Cog for background tasks. No real commands here."""
    def __init__(self, bot):
        self.bot = bot
        self.guild = self.bot.get_guild(settings['discord']['rcsguild_id'])
        self.media_stats = self.guild.get_channel(settings['rcs_channels']['media_stats'])

        self.bot.coc.add_events(self.on_clan_war_win_streak_change,
                                self.on_clan_level_change,
                                self.on_clan_war_win_change,
                                self.on_clan_member_join,
                                )
        self.bot.coc.add_clan_update(rcs_tags())
        self.bot.coc.start_updates("clan")

    def cog_unload(self):
        self.bot.coc.remove_events(self.on_clan_war_win_streak_change,
                                   self.on_clan_level_change,
                                   self.on_clan_war_win_change,
                                   self.on_clan_member_join,
                                   )

    @property
    def event_channel(self):
        return self.guild.get_channel(settings['log_channels']['events'])

    async def on_clan_member_join(self, member, clan):
        self.bot.logger.debug("Start clan member join")
        ch = self.bot.get_channel(628008799663292436)
        await ch.send(f"{member.name} has joined {clan.name} with {member.trophies} cups.")

    async def on_clan_war_win_streak_change(self, old_streak, new_streak, clan):
        """Watch for changes in war win streak and report to media/stats channel"""
        self.bot.logger.debug("Start war win streak change")
        if new_streak >= 5:
            msg = random.choice["And the wins keep coming! ",
                                "We've got another streak! ",
                                "Impressive numbers! ",
                                ]
            msg += f"**{clan.name}** has just won another one, bringing their streak to {new_streak}."
            await self.media_stats.send(msg)

    async def on_clan_level_change(self, old_level, new_level, clan):
        """Watch for changes in clan level and report to media/stats channel"""
        self.bot.logger.debug("Start clan level change")
        msg = f"Please help us in congratulating {clan.name} on reaching Level {new_level}."
        await self.media_stats.send(msg)

    async def on_clan_war_win_change(self, old_wins, new_wins, clan):
        """Watch for war wins divisible by 50 and report to media/stats channel"""
        self.bot.logger.debug("Start war win div 50 change")
        if new_wins % 50 == 0:
            prefix = random.choice(["Holy smokes, that is a lot of wins! ",
                                    "Check this out! ",
                                    "Milestone! ",
                                    "Hot diggity dog! ",
                                    "Want to see something cool? "
                                    "And the wins keep coming! "])
            suffix = random.choice(["You are awesome!",
                                    "Keep up the great work!",
                                    "You're making us all proud!"
                                    "Go win a few more!"])
            msg = f"{prefix}{clan.name} just hit **{new_wins}** wins! {suffix}"
            await self.media_stats(msg)

    @tasks.loop(time=time(hour=17))
    async def clan_checks(self):
        """Check clans for member count, badge, etc."""
        if date.today().weekday() != 2:
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

    # @commands.Cog.listener()
    # async def on_message(self, message):
    #     """Awards random points to members when posting messages"""
    #     if isinstance(message.channel, discord.DMChannel) and message.author != self.bot.user:
    #         return
    #     if message.author.bot or message.guild.id != settings['discord']['rcsGuildId']:
    #         return
    #     if settings['rcsRoles']['members'] not in [role.id for role in message.author.roles]:
    #         return
    #     conn = self.bot.pool
    #     row = await conn.fetchrow(f"SELECT * FROM rcs_discord WHERE discord_id = {message.author.id}")
    #     points = randint(7, 14)
    #     if row:
    #         if datetime.now() > row['last_message'] + timedelta(minutes=1):
    #             await conn.execute(f"UPDATE rcs_discord "
    #                                f"SET message_points = {row['message_points']+points}, "
    #                                f"last_message = '{datetime.now()}', "
    #                                f"message_count = {row['message_count']+1} "
    #                                f"WHERE discord_id = {message.author.id}")
    #         else:
    #             await conn.execute(f"UPDATE rcs_discord "
    #                                f"SET last_message = '{datetime.now()}' "
    #                                f"WHERE discord_id = {message.author.id}")
    #     else:
    #         await conn.execute(f"INSERT INTO rcs_discord "
    #                            f"VALUES ({message.author.id}, {points}, 0, '{datetime.now()}', 1)")


def setup(bot):
    bot.add_cog(Background(bot))
