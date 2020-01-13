import coc
import re

from discord.ext import commands
from cogs.utils.helper import rcs_names_tags, rcs_tags

tag_validator = re.compile("^#?[PYLQGRJCUV0289]+$")


class PlayerConverter(commands.Converter):
    async def convert(self, ctx, argument):
        if isinstance(argument, coc.BasicPlayer):
            return argument

        tag = coc.utils.correct_tag(argument)
        name = argument.strip()

        if tag_validator.match(tag):
            try:
                return await ctx.coc.get_player(tag)
            except coc.NotFound:
                raise commands.BadArgument('I detected a player tag; and couldn\'t '
                                           'find an account with that tag! '
                                           'If you didn\'t pass in a tag, '
                                           'please drop the owner a message.'
                                           )
        for rcs_tag in rcs_tags():
            clan = await ctx.coc.get_clan(rcs_tag)
            if clan.name == name or clan.tag == tag:
                raise commands.BadArgument(f'You appear to be passing '
                                           f'the clan tag/name for `{str(clan)}`')

            member = clan.get_member(name=name)
            if member:
                return member

        raise commands.BadArgument(f"Invalid tag or IGN. Please try again.")


class ClanConverter(commands.Converter):
    async def convert(self, ctx, argument):
        if isinstance(argument, coc.BasicClan):
            return argument

        tag = coc.utils.correct_tag(argument)
        name = argument.strip().lower()
        clans = rcs_names_tags()

        # If tag is valid, use the tag
        if tag_validator.match(tag):
            try:
                if tag[1:] in clans.values():
                    clan = await ctx.coc.get_clan(tag)
                else:
                    raise commands.BadArgument(f"{tag} is not a valid RCS clan.")
            except coc.NotFound:
                raise commands.BadArgument(f"{tag} is not a valid clan tag.")

            if clan:
                return clan

            raise commands.BadArgument(f'{tag} is not a valid clan tag.')

        # If no valid tag, try working with the name
        if name in clans.keys():
            tag = "#" + clans[name]
        else:
            raise commands.BadArgument(f"{name} is not a valid RCS clan.")

        try:
            clan = await ctx.coc.get_clan(tag)
        except coc.NotFound:
            raise commands.BadArgument(f"{tag} is not a valid clan tag.")

        if clan:
            return clan

        raise commands.BadArgument(f'Clan name or tag `{argument}` not found')

