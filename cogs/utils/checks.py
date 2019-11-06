from discord.ext import commands
from config import settings


async def check_guild_permissions(ctx, perms, check=all):
    if await ctx.bot.is_owner(ctx.author):
        return True
    is_owner = await ctx.bot.is_owner(ctx.author)
    if is_owner:
        return True

    if ctx.guild is None:
        return False

    resolved = ctx.author.guild_permissions
    return check(getattr(resolved, name, None) == value for name, value in perms.items())


def manage_guild():
    async def pred(ctx):
        return await check_guild_permissions(ctx, {"manage_guild": True})
    return commands.check(pred)


async def check_is_council(ctx):
    rcs_guild = ctx.bot.get_guild(settings['discord']['rcsGuildId'])
    council_role = rcs_guild.get_role(settings['rcs_roles']['council'])
    rcs_member = rcs_guild.get_member(ctx.author.id)
    if council_role in rcs_member.roles:
        return True
    else:
        return False


def is_council():
    async def pred(ctx):
        return await check_is_council(ctx)
    return commands.check(pred)


async def check_is_mod(ctx):
    rcs_guild = ctx.bot.get_guild(settings['discord']['rcsGuildId'])
    council_role = rcs_guild.get_role(settings['rcs_roles']['chat_mods'])
    rcs_member = rcs_guild.get_member(ctx.author.id)
    if council_role in rcs_member.roles:
        return True
    else:
        return False


def is_mod():
    async def pred(ctx):
        return await check_is_mod(ctx)
    return commands.check(pred)


def is_mod_or_council():
    async def pred(ctx):
        return await check_is_mod(ctx) or await check_is_council(ctx)
    return commands.check(pred)
