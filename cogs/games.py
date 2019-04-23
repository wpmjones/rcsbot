import discord, pymssql
from discord.ext import commands
from datetime import datetime
from config import settings, bot_log

'''Cog for trophy push'''


class Games:
    """Cog for Clan Games"""
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def games(self, ctx, *, arg: str = 'all'):
        """Clan Games scores (type "++help games" for more information)
          (use "++games all" compare clan totals)
          (use "++games clan name/tag for clan specific scores)
          (use "++games average" to compare clan averages)"""
        conn = pymssql.connect(server=settings['database']['server'],
                               user=settings['database']['username'],
                               password=settings['database']['password'],
                               database=settings['database']['database'])
        conn.autocommit(True)
        cursor = conn.cursor(as_dict=True)
        if arg == 'all':
            clan_list = []
            cursor.execute("""SELECT TOP 1 playerPoints, clanPoints 
                FROM rcs_events 
                WHERE eventType = 5 
                ORDER BY eventId DESC""")
            row = cursor.fetchone()
            clan_points = row['clanPoints']
            cursor.callproc('rcs_spClanGamesTotal')
            for clan in cursor:
                if clan['clanTotal'] >= clan_points:
                    clan_list.append({'name': clan['clanName'] + ' *', 'clanTotal': clan['clanTotal']})
                else:
                    clan_list.append({'name': clan['clanName'], 'clanTotal': clan['clanTotal']})
            conn.close()
            content = '```RCS Clan Games\n{0:20}{1:>12}'.format('Clan Name', 'Clan Total')
            content += '\n--------------------------------'
            for item in clan_list:
                content += '\n{0:20}{1:12}'.format(item['name'], item['clanTotal'])
            content += '```'
            # fix for +2000 characters
            content1, content2 = split_string(content, '```', '```')
            bot_log(ctx.command, arg, ctx.author, ctx.guild)
            await ctx.send(content1)
            await ctx.send(content2)
        elif arg in ['average', 'avg', 'averages']:
            clan_list = []
            cursor.callproc('rcs_spClanGamesAverage')
            for clan in cursor:
                clan_list.append({'name': clan['clanName'], 'clan_average': clan['clanAverage']})
            conn.close()
            content = '```RCS Clan Games\n{0:20}{1:>12}'.format('Clan Name', 'Clan Average')
            content += '\n--------------------------------'
            for item in clan_list:
                content += '\n{0:20}{1:12}'.format(item['name'], item['clan_average'])
            content += '```'
            # fix for +2000 characters
            content1, content2 = split_string(content, '```', '```')
            bot_log(ctx.command, arg, ctx.author, ctx.guild)
            await ctx.send(content1)
            await ctx.send(content2)
        else:
            clan_tag, clan_name = resolve_clan_tag(arg)
            if clan_tag == 'x':
                bot_log(ctx.command, arg, ctx.author, ctx.guild, 1)
                await ctx.send('You have not provided a valid clan name or clan tag.')
                return
            member_list = []
            cursor.execute("SELECT TOP 1 playerPoints, startTime "
                           "FROM rcs_events "
                           "WHERE eventType = 5 "
                           "ORDER BY eventId DESC")
            row = cursor.fetchone()
            player_points = row['playerPoints']
            cursor.execute("""CREATE TABLE #rcs_players (playerTag varchar(15), playerName nvarchar(50))
                INSERT INTO #rcs_players
                SELECT DISTINCT playerTag, playerName FROM rcs_members""")
            cursor.execute("""SELECT b.playerName, CASE WHEN (a.currentPoints - a.startingPoints) > {} THEN {}
                ELSE (a.currentPoints - a.startingPoints) END AS points
                FROM rcs_clanGames a LEFT JOIN #rcs_players b ON a.playerTag = b.playerTag
                WHERE eventId = (SELECT MAX(eventId) FROM rcs_events WHERE eventType = 5) AND a.clanTag = '{}'
                ORDER BY points DESC""".format(player_points, player_points, clan_tag))
            fetched = cursor.fetchall()
            cursor.callproc('rcs_spClanGamesAverage')
            for clan in cursor:
                if clan_name.lower() == clan['clanName'].lower():
                    clan_average = clan['clanAverage']
                    break
            conn.close()
            clan_total = 0
            for member in fetched:
                clan_total += member['points']
                if member['points'] >= player_points:
                    member_list.append({'name': member['playerName'] + ' *', 'gamePoints': member['points']})
                else:
                    member_list.append({'name': member['playerName'], 'gamePoints': member['points']})
            content = '```' + clan_name + ' (#' + clan_tag.upper() + ')'
            content += '\n{0:20}{1:>12}'.format('Clan Total: ', str(clan_total))
            content += '\n{0:20}{1:>12}'.format('Clan Average: ', str(clan_average))
            content += '\n{0:20}{1:>12}'.format('Name', 'Game Points')
            content += '\n--------------------------------'
            for item in member_list:
                content += '\n{0:20}{1:12}'.format(item['name'], item['gamePoints'])
            content += '```'
            bot_log(ctx.command, arg, ctx.author, ctx.guild)
            await ctx.send(content)


def get_clan_name(clan_tag):
    for clan in clans:
        if clan['clanTag'].lower() == clan_tag.lower():
            return clan['clanName']
    return 'x'


def get_clan_tag(clan_name):
    for clan in clans:
        if clan['clanName'].lower() == clan_name.lower():
            return clan['clanTag']
    return 'x'


def resolve_clan_tag(tag_input):
    if tag_input.startswith('#'):
        clan_tag = tag_input[1:]
        clan_name = get_clan_name(clan_tag)
    else:
        clan_tag = get_clan_tag(tag_input)
        clan_name = tag_input
        if clan_tag == 'x':
            clan_name = get_clan_name(tag_input)
            clan_tag = tag_input
            if clan_name == 'x':
                return 'x', 'x'
    return clan_tag, clan_name


def split_string(string, prepend="", append=""):
    message_limit = 2000
    if len(string) <= 2000:
        return [string]
    else:
        sets = (len(string) // message_limit) + 1
        content = []
        while sets > 1:
            split_index = string.rfind("\n", 0, message_limit-len(prepend)-len(append))
            content.append(string[:split_index] + append)
            string = prepend + string[split_index:]
            sets -= 1
        content.append(string)
        return content


mainConn = pymssql.connect(settings['database']['server'], 
                           settings['database']['username'], 
                           settings['database']['password'], 
                           settings['database']['database'])
mainCursor = mainConn.cursor(as_dict=True)
mainCursor.execute('SELECT clanName, clanTag FROM rcs_data ORDER BY clanName')
clans = mainCursor.fetchall()
mainConn.close()


def setup(bot):
    bot.add_cog(Games(bot))
