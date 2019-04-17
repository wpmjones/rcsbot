from discord.ext import commands

class OwnerCog:
  def __init__(self, bot):
    self.bot = bot

  @commands.command(name='load', hidden=True)
  @commands.is_owner()
  async def cog_load(self, ctx, *, cog: str):
    """Command which loads a module.
    Remember to use dot path. e.g: cogs.owner"""

    try:
      self.bot.load_extension(cog)
    except Exception as e:
      print(f'ERROR: {type(e).__name__} - {e}')
      await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
    else:
      print(f'{cog} successfully loaded')
      await ctx.send('**`SUCCESS`**')

  @commands.command(name='unload', hidden=True)
  @commands.is_owner()
  async def cog_unload(self, ctx, *, cog: str):
    """Command which unloads a module.
    Remember to use dot path. e.g: cogs.owner"""

    try:
      self.bot.unload_extension(cog)
    except Exception as e:
      print(f'ERROR: {type(e).__name__} - {e}')
      await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
    else:
      print(f'{cog} successfully unloaded')
      await ctx.send('**`SUCCESS`**')

  @commands.command(name='reload', hidden=True)
  @commands.is_owner()
  async def cog_reload(self, ctx, *, cog: str):
    """Command which reloads a module.
    Remember to use dot path. e.g: cogs.owner"""

    try:
      self.bot.unload_extension(cog)
      self.bot.load_extension(cog)
    except Exception as e:
      print(f'ERROR: {type(e).__name__} - {e}')
      await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
    else:
      print(f'{cog} reloaded successfully')
      await ctx.send('**`SUCCESS`**')

def setup(bot):
    bot.add_cog(OwnerCog(bot))
