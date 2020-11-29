import discord
import pandas as pd
import matplotlib.pyplot as plt

from discord.ext import commands
from cogs.utils.converters import ClanConverter
from cogs.utils.helper import rcs_tags


class Plots(commands.Cog):
    """Cog for Plot related bot commands"""
    def __init__(self, bot):
        self.bot = bot

    async def fetch_as_dataframe(self, sql):
        fetch = await self.bot.pool.fetch(sql)
        columns = [key for key in fetch[0].keys()]
        return pd.DataFrame(fetch, columns=columns)

    @staticmethod
    def breakdown(members, blanks=False):
        if blanks:
            res = {13: 0, 12: 0, 11: 0, 10: 0, 9: 0, 8: 0, 7: 0, 6: 0, 5: 0, 4: 0, 3: 0}
        else:
            res = {}
        for m in members:
            th = m.town_hall
            if th not in res:
                res[th] = 0
            res[th] += 1
        return res

    @commands.group(name="plot")
    async def plot(self, ctx):
        """[Group] Create plots for RCS data
        """
        if ctx.invoked_subcommand is None:
            return await ctx.send_help(ctx.command)

    @plot.command(name="townhalls", aliases=["th", "ths"])
    async def plot_th(self, ctx, clan: ClanConverter = None):
        """Returns a bar chart of town hall levels for your clan"""
        members = await clan.get_detailed_members().flatten()
        data = self.breakdown(members)
        df = pd.DataFrame(data.items(), columns=["Town Hall", "Count"])
        df.plot(x="Town Hall", y="Count", kind="bar", xlabel="Town Hall Level", title=clan.name, legend=False, rot=0)
        plt.savefig(fname='plot')
        await ctx.send(file=discord.File('plot.png'))

    @plot.command(name="war_th", aliases=["warth", ])
    async def plot_war_th(self, ctx, clan: ClanConverter = None):
        """Returns a bar chart of town halls for both clans in war"""
        if not clan:
            return await ctx.send("Please provide a valid RCS clan")
        war = await self.bot.coc.get_current_war(clan.tag)
        if war.state in ["notInWar", "warEnded"]:
            return await ctx.send(f"{clan.name} is not currently in a war.")
        clan_members = war.clan.members
        oppo_members = war.opponent.members
        index = [13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3]
        clan_th = list(self.breakdown(clan_members, blanks=True).values())
        oppo_th = list(self.breakdown(oppo_members, blanks=True).values())
        df = pd.DataFrame({war.clan.name: clan_th, war.opponent.name: oppo_th}, index=index)
        df.plot(kind="bar", rot=0, xlabel="Town Hall Level")
        plt.savefig(fname='plot')
        await ctx.send(file=discord.File('plot.png'))

    @plot.command(name="trophyattack")
    async def plot_trophy_attack(self, ctx):
        """Correlation plot for all RCS clans. Determines connections between trophy count and attack wins."""
        await ctx.send("Sit tight! This one takes about 70 seconds.", delete_after=60.0)
        trophies = []
        attack_wins = []
        async with ctx.typing():
            for tag in rcs_tags(prefix=True):
                clan = await self.bot.coc.get_clan(tag)
                async for member in clan.get_detailed_members():
                    if member.trophies > 500 and member.attack_wins > 0:
                        trophies.append(member.trophies)
                        attack_wins.append(member.attack_wins)
        df = pd.DataFrame({"Trophy Count": trophies, "Attack Wins": attack_wins})
        df.plot(kind="scatter", y="Attack Wins", x="Trophy Count")
        plt.savefig(fname='plot')
        await ctx.send(file=discord.File('plot.png'))

    @plot.command(name="by_teamsize", aliases=["avg", ])
    async def plot_by_teamsize(self, ctx, clan: ClanConverter = None):
        """Returns a line chart of average stars and attacks
        based on the team size of the war"""
        if not clan:
            return await ctx.send("Please provide a valid RCS clan")
        sql = (f"SELECT clan_tag, AVG(clan_stars) as avg_stars, team_size * 3 AS max_stars, "
               f"AVG(clan_attacks) AS avg_attacks, team_size * 2 AS max_attacks, team_size FROM rcs_wars "
               f"WHERE war_type = 'random' "
               f"AND war_state = 'warEnded' "
               f"AND clan_tag in (SELECT clan_tag FROM rcs_clans) "
               f"GROUP BY clan_tag, team_size "
               f"ORDER BY clan_tag, team_size")
        df = await self.fetch_as_dataframe(sql)
        df = df[df['clan_tag'] == clan.tag[1:]]
        df = df.astype({"avg_stars": 'float', "avg_attacks": 'float'})
        sizes = [i for i in range(50, 0, -5)]
        min_size = df["team_size"].min()
        max_size = df['team_size'].max()
        for i in sizes:
            if i < min_size or i > max_size:
                sizes.remove(i)
        df.plot(x="team_size", y=["avg_stars", "max_stars", "avg_attacks", "max_attacks"],
                color=["#0000FF", "#C0C0FF", "#FF8900", "#FFD8A9"], title=clan.name,
                xlabel="Team Size", xticks=sizes, style=".-")
        plt.legend(["Avg Stars", "Max Stars", "Avg Attacks", "Max Attacks"])
        plt.savefig(fname='plot')
        await ctx.send(file=discord.File('plot.png'))


def setup(bot):
    bot.add_cog(Plots(bot))
