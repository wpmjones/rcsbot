import discord, pymssql
from discord.ext import commands
from datetime import datetime
from config import settings

'''Cog for trophy push'''

class Games:
  '''Cog for Clan Games'''
  def __init__(self, bot):
    self.bot = bot

  @commands.command()
  async def games(self, ctx, *, arg: str = 'all'):
    '''Clan Games scores (type "++help games" for more information)
      (use "++games all" compare clan totals)
      (use "++games clan name/tag for clan specific scores)
      (use "++games average" to compare clan averages)'''
    conn = pymssql.connect(server=settings['database']['server'], user=settings['database']['username'], password=settings['database']['password'], database=settings['database']['database'])
    conn.autocommit(True)
    cursor = conn.cursor(as_dict=True)
    if arg == 'all':
      clanList = []
      cursor.execute("SELECT TOP 1 playerPoints, clanPoints FROM rcs_events WHERE eventType = 5 ORDER BY eventId DESC")
      row = cursor.fetchone()
      playerPoints = row['playerPoints']
      clanPoints = row['clanPoints']
      cursor.callproc('rcs_spClanGamesTotal')
      for clan in cursor:
        if clan['clanTotal'] >= clanPoints:
          clanList.append({'name':clan['clanName'] + ' *', 'clanTotal':clan['clanTotal']})
        else:
          clanList.append({'name':clan['clanName'], 'clanTotal':clan['clanTotal']})
      conn.close()
      content = '```RCS Clan Games\n{0:20}{1:>12}'.format('Clan Name','Clan Total')
      content += '\n--------------------------------'
      for item in clanList:
        content += '\n{0:20}{1:12}'.format(item['name'],item['clanTotal'])
      content += '```'
      # fix for +2000 characters
      content1, content2 = splitString(content,'```','```')
      botLog(ctx.command,arg,ctx.author,ctx.guild)
      await ctx.send(content1)
      await ctx.send(content2)
    elif arg in ['average','avg','averages']:
      clanList = []
      cursor.callproc('rcs_spClanGamesAverage')
      for clan in cursor:
        clanList.append({'name':clan['clanName'], 'clanAverage':clan['clanAverage']})
      conn.close()
      content = '```RCS Clan Games\n{0:20}{1:>12}'.format('Clan Name','Clan Average')
      content += '\n--------------------------------'
      for item in clanList:
        content += '\n{0:20}{1:12}'.format(item['name'],item['clanAverage'])
      content += '```'
      # fix for +2000 characters
      content1, content2 = splitString(content,'```','```')
      botLog(ctx.command,arg,ctx.author,ctx.guild)
      await ctx.send(content1)
      await ctx.send(content2)
    else:
      clanTag, clanName = resolveClanTag(arg)
      if clanTag == 'x':
        botLog(ctx.command,arg,ctx.author,ctx.guild,1)
        await ctx.send('You have not provided a valid clan name or clan tag.')
        return
      memberList = []
      cursor.execute("SELECT TOP 1 playerPoints, startTime FROM rcs_events WHERE eventType = 5 ORDER BY eventId DESC")
      row = cursor.fetchone()
      playerPoints = row['playerPoints']
      cursor.execute("""CREATE TABLE #rcs_players (playerTag varchar(15), playerName nvarchar(50))
      INSERT INTO #rcs_players
      SELECT DISTINCT playerTag, playerName FROM rcs_members""")
#      SELECT DISTINCT playerTag, playerName FROM rcs_members WHERE timestamp >
#        (SELECT startTime FROM rcs_events WHERE eventId =
#        (SELECT MAX(eventId) FROM rcs_events WHERE eventType = 5))""")
      cursor.execute("""SELECT b.playerName, CASE WHEN (a.currentPoints - a.startingPoints) > {} THEN {} ELSE (a.currentPoints - a.startingPoints) END AS points
      FROM rcs_clanGames a LEFT JOIN #rcs_players b ON a.playerTag = b.playerTag
      WHERE eventId = (SELECT MAX(eventId) FROM rcs_events WHERE eventType = 5) AND a.clanTag = '{}'
      ORDER BY points DESC""".format(playerPoints, playerPoints, clanTag))
      fetched = cursor.fetchall()
      cursor.callproc('rcs_spClanGamesAverage')
      for clan in cursor:
        if clanName.lower() == clan['clanName'].lower():
          clanAverage = clan['clanAverage']
          break
      conn.close()
      clanTotal = 0
      for member in fetched:
        clanTotal += member['points']
        if member['points'] >= playerPoints:
          memberList.append({'name':member['playerName'] + ' *', 'gamePoints':member['points']})
        else:
          memberList.append({'name':member['playerName'], 'gamePoints':member['points']})
      content = '```' + clanName + ' (#' + clanTag.upper() + ')'
      content += '\n{0:20}{1:>12}'.format('Clan Total: ',str(clanTotal))
      content += '\n{0:20}{1:>12}'.format('Clan Average: ',str(clanAverage))
      content += '\n{0:20}{1:>12}'.format('Name','Game Points')
      content += '\n--------------------------------'
      for item in memberList:
        content += '\n{0:20}{1:12}'.format(item['name'],item['gamePoints'])
      content += '```'
      botLog(ctx.command,arg,ctx.author,ctx.guild)
      await ctx.send(content)

def getClanName(clanTag):
  clanName = ''
  for clan in clans:
    if clan['clanTag'].lower() == clanTag.lower():
      return clan['clanName']
  return 'x'

def getClanTag(clanName):
  clanTag = ''
  for clan in clans:
    if clan['clanName'].lower() == clanName.lower():
      return clan['clanTag']
  return 'x'

def resolveClanTag(input):
  if input.startswith('#'):
    clanTag = input[1:]
    clanName = getClanName(clanTag)
  else:
    clanTag = getClanTag(input)
    clanName = input
    if clanTag == 'x':
      clanName = getClanName(input)
      clanTag = input
      if clanName == 'x':
        return 'x','x'
  return clanTag, clanName

def splitString(string, prepend='', append=''):
  messageLimit = 2000
  if len(string) <= 2000:
    return string, 'Thank you for using rcs-bot!'
  else:
    splitIndex = string.rfind('\n',0,messageLimit-len(prepend)-len(append))
    string1 = string[:splitIndex] + append
    string2 = prepend + string[splitIndex:]
    return string1, string2

def botLog(command, request, author, guild, errFlag=0):
  msg = str(datetime.now())[:16] + ' - '
  if errFlag == 0:
    msg += 'Printing {} for {}. Requested by {} for {}.'.format(command, request, author, guild)
  else:
    msg += 'ERROR: User provided an incorrect argument for {}. Argument provided: {}. Requested by {} for {}.'.format(command, request, author, guild)
  print(msg)

mainConn = pymssql.connect(settings['database']['server'], settings['database']['username'], settings['database']['password'], settings['database']['database'])
mainCursor = mainConn.cursor(as_dict=True)
mainCursor.execute('SELECT clanName, clanTag FROM rcs_data ORDER BY clanName')
clans = mainCursor.fetchall()
mainConn.close()

def setup(bot):
  bot.add_cog(Games(bot))
