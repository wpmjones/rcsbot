import discord
import requests
import asyncio
from discord.ext import commands
from config import settings
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

# Connect to Google Sheets
scope = "https://www.googleapis.com/auth/spreadsheets.readonly"
spreadsheet_id = settings['google']['commLogId']
store = file.Storage("token.json")
creds = store.get()
if not creds or creds.invalid:
    flow = client.flow_from_clientsecrets("credentials.json", scope)
    creds = tools.run_flow(flow, store)
service = build("sheets", "v4", http=creds.authorize(Http()), cache_discovery=False)
sheet = service.spreadsheets()


class Contact(commands.Cog):
    """Cog for handling Council Tasks"""
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="tasks", aliases=["task", "tasklist", "list"], hidden=True)
    async def task_list(self, ctx, cmd: str = ""):
        if await self.is_council(ctx.author.id):
            guild = self.bot.get_guild(settings['discord']['rcsGuildId'])
            if cmd.lower() == "all":
                if ctx.channel.id == settings['rcsChannels']['council']:
                    await ctx.send("This is a long list. I'm going to send it to your DM. To view items "
                                   "in the Council Chat, please request them individually (`++tasks suggestions`).")
                # Suggestions
                result = sheet.values().get(spreadsheetId=spreadsheet_id, range="Suggestions!A2:I").execute()
                values = result.get("values", [])
                embed = discord.Embed(title="RCS Council Suggestions", color=discord.Color.blurple())
                flag = 0
                for row in values:
                    if len(row) < 9:
                        embed.add_field(name=f"Suggestion from {row[1]}\n{row[7]}",
                                        value=f"{row[3][:500]}\nDated {row[0]}",
                                        inline=False)
                embed.set_footer(text="Use ++done <Task ID> to complete a task")
                if len(embed.fields) > 0:
                    flag = 1
                    await ctx.author.send(embed=embed)
                # Council Nominations
                result = sheet.values().get(spreadsheetId=spreadsheet_id, range="Council!A2:J").execute()
                values = result.get("values", [])
                embed = discord.Embed(title="RCS Council Nominations", color=discord.Color.dark_gold())
                for row in values:
                    if row[8] == "":
                        embed.add_field(name=f"Council Nomination for {row[3]}\n{row[9]}",
                                        value=f"Submitted by {row[1]}\nDated {row[0]}",
                                        inline=False)
                embed.set_footer(text="Use ++done <Task ID> to complete a task")
                if len(embed.fields) > 0:
                    flag = 1
                    await ctx.author.send(embed=embed)
                # Verification Requests
                result = sheet.values().get(spreadsheetId=spreadsheet_id, range="Verification!A2:I").execute()
                values = result.get("values", [])
                embed = discord.Embed(title="RCS Council Verification Requests", color=discord.Color.dark_blue())
                for row in values:
                    if len(row) < 9 or row[8] in ("1", "2", "3", "4"):
                        status = "has not been addressed"
                        try:
                            if row[8] == "1": status = " is awaiting a scout"
                            if row[8] == "2": status = " is currently being scouted"
                            if row[8] == "3": status = " is awaiting the post-scout survey"
                            if row[8] == "4": status = " is awaiting a decision by Council"
                        except:
                            self.bot.logger.debug("row is shorter than 9")
                        embed.add_field(name=f"Verification for {row[1]} {status}.\n{row[7]}",
                                        value=f"Leader: {row[3]}\nDated {row[0]}",
                                        inline=False)
                embed.set_footer(text="User ++verification <Task ID> to change the status.")
                if len(embed.fields) > 0:
                    flag = 1
                    await ctx.author.send(embed=embed)
                # Other Submissions
                result = sheet.values().get(spreadsheetId=spreadsheet_id, range="Other!A2:I").execute()
                values = result.get("values", [])
                embed = discord.Embed(title="RCS Council Other Items", color=discord.Color.gold())
                for row in values:
                    if len(row) < 9:
                        if len(row[6]) > 1:
                            assigned_to = f"Assigned to: {guild.get_member(int(row[6])).display_name}"
                        else:
                            assigned_to = "Unassigned"
                        embed.add_field(name=f"Other Comment from {row[1]}\n{row[7]}",
                                        value=(f"{row[3][:500]}\n{assigned_to}\n"
                                               f"Dated {row[0]}"),
                                        inline=False)
                embed.set_footer(text="Use ++done <Task ID> to complete a task")
                if len(embed.fields) > 0:
                    flag = 1
                    await ctx.author.send(embed=embed)
                # Tasks (Individual Action Items)
                result = sheet.values().get(spreadsheetId=spreadsheet_id, range="Tasks!A2:I").execute()
                values = result.get("values", [])
                embed = discord.Embed(title="RCS Council Action Items", color=discord.Color.dark_magenta())
                for row in values:
                    if len(row) < 9:
                        if len(row[6]) > 1:
                            assigned_to = f"Assigned to: {guild.get_member(int(row[6])).display_name}"
                        else:
                            assigned_to = "Unassigned"
                        embed.add_field(name=f"{assigned_to}\n{row[7]}",
                                        value=f"{row[1]}\nDated: {row[0]}",
                                        inline=False)
                embed.set_footer(text="Use ++done <Task ID> to complete a task")
                if len(embed.fields) > 0:
                    flag = 1
                    await ctx.author.send(embed=embed)
                if flag == 0:
                    await ctx.send("No incomplete tasks at this time! Well done!")
            if cmd.lower() in ("suggestions", "suggest", "suggestion", "sugg", "sug"):
                result = sheet.values().get(spreadsheetId=spreadsheet_id, range="Suggestions!A2:I").execute()
                values = result.get("values", [])
                embed = discord.Embed(title="RCS Council Suggestions", color=discord.Color.blurple())
                for row in values:
                    if len(row) < 9:
                        embed.add_field(name=f"Suggestion from {row[1]}\n{row[7]}\nDated {row[0]}",
                                        value=row[3][:1023],
                                        inline=True)
                embed.set_footer(text="Use ++done <Task ID> to complete a task")
                if len(embed.fields) > 0:
                    await ctx.send(embed=embed)
                else:
                    await ctx.send("No incomplete suggestions at this time.")
            if cmd.lower() in ("council", "nomination", "nominations", "nomi", "coun"):
                result = sheet.values().get(spreadsheetId=spreadsheet_id, range="Council!A2:J").execute()
                values = result.get("values", [])
                embed = discord.Embed(title="RCS Council Nominations", color=discord.Color.dark_gold())
                for row in values:
                    if row[8] == "":
                        embed.add_field(name=f"Council Nomination for {row[3]}\n{row[9]}\nDated {row[0]}",
                                        value=f"Submitted by {row[1]}",
                                        inline=True)
                embed.set_footer(text="Use ++done <Task ID> to complete a task")
                if len(embed.fields) > 0:
                    await ctx.send(embed=embed)
                else:
                    await ctx.send("No incomplete Council nominations at this time.")
            if cmd.lower() in ("verification", "verifications", "veri"):
                result = sheet.values().get(spreadsheetId=spreadsheet_id, range="Verification!A2:I").execute()
                values = result.get("values", [])
                embed = discord.Embed(title="RCS Council Verification Requests", color=discord.Color.dark_blue())
                for row in values:
                    if len(row) < 9 or row[8] in ("1", "2", "3", "4"):
                        status = "has not been addressed"
                        if row[8] == "1": status = "is awaiting a scout"
                        if row[8] == "2": status = "is currently being scouted"
                        if row[8] == "3": status = "is awaiting the post-scout survey"
                        if row[8] == "4": status = "is awaiting a decision by Council"
                        embed.add_field(name=f"Verification for {row[1]} {status}.\n{row[7]}\nDated {row[0]}",
                                        value=f"Leader: {row[3]}",
                                        inline=True)
                embed.set_footer(text="To change status, use ++veri <task ID> <new status> (e.g. ++veri V128 3)")
                if len(embed.fields) > 0:
                    await ctx.send(embed=embed)
            if cmd.lower() in ("other", "oth", "othe"):
                try:
                    result = sheet.values().get(spreadsheetId=spreadsheet_id, range="Other!A2:I").execute()
                    values = result.get("values", [])
                    embed = discord.Embed(title="RCS Council Other Items", color=discord.Color.gold())
                    for row in values:
                        if len(row) < 9:
                            if len(row[6]) > 1:
                                assigned_to = f"Assigned to: {guild.get_member(int(row[6])).display_name}"
                            else:
                                assigned_to = "Unassigned"
                            embed.add_field(name=f"Other Comment from {row[1]}\n{row[7]}",
                                            value=f"{row[3][:1000]}\n{assigned_to}\nDated: {row[0]}",
                                            inline=False)
                    embed.set_footer(text="Use ++done <Task ID> to complete a task")
                    if len(embed.fields) > 0:
                        await ctx.send(embed=embed)
                    else:
                        await ctx.send("No tasks in the Other category at this time.")
                except:
                    self.bot.logger.exception("++tasks other failed")
            if cmd.lower() in ("tasks", "task", "action", "agenda", "act"):
                result = sheet.values().get(spreadsheetId=spreadsheet_id, range="Tasks!A2:I").execute()
                values = result.get("values", [])
                embed = discord.Embed(title="RCS Council Action Items", color=discord.Color.dark_magenta())
                for row in values:
                    if len(row) < 9:
                        if len(row[6]) > 1:
                            assigned_to = f"Assigned to: {guild.get_member(int(row[6])).display_name}"
                        else:
                            assigned_to = "Unassigned"
                        embed.add_field(name=f"{assigned_to}\n{row[7]}",
                                        value=f"{row[1]}\nDated: {row[0]}",
                                        inline=False)
                embed.set_footer(text="Use ++done <Task ID> to complete a task")
                if len(embed.fields):
                    await ctx.send(embed=embed)
                else:
                    await ctx.send("No incomplete action items at this time.")
            if cmd.lower() == "":
                await ctx.author.send("In the future, this command will send you a DM with tasks assigned to you. "
                                      "For now, please use `++tasks all` to see all task items.")
        else:
            await ctx.send("This very special and important command is reserved for #council-chat only!")

    @commands.command(name="add", aliases=["new", "newtask", "addtask"], hidden=True)
    async def add_task(self, ctx, user: discord.Member, *task):
        if await self.is_council(ctx.author.id):
            if await self.is_council(user.id):
                url = (f"{settings['google']['commLog']}?call=addtask&task={' '.join(task)}&"
                       f"discord={user.id}")
                r = requests.get(url)
                if r.status_code == requests.codes.ok:
                    await ctx.send(f"Action Item {r.text} - {' '.join(task)} added for {user.display_name}")
                    await user.send(f"Action Item {r.text} - {' '.join(task)} was assigned "
                                    f"to you by {ctx.author.display_name}.")
                else:
                    await ctx.send(f"Something went wrong. Here's an error code for you to play with.\n"
                                   f"Add Task Error: {r.text}")
            else:
                await ctx.send("You are trying to assign this task to a non-council member and I'm not real "
                               "comfortable doing that!")
        else:
            await ctx.send("This very special and important command is reserved for council members only!")

    @commands.command(name="assign", hidden=True)
    async def assign_task(self, ctx, user: discord.Member, task_id):
        if await self.is_council(ctx.author.id):
            if task_id[:1].lower() in ("c", "v"):
                await ctx.send("Tasks in this category cannot be assigned to an individual.")
                return
            url = f"{settings['google']['commLog']}?call=assigntask&task={task_id}&discord={user.id}"
            r = requests.get(url)
            if r.status_code == requests.codes.ok and r.text != "-1":
                if r.text == "1":
                    await ctx.send(f"{task_id} assigned to {user.name}")
                    await user.send(f"{task_id} was assigned to you by {ctx.author.display_name}.")
                if r.text == "2":
                    await ctx.send(f"It would appear that tasks has already been completed!")
            else:
                await ctx.send(f"That didn't work, but here's an error code to chew on.\n"
                               f"Assign Task Error: {r.text}")
        else:
            await ctx.send("This very special and important command is reserved for council members only!")

    @commands.command(name="change", aliases=["modify", "alter"], hidden=True)
    async def change_task(self, ctx, task_id, *new_task):
        if await self.is_council(ctx.author.id):
            if task_id[:1].lower() != "a":
                await ctx.send("Only action items can be modified. Please try again with the proper Task ID.")
                return
            url = f"{settings['google']['commLog']}?call=changetask&task={task_id}&newtask={'%20'.join(new_task)}"
            r = requests.get(url)
            if r.status_code == requests.codes.ok and r.text != "-1":
                if r.text == "1":
                    await ctx.send(f"Action Item {task_id} changed.")
                if r.text == "2":
                    await ctx.send("I'd rather not change a task that is already complete.")
            else:
                await ctx.send("That action item was not found in the sheet. Make sure you have the "
                               "correct Task ID. Use `++tasks action` if you are unsure.")
        else:
            await ctx.send("This very special and important command is reserved for council members only!")

    @commands.command(name="verification", aliases=["veri", "verifications", "veris"], hidden=True)
    async def veri(self, ctx, task_id, new_status: int = 9):

        def check_reaction(reaction, user):
            return user == ctx.message.author and str(reaction.emoji) in ["1⃣", "2⃣", "3⃣", "4⃣", "☑",
                                                                          "<:upvote:295295304859910144>",
                                                                          "<:downvote:295295520187088906>"]

        if await self.is_council(ctx.author.id):
            if task_id[:1].lower() != "v":
                await ctx.send("This command only works on Verification tasks.")
                return
            result = sheet.values().get(spreadsheetId=spreadsheet_id, range="Verification!A2:I").execute()
            values = result.get("values", [])
            row_num = 1
            found = 0
            for row in values:
                row_num += 1
                if row[7] == task_id:
                    task_row = row_num
                    clan_name = row[1]
                    leader = row[3]
                    if len(row) >= 9:
                        cur_status_num = row[8]
                    else:
                        cur_status_num = 0
                    found = 1
            if found == 0:
                await ctx.send(f"I could not find {task_id} in the Verification tab. Are you sure that's the "
                               f"right ID?")
                return
            cur_status_text = " has not been addressed"
            if cur_status_num == "1": cur_status_text = "is awaiting a scout"
            if cur_status_num == "2": cur_status_text = "is currently being scouted"
            if cur_status_num == "3": cur_status_text = "is awaiting the post-scout survey"
            if cur_status_num == "4": cur_status_text = "is awaiting a decision by Council"
            await ctx.send(f"Verification for {clan_name} {cur_status_text}\nLeader: {leader}")
            if new_status == 9:
                prompt = await ctx.prompt(f"Please select a new status:\n"
                                            f":one: Awaiting a scout\n"
                                            f":two: Being scouted\n"
                                            f":three: Awaiting the post-scout surveys\n"
                                            f":four: Awaiting a decision by Council\n"
                                            f":five: Mark complete",
                                            additional_options=5)
            if prompt == "5":
                prompt = await ctx.send("Did this clan get verified?")
                if prompt:
                    new_status = 5
                else:
                    new_status = 6
            else:
                new_status = prompt
            url = f"{settings['google']['commLog']}?call=verification&status={new_status}&row={task_row}"
            r = requests.get(url)
            if r.status_code == requests.codes.ok:
                if r.text == "1":
                    await ctx.send(f"Verification for {clan_name} has been changed to {new_status}.")
            else:
                await ctx.send(f"Whoops! Something went sideways!\nVerification Error: {r.text}")
        else:
            await ctx.send("This very special and important command is reserved for council members only!")

    @commands.command(name="complete", aliases=["done", "finished", "x"], hidden=True)
    async def complete_task(self, ctx, task_id):
        if await self.is_council(ctx.author.id):
            if task_id[:1].lower() not in ("s", "v", "c", "o", "a"):
                await ctx.send("Please provide a valid task ID (Sug123, Cou123, Oth123, Act123).")
                return
            if task_id[:1].lower() == "v":
                ctx.invoke(self.veri, task_id=task_id, new_status=9)
            url = f"{settings['google']['commLog']}?call=completetask&task={task_id}"
            r = requests.get(url)
            if r.status_code == requests.codes.ok:
                if r.text == "1":
                    await ctx.send(f"Task {task_id} has been marked complete.")
                if r.text == "2":
                    await ctx.send(f"It would appear that tasks has already been completed!")
            else:
                await ctx.send(f"Yeah, we're going to have to try that one again.\n"
                               f"Complete Task Error: {r.text}")
        else:
            await ctx.send("This very special and important command is reserved for council members only!")

    async def send_text(self, channel, text, block=None):
        """ Sends text to channel, splitting if necessary
        Discord has a 2000 character limit
        """
        if len(text) < 2000:
            if block:
                await channel.send(f"```{text}```")
            else:
                await channel.send(text)
        else:
            coll = ""
            for line in text.splitlines(keepends=True):
                if len(coll) + len(line) > 1994:
                    # if collection is going to be too long, send  what you have so far
                    if block:
                        await channel.send(f"```{coll}```")
                    else:
                        await channel.send(coll)
                    coll = ""
                coll += line
            await channel.send(coll)

    async def is_council(self, user_id):
        rcs_guild = self.bot.get_guild(settings['discord']['rcsGuildId'])
        council_role = rcs_guild.get_role(settings['rcsRoles']['council'])
        council_members = [member.id for member in council_role.members]
        if user_id in council_members:
            return True
        return False


def setup(bot):
    bot.add_cog(Contact(bot))
