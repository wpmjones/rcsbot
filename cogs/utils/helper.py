from cogs.utils.db import Sql
from functools import lru_cache


@lru_cache(maxsize=4)
def rcs_names_tags():
    """Retrieve and cache all RCS clan names and tags"""
    with Sql(as_dict=True) as cursor:
        sql = "SELECT clanName, clanTag, altName FROM rcs_data ORDER BY clanName"
        cursor.execute(sql)
        fetch = cursor.fetchall()
    clans = {}
    for clan in fetch:
        clans[clan['clanName']] = clan['clanTag']
        clans[clan['altName']] = clan['clanTag']
    return clans


@lru_cache(maxsize=2)
def rcs_tags():
    """Retrieve and cache clan tags for all RCS clans"""
    with Sql(as_dict=True) as cursor:
        sql = "SELECT clanTag FROM rcs_data ORDER BY clanName"
        cursor.execute(sql)
        fetch = cursor.fetchall()
    clans = []
    for clan in fetch:
        clans.append(clan['clanTag'])
    return clans


@lru_cache(maxsize=64)
def get_clan(tag):
    """Retrieve the details of a specific clan (provide clan tag without hashtag"""
    with Sql(as_dict=True) as cursor:
        sql = ("SELECT clanName, subReddit, clanLeader, cwlLeague, discordServer, feeder, classification "
               "FROM rcs_data "
               "WHERE clanTag = %s")
        cursor.execute(sql, tag)
        clan = cursor.fetchone()
    return clan
