import discord
import requests

from discord.ext import commands
from cogs.utils.checks import is_council
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from config import settings

# Connect to Google Sheets
scope = "https://www.googleapis.com/auth/spreadsheets.readonly"
spreadsheet_id = settings['google']['comm_log_id']
store = file.Storage("token.json")
creds = store.get()
if not creds or creds.invalid:
    flow = client.flow_from_clientsecrets("credentials.json", scope)
    creds = tools.run_flow(flow, store)
service = build("sheets", "v4", http=creds.authorize(Http()), cache_discovery=False)
sheet = service.spreadsheets()


class Tasks(commands.Cog):
    """Cog for handling Council Tasks"""
    def __init__(self, bot):
        self.bot = bot
        self.guild = self.bot.get_guild(settings['discord']['rcsguild_id'])
        # TODO Set up DM for assigned action items

    @commands.group(name="tasks", aliases=["task"], hidden=True)
    @is_council()
    async def tasks(self, ctx):
        """[Group] Task Manager for RCS Council

        **Permissions:**
        Council
        """
        if ctx.invoked_subcommand is None:
            return await ctx.send_help(ctx.command)

    @tasks.command(name="all")
    @is_council()
    async def tasks_all(self, ctx):
        """Sends all incomplete tasks to requestor via DM"""
        if isinstance(ctx.channel, discord.TextChannel):
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
                    assigned_to = f"Assigned to: {self.guild.get_member(int(row[6])).display_name}"
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
                    assigned_to = f"Assigned to: {self.guild.get_member(int(row[6])).display_name}"
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

    @tasks.command(name="suggestions", aliases=["sug", "sugg", "suggest", "suggestion"])
    @is_council()
    async def tasks_suggestions(self, ctx):
        """Displays all incomplete suggestion tasks"""
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

    @tasks.command(name="council", aliases=["nomination", "nominations", "nomi", "coun"])
    @is_council()
    async def tasks_council(self, ctx):
        """Displays all incomplete council nominations"""
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

    @tasks.command(name="verification", aliases=["verifications", "ver", "veri"])
    @is_council()
    async def tasks_verification(self, ctx):
        """Displays all incomplete RCS clan verification requests"""
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

    @tasks.command(name="other", aliases=["oth", "othe"])
    @is_council()
    async def tasks_other(self, ctx):
        """Displays all incomplete tasks from the Other category"""
        try:
            result = sheet.values().get(spreadsheetId=spreadsheet_id, range="Other!A2:I").execute()
            values = result.get("values", [])
            embed = discord.Embed(title="RCS Council Other Items", color=discord.Color.gold())
            for row in values:
                if len(row) < 9:
                    if len(row[6]) > 1:
                        assigned_to = f"Assigned to: {self.guild.get_member(int(row[6])).display_name}"
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

    @tasks.command(name="action", aliases=["act"])
    @is_council()
    async def tasks_action(self, ctx):
        """Displays all incomplete Action Items"""
        result = sheet.values().get(spreadsheetId=spreadsheet_id, range="Tasks!A2:I").execute()
        values = result.get("values", [])
        embed = discord.Embed(title="RCS Council Action Items", color=discord.Color.dark_magenta())
        for row in values:
            if len(row) < 9:
                if len(row[6]) > 1:
                    assigned_to = f"Assigned to: {self.guild.get_member(int(row[6])).display_name}"
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

    @tasks.command(name="add", aliases=["new"])
    @is_council()
    async def tasks_add(self, ctx, user: discord.Member, *, task):
        """Adds a new action item and assigns it to the specified Discord user

        **Example:**
        ++task add @zig Don't forget to feed the cats!
        """
        if await self.is_council(user.id):
            url = (f"{settings['google']['comm_log']}?call=addtask&task={task}&"
                   f"discord={user.id}")
            async with ctx.session.get(url) as r:
                if r.status == 200:
                    async for line in r.content:
                        task_id = line.decode("utf-8")
                    await ctx.send(f"Action Item {task_id} - {task} added for {user.display_name}")
                    await user.send(f"Action Item {task_id} - {task} was assigned "
                                    f"to you by {ctx.author.display_name}.")
                else:
                    await ctx.send(f"Something went wrong. Here's an error code for you to play with.\n"
                                   f"Add Task Error: {r.status} - {r.reason}")
        else:
            await ctx.send("You are trying to assign this task to a non-council member and I'm not real "
                           "comfortable doing that!")

    @tasks.command(name="assign")
    @is_council()
    async def tasks_assign(self, ctx, user: discord.Member, task_id):
        """Assigns the specified tasks to the Discord user provided

        **Example:**
        ++task assign @Elocuencia Oth035

        **Notes:**
        Tasks that can be assigned include Suggestions, Other, and Action Items.
        Council Nominations and Clan Verifications cannot be assigned to an individual.
        """
        if task_id[:1].lower() in ("c", "v"):
            return await ctx.send("Tasks in this category cannot be assigned to an individual.")
        url = f"{settings['google']['comm_log']}?call=assigntask&task={task_id}&discord={user.id}"
        async with ctx.session.get(url) as r:
            if r.status == 200:
                async for line in r.content:
                    response = line.decode("utf-8")
                if response != "-1":
                    if response == "1":
                        await ctx.send(f"{task_id} assigned to {user.name}")
                        await user.send(f"{task_id} was assigned to you by {ctx.author.display_name}.")
                    if response == "2":
                        await ctx.send(f"It would appear that tasks has already been completed!")
                else:
                    await ctx.send(f"I'm having a little trouble finding the row for that tasks. You might"
                                   f"want to hop on sheets and check the row manually.\n"
                                   f"{settings['google']['comm_log']}")
            else:
                await ctx.send(f"That didn't work, but here's an error code to chew on.\n"
                               f"Assign Task Error: {r.status} - {r.reason}")

    @tasks.command(name="change", aliases=["modify", "alter"])
    @is_council()
    async def tasks_change(self, ctx, task_id, *, new_task):
        """Change an existing action item

        **Example:**
        ++task change Oth103 This is my new task.

        **Notes:**
        Only action items can be modified/changed.
        """
        if task_id[:1].lower() != "a":
            await ctx.send("Only action items can be modified. Please try again with the proper Task ID.")
            return
        url = f"{settings['google']['comm_log']}?call=changetask&task={task_id}&newtask={new_task}"
        async with ctx.session.get(url) as r:
            if r.status == 200:
                async for line in r.content:
                    response = line.decode("utf-8")
                if response != "-1":
                    if response == "1":
                        await ctx.send(f"Action Item {task_id} changed.")
                    if response == "2":
                        await ctx.send("I'd rather not change a task that is already complete.")
                else:
                    await ctx.send(f"I'm having a little trouble finding the row for that tasks. Make sure that "
                                   f"you have the correct ID.  You might want to hop on sheets and "
                                   f"check the row manually.\n{settings['google']['comm_log']}")
            else:
                await ctx.send("That action item was not found in the sheet. Make sure you have the "
                               "correct Task ID. Use `++tasks action` if you are unsure.")

    @commands.command(name="verification", aliases=["veri", "verifications", "veris"], hidden=True)
    async def veri(self, ctx, task_id, new_status: int = 9):
        if await self.is_council(ctx.author.id):
            if task_id[:1].lower() != "v":
                await ctx.send("This command only works on Verification tasks.")
                return
            if len(task_id) == 7:
                task_id = task_id[:3] + task_id[4:]
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
            if prompt == 5:
                prompt = await ctx.prompt("Did this clan get verified?", delete_after=False)
                if prompt:
                    new_status = 5
                else:
                    new_status = 6
            else:
                new_status = prompt
            url = f"{settings['google']['comm_log']}?call=verification&status={new_status}&row={task_row}"
            r = requests.get(url)
            if r.status_code == requests.codes.ok:
                if r.text == "1":
                    if new_status <= 4:
                        await ctx.send(f"Verification for {clan_name} has been changed to {new_status}.")
                    elif new_status == 5:
                        await ctx.send(f"Verification for {clan_name} has been changed to Verified.")
                    else:
                        await ctx.send(f"Verification for {clan_name} has been changed to 'Heck No!' :wink:")
            else:
                await ctx.send(f"Whoops! Something went sideways!\nVerification Error: {r.text}")
        else:
            await ctx.send("This very special and important command is reserved for council members only!")

    @commands.command(name="complete", aliases=["done", "finished", "x"], hidden=True)
    async def complete_task(self, ctx, task_id):
        if await self.is_council(ctx.author.id):
            if task_id[:1].lower() not in ("s", "v", "c", "o", "a"):
                return await ctx.send("Please provide a valid task ID (Sug123, Cou123, Oth123, Act123).")
            if task_id[:1].lower() == "v":
                return await ctx.invoke(self.veri, task_id=task_id, new_status=9)
            url = f"{settings['google']['comm_log']}?call=completetask&task={task_id}"
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
        council_role = self.guild.get_role(settings['rcs_roles']['council'])
        council_members = [member.id for member in council_role.members]
        if user_id in council_members:
            return True
        return False


def setup(bot):
    bot.add_cog(Tasks(bot))
