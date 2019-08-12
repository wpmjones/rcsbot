import discord
import requests
from datetime import datetime
from discord.ext import commands
from config import settings, color_pick, bot_log


class NewHelp(commands.Cog):
    """New help file for rcs-bot"""
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help", hidden=True)
    async def help(self, ctx, command: str = "all"):
        """Welcome to the rcs-bot"""
        desc = ("All commands must begin with a ++\n\n"        
                "References to a clan can be in the form of the clan name (spelled correctly) or the clan tag "
                "(with or without the #).\n\n"
                "You can type ++help <command> to display only the help for that command.")

        command_list = ["all", "attacks", "defenses", "donations", "trophies", "besttrophies",
                        "townhalls", "builderhalls", "warstars", "games", "push",
                        "top", "reddit", "council", "tasks"]

        # respond if help is requested for a command that does not exist
        if command not in command_list:
            await ctx.send(":x: You have provided a command that does not exist.  "
                           "Perhaps try ++help to see all commands.")
            channel = self.bot.get_channel(settings['rcsChannels']['botDev'])
            await channel.send(f"Do we need a help command for {command}?")
            bot_log(ctx.command, f"{command} is an invalid option", ctx.author, ctx.guild)
            return

        # respond to help request
        embed = discord.Embed(title="rcs-bot Help File", description=desc, color=color_pick(15, 250, 15))
        embed.add_field(name="Commands:", value="-----------")
        if command in ["all", "cwl"]:
            help_text = "Updates the specified clan's CWL league"
            embed.add_field(name="++cwl <clan name> <CWL league name>", value=help_text)
        if command in ["all", "attacks", "attack", "attackwins", "att"]:
            help_text = "Responds with the current attack wins for all members of the clan specified."
            embed.add_field(name="++attacks <clan name or tag>", value=help_text)
        if command in ["all", "defenses", "defense", "defensewins", "defences", "defence", "defencewins", "def", 
                       "defend", "defends"]:
            help_text = "Responds with the current defense wins for all members of the clan specified."
            embed.add_field(name="++defenses <clan name or tag>", value=help_text)
        if command in ["all", "donations", "donates", "donate", "donation"]:
            help_text = ("Responds with the donation count and the donations received count for all members "
                         "of the clan specified.")
            embed.add_field(name="++donations <clan name or tag>", value=help_text)
        if command in ["all", "trophies", "trophy"]:
            help_text = "Responds with the trophy count for all members of the clan specified."
            embed.add_field(name="++trophies <clan name or tag>", value=help_text)
        if command in ["all", "besttrophies", "besttrophy", "mosttrophies"]:
            help_text = "Responds wtih the best trophy count for all members of the clan specified."
            embed.add_field(name="++besttrophies <clan name or tag>", value=help_text)
        if command in ["all", "townhalls", "th", "townhall"]:
            help_text = "Responds with the town hall levels for all members of the clan specified."
            embed.add_field(name="++townhalls <clan name or tag>", value=help_text)
        if command in ["all", "builderhalls", "bh", "builderhall"]:
            help_text = "Responds with the builder hall  levels for all members of the clan specified."
            embed.add_field(name="++builderhalls <clan name or tag>", value=help_text)
        if command in ["all", "warstars", "stars"]:
            help_text = "Responds with the war star counts for all members of the clan specified."
            embed.add_field(name="++warstars <clan name or tag>", value=help_text)
        if command in ["all", "top"]:
            help_text = ("Responds with the top ten players across all of the RCS for the category specified."
                         "\nOptions include:"
                         "\n  :crossed_swords: attacks"
                         "\n  :shield:  defenses"
                         "\n  :trophy: trophies"
                         "\n  :moneybag: donations"
                         "\n  :star: warstars"
                         "\n  :medal: games")
            embed.add_field(name="++top <category>", value=help_text)
        if command in ["all", "games"]:
            help_text = ("Responds with the Clan Games information for the category specified."
                         "\n  - <all (or no category)> responds with all RCS clans and their current Clan Games score."
                         "\n  - <clan name or tag> responds with individual scores for the clan specified."
                         "\n  - <average> responds with the average individual score for all clans in the RCS.")
            embed.add_field(name="++games <category or clan name/tag>", value=help_text)
        if command in ["all", "push"]:
            help_text = ("Responds with the Trophy Push information for the category specified."
                         "\n  - <all (or no category)> responds with all RCS clans and their current Trophy Push score."
                         "\n  - <diff> responds with the top clan and the difference in points for the other clans."
                         "\n  - <TH#> responds with all players of the town hall level specified and their scores."
                         "\n  - <clan name or tag> responds with all players in the clan specified and their scores."
                         "\n  - <top> responds with the top ten players for each town hall level and their scores."
                         "\n  - <gain> responds with the top 25 players in trophies gained.")
            embed.add_field(name="++push <category or clan name/tag>", value=help_text)
        if command in ["all", "reddit"]:
            help_text = "Responds with the subreddit link for the clan specified."
            embed.add_field(name="++reddit <clan name/tag>", value=help_text)
        if command == "council" and is_council(ctx.author.roles):
            help_text = "Responds with a link to the Council Magic Google Form"
            embed.add_field(name="++magic", value=help_text)
            help_text = "Leader command responds with the leader of the requested clan name/tag"
            embed.add_field(name="++leader <clan name/tag>", value=help_text)
            help_text = "Find command responds with the Discord names that contain the specified string"
            embed.add_field(name="++find <search string>", value=help_text)
            help_text = "Adds clan to the RCS database, add leader roles"
            embed.add_field(name="++addClan <clan name [no tags]>", value=help_text)
            help_text = "Remove clan from RCS database, remove feeder (if it exists), remove roles from leader"
            embed.add_field(name="++removeClan <clan name [no tags]>", value=help_text)
            help_text = "Reports user information on the Discord ID provided"
            embed.add_field(name="++ui <discord user or ID>", value=help_text)
            help_text = "Responds with a larger version of the specified user's avatar"
            embed.add_field(name="++avatar <discord mention or ID>", value=help_text)
            help_text = "Sends the provided message to all RCS leaders via DM"
            embed.add_field(name="++dm_leaders <message>", value=help_text)
            help_text = ("Used to manage tasks for council\nThere are a number of commands for this category\n"
                         "Please use `++help tasks` for more detailed information")
            embed.add_field(name="++tasks ++add ++assign ++change ++done", value=help_text)
        elif command == "council":
            await ctx.send(":x: You've requested help for commands you cannot access.")
            return
        if command == "tasks" and is_council(ctx.author.roles):
            help_text = "Responds with all active tasks for the RCS Council (via DM)"
            embed.add_field(name="++tasks all", value=help_text)
            help_text = "Responds with all tasks assigned to you (COMING SOON)"
            embed.add_field(name="++tasks mine", value=help_text, inline=False)
            help_text = "Responds with all Suggestions"
            embed.add_field(name="++tasks suggestions or ++tasks sugg", value=help_text, inline=False)
            help_text = "Responds with all Council Nominations"
            embed.add_field(name="++tasks council", value=help_text, inline=False)
            help_text = "Responds with all Verification Requests"
            embed.add_field(name="++tasks verification or ++tasks veri", value=help_text, inline=False)
            help_text = "Responds with all other comments from the Comm Log"
            embed.add_field(name="++tasks other", value=help_text, inline=False)
            help_text = "Responds with all action items"
            embed.add_field(name="++tasks action or ++tasks act", value=help_text, inline=False)
            help_text = ("Adds the specified action item and assigns it you choose. A DM will be sent to the "
                         "user so they are aware of the action item.  Action items can only be assigned to "
                         "council members.")
            embed.add_field(name="++add <Discord User> <Action Item>", value=help_text, inline=False)
            help_text = ("Assigns the specified task to the user you choose. Only suggestions, other items, and "
                         "action items can be assigned to an individual. If you don't know the Task ID, use ++task "
                         "to find it.")
            embed.add_field(name="++assign <Discord User> <Task ID>", value=help_text, inline=False)
            help_text = ("Modifies the status of a Clan Verification. If you know the status number, use it. If "
                         "you leave off the status number, it will prompt you for the new status.")
            embed.add_field(name="++verification <Task ID> <status number (optional)>", value=help_text, inline=False)
            help_text = "Change the action item to the newly specified text."
            embed.add_field(name="++change <Task ID> <new action item text>", value=help_text, inline=False)
            help_text = "Marks the specified task as completed."
            embed.add_field(name="++done <Task ID>", value=help_text, inline=False)
        elif command == "tasks":
            await ctx.send(":x: You've requested help for commands you cannot access.")
            return
        embed.set_footer(icon_url="https://openclipart.org/image/300px/svg_to_png/122449/1298569779.png",
                         text="rcs-bot proudly maintained by TubaKid.")
        bot_log("help", command, ctx.author, ctx.guild)
        await ctx.send(embed=embed)


def is_council(user_roles):
    for role in user_roles:
        if role.id == settings['rcsRoles']['council']:
            return True
    return False


def setup(bot):
    bot.add_cog(NewHelp(bot))
