import discord, pymssql
from discord.ext import commands
from datetime import datetime
from config import settings

"""Cog for trophy push"""


class Push(commands.Cog):
    """Cog for RCS trophy push"""
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='push', hidden=True)
    async def push(self, ctx, *, arg: str = 'all'):
        """Report stats on trophy push.

        [] - List of clans in the push and their current scores
        [TH#] - All players of the specified town hall level
        [clan name | clan tag] - All players in the specified clan
        [top] - Displays the top ten players at each TH level"""
        conn = pymssql.connect(server=settings['database']['server'],
                               user=settings['database']['username'],
                               password=settings['database']['password'],
                               database=settings['database']['database'])
        conn.autocommit(True)
        cursor = conn.cursor(as_dict=True)
        if arg == "all":
            cursor.execute("SELECT clanName, SUM(clanPoints) AS totals FROM rcspush_vwClanPointsTop30 "
                           "GROUP BY clanName "
                           "ORDER BY totals DESC")
            fetched = cursor.fetchall()
            conn.close()
            msg_list = []
            for row in fetched:
                msg_list.append({"clan": row['clanName'],
                                 "points": str(row['totals'])[:7]})
            content = "```RCS Trophy Push - Standings\n{0:20}{1:>12}".format("Clan Name", "Point Total")
            content += "\n--------------------------------"
            for item in msg_list:
                content += "\n{0:20}{1:>12}".format(item['clan'], item['points'])
            content += "```"
        elif arg[:3].lower() == "top":
            th_list = [12, 11, 10, 9, 8, 7]
            for level in th_list:
                cursor.execute(f"SELECT TOP 10 playerName, clanName, clanPoints, currentTrophies "
                               f"FROM rcspush_vwClanPoints "
                               f"WHERE thLevel = {level} "
                               f"ORDER BY clanPoints DESC")
                fetched = cursor.fetchall()
                msg_list = []
                for row in fetched:
                    if row['clanName'][:6] == "Reddit":
                        clan_name = row['clanName'][7:]
                    else:
                        clan_name = row['clanName']
                    msg_list.append({"name": f"{row['playerName']} ({clan_name})",
                                     "points": f"{str(row['clanPoints'])[:5]} ({str(row['currentTrophies'])})"})
                    content = f"```RCS Trophy Push - Top TH{str(level)}"
                    content += "\n{0:25}{1:>17}".format("Player Name (clan)", "Points (Trophies)")
                    content += "\n------------------------------------------"
                    for item in msg_list:
                        content += "\n{0:30}{1:>12}".format(item['name'], item['points'])
                    content += "```"
                await ctx.send(content)
            conn.close()
            return
        elif arg[:2].lower() == "th":
            th_level = int(arg[2:])
            if (th_level > 12) or (th_level< 6):
                bot_log(ctx.command, arg, ctx.author, ctx.guild, 1)
                await ctx.send("You have not provided a valid town hall level.")
                return
            cursor.execute(f"SELECT TOP 80 playerName, clanName, clanPoints, currentTrophies "
                           f"FROM rcspush_vwClanPoints "
                           f"WHERE thLevel = {th_level} "
                           f"ORDER BY clanPoints DESC")
            fetched = cursor.fetchall()
            conn.close()
            msg_list = []
            for row in fetched:
                if row['clanName'][:6] == 'Reddit':
                    clan_name = row['clanName'][7:]
                else:
                    clan_name = row['clanName']
                msg_list.append({"name": f"{row['playerName']} ({clan_name})",
                                 "points": f"{str(row['clanPoints'])[:5]} ({str(row['currentTrophies'])})"})
            content = "```RCS Trophy Push - {0:4}".format(arg.upper())
            content += "\n{0:25}{1:>17}".format("Player (Clan)", "Points (Trophies)")
            content += "\n------------------------------------------"
            for item in msg_list:
                content += "\n{0:30}{1:>12}".format(item['name'], item['points'])
            content += "```"
        else:
            # By clan
            clan_tag, clan_name = resolveClanTag(arg)
            if clan_tag == "x":
                bot_log(ctx.command, arg, ctx.author, ctx.guild, 1)
                await ctx.send("You have not provided a valid clan name or clan tag.")
                return
            cursor.execute(f"SELECT playerName, thLevel, clanPoints FROM rcspush_vwClanPoints "
                           f"WHERE clanName = '{clan_name}' "
                           f"ORDER BY clanPoints DESC")
            fetched = cursor.fetchall()
            conn.close()
            msg_list = []
            for row in fetched:
                msg_list.append({"name": f"{row['playerName']} (TH{str(row['thLevel'])})",
                                 "points": f"{str(row['clanPoints'])[:5]}"})
            content = "RCS Trophy Push\n{0:23}{1:>12}".format(clan_name, "Push Points")
            content += "\n-----------------------------------"
            for item in msg_list:
                content += "\n{0:23}{1:>12}".format(item['name'], item['points'])
        await self.send_text(ctx.channel, content, 1)

    async def send_text(self, channel, text, block=None):
        """ Sends text ot channel, splitting if necessary """
        if len(text) < 2000:
            if block:
                await channel.send(f"```{text}```")
            else:
                await channel.send(text)
        else:
            coll = ""
            for line in text.splitlines(keepends=True):
                if len(coll) + len(line) > 1994:
                    # if collecting is going to be too long, send  what you have so far
                    if block:
                        await channel.send(f"```{coll}```")
                    else:
                        await channel.send(coll)
                    coll = ""
                coll += line
            await channel.send(coll)


def getClanName(clan_tag):
    for clan in clans:
        if clan['clanTag'].lower() == clan_tag.lower():
            return clan['clanName']
    return "x"


def getClanTag(clan_name):
    for clan in clans:
        if clan['clanName'].lower() == clan_name.lower():
            return clan['clanTag']
    return "x"


def resolveClanTag(input):
    if input.startswith("#"):
        clan_tag = input[1:]
        clan_name = getClanName(clan_tag)
    else:
        clan_tag = getClanTag(input)
        clan_name = input
        if clan_tag == "x":
            clan_name = getClanName(input)
            clan_tag = input
            if clan_name == "x":
                return "x","x"
    return clan_tag, clan_name


def bot_log(command, request, author, guild, err_flag=0):
    msg = str(datetime.now())[:16] + ' - '
    if err_flag == 0:
        msg += f"Printing {command} for {request}. Requested by {author} for {guild}."
    else:
        msg += (f"ERROR: User provided an incorrect argument for {command}. Argument provided: {request}. "
                f"Requested by {author}.")
    print(msg)


mainConn = pymssql.connect(settings['database']['server'],
                           settings['database']['username'],
                           settings['database']['password'],
                           settings['database']['database'])
mainCursor = mainConn.cursor(as_dict=True)
mainCursor.execute('SELECT clanName, clanTag FROM rcs_data ORDER BY clanName')
clans = mainCursor.fetchall()
mainConn.close()


def setup(bot):
    bot.add_cog(Push(bot))
