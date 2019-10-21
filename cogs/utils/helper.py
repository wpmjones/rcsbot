from cogs.utils.db import conn_sql
from functools import lru_cache


@lru_cache(maxsize=4)
def rcs_clans():
    """Retrieve and cache all RCS clan names and tags"""
    conn = conn_sql()
    cursor = conn.cursor(as_dict=True)
    sql = "SELECT clanName, clanTag FROM rcs_data ORDER BY clanName"
    cursor.execute(sql)
    fetch = cursor.fetchall()
    conn.close()
    clans = {}
    for clan in fetch:
        clans[clan['clanName']] = clan['clanTag']
    return clans


@lru_cache(maxsize=64)
def get_clan(tag):
    """Retrieve the details of a specific clan"""
    conn = conn_sql()
    cursor = conn.cursor(as_dict=True)
    sql = "SELECT clanName, subReddit, clanLeader, cwlLeague, discordServer FROM rcs_data WHERE clanTag = %s"
    cursor.execute(sql, tag)
    clan = cursor.fetchone()
    conn.close()
    return clan


def get_emoji_url(emoji_id):
    return f"https://cdn.discordapp.com/emojis/{emoji_id}.png"
