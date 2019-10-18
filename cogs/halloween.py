

from discord.ext import commands


class Halloween(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name="halloween")
    async def halloween(self, ctx):
        """[Group] Let the halloween fun begin!  Trick or treat!"""
        if ctx.invoked_subcommand is None:
            return await ctx.send_help(ctx.command)

    @halloween.command(name="join")

def setup(bot):
    bot.add_cog(Halloween(bot))