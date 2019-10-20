import random
from datetime import datetime, date
from discord.ext import commands, tasks
from config import settings


class ProfilePics(commands.Cog):
    """Cog for SAQ to get a new pfp each week"""
    def __init__(self, bot):
        self.bot = bot
        self.send_request.start()

    def cog_unload(self):
        self.send_request.cancel()

    @tasks.loop(hours=24)
    async def send_request(self):
        if datetime.today().weekday() == 4:
            guild = self.bot.get_guild(settings['discord']['rcsGuildId'])
            pfp_role = guild.get_role(settings['rcsRoles']['pfp'])
            member_role = guild.get_role(settings['rcsRoles']['members'])
            members = member_role.members
            recipients = random.sample(members, k=15 * len(pfp_role.members))
            conn = self.bot.pool
            self.bot.logger.debug(f"{len(pfp_role.members)} with the pfp role\n"
                                  f"Recipients are {recipients}")
            for member in pfp_role.members:
                sql = "SELECT log_id FROM tcs_task_log WHERE log_date = $1 and argument = $2 and log_type = $3"
                result = await conn.fetch(sql, date.today().strftime('%Y-%m-%d'), member.id, 2)
                if not result:
                    await member.send("I hope you're ready for it!  I'm sending out requests now for a new pfp for "
                                      "you!\nThe first person to send you an appropriate pic wins!")
                    msg = (f"It's time for {member.display_name} to change their profile picture. If you're the "
                           f"first person to DM {member.mention} with an appropriate image, {member.display_name} will "
                           f"use it for their profile pic for the next week!")
                    print(msg)
                    for i in range(15):
                        recipient = recipients[0]
                        await recipient.send(msg)
                        print(f"{msg}\nTo: {recipient.display_name}")
                        recipients.remove(recipients[0])
                        self.bot.logger.debug(f"DM sent to {recipient.display_name}")
                        sql = ("INSERT INTO rcs_pfp_requests (discord_id, display_name) "
                               "VALUES ($1, $2)")
                        await conn.execute(sql, recipient.id, recipient.display_name)
                        sql = (f"INSERT INTO rcs_task_log (log_type, log_date, argument) "
                               f"VALUES ($1, $2, $3)")
                        await conn.execute(sql, 2, date.today().strftime('%Y-%m-%d'), member.id)

    @send_request.before_loop
    async def before_send_request(self):
        await self.bot.wait_until_ready()


def setup(bot):
    bot.add_cog(ProfilePics(bot))
