import discord
import requests
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
    """Cog for RCS trophy push"""
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="tasks", aliases=["task", "tasklist", "list"], hidden=True)
    async def task_list(self, ctx, cmd, cmd_input: str = ""):
        if is_council(ctx.author.roles) and (ctx.guild is None or ctx.channel.id == settings['rcsChannels']['council']):
            if cmd_input.lower() == "all":
                await ctx.send("Reply all")
            if cmd_input.lower() in ("suggestions", "council", "verification", "other", "tasks"):
                await ctx.send("Here's your specific list")
            if cmd_input.lower() == "":
                await ctx.author.send(ctx.author, "Here's your full list")
        else:
            await ctx.send("This very special and important command is reserved for council members only!")

    @commands.command(name="add", aliases=["new", "newtask", "addtask"], hidden=True)
    async def add_task(self, ctx, user: discord.Member, *task):
        if is_council(ctx.author.roles):
            url = (f"{settings['google']['commLog']}?call=addtask&task={' '.join(task)}&"
                   f"discord={user.id}")
            print(' '.join(task))
            r = requests.get(url)
            if r.status_code == requests.codes.ok:
                print(r.text)
                await ctx.send(f"Task {r.text} - {' '.join(task)} added for <@{user.id}>")
            else:
                await ctx.send(f"Something went wrong. Here's an error code for you to play with.\n{r.text}")
        else:
            await ctx.send("This very special and important command is reserved for council members only!")

    @commands.command(name="assign", hidden=True)
    async def assign_task(self, ctx, user: discord.Member):
        if is_council(ctx.author.roles):
            await ctx.send("Task assigned")
            await user.send("A new task was assigned to you by ...")
        else:
            await ctx.send("This very special and important command is reserved for council members only!")

    @commands.command(name="change", aliases=["modify", "alter"], hidden=True)
    async def change_task(self, ctx, task_id, new_task):
        if is_council(ctx.author.roles):
            await ctx.send("Task changed")
        else:
            await ctx.send("This very special and important command is reserved for council members only!")

    @commands.command(name="complete", aliases=["done", "finished", "x"], hidden=True)
    async def complete_task(self, ctx, task_id):
        if is_council(ctx.author.roles):
            await ctx.send("Task marked complete")
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


def is_council(user_roles):
    for role in user_roles:
        if role.id == settings['rcsRoles']['council']:
            return True
    return False


def setup(bot):
    bot.add_cog(Contact(bot))
