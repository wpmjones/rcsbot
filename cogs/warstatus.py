import coc
import discord
import asyncio
import pymssql
from config import settings


class WarStatus:
    def __init__(self, bot):
        self.bot = bot

    # TODO figure out how to close loop before stopping cog

    async def war_report(self):
        """ For reporting wars to RCS war-updates channel """
        await self.bot.wait_until_ready()
        api = coc.Client(settings['supercell']['apiKey'])
        channel = self.bot.get_channel(settings['oakChannels']['testChat'])
        while not self.bot.is_closed():
            seconds_until_post = 60
            print(f"Sleeping for {seconds_until_post / 60} minutes.")
            await asyncio.sleep(seconds_until_post)

            conn = pymssql.connect(settings['database']['server'],
                                   settings['database']['username'],
                                   settings['database']['password'],
                                   settings['database']['database'])
            cursor = conn.cursor()
            cursor.execute('SELECT clanTag FROM rcs_data ORDER BY clanName')
            rows = cursor.fetchall()
            conn.close()
            for tag in rows:
                clan = api.get_clan(tag[0])
                print(clan.name)
                await channel.send(clan.name)


def setup(bot):
    c = WarStatus(bot)
    bot.add_cog(c)
    bot.loop.create_task(c.war_report())
