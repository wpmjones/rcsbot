import nextcord

from nextcord.ext import menus


class MainPageSource(menus.ListPageSource):
    def __init__(self, data):
        super().__init__(data, per_page=20)

    async def format_page(self, menu, entries):
        return "\n".join(entries)


class MainFieldPageSource(menus.ListPageSource):
    def __init__(self, data, title, per_page):
        super().__init__(data, per_page=per_page)
        self.title = title

    async def format_page(self, menu, entries):
        embed = nextcord.Embed(title=self.title)
        for entry in entries:
            embed.add_field(name=entry[0], value=entry[1], inline=True)
        embed.set_footer(text=f"Page {menu.current_page + 1}/{self.get_max_pages()}")
        return embed


class MainEmbedPageSource(menus.ListPageSource):
    def __init__(self, data, title, per_page):
        super().__init__(data, per_page=per_page)
        self.title = title

    async def format_page(self, menu, entries):
        embed = nextcord.Embed(title=self.title, description="\n".join(entries))
        embed.set_footer(text=f"Page {menu.current_page + 1}/{self.get_max_pages()}")
        return embed


class TopTenSource(menus.ListPageSource):
    def __init__(self, data):
        super().__init__(data, per_page=10)

    async def format_page(self, menu, entries):
        th_level = -1 * (menu.current_page - 15)
        embed = nextcord.Embed(title=f"Top Ten for TH{th_level}", description="\n".join(entries))
        embed.set_footer(text=f"Page {menu.current_page + 1}/{self.get_max_pages()}")
        return embed
