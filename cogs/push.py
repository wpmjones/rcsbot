import discord, pymssql
from discord.ext import commands
from datetime import datetime
from config import settings

'''Cog for trophy push'''


class Push(commands.Cog):
  '''Cog for RCS trophy push'''
  def __init__(self, bot):
    self.bot = bot

  @commands.command(name='push', hidden=True)
  async def push(self, ctx, *, arg: str = 'all'):
    '''Report stats on trophy push.

    [] - List of clans in the push and their current scores
    [TH#] - All players of the specified town hall level
    [clan name | clan tag] - All players in the specified clan
    [top] - Displays the top ten players at each TH level'''
    conn = pymssql.connect(server=settings['database']['server'], user=settings['database']['username'], password=settings['database']['password'], database=settings['database']['database'])
    conn.autocommit(True)
    cursor = conn.cursor(as_dict=True)
    if arg == 'all':
      cursor.execute("""SELECT clanName, SUM(clanPoints) AS totals FROM rcspush_vwClanPointsTop30
      GROUP BY clanName
      ORDER BY totals DESC""")
      fetched = cursor.fetchall()
      conn.close()
      msgList = []
      for row in fetched:
        msgList.append({'clan':row['clanName'],'points':str(row['totals'])[:7]})
      content = '```RCS Trophy Push - Standings\n{0:20}{1:>12}'.format('Clan Name','Point Total')
      content += '\n--------------------------------'
      for item in msgList:
        content += '\n{0:20}{1:>12}'.format(item['clan'],item['points'])
      content += '```'
    elif arg[:3].lower() == 'top':
      thList = [12,11,10,9,8,7]
      for level in thList:
        cursor.execute("""SELECT TOP 10 playerName, clanName, clanPoints, currentTrophies
        FROM rcspush_vwClanPoints
        WHERE thLevel = {}
        ORDER BY clanPoints DESC""".format(level))
        fetched = cursor.fetchall()
        msgList = []
        for row in fetched:
          if row['clanName'][:6] == 'Reddit':
            clanName = row['clanName'][7:]
          else:
            clanName = row['clanName']
          msgList.append({'name':row['playerName'] + ' (' + clanName + ')','points':str(row['clanPoints'])[:5] + ' (' + str(row['currentTrophies']) + ')'})
          content = '```RCS Trophy Push - Top TH' + str(level)
          content += '\n{0:25}{1:>17}'.format('Player Name (clan)','Points (Trophies)')
          content += '\n------------------------------------------'
          for item in msgList:
            content += '\n{0:30}{1:>12}'.format(item['name'],item['points'])
          content += '```'
        await ctx.send(content)
      conn.close()
      return
    elif arg[:2].lower() == 'th':
      thLevel = int(arg[2:])
      if (thLevel > 12) or (thLevel< 6):
        botLog(ctx.command,arg,ctx.author,ctx.guild,1)
        await ctx.send('You have not provided a valid town hall level.')
        return
      cursor.execute("SELECT TOP 80 playerName, clanName, clanPoints, currentTrophies FROM rcspush_vwClanPoints WHERE thLevel = {} ORDER BY clanPoints DESC".format(thLevel))
      fetched = cursor.fetchall()
      conn.close()
      msgList = []
      for row in fetched:
        if row['clanName'][:6] == 'Reddit':
          clanName = row['clanName'][7:]
        else:
          clanName = row['clanName']
        msgList.append({'name':row['playerName'] + ' (' + clanName + ')','points':str(row['clanPoints'])[:5] + ' (' + str(row['currentTrophies']) + ')'})
      content = '```RCS Trophy Push - {0:4}'.format(arg.upper())
      content += '\n{0:25}{1:>17}'.format('Player (Clan)','Points (Trophies)')
      content += '\n------------------------------------------'
      for item in msgList:
        content += '\n{0:30}{1:>12}'.format(item['name'],item['points'])
      content += '```'
    else:
      # By clan
      clanTag, clanName = resolveClanTag(arg)
      if clanTag == 'x':
        botLog(ctx.command,arg,ctx.author,ctx.guild,1)
        await ctx.send('You have not provided a valid clan name or clan tag.')
        return
      cursor.execute("""SELECT playerName, thLevel, clanPoints FROM rcspush_vwClanPoints
      WHERE clanName = '{}'
      ORDER BY clanPoints DESC""".format(clanName))
      fetched = cursor.fetchall()
      conn.close()
      msgList = []
      for row in fetched:
        msgList.append({'name':row['playerName'] + ' (TH' + str(row['thLevel']) + ')','points':str(row['clanPoints'])[:5]})
      content = '```RCS Trophy Push\n{0:23}{1:>12}'.format(clanName,'Push Points')
      content += '\n-----------------------------------'
      for item in msgList:
        content += '\n{0:23}{1:>12}'.format(item['name'],item['points'])
      content += '```'
    # fix for +2000 characters
    content1, content2 = splitString(content,'```','```')
    botLog(ctx.command,arg,ctx.author,ctx.guild)
    await ctx.send(content1)
    await ctx.send(content2)

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
  if len(string) > 4000:
    print('String is longer than 4k')
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
    msg += 'ERROR: User provided an incorrect argument for {}. Argument provided: {}. Requested by {}.'.format(command, request, author)
  print(msg)

mainConn = pymssql.connect(settings['database']['server'], settings['database']['username'], settings['database']['password'], settings['database']['database'])
mainCursor = mainConn.cursor(as_dict=True)
mainCursor.execute('SELECT clanName, clanTag FROM rcs_data ORDER BY clanName')
clans = mainCursor.fetchall()
mainConn.close()

def setup(bot):
  bot.add_cog(Push(bot))
