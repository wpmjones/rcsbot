import asyncio
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
            self.bot.logger.info("loop started")
            clans = await self.bot.db.get_clans()
            clan_list = end_times = []
            for clan in clans:
                clan_list.append(f"#{clan['clan_tag']}")
                war = await self.bot.coc_client.get_current_war(f"#{clan['clan_tag']}")
                self.bot.logger.debug(f"#{clan['clan_tag']}")
                # async for war in self.bot.coc_client.get_current_wars(clan_list):
                self.bot.logger.debug(f"{war.clan['name']} is {war.state}")
                if war.state == "inWar":
                    end_times.append(war.end_time)
            await channel.send(end_times)
            end_times.sort(key=lambda tup: tup[1])
            await channel.send(end_times)
            await channel.send(datetime.now())
            await channel.send(end_times[0][1] - datetime.now())
            seconds_until_post = end_times[0][1] - datetime.now()
            await channel.send(f"Sleeping for {seconds_until_post // 60} minutes.")
            await asyncio.sleep(seconds_until_post)
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
