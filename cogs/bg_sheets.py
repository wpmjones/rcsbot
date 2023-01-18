import gspread
import asyncio

from config import settings
from datetime import datetime
from nextcord.ext import commands, tasks
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from oauth2client import file, client, tools

# Connect to Google Drive
scope = "https://www.googleapis.com/auth/drive"
store = file.Storage("archive_token.json")
creds = store.get()
if not creds or creds.invalid:
    flow = client.flow_from_clientsecrets("archive.json", scope)
    creds = tools.run_flow(flow, store)
service = build("docs", "v1", credentials=creds)
drive_service = build("drive", "v3", credentials=creds)

# Connect to Google Sheets using gspread
gc = gspread.service_account(filename="service_account.json")
comm_log_ss = gc.open_by_key(settings['google']['comm_log_id'])
pre_ss = gc.open_by_key(settings['google']['pre_id'])
post_ss = gc.open_by_key(settings['google']['post_id'])
scout_ss = gc.open_by_key(settings['google']['scout_id'])


def last_row(sheet) -> int:
    str_list = list(filter(None, sheet.col_values(1)))
    return len(str_list)


def row_to_dict_clan(row):
    clan = {
        "apply_date": row[0],
        "name": row[1],
        "tag": row[2],
        "leader": row[3],
        "leader_discord": row[4],
        "members": row[5],
        "discord": row[6],
        "timezone": row[7],
        "war_freq": row[8],
        "cos": f"https://www.clashofstats.com/clans/{row[1].replace(' ', '-').lower()}-{row[2][1:].lower()}",
        "ingame_link": f"https://link.clashofclans.com/?action=OpenClanProfile&tag=%23{row[2][1:].lower()}"
    }
    return clan

def row_to_dict_pre(row):
    response = {
        "survey_date": row[0],
        "age": row[1],
        "check_freq": row[2],
        "history": row[3],
        "alt_contact": row[4],
        "comm_freq": row[5],
        "rcs_events": row[6],
        "absence": row[7],
        "comm_agree": row[8],
        "feeder": row[9],
        "improve": row[10],
        "other_system": row[11],
        "resistance": row[12],
        "heard_about_us": row[13],
        "leader_agree": row[14],
        "clan_name": row[15],
        "leader_name": row[16],
        "reqs": row[17],
        "unique": row[18],
        "accomplish": row[19],
        "online_presence": row[20],
        "time_zone": row[21],
        "war_freq": row[22]
    }
    return response


class BgSheets(commands.Cog):
    """Cog for background tasks. No real commands here."""
    def __init__(self, bot):
        self.bot = bot
        self.check_sheets.start()
        self.fetch_changes.start()

    def cog_unload(self) -> None:
        self.check_sheets.cancel()
        self.fetch_changes.cancel()

    @tasks.loop(hours=1.0)
    async def fetch_changes(self):
        await asyncio.sleep(30)
        conn = self.bot.pool
        sql_check = "SELECT reported FROM rcs_reports WHERE google_key = $1"
        sql_insert = "INSERT INTO rcs_reports (google_key) VALUES ($1)"
        guild = self.bot.get_guild(settings['discord']['rcsguild_id'])
        with open("drive_token.txt", "r") as f:
            page_token = int(f.readline())
        while page_token is not None:
            response = drive_service.changes().list(pageToken=page_token, spaces="drive").execute()
            for change in response.get("changes"):
                # check to see if this is a sheet or a doc
                try:
                    is_sheet = gc.open_by_key(change.get("fileId"))
                except gspread.exceptions.APIError:
                    # If we get here, it should be a Google Doc and we can do something with it
                    key = change.get("fileId")
                    reported = await conn.fetchval(sql_check, key)
                    if reported:
                        continue
                    try:
                        doc = drive_service.files().get(fileId=key).execute()
                    except HttpError:
                        continue
                    doc_link = f"https://docs.google.com/document/d/{key}/edit"
                    title = doc['name'].lower()
                    self.bot.logger.info(f"Evaluating {title}")
                    if "application" in title and "scout" not in title:
                        # This is a verification application
                        self.bot.logger.info("Verification")
                        clan_name = title[:-12].strip()
                        channel_name = f"{clan_name.replace(' ', '-').lower()}-notes"
                        self.bot.logger.info(channel_name)
                        for channel in guild.channels:
                            if channel.name == channel_name:
                                content = (f"We have received the pre-scout survey for {clan_name.title()}.\n"
                                           f"<{doc_link}>")
                                await channel.send(content)
                                await conn.execute(sql_insert, key)
                    elif "post-survey" in title:
                        # This is the post scout survey from the clan leader
                        self.bot.logger.info("Post Survey")
                        end = title.find(" post")
                        clan_name = title[:end].strip()
                        channel_name = f"{clan_name.replace(' ', '-').lower()}-notes"
                        self.bot.logger.info(channel_name)
                        for channel in guild.channels:
                            if channel.name == channel_name:
                                content = (f"We have receive the post-scout survey for {clan_name.title()}.\n"
                                           f"<{doc_link}>")
                                await channel.send(content)
                                await conn.execute(sql_insert, key)
                    elif "post scout report" in title:
                        # This is a scouting report
                        self.bot.logger.info("Scouting Report")
                        end = title.find(" post")
                        start = title.find("-") + 2
                        clan_name = title[:end].strip()
                        scout_name = title[start:]
                        channel_name = f"{clan_name.replace(' ', '-').lower()}-notes"
                        self.bot.logger.info(channel_name)
                        for channel in guild.channels:
                            if channel.name == channel_name:
                                content = f"{clan_name.title()} scouting report by {scout_name.title()}: <{doc_link}>"
                                await channel.send(content)
                                await conn.execute(sql_insert, key)
            if "newStartPageToken" in response:
                # Last page, save this token for the next polling interval
                with open("drive_token.txt", "w") as f:
                    f.write(response.get('newStartPageToken'))
            page_token = response.get('nextPageToken')

    @fetch_changes.before_loop
    async def before_fetch_changes(self):
        await self.bot.wait_until_ready()

    @tasks.loop(hours=1.0)
    async def check_sheets(self):
        """Check RCS sheets for new rows"""
        await asyncio.sleep(30)

        NEW_THREAD_ANNOUNCE = ("{clan} has applied to become a verified RCS clan.\nClash of Stats link: {cos}\n"
                               "Please send a Pre-Scout Survey and invite the leader to {channel}.")

        now = datetime.utcnow().strftime("%d %B %Y, %H:%M:%S")
        guild = self.bot.get_guild(settings['discord']['rcsguild_id'])
        category = guild.get_channel(settings['rcs_channels']['veri_category'])
        # Check for new applications
        with open("app.txt", "r") as f:
            prev_last_row = int(f.readline())
        sheet = comm_log_ss.worksheet("Verification")
        new_last_row = last_row(sheet)
        if new_last_row > prev_last_row:
            # we have new content!
            c = prev_last_row
            rows = sheet.get_all_values()
            while c < new_last_row:
                # process new row
                topic = "This channel will be where we discuss information regarding verification."
                clan = row_to_dict_clan(rows[c])
                clan_channel = await guild.create_text_channel(clan['name'].replace(" ", "-"),
                                                               topic=topic,
                                                               category=category)
                thread_name = f"{clan['name'].replace(' ', '-')}-notes"
                self.bot.logger.info(f"Attempting to create thread - {thread_name}")
                thread = await clan_channel.create_thread(thread_name)
                coc_clan = await self.bot.coc.get_clan(clan['tag'])
                cos_link = f"https://www.clashofstats.com/clans/{coc_clan.tag[1:]}"
                await thread.send(NEW_THREAD_ANNOUNCE.format(clan=f"{coc_clan.name} ({coc_clan.tag})",
                                                             cos=cos_link,
                                                             channel=clan_channel.mention))
                cos = 0
                elder = 0
                badgeless = 0
                for member in coc_clan.members:
                    if str(member.role) == "Co-Leader":
                        cos += 1
                    if str(member.role) == "Elder":
                        elder += 1
                    if member.league.name == "Unranked":
                        badgeless += 1
                content = (f"{clan['name']} ({clan['tag']}) has applied to become a verified RCS clan.\n"
                           f"Clash of Stats link: <{clan['cos']}>\n"
                           f"Please send Pre-scout Survey and invite {clan['leader']} ({clan['leader_discord']}) to "
                           f"{clan_channel.mention}\nLeader timezone: {clan['timezone']}\n"
                           f"War times: {clan['war_freq']}\n"
                           f"Public war log? {coc_clan.public_war_log}\n\n"
                           f"Clan Tag: {clan['tag']}\n\n"
                           f"In-game link: <{clan['ingame_link']}>\n"
                           f"Discord server invite: {clan['discord']}\n\n"
                           f"Co-Leaders: {cos}\n"
                           f"Elders: {elder}\n"
                           f"Unranked: {badgeless}")
                await thread.send(content)
                c += 1
            with open("app.txt", "w") as f:
                f.write(str(c))
            # TODO Can we add buttons or something to bring in the leader?
        # Check for new pre-scout surveys
        with open("pre.txt", "r") as f:
            prev_last_row = int(f.readline())
        sheet = pre_ss.worksheet("App Responses")
        new_last_row = last_row(sheet)
        if new_last_row > prev_last_row:
            c = prev_last_row
            rows = sheet.get_all_values()
            while c < new_last_row:
                # process new row
                response = row_to_dict_pre(rows[c])
                content = (f"**Pre-Scout Survey** completed by {response['leader_name']} ({response['clan_name']})\n\n"
                           f"**What is your age and occupation (if applicable)?**\n"
                           f"{response['age']}\n\n"
                           f"**How often can you check your Reddit messages, and how often do you plan to peruse "
                           f"the CoC subreddit posts?**\n"
                           f"{response['check_freq']}\n\n")
        await channel.send(f"Last pre-scout row was {prev_last_row}. Current row is {new_last_row}.")
        # Check for new post-scout surveys
        with open("post.txt", "r") as f:
            prev_last_row = int(f.readline())
        sheet = post_ss.worksheet("Form Responses")
        new_last_row = last_row(sheet)
        await channel.send(f"Last post-scout row was {prev_last_row}. Current row is {new_last_row}.")
        # Check for new scout reports
        with open("scout.txt", "r") as f:
            prev_last_row = int(f.readline())
        sheet = scout_ss.worksheet("Form Responses")
        new_last_row = last_row(sheet)
        await channel.send(f"Last scout survey row was {prev_last_row}. Current row is {new_last_row}.")

    @check_sheets.before_loop
    async def before_check_sheets(self):
        await self.bot.wait_until_ready()


def setup(bot):
    bot.add_cog(BgSheets(bot))
