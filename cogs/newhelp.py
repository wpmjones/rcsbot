import discord
import requests
from datetime import datetime
from discord.ext import commands
from config import settings, color_pick, bot_log


class newHelp(commands.Cog):
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
                        "townhalls", "builderhalls", "warstars", "games", "push", "top", "reddit", "council"]

        # respond if help is requested for a command that does not exist
        if command not in command_list:
            await ctx.send(":x: You have provided a command that does not exist.  "
                           "Perhaps try ++help to see all commands.")
            # TODO convert to aiohttp
            r = requests.post(settings['discord']['botDev'], f"Do we need a help command for {command}?")
            bot_log(ctx.command, f"{command} is an invalid option", ctx.author, ctx.guild)
            return

        # respond to help request
        embed = discord.Embed(title="rcs-bot Help File", description=desc, color=color_pick(15, 250, 15))
        embed.add_field(name="Commands:", value="-----------")
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
                         "\n  - <TH#> responds with all players of the town hall level specified and their scores."
                         "\n  - <clan name or tag> responds with all players in the clan specified and their scores."
                         "\n  - <top> responds with the top ten players for each town hall level and their scores.")
            embed.add_field(name="++push <category or clan name/tag", value=help_text)
        if command in ["all", "reddit"]:
            help_text = "Responds with the subreddit link for the clan specified."
            embed.add_field(name="++reddit <clan name/tag>", value=help_text)
        if command == "council":
            help_text = "Leader command responds with the leader of the requested clan name/tag."
            embed.add_field(name="++leader <clan name/tag>", value=help_text)
            help_text = "Find command responds with the Discord names that contain the specified string."
            embed.add_field(name="++find <search string>", value=help_text)
            help_text = "Adds clan to the RCS database, add leader roles."
            embed.add_field(name="++addClan <clan name [no tags]>", value=help_text)
            help_text = "Remove clan from RCS database, remove feeder (if it exists), remove roles from leader."
            embed.add_field(name="++removeClan <clan name [no tags]>", value=help_text)
            help_text = "Reports user information on the Discord ID provided"
            embed.add_field(name="++ui <discord user or ID>", value=help_text)
            help_text = "Responds with a larger version of the specified user's avatar"
            embed.add_field(name="++avatar <discord user or ID>", value=help_text)
        embed.set_footer(icon_url="https://openclipart.org/image/300px/svg_to_png/122449/1298569779.png",
                         text="rcs-bot proudly maintained by TubaKid.")
        bot_log("help", command, ctx.author, ctx.guild)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(newHelp(bot))
