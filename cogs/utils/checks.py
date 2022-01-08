from nextcord.ext import commands
from config import settings


class NoConfigFailure(commands.CheckFailure):
    pass


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


def check_is_council(ctx):
    if ctx.author.id == 251150854571163648:
        return True
    if ctx.guild.id == 566451504332931073:
        return True
    rcs_guild = ctx.bot.get_guild(settings['discord']['rcsguild_id'])
    council_role = rcs_guild.get_role(settings['rcs_roles']['council'])
    rcs_member = rcs_guild.get_member(ctx.author.id)
    if not rcs_member:
        return False
    if not rcs_member.roles:
        return False
    if council_role in rcs_member.roles:
        return True
    else:
        return False


def is_council():
    def pred(ctx):
        return check_is_council(ctx)
    return commands.check(pred)


def check_is_mod(ctx):
    if ctx.author.id == 251150854571163648:
        return True
    if ctx.guild.id == 566451504332931073:
        return True
    rcs_guild = ctx.bot.get_guild(settings['discord']['rcsguild_id'])
    mod_role = rcs_guild.get_role(settings['rcs_roles']['chat_mods'])
    rcs_member = rcs_guild.get_member(ctx.author.id)
    if not rcs_member:
        return False
    if not rcs_member.roles:
        return False
    if mod_role in rcs_member.roles:
        return True
    else:
        return False


def is_mod():
    def pred(ctx):
        return check_is_mod(ctx)
    return commands.check(pred)


def check_is_scout(ctx):
    if ctx.author.id == 251150854571163648:
        return True
    rcs_guild = ctx.bot.get_guild(338884664335007755)
    scout_role = rcs_guild.get_role(340969543402913803)
    rcs_member = rcs_guild.get_member(ctx.author.id)
    if not rcs_member:
        return False
    if not rcs_member.roles:
        return False
    if scout_role in rcs_member.roles:
        return True
    else:
        return False


def is_scout():
    def pred(ctx):
        return check_is_scout(ctx)
    return commands.check(pred)


def check_is_leader(ctx):
    if ctx.author.id == 251150854571163648:
        return True
    if ctx.guild.id == 566451504332931073:
        return True
    rcs_guild = ctx.bot.get_guild(settings['discord']['rcsguild_id'])
    leader_role = rcs_guild.get_role(settings['rcs_roles']['leaders'])
    rcs_member = rcs_guild.get_member(ctx.author.id)
    if not rcs_member:
        return False
    if not rcs_member.roles:
        return False
    if leader_role in rcs_member.roles:
        return True
    else:
        return False


def is_leader():
    def pred(ctx):
        return check_is_leader(ctx)
    return commands.check(pred)


def is_mod_or_council():
    async def pred(ctx):
        return check_is_mod(ctx) or check_is_council(ctx)
    return commands.check(pred)


def is_scout_or_council():
    async def pred(ctx):
        return check_is_scout(ctx) or check_is_council(ctx)
    return commands.check(pred)


def is_leader_or_mod_or_council():
    async def pred(ctx):
        return check_is_leader(ctx) or check_is_mod(ctx) or check_is_council(ctx)
    return commands.check(pred)
