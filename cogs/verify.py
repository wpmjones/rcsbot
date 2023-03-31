import coc
import gspread
import nextcord

from nextcord import ui
from nextcord.ext import commands
from config import settings

GUILD_IDS = [settings['discord']['rcsguild_id'], settings['discord']['botlogguild_id']]

NEW_THREAD_ANNOUNCE = ("{clan} has applied to become a verified RCS clan.\nClash of Stats link: <{cos}>\n"
                       "Please send a Pre-Scout Survey and invite the leader to {channel}.")

LEADER_WELCOME = ("Hello and welcome to the server!\n\n"
                  "This is where we will handle the verification process.  Here we will ask you any questions we have "
                  "and you are most definitely free to ask us questions as well!\n\n"
                  "The next step now that you've applied to join and made it here is to fill out the initial survey.  "
                  "These are some basic questions about your clan and leadership style.  Please feel free to take "
                  "time with it and get it to us some time in the next few days. Please note: you must spell your "
                  "clan's name correctly for our bot to deliver it back to us.\n\n"
                  "Pre survey link: <https://docs.google.com/forms/d/e/1FAIpQLScmC__"
                  "0WSsvdid_Cu48MbkdRP9A7wOZ2VWwyZbFWW-SeA1s4A/viewform>\n\n"
                  "The next step will be to arrange for 1-2 Scouts to join your clan for about 2 weeks.  To help "
                  "us with this,  please let us know what the requirements are for joining your clan and if you "
                  "have any particular rules. We will try pick the most appropriate scouts available.\n\n"
                  "There will be a follow up survey after the visit, and then the Council will vote based on "
                  "the survey responses,  any conversation here,  and the scout reports.  Council meets once a "
                  "month but we'll try get you a response within 1-2 weeks after the scout visit concludes. "
                  "You may ask for more specific dates once we get closer.\n\nGood luck!")

# Connect to Google Sheets using gspread
# TODO switch to pygsheets
gc = gspread.service_account(filename="service_account.json")
comm_log_ss = gc.open_by_key(settings['google']['comm_log_id'])

class Scout(ui.Modal):
    def __init__(self, bot):
        super().__init__(
            "Scouting Report",
            timeout=None
        )
        self.bot = bot

        self.clan_name = ui.TextInput(
            label="Clan Name",
            required=True
        )
        self.add_item(self.clan_name)
        self.atmosphere = ui.TextInput(
            label="What is the atmosphere like in the clan?",
            required=True,
            style=nextcord.TextInputStyle.paragraph
        )
        self.add_item(self.atmosphere)
        self.leader_attr = ui.TextInput(
            label="Does the leader make good decisions? Deal with conflict fairly? Are they active?",
            required=True
        )
        self.add_item(self.leader_attr)

    async def callback(self, interaction: nextcord.Interaction):
        pass


class Verify(commands.Cog):
    """Cog for General bot commands"""

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        if channel.category_id != 1049133819590099025:  # settings['rcs_channels']['veri_category']:
            return
        clan_tag = channel.name
        try:
            clan = await self.bot.coc.get_clan(clan_tag)
        except coc.NotFound:
            # Assume this is not a new clan channel
            return
        cos_link = f"https://www.clashofstats.com/clans/{clan.tag[1:]}"
        # Rename channel to clan name
        await channel.edit(name=clan.name.replace(" ", "-"))
        # create thread for scouts to converse
        thread = await channel.create_thread(
            name=f"{clan.name.replace(' ', '-')}-notes",
            type=nextcord.ChannelType.private_thread
        )
        await thread.send(NEW_THREAD_ANNOUNCE.format(clan=f"{clan.name} ({clan.tag})",
                                                     cos=cos_link,
                                                     channel=channel.mention)
                          )
        await channel.send(LEADER_WELCOME)
        await thread.send(f"<@&{settings['rcs_roles']['scouts']}>", delete_after=5)

    @commands.command(name="scout", hidden=True)
    async def scout_survey(self, ctx):
        """Proceed with surveys"""
        # Select Menu to ask which kind of survey to access
        return await ctx.send("Still in testing mode")



def setup(bot):
    bot.add_cog(Verify(bot))
