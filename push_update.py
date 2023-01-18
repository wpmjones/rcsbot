import asyncio
import coc
import pyodbc

from datetime import datetime, timedelta
from config import settings

coc_client = coc.login(settings['supercell']['user1'],
                       settings['supercell']['pass1'],
                       client=coc.EventsClient,
                       key_count=2,
                       key_names="galaxy",
                       throttle_limit=25,
                       correct_tags=True)

start_time = datetime(2023, 1, 18, 5, 0)
end_time = datetime(2023, 1, 27, 2, 55)

class Sql:
    def __init__(self, autocommit=False):
        self.autocommit = autocommit

    def __enter__(self):
        driver = "ODBC Driver 17 for SQL Server"
        self.conn = pyodbc.connect(f"DRIVER={driver};"
                                   f"SERVER={settings['database']['server']};"
                                   f"DATABASE={settings['database']['database']};"
                                   f"UID={settings['database']['username']};"
                                   f"PWD={settings['database']['password']}")
        self.conn.autocommit = self.autocommit
        self.cursor = self.conn.cursor()
        return self.cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not self.autocommit:
            self.conn.commit()
        self.conn.close()

async def update_push():
    """Task to pull API data for the push"""
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
            async for player in coc_client.get_players(player_tags):
                print(f"{counter + 1} - {player.name} ({player.clan.tag})")
                if player.clan:
                    cursor.execute(sql_1, player.trophies, player.town_hall, player.tag[1:])
                if (player.town_hall < 14 and
                        player.trophies >= 5000 and
                        datetime.utcnow() > (end_time - timedelta(days=2))):
                    cursor.execute(sql_2, player.tag[1:])
                    row = cursor.fetchone()
                    legend_trophies = row[0]
                    if player.trophies > legend_trophies:
                        cursor.execute(sql_3, player.trophies, player.tag[1:])
                counter += 1
        except:
            print(f"Failed on {player_tags[counter]}")
        print("push update complete")

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(update_push())