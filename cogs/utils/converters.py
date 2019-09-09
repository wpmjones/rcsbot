import coc
import re

from discord.ext import commands

tag_validator = re.compile("^#?[PYLQGRJCUV0289]+$")


class PlayerConverter(commands.Converter):
    async def convert(self, ctx, argument):
        if isinstance(argument, coc.BasicPlayer):
            return argument

        tag = coc.utils.correct_tag(argument)
        name = argument.strip()

        if tag_validator.match(argument):
            try:
                return await ctx.coc.get_player(tag)
            except coc.NotFound:
                raise commands.BadArgument('I detected a player tag; and couldn\'t '
                                           'find an account with that tag! '
                                           'If you didn\'t pass in a tag, '
                                           'please drop the owner a message.'
                                           )
        guild_clans = await ctx.get_clans()
        for g in guild_clans:
            if g.name == name or g.tag == tag:
                raise commands.BadArgument(f'You appear to be passing '
                                           f'the clan tag/name for `{str(g)}`')

            member = g.get_member(name=name)
            if member:
                return member

            member_by_tag = g.get_member(tag=tag)
            if member_by_tag:
                return member_by_tag

        raise commands.BadArgument(f"Invalid tag or IGN in "
                                   f"`{','.join(str(n) for n in guild_clans)}` clans.")


class ClanConverter(commands.Converter):
    async def convert(self, ctx, argument):
        if argument in ['all', 'guild', 'server'] or not argument:
            return await ctx.get_clans()
        if isinstance(argument, coc.BasicClan):
            return argument

        tag = coc.utils.correct_tag(argument)
        name = argument.strip()

        if tag_validator.match(tag):
            try:
                clan = await ctx.coc.get_clan(argument)
            except coc.NotFound:
                raise commands.BadArgument(f'{tag} is not a valid clan tag.')

            if clan:
                return [clan]

            raise commands.BadArgument(f'{tag} is not a valid clan tag.')

        guild_clans = await ctx.get_clans()
        matches = [n for n in guild_clans if n.name == name or n.tag == tag]

        if not matches:
            raise commands.BadArgument(f'Clan name or tag `{argument}` not found')

        return matches