import pymssql
import time
import discord
from discord.ext import commands
from datetime import datetime
from config import settings, color_pick

"""Cog for trophy push"""


class Push(commands.Cog):
    """Cog for RCS trophy push"""
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="zpush", hidden=True)
    async def zpush(self, ctx, arg: str = "all"):
        await ctx.send("The RCS Summer 2019 Trophy Push begins at 6pm ET.  Please check back then to all the latest "
                       "scores!")

    @commands.command(name="push", hidden=True)
    async def push(self, ctx, *, arg: str = "all"):
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
        if arg == "help":
            embed = discord.Embed(title="rcs-bot Help File",
                                  description="All commands must begin with a ++\n"
                                              "References to a clan can be in the form of the clan name "
                                              "(spelled correctly) or the clan tag (with or without the #).",
                                  color=color_pick(15, 250, 15))
            help_text = ("Responds with the Trophy Push information for the category specified."
                         "\n  - <all (or no category)> responds with all RCS clans and their current Trophy Push score."
                         "\n  - <TH#> responds with all players of the town hall level specified and their scores."
                         "\n  - <clan name or tag> responds with all players in the clan specified and their scores."
                         "\n  - <top> responds with the top ten players for each town hall level and their scores."
                         "\n  - <gain> responds with the top 25 players in trophies gained.")
            embed.add_field(name="++push <category or clan name/tag>", value=help_text)
            await ctx.send(embed=embed)
            return
        if arg == "end":
            now = datetime.now()
            end_time = datetime(2019, 6, 24, 5, 0)
            delta = end_time - now
            embed = discord.Embed(title="Push Information", color=discord.Color.green())
            embed.add_field(name="Push End", value="24 June 2019, 1am ET")
            embed.add_field(name="Time Left", value=str(delta))
            embed.set_thumbnail(url="http://www.mayodev.com/images/clock.png")
            await ctx.send(embed=embed)
            return
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
            content = "RCS Trophy Push - Standings\n{0:20}{1:>12}".format("Clan Name", "Point Total")
            content += "\n--------------------------------"
            for item in msg_list:
                content += "\n{0:20}{1:>12}".format(item['clan'], item['points'])
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
        elif arg in ("diff", "diffs", "dif", "difs", "difference", "differential"):
            cursor.execute("SELECT clanName, SUM(clanPoints) AS totals FROM rcspush_vwClanPointsTop30 "
                           "GROUP BY clanName "
                           "ORDER BY totals DESC")
            fetched = cursor.fetchall()
            conn.close()
            msg_list = []
            for row in fetched:
                msg_list.append({"clan": row['clanName'],
                                 "points": row['totals']})

            content = "RCS Trophy Push - Standings\n{0:20}{1:>12}".format("Clan Name", "Point Diffs")
            content += "\n--------------------------------"
            iter_list = iter(msg_list)
            item = next(iter_list)
            top_score = item['points']
            content += "\n{0:20}{1:>12}".format(item['clan'], str(item['points'])[:7])
            for item in iter_list:
                content += "\n{0:20}{1:>12}".format(item['clan'], "-" + str(top_score - item['points'])[:6])
        elif arg[:2].lower() == "th" and arg[2].isdigit():
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
                if row['clanName'][:7] == 'Reddit ':
                    clan_name = row['clanName'][7:]
                else:
                    clan_name = row['clanName']
                msg_list.append({"name": f"{row['playerName']} ({clan_name})",
                                 "points": f"{str(row['clanPoints'])[:5]} ({str(row['currentTrophies'])})"})
            content = "RCS Trophy Push - {0:4}".format(arg.upper())
            content += "\n{0:25}{1:>17}".format("Player (Clan)", "Points (Trophies)")
            content += "\n------------------------------------------"
            for item in msg_list:
                content += "\n{0:30}{1:>12}".format(item['name'], item['points'])
        elif arg in ("gains", "gain", "increase"):
            cursor.execute("SELECT * FROM rcspush_vwGains ORDER BY trophyGain DESC")
            fetched = cursor.fetchall()
            conn.close()
            content = "RCS Trophy Push - Trophy Gains"
            content += "\n{0:25}{1:>17}".format("Player (Clan)", "Trophies Gained")
            content += "\n------------------------------------------"
            for row in fetched:
                content += f"\n{row['player']:30}{row['trophyGain']:>12}"
        else:
            # By clan
            clan_tag, clan_name = resolve_clan_tag(arg)
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

    @commands.command(name="xpush", hidden=True)
    @commands.is_owner()
    async def xpush(self, ctx, cmd: str):
        if cmd in ["begin", "start", "add"]:
            await ctx.send("Starting process...")
            # start push
            start = time.perf_counter()
            # conn = self.bot.db.pool
            conn = pymssql.connect(server=settings['database']['server'],
                                   user=settings['database']['username'],
                                   password=settings['database']['password'],
                                   database=settings['database']['database'])
            conn.autocommit(True)
            cursor = conn.cursor(as_dict=True)
            sql = (f"SELECT clanTag FROM rcs_data "
                   f"WHERE clanTag <> '888GPQ0J'")
            cursor.execute(sql)
            push_clans = cursor.fetchall()
            push_clans.append({"clanTag": "29Q9809"})
            push_clans.append({"clanTag": "90CLYP88"})
            print(push_clans)
            for clan in push_clans:
                self.bot.logger.info(f"Starting {clan['clanTag']}")
                coc_clan = await self.bot.coc_client.get_clan(f"#{clan['clanTag']}")
                self.bot.logger.info(f" - {coc_clan.name}")
                async for player in coc_clan.get_detailed_members():
                    pname = player.name.replace("'", "''")
                    cname = player.clan.name.replace("'", "''")
                    sql = (f"INSERT INTO rcspush_2019_1 "
                           f"(playerTag, clanTag, startingTrophies, currentTrophies, "
                           f"bestTrophies, thLevel, playerName, clanName) "
                           f"VALUES ('{player.tag[1:]}', '{player.clan.tag[1:]}', {player.trophies}, "
                           f"{player.trophies}, {player.best_trophies}, {player.town_hall}, "
                           f"'{pname}', '{cname}')")
                    cursor.execute(sql)
            conn.close()
            print(time.perf_counter() - start)
            await ctx.send(f"All members added. Elapsed time: {(time.perf_counter() - start)/60:.2f} minutes")
        else:
            await ctx.send(f"{cmd} is not a valid command for ++xpush.")

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
            if block:
                await channel.send(f"```{coll}```")
            else:
                await channel.send(coll)


def get_clan_name(clan_tag):
    for clan in clans:
        if clan['clanTag'].lower() == clan_tag.lower():
            return clan['clanName']
    return "x"


def get_clan_tag(clan_name):
    for clan in clans:
        if clan['clanName'].lower() == clan_name.lower():
            return clan['clanTag']
    return "x"


def resolve_clan_tag(input):
    if input.startswith("#"):
        clan_tag = input[1:]
        clan_name = get_clan_name(clan_tag)
    else:
        clan_tag = get_clan_tag(input)
        clan_name = input
        if clan_tag == "x":
            clan_name = get_clan_name(input)
            clan_tag = input
            if clan_name == "x":
                return "x", "x"
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
