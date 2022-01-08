import nextcord
import asyncio
import itertools

from nextcord.ext import commands
from cogs.utils.paginator import Pages
from datetime import datetime
from config import emojis


class NewHelp(commands.Cog):
    """New help file for rcs-bot"""
    def __init__(self, bot):
        self.bot = bot

        bot.help_command = HelpCommand()
        bot.help_command.cog = self

    @commands.command(aliases=["join"])
    async def invite(self, ctx):
        """Get an invite to add the bot to a server."""
        await ctx.send(f"<https://discord.gg/X8U9XjD>")

    @commands.command()
    async def feedback(self, ctx, *, content):
        """Give feedback on the bot."""
        embed = nextcord.Embed(title="Feedback", color=nextcord.Color.green())
        channel = self.bot.get_channel(640755164004745235)
        if channel is None:
            return

        embed.set_author(name=str(ctx.author), icon_url=ctx.author.avatar_url)
        embed.description = content
        embed.timestamp = ctx.message.created_at

        if ctx.guild is not None:
            embed.add_field(name="Guild", value=f"{ctx.guild.name} (ID: {ctx.guild.id})", inline=False)

        embed.add_field(name="Channel", value=f"{ctx.channel} (ID: {ctx.channel.id})", inline=False)
        embed.set_footer(text=f"Author ID: {ctx.author.id}")

        await channel.send(embed=embed)
        await ctx.send(f"{ctx.tick(True)} Successfully sent feedback")


class HelpPaginator(Pages):
    def __init__(self, help_command, ctx, entries, *, per_page=9):
        super().__init__(ctx, entries=entries, per_page=per_page)
        self.ctx = ctx
        self.embed.colour = nextcord.Colour.green()
        self.title = ""
        self.description = ""
        self.prefix = help_command.clean_prefix
        self.total = len(entries)
        self.help_command = help_command
        self.reaction_emojis = [
            ('\N{BLACK LEFT-POINTING TRIANGLE}', self.previous_page),
            ('\N{BLACK RIGHT-POINTING TRIANGLE}', self.next_page),
            ('\N{INPUT SYMBOL FOR NUMBERS}', self.numbered_page),
            ('\N{WHITE QUESTION MARK ORNAMENT}', self.show_help)
        ]

    def get_bot_page(self, page):
        cog, description, commands = self.entries[page - 1]
        if hasattr(cog, 'qualified_name'):
            self.title = cog.qualified_name
        else:
            self.title = cog.name
        self.description = description
        return commands

    def prepare_embed(self, entries, page, *, first=False):
        self.embed.clear_fields()
        self.embed.title = self.title
        self.embed.description = self.description

        self.embed.set_footer(text=f'Use the reactions to navigate pages, '
                                   f'and "{self.prefix}help command" for more help.')
        self.embed.timestamp = datetime.utcnow()

        for i, entry in enumerate(entries):
            sig = f'{self.help_command.get_command_signature(command=entry)}'
            fmt = f"{emojis['other']['green']}{entry.short_doc}"
            if entry.short_doc.startswith('[Group]'):
                fmt += f"\n{emojis['other']['amber']} Use `{self.prefix}help {entry.name}` for subcommands."
            if not entry._can_run:
                fmt += f"\n{emojis['other']['red']} You don't have the required permissions to run this command."

            self.embed.add_field(name=sig,
                                 value=fmt + '\n\u200b' if i == (len(entries) - 1) else fmt,
                                 inline=False
                                 )

        self.embed.add_field(name="Support",
                             value=f"Problem? Bug? Please submit feedback using {self.prefix}feedback")

        if self.maximum_pages:
            self.embed.set_author(name=f'Page {page}/{self.maximum_pages} ({self.total} commands)')

    async def show_help(self):
        self.title = "RCS-Bot Help"
        description = ("This is the help command for the bot.\nA few points to notice:\n\n"
                       f"{emojis['other']['green']} This command is powered by reactions: \n"
                       ":arrow_backward: goes to the previous page\n"
                       ":arrow_forward: goes to the next page\n"
                       ":1234: lets you type a page number to go to\n"
                       ":grey_question: Takes you to this page\n"
                       f"{emojis['other']['green']} Help for a specific command can be found with `+help commandname`\n"
                       f"{emojis['other']['green']} e.g `+help don` or `+help add donationboard`.\n\n"
                       f"{emojis['other']['green']} Press :arrow_forward: to proceed.")

        self.description = description
        embed = self.embed.copy() if self.embed else nextcord.Embed(colour=self.bot.colour)
        embed.clear_fields()
        embed.description = description
        embed.set_footer(text=f'We were on page {self.current_page} before this message.')
        await self.message.edit(content=None, embed=embed)

        async def go_back_to_current_page():
            await asyncio.sleep(60.0)
            await self.show_current_page()

        self.bot.loop.create_task(go_back_to_current_page())


class HelpCommand(commands.HelpCommand):
    async def command_callback(self, ctx, *, command=None):
        category = self.context.bot.get_category(command)
        if category:
            return await self.send_category_help(category)
        return await super().command_callback(ctx, command=command)

    async def send_bot_help(self, mapping):
        def key(c):
            if c.cog:
                if hasattr(c.cog, "category"):
                    return c.cog.category.name or "\u200bNo Category"
            return c.cog_name or "\u200bNo Category"

        bot = self.context.bot
        entries = await self.filter_commands(bot.commands, sort=True, key=key)
        nested_pages = []
        per_page = 9
        total = len(entries)

        for cog, commands in itertools.groupby(entries, key=key):
            def key(c):
                if c.short_doc.startswith("[Group]"):
                    c.name = f"\u200b{c.name}"
                return c.name
            commands = sorted(commands, key=key)
            if len(commands) == 0:
                continue

            total += len(commands)
            actual_cog = bot.get_cog(cog) or bot.get_category(cog)
            # get the description if it exists (and the cog is valid) or return Empty embed.
            description = actual_cog.description or nextcord.Embed.Empty
            nested_pages.extend((actual_cog, description, commands[i:i + per_page])
                                for i in range(0, len(commands), per_page
                                               )
                                )

        # a value of 1 forces the pagination session
        pages = HelpPaginator(self, self.context, entries=nested_pages, per_page=1)

        # swap the get_page implementation to work with our nested pages.
        pages.is_bot = True
        pages.total = total
        pages.get_page = pages.get_bot_page
        await self.context.release()
        await pages.paginate()

    async def send_category_help(self, category):
        entries = await self.filter_commands(category.commands, sort=True)
        pages = HelpPaginator(self, self.context, entries)
        pages.title = f"{category.name} Commands"
        pages.description = f"{category.description}\n\n"

        await self.context.release()
        await pages.paginate()

    async def filter_commands(self, _commands, *, sort=False, key=None):
        self.verify_checks = False
        valid = await super().filter_commands(_commands, sort=sort, key=key)
        for n in valid:
            try:
                can_run = await n.can_run(self.context)
                n._can_run = can_run
            except commands.CommandError:
                n._can_run = False
        return valid

    async def send_cog_help(self, cog):
        entries = await self.filter_commands(cog.get_commands(), sort=True)
        pages = HelpPaginator(self, self.context, entries)
        pages.title = f"{cog.qualified_name} Commands"
        pages.description = f"{cog.description}\n\n"

        await self.context.release()
        await pages.paginate()

    def common_command_formatting(self, page_or_embed, command):
        page_or_embed.title = f'{self.clean_prefix}{command.name}'
        if command.description:
            page_or_embed.description = f"{command.description}\n\n{command.help}"
        else:
            page_or_embed.description = command.help or "No help found..."

    async def send_command_help(self, command):
        # No pagination necessary for a single command.
        embed = nextcord.Embed(colour=nextcord.Colour.blurple())
        self.common_command_formatting(embed, command)
        await self.context.send(embed=embed)

    async def send_group_help(self, group):
        subcommands = group.commands
        if len(subcommands) == 0:
            return await self.send_command_help(group)

        entries = await self.filter_commands(subcommands, sort=True)
        pages = HelpPaginator(self, self.context, entries)
        self.common_command_formatting(pages, group)

        await self.context.release()
        await pages.paginate()


def setup(bot):
    bot.add_cog(NewHelp(bot))
