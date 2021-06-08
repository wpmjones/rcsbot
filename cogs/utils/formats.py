import textwrap

from cogs.utils.paginator import Pages
from config import emojis


def get_render_type(table, type_):
    board_choice = {
        "attacks": (table.board_1, "Att"),
        "defenses": (table.board_1, "Def"),
        "donations": (table.board_2, "Don", "Rec"),
        "donates": (table.board_1, "Don"),
        "trophies": (table.board_1, "Cups"),
        "besttrophies": (table.board_1, "Cups"),
        "bhtrophies": (table.board_1, "vsCups"),
        "warstars": (table.board_1, "Stars"),
        "games": (table.board_1, "Points"),
        "games all": (table.board_1, "Points"),
        "games average": (table.board_1, "Avg"),
        "games clan": (table.board_1, "Points"),
        "games top": (table.board_1, "Points"),
        "top attacks": (table.board_1, "Att"),
        "top defenses": (table.board_1, "Def"),
        "top donates": (table.board_1, "Don"),
        "top warstars": (table.board_1, "Stars"),
        "top trophies": (table.board_1, "Cups"),
        "top bhtrophies": (table.board_1, "Cups"),
        "top besttrophies": (table.board_1, "Cups"),
        "top games": (table.board_1, "Pts"),
        "townhalls": (table.board_3, ),
        "builderhalls": (table.board_4, ),
        "push all": (table.board_1, "Points"),
        "push diff": (table.board_1, "Diff"),
        "push top": (table.board_1, "Cups"),
        "push th": (table.board_5, "Cups", "Pts"),
        "push th14": (table.board_5, "Cups", "Pts"),
        "push th13": (table.board_5, "Cups", "Pts"),
        "push th12": (table.board_5, "Cups", "Pts"),
        "push th11": (table.board_5, "Cups", "Pts"),
        "push th10": (table.board_5, "Cups", "Pts"),
        "push th9": (table.board_5, "Cups", "Pts"),
        "push th8": (table.board_5, "Cups", "Pts"),
        "push th7": (table.board_5, "Cups", "Pts"),
        "push gain": (table.board_1, "Gain"),
        "push clan": (table.board_1, "Points"),
    }
    func, *args = board_choice.get(type_, (table.board_1, ""))

    return func(*args)


class plural:
    def __init__(self, value):
        self.value = value

    def __format__(self, format_spec):
        v = self.value
        singular, sep, plural = format_spec.partition('|')
        plural = plural or f'{singular}s'
        if abs(v) != 1:
            return f'{v} {plural}'
        return f'{v} {singular}'


def human_join(seq, delim=', ', final='or'):
    size = len(seq)
    if size == 0:
        return ''

    if size == 1:
        return seq[0]

    if size == 2:
        return f'{seq[0]} {final} {seq[1]}'

    return delim.join(seq[:-1]) + f' {final} {seq[-1]}'


class TabularData:
    def __init__(self):
        self._widths = []
        self._columns = []
        self._rows = []

    def set_columns(self, columns):
        self._columns = columns
        self._widths = [len(c) + 2 for c in columns]

    def add_row(self, row):
        rows = [str(r) for r in row]
        self._rows.append(rows)
        for index, element in enumerate(rows):
            width = len(element) + 2
            if width > self._widths[index]:
                self._widths[index] = width

    def add_rows(self, rows):
        for row in rows:
            self.add_row(row)

    def render(self):
        """Renders a table in rST format.

        Example:

        +-------+-----+
        | Name  | Age |
        +-------+-----+
        | Alice | 24  |
        |  Bob  | 19  |
        +-------+-----+
        """

        sep = '+'.join('-' * w for w in self._widths)
        sep = f'+{sep}+'

        to_draw = [sep]

        def get_entry(d):
            elem = '|'.join(f'{e:^{self._widths[i]}}' for i, e in enumerate(d))
            return f'|{elem}|'

        to_draw.append(get_entry(self._columns))
        to_draw.append(sep)

        for row in self._rows:
            to_draw.append(get_entry(row))

        to_draw.append(sep)
        return '\n'.join(to_draw)


class CLYTable:
    def __init__(self):
        self._widths = []
        self._rows = []

    def add_row(self, row):
        rows = [str(r) for r in row]
        self._rows.append(rows)

    def add_rows(self, rows):
        for row in rows:
            self.add_row(row)

    def clear_rows(self):
        self._rows = []

    def board_1(self, category):
        fmt = f"{emojis['other']['num']}`⠀{category:\u00A0>6.6}⠀` `⠀{'Name':\u00A0>22.22}⠀`\n"
        for v in self._rows:
            index = int(v[0]) + 1
            index = emojis['level'][index]  # if index <= 100 else misc['idle']
            fmt += f"{index}`⠀{str(v[1]):\u00A0>6.6}⠀` `⠀{str(v[2]):\u00A0>22.22}⠀`\n"
        return fmt

    def board_2(self, category_1, category_2):
        fmt = f"{emojis['other']['num']}`⠀{category_1:\u00A0>6.6}⠀` `⠀{category_2:\u00A0>5.5}⠀` `⠀{'Name':\u00A0>16.16}⠀`\n"
        for v in self._rows:
            index = int(v[0]) + 1
            index = emojis['level'][index]  # if index <= 100 else misc['idle']
            fmt += f"{index}`⠀{str(v[1]):\u00A0>6.6}⠀` `⠀{str(v[2]):\u00A0>5.5}⠀` `⠀{str(v[3]):\u00A0>16.16}⠀`\n"
        return fmt

    def board_3(self):
        fmt = ""
        for v in self._rows:
            fmt += f"{emojis['th_icon'][int(v[0])]}`⠀{str(v[1]):\u00A0<27.27}⠀`\n"
        return fmt

    def board_4(self):
        fmt = ""
        for v in self._rows:
            fmt += f"{emojis['th'][int(v[0])]}`⠀{str(v[1]):\u00A0<27.27}⠀`\n"
        return fmt

    def board_5(self, category_1, category_2):
        fmt = f"{emojis['other']['num']}`⠀{category_1:\u00A0>4.4}⠀` `⠀{category_2:\u00A0>5.5}⠀` `⠀{'Name':\u00A0>18.18}⠀`\n"
        for v in self._rows:
            index = int(v[0]) + 1
            index = emojis['level'][index]  # if index <= 100 else misc['idle']
            fmt += f"{index}`⠀{str(v[1]):\u00A0>4.4}⠀` `⠀{str(v[2]):\u00A0>5.5}⠀` `⠀{str(v[3]):\u00A0>18.18}⠀`\n"
        return fmt


class TablePaginator(Pages):
    def __init__(self, ctx, data, title=None, page_count=1, rows_per_table=25):
        super().__init__(ctx, entries=[i for i in range(page_count)], per_page=1)
        self.table = CLYTable()
        self.data = [(i, v) for (i, v) in enumerate(data)]
        self.entries = [None for _ in range(page_count)]
        self.rows_per_table = rows_per_table
        self.title = title
        self.message = None
        self.ctx = ctx
        self.type_ = ctx.command.qualified_name

    async def get_page(self, page):
        entry = self.entries[page - 1]
        if entry:
            return entry

        if not self.message:
            self.message = await self.channel.send('Loading...')
        else:
            await self.message.edit(content='Loading...', embed=None)

        entry = await self.prepare_entry(page)
        self.entries[page - 1] = entry
        return self.entries[page - 1]

    def create_row(self, data):
        row = [data[0], data[1][0], data[1][1]]
        if self.type_.startswith("push th"):
            row = [data[0], data[1][0], data[1][1], data[1][2]]
        elif self.type_ in ("townhalls",
                            "builderhalls",
                            ):
            row = [data[1][0], data[1][1]]
        elif self.type_ in ("donations",):
            row = [data[0], data[1][0], data[1][1], data[1][2]]

        self.table.add_row(row)

    async def prepare_entry(self, page):
        self.table.clear_rows()
        base = (page - 1) * self.rows_per_table
        data = self.data[base:base + self.rows_per_table]
        for n in data:
            self.create_row(n)

        render = get_render_type(self.table, self.type_)
        return render

    async def get_embed(self, entries, page, *, first=False):
        if self.maximum_pages > 1:
            if self.show_entry_count:
                text = f'Page {page}/{self.maximum_pages} ({len(self.entries)} entries)'
            else:
                text = f'Page {page}/{self.maximum_pages}'

            self.embed.set_footer(text=text)

        self.embed.description = entries

        self.embed.set_author(name=textwrap.shorten(self.title, width=240, placeholder="..."),
                              icon_url=self.ctx.icon)

        return self.embed

    async def show_page(self, page, *, first=False):
        self.current_page = page
        entries = await self.get_page(page)
        embed = await self.get_embed(entries, page, first=first)

        if not self.paginating:
            return await self.message.edit(content=None, embed=embed)

        await self.message.edit(content=None, embed=embed)

        if not first:
            return

        for (reaction, _) in self.reaction_emojis:
            if self.maximum_pages == 2 and reaction in ('\u23ed', '\u23ee'):
                # no |<< or >>| buttons if we only have two pages
                # we can't forbid it if someone ends up using it but remove
                # it from the default set
                continue

            await self.message.add_reaction(reaction)


class TopTenPaginator(TablePaginator):
    def __init__(self, ctx, data):
        super().__init__(ctx, data, title=None, page_count=8, rows_per_table=10)
        self.data = data
        self.title_prefix = "RCS Push Top Ten for TH"
        self.th_by_page = {1: 14, 2: 13, 3: 12, 4: 11, 5: 10, 6: 9, 7: 8, 8: 7}

    def create_row(self, data):
        row = [data[0], data[1][0], data[1][1]]
        self.table.add_row(row)

    async def prepare_entry(self, page):
        self.table.clear_rows()
        base = (page - 1) * self.rows_per_table
        data = self.data[base:base + self.rows_per_table]
        data = [(i, v) for (i, v) in enumerate(data)]
        for n in data:
            self.create_row(n)

        render = get_render_type(self.table, self.type_)
        return render

    async def get_embed(self, entries, page, *, first=False):
        if self.maximum_pages > 1:
            if self.show_entry_count:
                text = f'Page {page}/{self.maximum_pages} ({len(self.entries)} entries)'
            else:
                text = f'Page {page}/{self.maximum_pages}'

            self.embed.set_footer(text=text)

        self.embed.description = entries
        self.title = f"{self.title_prefix}{self.th_by_page[page]}"

        self.embed.set_author(name=textwrap.shorten(self.title, width=240, placeholder="..."),
                              icon_url=self.ctx.icon)

        return self.embed
