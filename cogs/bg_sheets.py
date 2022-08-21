import discord
import gspread

from config import settings
from datetime import datetime
from discord.ext import commands, tasks
from googleapiclient.discovery import build
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


def row_to_dict(row):
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
        guild = self.bot.get_guild(settings['discord']['prospectguild_id'])
        category = self.bot.get_channel(364153344203423765)
        template_names = ["Post Scout Report", "Application", "Post-Survey"]
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
                    doc = drive_service.files().get(fileId=key).execute()
                    doc_link = f"https://docs.google.com/document/d/{key}/edit"
                    title = doc['name'].lower()
                    if "application" in title and "scout" not in title:
                        # This is a verification application
                        clan_name = title[:-12]
                        channel_name = f"{clan_name.replace(' ', '-').lower()}-notes"
                        for channel in guild.channels:
                            if channel.name == channel_name:
                                content = f"We have received the pre-scout survey for {clan_name}.\n<{doc_link}>"
                                await channel.send(content)
                    elif "post-survey" in title:
                        # This is the post scout survey from the clan leader
                        end = title.find(" Post")
                        clan_name = title[:end]
                        channel_name = f"{clan_name.replace(' ', '-').lower()}-notes"
                        for channel in guild.channels:
                            if channel.name == channel_name:
                                content = f"We have receive the post-scout survey for {clan_name}.\n<{doc_link}>"
                                await channel.send(content)
                    elif "post scout report" in title:
                        # This is a scouting report
                        end = title.find(" Post")
                        start = title.find("-") + 2
                        clan_name = title[:end]
                        scout_name = title[start:]
                        channel_name = f"{clan_name.replace(' ', '-').lower()}-notes"
                        for channel in guild.channels:
                            if channel.name == channel_name:
                                content = f"{clan_name} scouting report by {scout_name}: <{doc_link}>"
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
        now = datetime.utcnow().strftime("%d %B %Y, %H:%M:%S")
        guild = self.bot.get_guild(settings['discord']['prospectguild_id'])
        category = guild.get_channel(364153344203423765)
        council_channel = self.bot.get_channel(settings['rcs_channels']['council'])
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
                clan = row_to_dict(rows[c])
                clan_channel = await guild.create_text_channel(clan['name'].replace(" ", "-"),
                                                               topic=topic,
                                                               category=category)
                notes_channel = await guild.create_text_channel(f"{clan['name'].replace(' ', '-')}-notes",
                                                                topic=topic,
                                                                category=category)
                coc_clan = await self.bot.coc.get_clan(clan['tag'])
                cos = 0
                elder = 0
                badgeless = 0
                for member in coc_clan.members:
                    if str(member.role) == "Co-Leader":
                        cos += 0
                    if str(member.role) == "Elder":
                        elder += 1
                    if member.league == "Unranked":
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
                await notes_channel.send(content)
                content = (f"{clan['name']} ({clan['tag']}) has applied to become a verified RCS clan.\n"
                           f"Clash of Stats link: <{clan['cos']}>\n"
                           f"Leader: {clan['leader']} ({clan['leader_discord']})\n"
                           f"Leader timezone: {clan['timezone']}\n"
                           f"War times: {clan['war_freq']}\n"
                           f"More information is available on the Prspectives Server\n\n"
                           f"In-game link: <{clan['ingame_link']}>\n"
                           f"Discord server invite: {clan['discord']}\n\n")
                await council_channel.send(content)
                c += 1
            with open("app.txt", "w") as f:
                f.write(str(c))
        # Check for new pre-scout surveys
        # with open("pre.txt", "r") as f:
        #     prev_last_row = int(f.readline())
        # sheet = pre_ss.worksheet("App Responses")
        # new_last_row = last_row(sheet)
        # await channel.send(f"Last pre-scout row was {prev_last_row}. Current row is {new_last_row}.")
        # Check for new post-scout surveys
        # with open("post.txt", "r") as f:
        #     prev_last_row = int(f.readline())
        # sheet = post_ss.worksheet("Form Responses")
        # new_last_row = last_row(sheet)
        # await channel.send(f"Last post-scout row was {prev_last_row}. Current row is {new_last_row}.")
        # Check for new scout reports
        # with open("scout.txt", "r") as f:
        #     prev_last_row = int(f.readline())
        # sheet = scout_ss.worksheet("Form Responses")
        # new_last_row = last_row(sheet)
        # await channel.send(f"Last scout survey row was {prev_last_row}. Current row is {new_last_row}.")

    @check_sheets.before_loop
    async def before_check_sheets(self):
        await self.bot.wait_until_ready()


def setup(bot):
    bot.add_cog(BgSheets(bot))
