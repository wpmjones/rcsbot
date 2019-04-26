from discord.ext import commands


class OwnerCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="load", hidden=True)
    @commands.is_owner()
    async def load(self, ctx, *, cog: str):
        """Command which loads a module.
        Remember to use dot path. e.g: cogs.owner"""

        try:
            self.bot.load_extension(cog)
        except Exception as e:
            print(f"ERROR: {type(e).__name__} - {e}")
            await ctx.send(f"**`ERROR:`** {type(e).__name__} - {e}")
        else:
            print(f"{cog} successfully loaded")
            await ctx.send("**`SUCCESS`**")

    @commands.command(name="unload", hidden=True)
    @commands.is_owner()
    async def unload(self, ctx, *, cog: str):
        """Command which unloads a module.
        Remember to use dot path. e.g: cogs.owner"""

        try:
            self.bot.unload_extension(cog)
        except Exception as e:
            print(f"ERROR: {type(e).__name__} - {e}")
            await ctx.send(f"**`ERROR:`** {type(e).__name__} - {e}")
        else:
            print(f"{cog} successfully unloaded")
            await ctx.send("**`SUCCESS`**")

    @commands.command(name="reload", hidden=True)
    @commands.is_owner()
    async def reload(self, ctx, *, cog: str):
        """Command which reloads a module.
        Remember to use dot path. e.g: cogs.owner"""

        try:
            self.bot.unload_extension(cog)
            self.bot.load_extension(cog)
        except Exception as e:
            print(f"ERROR: {type(e).__name__} - {e}")
            await ctx.send(f"**`ERROR:`** {type(e).__name__} - {e}")
        else:
            print(f"{cog} reloaded successfully")
            await ctx.send("**`SUCCESS`**")

    @commands.command(name="pull", hidden=True)
    @commands.is_owner()
    async def git_pull(self, ctx):
        """Command to pull latest updates from master branch on GitHub"""
        origin = self.bot.repo.remotes.origin
        try:
            origin.pull()
            print("Code successfully pulled from GitHub")
            await ctx.send("Code successfully pulled from GitHub")
        except Exception as e:
            print(f"ERROR: {type(e).__name__} - {e}")
            await ctx.send(f"**`ERROR:`** {type(e).__name__} - {e}")


def setup(bot):
    bot.add_cog(OwnerCog(bot))
