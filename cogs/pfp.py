import discord

from discord.ext import commands, tasks
from cogs.utils.constants import log_types
from datetime import timedelta, date
from config import settings


class ProfilePics(commands.Cog):
    """Cog for PFP Fun role to get a new pfp each week"""
    def __init__(self, bot):
        self.bot = bot
        self.send_request.start()
        self.global_webhook = discord.Webhook.partial(id=settings['rcs_hooks']['global_id'],
                                                      token=settings['rcs_hooks']['global_token'],
                                                      adapter=discord.AsyncWebhookAdapter(session=self.bot.session))

    def cog_unload(self):
        self.send_request.cancel()

    @tasks.loop(hours=24)
    async def send_request(self):
        guild = self.bot.get_guild(settings['discord']['rcsguild_id'])
        pfp_role = guild.get_role(settings['rcs_roles']['pfp'])
        conn = self.bot.pool
        for member in pfp_role.members:
            sql = ("SELECT log_date FROM rcs_task_log "
                   "WHERE log_type_id = $1 AND argument = $2")
            fetch = conn.fetchrow(sql, log_types['pfp'], member.id)
            if fetch[0] < date.today() - timedelta(days=7):
                await member.send("I hope you're ready for it!  I'm sending out requests now for a new pfp for "
                                  "you!\nThe first person to send you an appropriate pic wins!")
                msg = (f"It's time for {member.display_name} to change their profile picture. If you're the "
                       f"first person to DM {member.mention} with an appropriate image, {member.display_name} will "
                       f"use it for their profile pic for the next week!")
                await self.global_webhook.send(msg)
                sql = ("INSERT INTO rcs_task_log (log_type_id, log_date, argument) "
                       "VALUES ($1, $2, $3)")
                await conn.execute(sql, log_types['pfp'], date.today().strftime('%Y-%m-%d'), member.id)

    @send_request.before_loop
    async def before_send_request(self):
        await self.bot.wait_until_ready()


def setup(bot):
    bot.add_cog(ProfilePics(bot))
