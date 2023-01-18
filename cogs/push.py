import nextcord
import time

from nextcord import SlashOption
from nextcord.ext import commands, tasks, menus
from cogs.utils.converters import ClanConverter
from cogs.utils.page_sources import MainEmbedPageSource, TopTenSource
from cogs.utils.db import Sql
from cogs.utils.helper import rcs_tags
from datetime import datetime, timedelta

th_choices = {
    "Town Hall 15": 15,
    "Town Hall 14": 14,
    "Town Hall 13": 13,
    "Town Hall 12": 12,
    "Town Hall 11": 11,
    "Town Hall 10": 10,
    "Town Hall 9": 9,
    "Town Hall 8": 8,
    "Town Hall 7": 7,
}


class Push(commands.Cog):
    """Cog for RCS trophy push"""

    def __init__(self, bot):
        self.bot = bot
        self.title = "2023 Wonderful Winter Trophy Push"
        self.start_time = datetime(2023, 1, 18, 5, 0)
        self.end_time = datetime(2023, 1, 27, 2, 55)
        self.update_push.start()

    def cog_unload(self):
        self.update_push.cancel()

    @tasks.loop(minutes=12)
    async def update_push(self):
        """Task to pull API data for the push"""
        now = datetime.utcnow()
        if self.start_time < now < self.end_time:
            self.bot.logger.info("Starting push update")
            with Sql(autocommit=True) as cursor:
                sql = "SELECT playerTag from rcspush_2023_1"
                cursor.execute(sql)
                fetch = cursor.fetchall()
                player_tags = []
                for row in fetch:
                    player_tags.append(row[0])
                sql_1 = ("UPDATE rcspush_2023_1 "
                         "SET currentTrophies = ?, currentThLevel = ? "
                         "WHERE playerTag = ?")
                sql_2 = "SELECT legendTrophies FROM rcspush_2023_1 WHERE playerTag = ?"
                sql_3 = ("UPDATE rcspush_2023_1 "
                         "SET legendTrophies = ? "
                         "WHERE playerTag = ?")
                counter = 0
                try:
                    async for player in self.bot.coc.get_players(player_tags):
                        print(f"{player.name} ({player.clan.tag})")
                        if player.clan:
                            cursor.execute(sql_1, player.trophies, player.town_hall, player.tag[1:])
                        if (player.town_hall < 14 and
                                player.trophies >= 5000 and
                                datetime.utcnow() > (self.end_time - timedelta(days=2))):
                            cursor.execute(sql_2, player.tag[1:])
                            row = cursor.fetchone()
                            legend_trophies = row[0]
                            if player.trophies > legend_trophies:
                                cursor.execute(sql_3, player.trophies, player.tag[1:])
                        counter += 1
                except:
                    self.bot.logger.exception(f"Failed on {player_tags[counter]}")
            self.bot.logger.info("push update complete")

    @update_push.before_loop
    async def before_update_push(self):
        await self.bot.wait_until_ready()

    async def get_push_embed(self):
        delta = self.start_time - datetime.utcnow()
        embed = nextcord.Embed(title=self.title, color=nextcord.Color.from_rgb(0, 183, 0))
        embed.add_field(name="Start time (UTC):", value=self.start_time.strftime("%d-%b-%Y %H:%M"), inline=True)
        embed.add_field(name="End time (UTC):", value=self.end_time.strftime("%d-%b-%Y %H:%M"), inline=True)
        if delta.days > 0:
            start_info = f"Starting in {delta.days} day(s)."
        else:
            hours, _ = divmod(delta.total_seconds(), 3600)
            start_info = f"Starting in {hours:02} hour(s)."
        embed.set_author(name=start_info,
                         icon_url="https://cdn.discordapp.com/emojis/641101630351212567.png")
        return embed

    @nextcord.slash_command(name="push",
                            description="Provides information on the push event")
    async def push(self, interaction: nextcord.Interaction):
        """This is the slash group and will never be called"""
        pass

    @push.subcommand(name="info", description="Provides information on the push event")
    async def push_info(self, interaction: nextcord.Interaction):
        """The main push command for the event and provides information relating to the status of the push."""
        now = datetime.utcnow()
        embed = nextcord.Embed(title=self.title, color=nextcord.Color.from_rgb(0, 183, 0))
        embed.add_field(name="Start time (UTC):", value=self.start_time.strftime("%d-%b-%Y %H:%M"), inline=True)
        embed.add_field(name="End time (UTC):", value=self.end_time.strftime("%d-%b-%Y %H:%M"), inline=True)
        if now < self.start_time:
            delta = self.start_time - now
            if delta.days > 0:
                start_info = f"Starting in {delta.days} day(s)."
            else:
                hours, _ = divmod(delta.total_seconds(), 3600)
                start_info = f"Starting in {hours:02} hour(s)."
            embed.set_author(name=start_info,
                             icon_url="https://cdn.discordapp.com/emojis/641101630351212567.png")
        elif self.start_time < now < self.end_time:
            delta = self.end_time - now
            if delta.days > 0:
                end_info = f"Ending in {delta.days} day(s)."
            else:
                hours, _ = divmod(delta.total_seconds(), 3600)
                end_info = f"Ending in {hours:02} hour(s)."
            embed.set_author(name=end_info,
                             icon_url="https://cdn.discordapp.com/emojis/641101629881319434.png")
        else:
            # embed.add_field(name="Winning clan:", value="Winning clan")
            # TODO other cool stats here
            embed.set_author(name="Event complete!",
                             icon_url="https://cdn.discordapp.com/emojis/641101630342692884.png")
        await interaction.response.send_message(embed=embed)

    @push.subcommand(name="all", description="Lists all clans ranked by score")
    async def push_all(self, interaction: nextcord.Interaction):
        """Returns list of all clans ranked by score (only top 30 trophies contribute to the score)."""
        if datetime.utcnow() < self.start_time:
            embed = await self.get_push_embed()
            return await interaction.response.send_message(embed=embed)
        with Sql() as cursor:
            cursor.execute("SELECT clanName, SUM(clanPoints) AS totals FROM vRCSPush30 "
                           "GROUP BY clanName "
                           "ORDER BY totals DESC")
            fetch = cursor.fetchall()
        data = []
        for row in fetch:
            formatted = f"`{row[0]:\u00A0<20.20} {row[1]:\u00A0>7.7}`"
            data.append(formatted)
        pages = menus.ButtonMenuPages(source=MainEmbedPageSource(data, "All Clans", 20), clear_buttons_after=True)
        await pages.start(interaction=interaction)

    @push.subcommand(name="diff", description="Lists all clans rank by score as compared to top clan")
    async def push_diff(self, interaction: nextcord.Interaction):
        """Returns list of clans ranked by score, showing the differential to the top clan."""
        if datetime.utcnow() < self.start_time:
            embed = await self.get_push_embed()
            return await interaction.response.send_message(embed=embed)
        with Sql() as cursor:
            cursor.execute("SELECT clanName, SUM(clanPoints) AS totals FROM vRCSPush30 "
                           "GROUP BY clanName "
                           "ORDER BY totals DESC")
            fetch = cursor.fetchall()
        top_score = fetch[0][1]
        data = []
        for row in fetch:
            if row[1] == top_score:
                title = f"{row[0]:\u00A0<20.20} {row[1]:\u00A0>7.7}"
            else:
                formatted = f"`{row[0]:\u00A0<20.20} {-1 * (top_score - row[1]):\u00A0>7.7}`"
                data.append(formatted)
        pages = menus.ButtonMenuPages(source=MainEmbedPageSource(data, f"Push Score Differential\n{title}", 20),
                                      clear_buttons_after=True)
        await pages.start(interaction=interaction)

    @push.subcommand(name="top", description="List of top 10 players for each TH level")
    async def push_top(self, interaction: nextcord.Interaction):
        """Returns list of top 10 players for each TH level."""
        if datetime.utcnow() < self.start_time:
            embed = await self.get_push_embed()
            return await interaction.response.send_message(embed=embed)
        # TODO change author icon with TH
        with Sql() as cursor:
            cursor.execute("SELECT playerName, currentTrophies "
                           "FROM rcspush_vwTopTenByTh "
                           "ORDER BY th DESC, currentTrophies DESC")
            fetch = cursor.fetchall()
        data = []
        for row in fetch:
            formatted = f"`{row[0].replace('`', ''):\u00A0<24} {row[1]:\u00A0>7}`"
            data.append(formatted)
        pages = menus.ButtonMenuPages(source=TopTenSource(data),
                                      clear_buttons_after=True)
        await pages.start(interaction=interaction)

    @push.subcommand(name="th", description="Top 100 by TH level")
    async def push_th(self,
                      interaction: nextcord.Interaction,
                      th_level: int = nextcord.SlashOption(
                          name="th_level",
                          choices=th_choices)
                      ):
        """Returns list of top 100 players at the TH specified"""
        if datetime.utcnow() < self.start_time:
            embed = await self.get_push_embed()
            return await interaction.response.send_message(embed=embed)
        with Sql() as cursor:
            cursor.execute(f"SELECT TOP 100 currentTrophies, CAST(clanPoints AS DECIMAL(5,2)) as Pts, "
                           f"playerName + ' (' + COALESCE(altName, clanName) + ')' as Name "
                           f"FROM vRCSPush "
                           f"WHERE currentThLevel = {th_level} "
                           f"ORDER BY clanPoints DESC")
            fetch = cursor.fetchall()
        data = []
        for row in fetch:
            formatted = f"`{row[0]:<4} {row[1]:>6} {row[2].replace('`', ''):\u00A0<23}`"
            data.append(formatted)
        pages = menus.ButtonMenuPages(source=MainEmbedPageSource(data, f"TH{th_level} Scores", 10),
                                      clear_buttons_after=True)
        await pages.start(interaction=interaction)

    @push.subcommand(name="gain", description="Top 25 by trophies gained")
    async def push_gain(self, interaction: nextcord.Interaction):
        """Returns top 25 players based on number of trophies gained."""
        if datetime.utcnow() < self.start_time:
            embed = await self.get_push_embed()
            return await interaction.response.send_message(embed=embed)
        with Sql() as cursor:
            cursor.execute("SELECT trophyGain, player FROM rcspush_vwGains ORDER BY trophyGain DESC")
            fetch = cursor.fetchall()
        data = []
        for row in fetch:
            formatted = f"`{row[1].replace('`', ''):\u00A0<24} {row[0]:\u00A0>7}`"
            data.append(formatted)
        pages = menus.ButtonMenuPages(source=MainEmbedPageSource(data, "Trophy Gains", 25),
                                      clear_buttons_after=True)
        await pages.start(interaction=interaction)

    @push.subcommand(name="clan", description="Push score for specified clan")
    async def push_clan(self, interaction,
                        clan: ClanConverter = SlashOption(name="clan", required=True)):
        """Returns a list of players from the specified clan with their push points"""
        if datetime.utcnow() < self.start_time:
            embed = await self.get_push_embed()
            return await interaction.response.send_message(embed=embed)
        with Sql() as cursor:
            cursor.execute(f"SELECT CAST(clanPoints as decimal(5,2)), "
                           f"playerName + ' (TH' + CAST(currentThLevel as varchar(2)) + ')' "
                           f"FROM vRCSPush "
                           f"WHERE clanName = ? "
                           f"ORDER BY clanPoints DESC",
                           clan.name)
            fetch = cursor.fetchall()
        data = []
        for row in fetch:
            formatted = f"`{row[1].replace('`', ''):\u00A0<24} {row[0]:\u00A0>7}`"
            data.append(formatted)
        pages = menus.ButtonMenuPages(source=MainEmbedPageSource(data, f"Scores for {clan.name}", 25),
                                      clear_buttons_after=True)
        await pages.start(interaction=interaction)

    @commands.command(name="push_start", hidden=True)
    @commands.is_owner()
    async def push_start(self, ctx):
        msg = await ctx.send("Starting process...")
        # start push
        start = time.perf_counter()
        player_list = []
        async for clan in self.bot.coc.get_clans(rcs_tags()):
            for member in clan.members:
                player_list.append(member.tag)
        players_many = []
        async for player in self.bot.coc.get_players(player_list):
            players_many.append([player.tag[1:], player.clan.tag[1:],
                                 player.trophies, player.trophies,
                                 player.best_trophies, player.town_hall, player.town_hall,
                                 player.name.replace("'", "''"), player.clan.name])
        with Sql() as cursor:
            cursor.fast_executemany = True
            sql = (f"INSERT INTO rcspush_2023_1 "
                   f"(playerTag, clanTag, startingTrophies, currentTrophies, "
                   f"bestTrophies, startingThLevel, currentThLevel, playerName, clanName) "
                   f"VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)")
            cursor.executemany(sql, players_many)
        await msg.delete()
        await ctx.send(f"{len(players_many)} members added. Elapsed time: "
                       f"{(time.perf_counter() - start) / 60:.2f} minutes")


def setup(bot):
    bot.add_cog(Push(bot))
