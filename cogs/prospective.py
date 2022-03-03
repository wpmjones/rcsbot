import coc

from typing import Optional
from asyncio import TimeoutError
from cogs.utils import interactions
from config import settings
from datetime import timedelta
from re import match

from nextcord.ext import commands, tasks
from nextcord import (
    Button,
    ButtonStyle,
    ChannelType,
    Colour,
    Embed,
    Forbidden,
    HTTPException,
    Interaction,
    Member,
    MessageType,
    Thread,
    ThreadMember,
    Message,
    ui,
    utils,
    AllowedMentions
)

from utils.split_txtfile import split_txtfile


if settings['enviro'] == 'LIVE':
    WELCOME_CHANNEL_ID: int = 338884664335007755
    LOG_CHANNEL_ID: int = 678664032542261250
    VIP_CHANNEL_ID: int = 364153344203423765
    COUNCIL_ROLE_ID: int = 340968315960950788
    SCOUTS_ROLE_ID: int = 340969543402913803
    GUILD_ID: int = 338884664335007755
else:
    WELCOME_CHANNEL_ID = 935780614349656075
    LOG_CHANNEL_ID = 603424347994193930
    VIP_CHANNEL_ID = 935793224025505792
    COUNCIL_ROLE_ID = 620338168331370538
    SCOUTS_ROLE_ID = 810734340627365888
    GUILD_ID = 602621563770109992
CUSTOM_ID_PREFIX = "welcome:"
WAIT_FOR_TIMEOUT: int = 1800  # 30 minutes

timeout_message: str = "You are currently timed out, please wait until it ends before trying again."
positive_close = ("Congratulations! We will be evaluating your clan for prospective members in the Reddit Clan "
                  "System. We are creating a new channel where we can discuss the process with you and initiate "
                  "the scouting procedure.")
negative_close = ("Thank you for your interest in the Reddit Clan System. We will not be moving forward with your clan "
                  "at this time.")


async def get_thread_author(channel: Thread) -> Member:
    history = channel.history(oldest_first=True, limit=1)
    history_flat = await history.flatten()
    user = history_flat[0].mentions[0]
    return user


async def close_welcome_thread(method: str, thread_channel, thread_author):
    """Closes a thread. Is called from the close button."""

    # no need to do any of this if the thread is already closed.
    if thread_channel.locked or thread_channel.archived:
        return

    if not thread_channel.last_message or not thread_channel.last_message_id:
        _last_msg = (await thread_channel.history(limit = 1).flatten())[0]
    else:
        _last_msg = thread_channel.get_partial_message(thread_channel.last_message_id)

    thread_jump_url = _last_msg.jump_url

    embed_reply = Embed(title="This thread has now been closed",
                        description=closing_message,  # TODO pass in pro or con
                        colour=Colour.dark_theme())

    await thread_channel.send(embed=embed_reply)  # Send the closing message to the help thread
    await thread_channel.edit(locked=True, archived=True)  # Lock thread
    await thread_channel.guild.get_channel(LOG_CHANNEL_ID).send(  # Send log
        content=f"Wecome thread {thread_channel.name} (created by {thread_author.name}) has been closed."
    )
    # Make some slight changes to the previous thread-closer embed
    # to send to the user via DM.
    embed_reply.title = "Your thread in the RCS Prospective server has been closed."
    embed_reply.description += (f"\n\nYou can use [**this link**]({thread_jump_url}) to access the archived "
                                f"thread for future reference")
    if thread_channel.guild.icon:
        embed_reply.set_thumbnail(url=thread_channel.guild.icon.url)
    try:
        await thread_author.send(embed=embed_reply)
    except (HTTPException, Forbidden):
        pass


class StartButton(ui.Button["WelcomeView"]):
    def __init__(self, help_type: str, *, style: ButtonStyle, custom_id: str):
        super().__init__(label=f"{help_type} help", style=style, custom_id=f"{CUSTOM_ID_PREFIX}{custom_id}")
        self._help_type: str = help_type

    async def create_welcome_thread(self, interaction: Interaction) -> Thread:
        thread = await interaction.channel.create_thread(
            name=f"Welcome ({interaction.user})",
            type=ChannelType.public_thread,
        )

        await interaction.guild.get_channel(LOG_CHANNEL_ID).send(
            content=f"Welcome thread created by {interaction.user.mention}: {thread.mention}!",
            allowed_mentions=AllowedMentions(users=False)
        )
        close_button_view = ThreadCloseView()
        close_button_view._thread_author = interaction.user

        embed = Embed(
            title="Verification Survey Thread",
            colour=Colour.green(),
            description=(
                "We are always excited to add new, quality clans to the Reddit Clan System.  If you are the leader "
                "of your clan, you may proceed."
            )
        )
        embed.set_footer(text="You can close this thread with the button or by typing ++close.")

        msg = await thread.send(
            content=interaction.user.mention,
            embed=embed,
            view=ThreadCloseView()
        )
        await msg.pin(reason="First message in thread with the close button.")
        return thread

    async def __launch_wait_for_message(self, thread: Thread, interaction: Interaction) -> None:
        assert self.view is not None

        def is_allowed(message: Message) -> bool:
            return message.author.id == interaction.user.id and message.channel.id == thread.id and not thread.archived

        try:
            await self.view.bot.wait_for("message", timeout=WAIT_FOR_TIMEOUT, check=is_allowed)
        except TimeoutError:
            await close_welcome_thread("TIMEOUT [launch_wait_for_message]", thread, interaction.user)
            return
        else:
            # Ping council if the user stops interacting
            await thread.send(f"<@&{COUNCIL_ROLE_ID}>", delete_after=5)
            return

    async def callback(self, interaction: Interaction):
        confirm_view = ConfirmView()

        def disable_all_buttons():
            for _item in confirm_view.children:
                _item.disabled = True

        confirm_content = f"Are you ready to begin the pre-verification survey?"
        await interaction.send(content=confirm_content, ephemeral=True, view=confirm_view)
        await confirm_view.wait()
        if confirm_view.value is False or confirm_view.value is None:
            disable_all_buttons()
            content = "Ok, cancelled." if confirm_view.value is False else f"~~{confirm_content}~~ I guess not..."
            await interaction.edit_original_message(content=content, view=confirm_view)
        else:
            disable_all_buttons()
            await interaction.edit_original_message(content="Created!", view=confirm_view)
            created_thread = await self.create_welcome_thread(interaction)
            await self.__launch_wait_for_message(created_thread, interaction)


class WelcomeView(ui.View):
    def __init__(self, bot: commands.Bot):
        super().__init__(timeout=None)
        self.bot: commands.Bot = bot

        self.add_item(StartButton("Start Survey", style=ButtonStyle.green, custom_id="welcome"))

    async def interaction_check(self, interaction: Interaction) -> bool:
        if interaction.user.timeout is not None:
            await interaction.send(timeout_message, ephemeral=True)
            return False

        return await super().interaction_check(interaction)


class ConfirmButton(ui.Button["ConfirmView"]):
    def __init__(self, label: str, style: ButtonStyle, *, custom_id: str):
        super().__init__(label=label, style=style, custom_id=f"{CUSTOM_ID_PREFIX}{custom_id}")

    async def callback(self, interaction: Interaction):
        self.view.value = True if self.custom_id == f"{CUSTOM_ID_PREFIX}confirm_button" else False
        self.view.stop()


class ConfirmView(ui.View):
    def __init__(self):
        super().__init__(timeout=10.0)
        self.value = None
        self.add_item(ConfirmButton("Yes", ButtonStyle.green, custom_id="confirm_button"))
        self.add_item(ConfirmButton("No", ButtonStyle.red, custom_id="decline_button"))


class ThreadCloseView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self._thread_author: Optional[Member] = None

    async def _get_thread_author(self, channel: Thread) -> None:
        self._thread_author = await get_thread_author(channel)

    @ui.button(label="Close", style=ButtonStyle.red, custom_id=f"{CUSTOM_ID_PREFIX}thread_close")
    async def thread_close_button(self, button: Button, interaction: Interaction):
        if interaction.channel.archived:
            button.disabled = True
            await interaction.response.edit_message(view=self)
            return

        if not self._thread_author:
            await self._get_thread_author(interaction.channel)  # type: ignore

        button.disabled = True
        await interaction.response.edit_message(view=self)
        await close_welcome_thread("BUTTON", interaction.channel, self._thread_author)

    async def interaction_check(self, interaction: Interaction) -> bool:
        if not self._thread_author:
            await self._get_thread_author(interaction.channel)  # type: ignore

        # because we aren't assigning the persistent view to a message_id.
        if not isinstance(interaction.channel, Thread) or interaction.channel.parent_id != WELCOME_CHANNEL_ID:
            return False

        if interaction.user.timeout is not None:
            await interaction.send(timeout_message, ephemeral=True)
            return False

        elif interaction.user.id != self._thread_author.id and not interaction.user.get_role(COUNCIL_ROLE_ID):
            await interaction.send("You are not allowed to close this thread.", ephemeral=True)
            return False

        return True


class ProspectiveCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.close_empty_threads.start()
        self.bot.loop.create_task(self.create_views())

    async def create_views(self):
        if getattr(self.bot, "welcome_view_set", False) is False:
            self.bot.welcome_view_set = True
            self.bot.add_view(WelcomeView(self.bot))
            self.bot.add_view(ThreadCloseView())

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.id == WELCOME_CHANNEL_ID and message.type is MessageType.thread_created:
            await message.delete(delay=5)
        if (isinstance(message.channel, Thread) and
                message.channel.parent_id == WELCOME_CHANNEL_ID and
                message.type is MessageType.pins_add):
            await message.delete(delay=10)

    @commands.Cog.listener()
    async def on_thread_member_remove(self, member: ThreadMember):
        thread = member.thread
        if thread.parent_id != WELCOME_CHANNEL_ID or thread.archived:
            return

        thread_author = await get_thread_author(thread)
        if member.id != thread_author.id:
            return

        await close_welcome_thread("EVENT", thread, thread_author)

    @commands.Cog.listener()
    async def on_thread_join(self, thread: Thread):
        """Triggered when a thread is created"""
        if thread.parent_id != WELCOME_CHANNEL_ID:
            return

        thread_author = await get_thread_author(thread)

        def check_author(m):
            return m.author == thread_author

        await thread.send("Please enter the tag of your clan.")
        clan_tag = await self.bot.wait_for("message", check=check_author)
        clan = await self.bot.coc.get_clan(clan_tag)
        if not clan:
            await thread.send("This doesn't appear to be a valid clan. Please enter the tag of your clan.")
            clan_tag = await self.bot.wait_for("message", check=check_author)
            clan = await self.bot.coc.get_clan(clan_tag)
        view = interactions.YesNo()
        await thread.send("Does your clan have a Discord server?", view=view)
        await view.wait()
        if view.value:
            await thread.send("Please provide the invite link to your clan's Discord server.")
            server_link = await self.bot.wait_for("message", check=check_author)
        else:
            server_link = ""
        await thread.send("In which time zone do you live?")
        time_zone = await self.bot.wait_for("message", check=check_author)
        await thread.send("When does your clan typically run wars? (Days/Times)")
        war_days = await self.bot.wait_for("message", check=check_author)
        msg = await thread.send("Thank you for the information.  One moment while I store everything.")

        clan_leader = clan.get_member_by(role=coc.Role.leader)
        sql = ("INSERT INTO rcs_apply (clan_tag, clan_name, clan_leader, leader_discord, clan_size, discord_server, "
               "time_zone, war_days)"
               "VALUES ($1, $2, $3, $4, $5, $6, $7, $8)")
        await self.bot.pool.execute(sql, clan.tag, clan.name, clan_leader, thread_author.id, clan.member_count,
                                    server_link, time_zone, war_days)
        await msg.edit(content="Information stored. The team will review your application soon and inform you of "
                               "next steps.")

        # Create notes channel and provide information to the team
        guild = await self.bot.get_guild(GUILD_ID)
        channel = await guild.create_text_channel(f"{clan.name.replace(' ', '-')}-notes")
        # TODO maybe create clan channel first, then make notes a sub thread?

    @tasks.loop(hours=24)
    async def close_empty_threads(self):
        await self.bot.wait_until_ready()

        guild = self.bot.get_guild(GUILD_ID)
        active_help_threads = [
            thread for thread in await guild.active_threads()
            if thread.parent_id == WELCOME_CHANNEL_ID and (not thread.locked and not thread.archived)
        ]

        thread: Thread
        for thread in active_help_threads:
            thread_created_at = utils.snowflake_time(thread.id)

            # We don't want to close it before the wait_for.
            if utils.utcnow() - timedelta(seconds=WAIT_FOR_TIMEOUT) <= thread_created_at:
                continue

            all_messages = [
                message for message in (await thread.history(limit=3, oldest_first=True).flatten())
                if message.type is MessageType.default
            ]
            # can happen, ignore.
            if not all_messages:
                continue

            thread_author = all_messages[0].mentions[0]
            if len(all_messages) < 2:
                await close_welcome_thread("TASK [close_empty_threads]", thread, thread_author)
                continue

    @commands.command()
    @commands.is_owner()
    async def welcome_menu(self, ctx):
        """Posts initial message in Welcome channel with button to start verification survey"""
        for section in split_txtfile("welcome.txt"):
            await ctx.send(embed=Embed(description=section, color=Colour.yellow()))

        await ctx.send(
            content=("**:white_check_mark: If you've read the above and would like to proceed with the verification "
                     "process, click the button below to begin the process!**"),
            view=WelcomeView(self.bot)
        )

    @commands.command()
    async def close(self, ctx):
        if not isinstance(ctx.channel, Thread) or ctx.channel.parent_id != WELCOME_CHANNEL_ID:
            return

        thread_author = await get_thread_author(ctx.channel)
        await close_welcome_thread("COMMAND", ctx.channel, thread_author)

    @commands.command()
    @commands.has_role(COUNCIL_ROLE_ID)
    async def topic(self, ctx, *, topic: str):
        """Allows council to change the topic name of the thread (Usually, this will be to add the clan name"""
        if not (isinstance(ctx.channel, Thread) and ctx.channel.parent.id == HELP_CHANNEL_ID):  # type: ignore
            return await ctx.send("This command can only be used in welcome threads!")

        author = match(NAME_TOPIC_REGEX, ctx.channel.name).group(2)  # type: ignore
        await ctx.channel.edit(name=f"{topic} ({author})")


def setup(bot):
    bot.add_cog(ProspectiveCog(bot))
