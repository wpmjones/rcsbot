import coc

from discord.ext import commands
from cogs.utils.helper import rcs_tags
from config import settings


class TestWarUpdates(commands.Cog, command_attrs=dict(hidden=True)):
    def __init__(self, bot):
        self.bot = bot

    @coc.WarEvents.state(rcs_tags(prefix=True))
    async def on_war_state_change(self, current_state, war):
        channel = self.bot.get_channel(settings['log_channels']['test'])
        if current_state == "preparation":
            await channel.send(f"Preparation has just begun for a war between **{war.clan.name}** and "
                               f"**{war.opponent.name}**.")
        elif current_state == "inWar":
            await channel.send(f"War has just begun between **{war.clan.name}** and **{war.opponent.name}**.")
        elif current_state == "warEnded":
            content = f"War has just ended between **{war.clan.name}** and **{war.opponent.name}**.\n"
            if war.status == "won":
                content += f"{war.clan.name} won!"
            elif war.status == "lost":
                content += f"{war.clan.name} lost! :("
            else:
                content += "Looks like a tie!"
            await channel.send(content)
        else:
            await channel.send(f"War state is {current_state} for {war.clan.name}")


def setup(bot):
    bot.add_cog(TestWarUpdates(bot))
