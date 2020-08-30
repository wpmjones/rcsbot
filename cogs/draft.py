import discord

from discord.ext import commands
from config import settings


class Draft(commands.Cog):
    """Cog for Draft Wars"""
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="draft")
    @commands.has_role("TDW Leaders")
    async def draft(self, ctx, user: discord.Member):
        print("ok")
        draft_roles = [settings['rcs_roles']['innuendo'],
                       settings['rcs_roles']['aardvark'],
                       settings['rcs_roles']['foxtrot'],
                       settings['rcs_roles']['heroes']
                       ]
        team_role = None
        try:
            print(ctx.author.roles)
            for role in ctx.author.roles:
                print(role)
                if role.id in draft_roles:
                    team_role = int(role.id)
                    draft_roles.remove(role.id)
                    break
            if not team_role:
                return await ctx.send(f"Hey {ctx.author.name}!  You don't have any team roles yet. Get a team role, "
                                      f"then try again.  K?")
            guild = ctx.bot.get_guild(settings['discord']['rcsguild_id'])
            role_obj = guild.get_role(team_role)
            for role in user.roles:
                if role.id in draft_roles:
                    return await ctx.send(f"{user.display_name} already has the {role.name} role. To change teams, "
                                          f"user `++undraft @mention`.")
            await user.add_roles(role_obj, reason=f"Role added through draft command by {ctx.author.display_name}.")
            await ctx.send(f"{user.mention} has been drafted to {role_obj.name}!")
        except:
            self.bot.logger.exception("fail")

    @commands.command(name="undraft")
    @commands.has_role("TDW Leaders")
    async def undraft(self, ctx, user: discord.Member):
        draft_roles = [settings['rcs_roles']['innuendo'],
                       settings['rcs_roles']['aardvark'],
                       settings['rcs_roles']['foxtrot'],
                       settings['rcs_roles']['heroes']
                       ]
        guild = ctx.bot.get_guild(settings['discord']['rcsguild_id'])
        for role in draft_roles:
            role_obj = guild.get_role(int(role))
            await user.remove_roles(role_obj, reason=f"Role removed through undraft command "
                                                     f"by {ctx.author.display_name}.")
        await ctx.send(f"All draft roles have been removed from {user.display_name}.")


def setup(bot):
    bot.add_cog(Draft(bot))
