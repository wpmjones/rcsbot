import discord
import pymssql
import coc
from discord.ext import commands
from datetime import datetime
from config import settings, emojis

class General:
  """Cog for General bot commands"""
  def __init__(self, bot):
    self.bot = bot

  @commands.command(name="attacks", aliases=["att", "attack", "attackwin", "attackwins"])
  async def attacks(self, ctx, *, arg: str = "x"):
    """Attack wins for the whole clan"""
    conn = pymssql.connect(server=settings['database']['server'], user=settings['database']['username'],
                           password=settings['database']['password'], database=settings['database']['database'])
    cursor = conn.cursor(as_dict=True)
    clanTag, clanName = resolveClanTag(arg)
    if clanTag == "x":
      botLog(ctx.command, arg, ctx.author, ctx.guild, 1)
      await ctx.send("You have not provided a valid clan name or clan tag.")
      return
    memberList = []
    cursor.execute(f"SELECT playerName, attackWins, timestamp FROM rcs_members WHERE clanTag = '{clanTag}' AND timestamp = (SELECT TOP 1 timestamp from rcs_members WHERE clanTag = '{clanTag}' ORDER BY timestamp DESC) ORDER BY attackWins DESC")
    fetched = cursor.fetchall()
    conn.close()
    for member in fetched:
      memberList.append({"name": member['playerName'], "attacks": member['attackWins']})
    content = f"```{clanName} (#{clanTag.upper()})\n{'Name':<20}{'Attack Wins':>12}"
    content += '\n--------------------------------'
    for item in memberList:
      content += '\n{0:20}{1:12}'.format(item['name'],item['attacks'])
    content += '\n--------------------------------'
    content += f"\nData from: {fetched[0]['timestamp'].strftime('%-d %b %Y')}```"
    botLog(ctx.command,arg,ctx.author,ctx.guild)
    await ctx.send(content)

  @commands.command(name='defenses', aliases=['defences','def','defense','defence','defends','defend','defensewins','defencewins'])
  async def defenses(self, ctx, *, arg: str = 'x'):
    '''Defense wins for the whole clan'''
    conn = pymssql.connect(settings['database']['server'], settings['database']['username'], settings['database']['password'], settings['database']['database'])
    cursor = conn.cursor(as_dict=True)
    clanTag, clanName = resolveClanTag(arg)
    if clanTag == 'x':
      botLog(ctx.command,arg,ctx.author, ctx.guild,1)
      await ctx.send('You have not provided a valid clan name or clan tag.')
      return
    memberList = []
    cursor.execute(f"SELECT playerName, defenceWins, timestamp FROM rcs_members WHERE clanTag = '{clanTag}' AND timestamp = (SELECT TOP 1 timestamp from rcs_members WHERE clanTag = '{clanTag}' ORDER BY timestamp DESC) ORDER BY defenceWins DESC")
    fetched = cursor.fetchall()
    conn.close()
    for member in fetched:
      memberList.append({'name':member['playerName'], 'defenses':member['defenceWins']})
    content = '```' + clanName + ' (#' + clanTag.upper() + ')\n' + '{0:20}{1:>12}'.format('Name','Defense Wins')
    content += '\n--------------------------------'
    for item in memberList:
      content += '\n{0:20}{1:12}'.format(item['name'],item['defenses'])
    content += '\n--------------------------------'
    content += f"\nData from: {fetched[0]['timestamp'].strftime('%-d %b %Y')}```"
    botLog(ctx.command,arg,ctx.author,ctx.guild)
    await ctx.send(content)

  @commands.command(name='donations', aliases=['donate','donates','donation'])
  async def donations(self, ctx, *, arg: str = 'x'):
    '''Donations for the whole clan'''
    conn = pymssql.connect(settings['database']['server'], settings['database']['username'], settings['database']['password'], settings['database']['database'])
    cursor = conn.cursor(as_dict=True)
    clanTag, clanName = resolveClanTag(arg)
    if clanTag == 'x':
      botLog(ctx.command,arg,ctx.author,ctx.guild,1)
      await ctx.send('You have not provided a valid clan name or clan tag.')
      return
    memberList = []
    cursor.execute(f"SELECT playerName, donations, donationsReceived, timestamp FROM rcs_members WHERE clanTag = '{clanTag}' AND timestamp = (SELECT TOP 1 timestamp from rcs_members WHERE clanTag = '{clanTag}' ORDER BY timestamp DESC) ORDER BY donations DESC")
    fetched = cursor.fetchall()
    conn.close()
    for member in fetched:
      memberList.append({'name':member['playerName'], 'donations':member['donations'],'received':member['donationsReceived']})
    content = '```' + clanName + ' (#' + clanTag.upper() + ')\n' + '{0:10}{1:>20}'.format('Name','Donations/Received')
    content += '\n------------------------------'
    for item in memberList:
      content += '\n{0:19}{1:>11}'.format(item['name'],str(item['donations']) + '/' + str(item['received']))
    content += '\n--------------------------------'
    content += f"\nData from: {fetched[0]['timestamp'].strftime('%-d %b %Y')}```"
    botLog(ctx.command,arg,ctx.author,ctx.guild)
    await ctx.send(content)

  @commands.command(name='trophies', aliases=['trophy'])
  async def trophies(self, ctx, *, arg: str = 'x'):
    '''Trophy count for the whole clan'''
    conn = pymssql.connect(settings['database']['server'], settings['database']['username'], settings['database']['password'], settings['database']['database'])
    cursor = conn.cursor(as_dict=True)
    clanTag, clanName = resolveClanTag(arg)
    if clanTag == 'x':
      botLog(ctx.command,arg,ctx.author,ctx.guild,1)
      await ctx.send('You have not provided a valid clan name or clan tag.')
      return
    memberList = []
    cursor.execute(f"SELECT playerName, trophies, timestamp FROM rcs_members WHERE clanTag = '{clanTag}' AND timestamp = (SELECT TOP 1 timestamp from rcs_members WHERE clanTag = '{clanTag}' ORDER BY timestamp DESC) ORDER BY trophies DESC")
    fetched = cursor.fetchall()
    conn.close()
    for member in fetched:
      memberList.append({'name':member['playerName'], 'trophies':member['trophies']})
    content = '```' + clanName + ' (#' + clanTag.upper() + ')\n' + '{0:20}{1:>10}'.format('Name','Trophies')
    content += '\n------------------------------'
    for item in memberList:
      content += '\n{0:20}{1:>10}'.format(item['name'],str(item['trophies']))
    content += '\n--------------------------------'
    content += f"\nData from: {fetched[0]['timestamp'].strftime('%-d %b %Y')}```"
    botLog(ctx.command,arg,ctx.author,ctx.guild)
    await ctx.send(content)

  @commands.command(name='besttrophies', aliases=['besttrophy','mosttrophies'])
  async def besttrophies(self, ctx, *, arg: str = 'x'):
    '''Best trophy count for the whole clan'''
    conn = pymssql.connect(settings['database']['server'], settings['database']['username'], settings['database']['password'], settings['database']['database'])
    cursor = conn.cursor(as_dict=True)
    clanTag, clanName = resolveClanTag(arg)
    if clanTag == 'x':
      botLog(ctx.command,arg,ctx.author,ctx.guild,1)
      await ctx.send('You have not provided a valid clan name or clan tag.')
      return
    memberList = []
    cursor.execute(f"SELECT playerName, bestTrophies, timestamp FROM rcs_members WHERE clanTag = '{clanTag}' AND timestamp = (SELECT TOP 1 timestamp from rcs_members WHERE clanTag = '{clanTag}' ORDER BY timestamp DESC) ORDER BY bestTrophies DESC")
    fetched = cursor.fetchall()
    conn.close()
    for member in fetched:
      memberList.append({'name':member['playerName'], 'bestTrophies':member['bestTrophies']})
    content = '```' + clanName + ' (#' + clanTag.upper() + ')\n' + '{0:10}{1:>20}'.format('Name','Best Trophies')
    content += '\n------------------------------'
    for item in memberList:
      content += '\n{0:20}{1:>10}'.format(item['name'],str(item['bestTrophies']))
    content += '\n--------------------------------'
    content += f"\nData from: {fetched[0]['timestamp'].strftime('%-d %b %Y')}```"
    botLog(ctx.command,arg,ctx.author,ctx.guild)
    await ctx.send(content)

  @commands.command(name='townhalls', aliases=['townhall','th'])
  async def townhalls(self, ctx, *, arg: str = 'x'):
    '''List of clan members by town hall level'''
    conn = pymssql.connect(settings['database']['server'], settings['database']['username'], settings['database']['password'], settings['database']['database'])
    cursor = conn.cursor(as_dict=True)
    clanTag, clanName = resolveClanTag(arg)
    if clanTag == 'x':
      botLog(ctx.command,arg,ctx.author,ctx.guild,1)
      await ctx.send('You have not provided a valid clan name or clan tag.')
      return
    memberList = []
    cursor.execute(f"SELECT playerName, thLevel, timestamp FROM rcs_members WHERE clanTag = '{clanTag}' AND timestamp = (SELECT TOP 1 timestamp from rcs_members WHERE clanTag = '{clanTag}' ORDER BY timestamp DESC) ORDER BY thLevel DESC, playerName")
    fetched = cursor.fetchall()
    conn.close()
    gap = emojis['other']['gap']
    for member in fetched:
      th = member['thLevel']
      memberList.append({'name':member['playerName'], 'thLevel':emojis['th'][th]})
    await ctx.send('**' + clanName + '** (#' + clanTag.upper() + ')')
    content = ''
    for item in memberList:
      content += f"\n{item['thLevel']} {gap}{item['name']}"
    content = splitString(content)
    botLog(ctx.command,arg,ctx.author,ctx.guild)
    for string in content:
      await ctx.send(string)

  @commands.command(name='builderhalls', aliases=['builderhall','bh'])
  async def builderhalls(self, ctx, *, arg: str = 'x'):
    '''List of clan members by builder hall level'''
    conn = pymssql.connect(settings['database']['server'], settings['database']['username'], settings['database']['password'], settings['database']['database'])
    cursor = conn.cursor(as_dict=True)
    clanTag, clanName = resolveClanTag(arg)
    if clanTag == 'x':
      botLog(ctx.command,arg,ctx.author,ctx.guild,1)
      await ctx.send('You have not provided a valid clan name or clan tag.')
      return
    memberList = []
    cursor.execute(f"SELECT playerName, builderHallLevel, timestamp FROM rcs_members WHERE clanTag = '{clanTag}' AND timestamp = (SELECT TOP 1 timestamp from rcs_members WHERE clanTag = '{clanTag}' ORDER BY timestamp DESC) ORDER BY builderHallLevel DESC, playerName")
    fetched = cursor.fetchall()
    conn.close()
    gap = emojis['other']['gap']
    for member in fetched:
      bh = member['builderHallLevel']
      memberList.append({'name':member['playerName'], 'bhLevel':emojis['th'][bh]})
    await ctx.send('**' + clanName + '** (#' + clanTag.upper() + ')')
    content = ''
    for item in memberList:
      content += '\n{} {}{}'.format(item['bhLevel'],gap,item['name'])
    content += f"\n```Data from: {fetched[0]['timestamp'].strftime('%-d %b %Y')}```"
    content = splitString(content)
    botLog(ctx.command,arg,ctx.author,ctx.guild)
    for string in content:
      await ctx.send(string)

  @commands.command(name='warstars', aliases=['stars'])
  async def warstars(self, ctx, *, arg: str = 'x'):
    '''List of clan members by war stars earned'''
    conn = pymssql.connect(settings['database']['server'], settings['database']['username'], settings['database']['password'], settings['database']['database'])
    cursor = conn.cursor(as_dict=True)
    clanTag, clanName = resolveClanTag(arg)
    if clanTag == 'x':
      botLog(ctx.command,arg,ctx.author,ctx.guild,1)
      await ctx.send('You have not provided a valid clan name or clan tag.')
      return
    memberList = []
    cursor.execute(f"SELECT playerName, warStars, timestamp FROM rcs_members WHERE clanTag = '{clanTag}' AND timestamp = (SELECT TOP 1 timestamp from rcs_members WHERE clanTag = '{clanTag}' ORDER BY timestamp DESC) ORDER BY warStars DESC")
    fetched = cursor.fetchall()
    conn.close()
    for member in fetched:
      memberList.append({'name':member['playerName'], 'warStars':member['warStars']})
    content = '```' + clanName + ' (#' + clanTag.upper() + ')\n' + '{0:10}{1:>20}'.format('Name','War Stars')
    content += '\n------------------------------'
    for item in memberList:
      content += '\n{0:20}{1:>10}'.format(item['name'],str(item['warStars']))
    content += '```'
    botLog(ctx.command,arg,ctx.author,ctx.guild)
    await ctx.send(content)

  @commands.command(name='top')
  async def top(self, ctx, category: str = 'x'):
    '''Lists top ten (type "++help top" for more information)
    (warstars, attacks, defenses, trophies, donations)'''
    categories = {
      'warstars': 'warStars',
      'attacks': 'attackWins',
      'defenses': 'defenceWins',
      'defences': 'defenceWins',
      'trophies': 'trophies',
      'donations': 'donations',
      'games': 'games'
    }
    conn = pymssql.connect(settings['database']['server'], settings['database']['username'], settings['database']['password'], settings['database']['database'])
    cursor = conn.cursor(as_dict=True)
    if category not in categories:
      botLog(ctx.command,category,ctx.author,ctx.guild,1)
      await ctx.send('You need to provide a valid category.\n(warstars, attacks, defenses, trophies, donations)')
      return
    if category != 'games':
      field = categories[category]
      memberList = []
      cursor.execute(f"SELECT TOP 10 playerName, clanName, {field} FROM rcs_members INNER JOIN rcs_data ON rcs_data.clanTag = rcs_members.clanTag AND timestamp = (SELECT MAX(timestamp) FROM rcs_members WHERE timestamp < (SELECT MAX(timestamp) FROM rcs_members)) ORDER BY {field} DESC")
      fetched = cursor.fetchall()
      for member in fetched:
        memberList.append({'name':member['playerName'], 'clan':member['clanName'], 'amount':member[field]})
      content = '```RCS Top Ten for: ' + category
      content += '\n----------------------------------------'
      for item in memberList:
        content += '\n{0:33}{1:>7}'.format(item['name'] + ' (' + item['clan'] + ')', str(item['amount']))
      content += '```'
      botLog(ctx.command,category,ctx.author,ctx.guild)
      await ctx.send(content)
    else:
      memberList = []
      tempTable = """CREATE TABLE #rcs_players (playerTag varchar(15), playerName nvarchar(50))
      INSERT INTO #rcs_players
      SELECT DISTINCT playerTag, playerName FROM rcs_members"""
      cursor.execute(tempTable)
      cursor.execute("""SELECT TOP 10 b.playerName, c.clanName, (a.currentPoints - a.startingPoints) as points
      FROM rcs_clanGames a
      INNER JOIN #rcs_players b ON b.playerTag = a.playerTag
      INNER JOIN rcs_data c ON c.clanTag = a.clanTag
      WHERE eventId = (SELECT MAX(eventId) FROM rcs_events WHERE eventType = 5)
      ORDER BY points DESC""")
      fetched = cursor.fetchall()
      for member in fetched:
        memberList.append({'name':member['playerName'] + ' (' + member['clanName'] + ')', 'points':member['points']})
      content = '```RCS Top Ten for: Clan Games'
      content += '\n----------------------------------------'
      for item in memberList:
        content += '\n{0:33}{1:>7}'.format(item['name'], str(item['points']))
      content += '```'
      botLog(ctx.command,category,ctx.author,ctx.guild)
      await ctx.send(content)

  @commands.command(name='reddit', aliases=['subreddit'])
  async def reddit(self, ctx, *, arg: str = 'x'):
    '''Return link to specified clan's subreddit'''
    if arg == 'x':
      botLog(ctx.command,'clan missing',ctx.author,ctx.guild,1)
      await ctx.send("You must provide a clan name or tag.")
      return
    clanTag, clanName = resolveClanTag(arg)
    if clanTag == 'x':
      botLog(ctx.command,arg,ctx.author,ctx.guild,1)
      await ctx.send('You have not provided a valid clan name or clan tag.')
      return
    conn = pymssql.connect(settings['database']['server'], settings['database']['username'], settings['database']['password'], settings['database']['database'])
    cursor = conn.cursor(as_dict=True)
    cursor.execute(f"SELECT subReddit FROM rcs_data WHERE clanTag = '{clanTag}'")
    fetched = cursor.fetchone()
    botLog(ctx.command,arg,ctx.author,ctx.guild)
    if fetched['subReddit'] != '':
      await ctx.send(fetched['subReddit'])
    else:
      await ctx.send("This clan does not have a subreddit.")

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

#def splitString(string, prepend='', append=''):
#  messageLimit = 2000
#  if len(string) <= 2000:
#    return string, ''
#  else:
#    splitIndex = string.rfind('\n',0,messageLimit-len(prepend)-len(append))
#    string1 = string[:splitIndex] + append
#    string2 = prepend + string[splitIndex:]
#    return string1, string2

def splitString(string, prepend='', append=''):
  messageLimit = 2000
  if len(string) <= 2000:
    return [string]
  else:
    sets = (len(string) // messageLimit) + 1
    content = []
    while sets > 1:
      splitIndex = string.rfind('\n',0,messageLimit-len(prepend)-len(append))
      content.append(string[:splitIndex] + append)
      string = prepend + string[splitIndex:]
      sets -= 1
    content.append(string)
    return content

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
  bot.add_cog(General(bot))
