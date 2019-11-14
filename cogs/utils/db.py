import asyncpg
import pymssql

from config import settings


class Sql:
    def __init__(self, as_dict=False):
        self.as_dict = as_dict

    def __enter__(self):
        self.conn = pymssql.connect(settings['database']['server'],
                                    settings['database']['username'],
                                    settings['database']['password'],
                                    settings['database']['database'],
                                    autocommit=True)
        self.cursor = self.conn.cursor(as_dict=self.as_dict)
        return self.cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()


# class Psql:
#     def __init__(self, bot):
#         self.bot = bot
#
#     @staticmethod
#     async def create_pool():
#         pool = await asyncpg.create_pool(f"{settings['pg']['uri']}/psadmin", max_size=85)
#         return pool
#
#     async def link_user(self, player_tag, discord_id):
#         conn = self.bot.pool
#         sql = f"SELECT discord_id FROM rcs_discord_links WHERE player_tag = '{player_tag}'"
#         row = await conn.fetchrow(sql)
#         if row is not None:
#             if row['discord_id'] == discord_id:
#                 # player record is already in db
#                 self.bot.logger.debug(f"{player_tag} is already in the database.")
#                 return
#             # row exists but has a different discord_id
#             sql = (f"UPDATE rcs_discord_links"
#                    f"SET discord_id = {discord_id}"
#                    f"WHERE player_tag = '{player_tag}'")
#             await conn.execute(sql)
#             self.bot.logger.debug(f"The discord id did not match {discord_id}, so I updated it!")
#             return
#         # no player record in db
#         sql = (f"INSERT INTO rcs_discord_links (discord_id, player_tag) "
#                f"VALUES ({discord_id}, '{player_tag}')")
#         await conn.execute(sql)
#         self.bot.logger.debug(f"{player_tag} added to the database")
#
#     async def get_clans(self):
#         conn = self.bot.pool
#         sql = "SELECT clan_name, clan_tag FROM rcs_clans ORDER BY clan_name"
#         return await conn.fetch(sql)