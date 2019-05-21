import asyncpg
from config import settings


class RcsDB:
    def __init__(self, bot):
        self.bot = bot

    async def create_pool(self):
        pool = await asyncpg.create_pool(settings['pg']['uri'], max_size=85)
        return pool

    async def link_user(self, player_tag, discord_id):
        conn = self.bot.db.pool
        sql = f"SELECT discord_id FROM rcs_discord_links WHERE player_tag = '{player_tag}'"
        row = await conn.fetchrow(sql)
        if row is not None:
            if row['discord_id'] == discord_id:
                # player record is already in db
                await self.bot.test_channel.send(f"{player_tag} is already in the database.")
                return
            # row exists but has a different discord_id
            sql = (f"UPDATE rcs_discord_links"
                   f"SET discord_id = {discord_id}"
                   f"WHERE player_tag = '{player_tag}'")
            await conn.execute(sql)
            await self.bot.test_channel.send(f"The discord id did not match {discord_id}, so I updated it!")
            return
        # no player record in db
        sql = (f"INSERT INTO rcs_discord_links (discord_id, player_tag) "
               f"VALUES ({discord_id}, '{player_tag}')")
        await conn.execute(sql)
        await self.bot.test_channel.send(f"{player_tag} added to the database")

    async def get_clans(self):
        conn = self.bot.db.pool
        sql = "SELECT clan_name, clan_tag FROM rcs_clans ORDER BY clan_name"
        return await conn.fetch(sql)

