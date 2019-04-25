import coc
import asyncio
import pymssql
from config import settings

api = coc.Client(settings['supercell']['user'], settings['supercell']['pass'])


class WarStatus:
    def __init__(self, bot):
        self.bot = bot

    async def war_report(self):
        """ For reporting wars to RCS war-updates channel """
        await self.bot.wait_until_ready()
        channel = self.bot.get_channel(settings['oakChannels']['testChat'])
        while self == self.bot.get_cog("WarStatus"):
            seconds_until_post = 60
            print(f"Sleeping for {seconds_until_post // 60} minutes.")
            await asyncio.sleep(seconds_until_post)
            print("I'm awake now.")
            conn = pymssql.connect(settings['database']['server'],
                                   settings['database']['username'],
                                   settings['database']['password'],
                                   settings['database']['database'])
            cursor = conn.cursor()
            cursor.execute("SELECT clanTag FROM rcs_data ORDER BY clanName")
            tags = [tag[0] for tag in cursor.fetchall()]
            print(tags)
            conn.close()
            async for clan_war in api.get_current_wars(tags):
                print(f"Printing {clan_war.clan.name}")
                await channel.send(f"{clan_war.clan.name}: {clan_war.state}")


def setup(bot):
    c = WarStatus(bot)
    bot.add_cog(c)
    bot.loop.create_task(c.war_report())
    bot.loop.run_until_complete(api.close())
