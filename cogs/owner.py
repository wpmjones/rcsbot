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

    @commands.command(name="emojis")
    @commands.is_owner()
    async def emoji_list(self, ctx):
        server_list = [self.bot.get_guild(506645671009583105),
                       self.bot.get_guild(506645764512940032),
                       self.bot.get_guild(531660501709750282)]
        for guild in server_list:
            content = f"**{guild.name}**\n```"
            for emoji in guild.emojis:
                content += f"\n{emoji.name}: {emoji.id}>"
            content += "```"
            await ctx.send(content)

    @commands.command(name="server")
    @commands.is_owner()
    async def server_list(self, ctx):
        guild_count = len(self.bot.guilds)
        # TODO create embed with guild.name and guild.owner
        for guild in self.bot.guilds:
            await ctx.send(guild.name)

    @commands.command(name="close_db", aliases=["cdb", "cbd"], hidden=True)
    @commands.is_owner()
    async def close_db(self, ctx):
        """Command to close db connection before shutting down bot"""
        if self.bot.db.pool is not None:
            await self.bot.db.pool.close()
            await ctx.send("Database connection closed.")


def setup(bot):
    bot.add_cog(OwnerCog(bot))
