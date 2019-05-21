import asyncio
import traceback
from datetime import datetime
from discord.ext import commands
from config import settings


class WarStatus(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def war_report(self):
        """ For reporting wars to RCS war-updates channel """
        await self.bot.wait_until_ready()
        channel = self.bot.get_channel(settings['oakChannels']['testChat'])
        while self == self.bot.get_cog("WarStatus"):
            try:
                clans = await self.bot.db.get_clans()
                clan_list = []
                end_times = [86400, 999000]
                for clan in clans:
                    clan_list.append(f"#{clan['clan_tag']}")
                async for war in self.bot.coc_client.get_current_wars(["#80YGRPC9", "#CVCJR89",  "#UPVV99V"]):
                    if war.state in ["inWar", "preparation", "warEnded"]:
                        self.bot.logger.debug(f"{war.clan.name} is {war.state}. End time = {war.end_time.time}")
                        end_times.append(war.end_time.seconds_until)
                    else:
                        self.bot.logger.debug(f"Clan not in war")
                end_times.sort()
                await channel.send(f"End times: {end_times}")
                seconds_until_post = end_times[0]
                await channel.send(f"Sleeping for {seconds_until_post // 60} minutes.")
                await asyncio.sleep(seconds_until_post)
            except:
                self.bot.logger.exception("Test")
                # tb_lines = traceback.format_exception(e.__class__, e, e.__traceback__)
                # tb_text = "".join(tb_lines)
                # self.bot.logger.error(tb_text)
            print("I'm awake now.")
            # conn = pymssql.connect(settings['database']['server'],
            #                        settings['database']['username'],
            #                        settings['database']['password'],
            #                        settings['database']['database'])
            # cursor = conn.cursor()
            # cursor.execute("SELECT clanTag FROM rcs_data ORDER BY clanName")
            # tags = [tag[0] for tag in cursor.fetchall()]
            # print(tags)
            # conn.close()
            # async for clan_war in self.bot.coc_client.get_current_wars(tags):
            #     print(f"Printing {clan_war.clan.name}")
            #     await channel.send(f"{clan_war.clan.name}: {clan_war.state}")


def setup(bot):
    c = WarStatus(bot)
    bot.add_cog(c)
    bot.loop.create_task(c.war_report())
