import discord
import coc

from discord.ext import commands
from cogs.utils.helper import rcs_tags
from cogs.utils.db import Sql
from PIL import Image, ImageDraw
from config import settings, color_pick


class WarStatus(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.test_channel = self.bot.get_channel(settings['log_channels']['test'])
        self.war_channel = self.bot.get_channel(settings['rcs_channels']['war_updates'])

        self.active_wars = self.get_active_wars()

        self.bot.coc.add_events(self.on_war_state_change,
                                )
        self.bot.coc.add_war_update(rcs_tags(prefix=True))
        self.bot.coc.start_updates("war")

    def cog_unload(self):
        self.bot.coc.remove_events(self.on_war_state_change,
                                   )

    @staticmethod
    def get_active_wars():
        with Sql(as_dict=True) as cursor:
            sql = "SELECT '#' + clanTag as tag, war_id FROM rcs_wars WHERE warState <> 'warEnded'"
            cursor.execute(sql)
            fetch = cursor.fetchall()
        wars = {}
        for row in fetch:
            wars[row['tag']] = row['war_id']
        return wars

    # TODO Create command to pull old war logs into DB

    @commands.command(name="img")
    async def report_war(self, ctx):
        """Send war report to #rcs-war-updates"""
        xa = -2.0
        xb = 1.0
        ya = -1.5
        yb = 1.5
        max_it = 256
        img_x = 800
        img_y = 500
        img = Image.new("RGBA", (img_x, img_y), color_pick(25, 25, 25))
        for y in range(img_y):
            cy = y * (yb - ya) / (img_y - 1) + ya
            for x in range(img_x):
                cx = x * (xb - xa) / (img_x - 1) + xa
                c = complex(cx, cy)
                z = 0
                for i in range(max_it):
                    if abs(z) > 2.0: break
                    z = z * z + c
                r = i % 4 * 64
                g = i % 8 * 32
                b = i % 16 * 16
                img.putpixel((x, y), b * 65536 + g * 256 + r)
        img.save("images/fractal.png")
        await ctx.send(file=discord.File("images/fractal.png"))

    async def on_war_state_change(self, current_state, war):
        if isinstance(war, coc.LeagueWar):
            # I don't want to do anything with CWL wars
            return
        if current_state == "preparation":
            # TODO move add_war elsewhere, use it with inwar/warended if war not in table
            with Sql() as cursor:
                sql = ("INSERT INTO rcs_wars (clanTag, opponentTag, opponentName, teamSize, warState, endTime) "
                       "VALUES ('{}', '{}', N'{}', {}, '{}', '{}')")
                cursor.execute(sql, (war.clan.tag, war.opponent.tag, war.opponent.name, war.team_size,
                                     war.state, war.end_time.time))
                self.active_wars[war.clan.tag] = cursor.lastrowid()
            self.bot.logger.info(f"New war added to database for {war.clan.name} "
                                 f"(war_id: {self.active_wars[war.clan.tag]}).")
        if current_state == "inWar":
            with Sql() as cursor:
                sql = ("UPDATE rcs_wars "
                       "SET warState = 'inWar' "
                       "WHERE war_id = %d")
                cursor.execute(sql, self.active_wars[war.clan.tag])
            self.bot.logger.info(f"War database updated for {war.clan.name} at the start of war. "
                                 f"(war_id: {self.active_wars[war.clan.tag]})")
        if current_state == "warEnded":
            await self.report_war(war)
            with Sql() as cursor:
                sql = ("UPDATE rcs_wars "
                       "SET clanStars = %d, "
                       "clanDestruction = %d, "
                       "clanAttacks = %d, "
                       "opponentStars = %d, "
                       "opponentDestruction = %d, "
                       "opponentAttacks = %d, "
                       "warState = 'warEnded', "
                       "reported = 1) "
                       "WHERE war_id = %d")
                cursor.execute(sql, (war.clan.stars, war.clan.destruction, war.clan.attacks_used,
                                     war.opponent.stars, war.opponent.destruction, war.opponent.attacks_used,
                                     self.active_wars[war.clan.tag]))
            self.bot.logger.info(f"War database updated for {war.clan.name} at the end of war. "
                                 f"(war_id: {self.active_wars[war.clan.tag]})")
            try:
                del self.active_wars[war.clan.tag]
            except KeyError:
                self.bot.logger.error(f"Could not remove active war from dict. Clan tag: {war.clan.tag}")


def setup(bot):
    bot.add_cog(WarStatus(bot))
