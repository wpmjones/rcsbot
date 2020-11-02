import requests

from cogs.utils.db import Sql
from functools import lru_cache
from config import settings


def get_link_token(maxsize=1):
    """Retrieve new token for links API"""
    payload = {"username": settings['links']['user'], "password": settings['links']['pass']}
    url = "https://api.amazingspinach.com/login"
    r = requests.post(url, json=payload)
    return r.json()['token']


@lru_cache(maxsize=4)
def rcs_names_tags():
    """Retrieve and cache all RCS clan names and tags"""
    with Sql() as cursor:
        sql = "SELECT clanName, clanTag, altName FROM rcs_data ORDER BY clanName"
        cursor.execute(sql)
        fetch = cursor.fetchall()
    clans = {}
    for clan in fetch:
        clans[clan.clanName.lower()] = clan.clanTag
        clans[clan.altName.lower()] = clan.clanTag
    return clans


@lru_cache(maxsize=2)
def rcs_tags(prefix=False):
    """Retrieve and cache clan tags for all RCS clans"""
    if prefix:
        field = "'#' + clanTag as tag"
    else:
        field = "clanTag as tag"
    with Sql() as cursor:
        sql = f"SELECT {field} FROM rcs_data ORDER BY clanName"
        cursor.execute(sql)
        fetch = cursor.fetchall()
    clans = []
    for clan in fetch:
        clans.append(clan.tag)
    return clans


@lru_cache(maxsize=64)
def get_clan(tag):
    """Retrieve the details of a specific clan (provide clan tag without hashtag)"""
    with Sql() as cursor:
        sql = ("SELECT clanName, subReddit, clanLeader, cwlLeague, discordServer, feeder, "
               "classification, discordTag as leaderTag "
               "FROM rcs_data "
               "WHERE clanTag = ?")
        cursor.execute(sql, tag)
        clan = cursor.fetchone()
    return clan


def get_emoji_url(emoji_id):
    return f"https://cdn.discordapp.com/emojis/{emoji_id}.png"


def get_active_wars():
    with Sql() as cursor:
        sql = "SELECT '#' + clanTag as tag, war_id FROM rcs_wars WHERE warState <> 'warEnded'"
        cursor.execute(sql)
        fetch = cursor.fetchall()
    wars = {}
    for row in fetch:
        wars[row.tag] = row.war_id
    return wars
