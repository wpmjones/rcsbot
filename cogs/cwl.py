import discord, pymssql
from discord.ext import commands
from datetime import datetime
from config import settings

'''Cog for clan war leagues'''

class CWL:
  '''Cog for Clan War League Info'''
  def __init__(self, bot):
    self.bot = bot

  @commands.command(name='cwl', hidden=True)
  async def cwl(self, ctx, *, arg: str = 'all'):
    '''Clan War Leagues
      (use "++cwl all" compare clan total stars)
      (use "++cwl clan name/tag for clan specific scores)
      (use "++cwl average" to compare clan averages per round)'''
    conn = pymssql.connect(server=settings['database']['server'], user=settings['database']['username'], password=settings['database']['password'], database=settings['database']['database'])
    cursor = conn.cursor(as_dict=True)
    if arg == 'all':
      clanList = []
      cursor.callproc('rcs_spCwlStars')
      for clan in cursor:
        clanList.append({'name':clan['clanName'], 'stars':clan['totalStars'], 'round':clan['rounds']})
      conn.close()
      content = '```RCS Clan War League Stars\n{0:19}{1:>5}{2:>8}'.format('Clan Name','Stars','Rounds')
      content += '\n' + '-'*32
      for item in clanList:
        content += '\n{0:20}{1:>4}{2:>8}'.format(item['name'],item['stars'],item['round'])
      content += '```'
      # fix for +2000 characters
      content1, content2 = splitString(content,'```','```')
      botLog(ctx.command,arg,ctx.author)
      await ctx.send(content1)
      await ctx.send(content2)
    elif arg == 'average':
      clanList = []
      cursor.callproc('rcs_spCwlAverage')
      for clan in cursor:
        clanList.append({'name':clan['clanName'], 'stars':clan['avgStars'], 'round':clan['rounds']})
      conn.close()
      content = '```RCS Clan War League Average Stars\n{0:19}{1:>5}{2:>8}'.format('Clan Name','Avg','Rounds')
      content += '\n' + '-'*32
      for item in clanList:
        content += '\n{0:20}{1:>4}{2:>8}'.format(item['name'],item['stars'],item['round'])
      content += '```'
      # fix for +2000 characters
      content1, content2 = splitString(content,'```','```')
      botLog(ctx.command,arg,ctx.author)
      await ctx.send(content1)
      await ctx.send(content2)
    else:
      clanTag, clanName = resolveClanTag(arg)
      if clanTag == 'x':
        botLog(ctx.command,arg,ctx.author,1)
        await ctx.send('You have not provided a valid clan name or clan tag.')
        return
      botLog(ctx.command,arg,ctx.author)
      await ctx.send('Under construction. Check back soon!')

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

def botLog(command, request, author, errFlag=0):
  msg = str(datetime.now())[:16] + ' - '
  if errFlag == 0:
    msg += 'Printing {} for {}. Requested by {}.'.format(command, request, author)
  else:
    msg += 'ERROR: User provided an incorrect argument for {}. Argument provided: {}. Requested by {}.'.format(command, request, author)
  print(msg)

mainConn = pymssql.connect(settings['database']['server'], settings['database']['username'], settings['database']['password'], settings['database']['database'])
mainCursor = mainConn.cursor(as_dict=True)
mainCursor.execute('SELECT clanName, clanTag FROM rcs_data ORDER BY clanName')
clans = mainCursor.fetchall()
mainConn.close()

def setup(bot):
  bot.add_cog(CWL(bot))
