from nextcord.ext import commands


class NewHelp(commands.Cog):
    """No longer in use. Just making sure it's safe to delete"""
    def __init__(self, bot):
        self.bot = bot



class HelpCommand(commands.HelpCommand):
    """No longer in use. Just making sure it's safe to delete"""


def setup(bot):
    bot.add_cog(NewHelp(bot))
