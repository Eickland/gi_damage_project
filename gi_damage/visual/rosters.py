"""Карточки ростеров: один отряд, у которого перебирают оружие, артефакты
или созвездия, — рейтинг вариантов с иконками.

Как и текстовый `roster_report`, модуль сам определяет, что в переборе
постоянно, а что меняется, сравнивая раскладки (`TeamResult.setup`).

    from gi_damage.visual import RosterBook

    book = RosterBook()
    book.add(roster, "оружие Мидзуки (C2)")       # печатает текст и запоминает
    book.add(roster2, "созвездия Мидзуки")
    book.save("rosters.html")
"""

from __future__ import annotations

import html
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

from .cards import CSS, fmt, split_weapon
from .icons import IconStore

#: какие поля раскладки сравниваем (время ротации сознательно не берём:
#: оно меняется «вслед» за созвездием, но отдельным вариантом не является)
FIELDS = ("constellation", "weapon", "artifacts")
FIELD_LABEL = {"constellation": "созвездие", "weapon": "оружие",
               "artifacts": "артефакты"}


# --------------------------------------------------------------------------- #
def _val(setup, field: str):
    return getattr(setup, field) if setup is not None else None


def analyze(results: Sequence):
    """-> (имена персонажей, {(имя, поле): значение} постоянное, [(имя, поле)] меняющееся)."""
    names = list(dict.fromkeys(n for r in results for n in r.setup))
    const: Dict[Tuple[str, str], object] = {}
    vary: List[Tuple[str, str]] = []
    for n in names:
        for f in FIELDS:
            values = {_val(r.setup.get(n), f) for r in results}
            if len(values) == 1:
                const[(n, f)] = values.pop()
            else:
                vary.append((n, f))
    return names, const, vary


# --------------------------------------------------------------------------- #
def _weapon_html(label: str, store: IconStore, size_cls: str = "weapon") -> str:
    name, ref = split_weapon(label or "")
    if not name:
        return '<div class="ic weapon none">—</div>'
    badge = f'<span class="badge br">R{ref}</span>' if ref else ""
    return (f'<div class="ic {size_cls}">{store.img("weapons", name, "pic")}{badge}</div>')


def _artifacts_html(label: str, store: IconStore) -> str:
    arts = [a for a in (label or "").split("/") if a]
    if not arts:
        return '<div class="ic art none">—</div>'
    return "".join(f'<div class="ic art">{store.img("artifacts", a, "pic")}</div>'
                   for a in arts)


def _const_unit(name: str, const: Dict, vary: Sequence, store: IconStore) -> str:
    changing = {f for (n, f) in vary if n == name}
    badge = (f'<span class="badge bc">C{const[(name, "constellation")]}</span>'
             if ("constellation" not in changing
                 and (name, "constellation") in const) else "")
    rows = [f'<div class="ic portrait">{store.img("characters", name, "pic")}{badge}</div>']

    if "weapon" in changing:
        rows.append('<div class="ic weapon var">↔</div>')
        caption = ""
    else:
        label = const.get((name, "weapon")) or ""
        rows.append(_weapon_html(label, store))
        caption = split_weapon(label)[0] or "—"

    if "artifacts" in changing:
        rows.append('<div class="ic art var">↔</div>')
        arts_caption = "артефакты меняются"
    else:
        label = const.get((name, "artifacts")) or ""
        rows.append(f'<div class="arts">{_artifacts_html(label, store)}</div>')
        arts_caption = " + ".join(a for a in label.split("/") if a) or "—"

    if "constellation" in changing:
        caption = f" · {caption}" if "weapon" not in changing else "·"

    cls = "unit chg" if changing else "unit"
    return (f'<div class="{cls}">{"".join(rows)}'
            f'<div class="wname">{html.escape(caption)}</div>'
            f'<div class="aname">{html.escape(arts_caption)}</div></div>')


def _cell(name: str, field: str, setup, store: IconStore) -> str:
    if setup is None:
        return "<td class='v'>—</td>"
    if field == "constellation":
        return f"<td class='v'><span class='chip'>C{setup.constellation}</span></td>"
    if field == "weapon":
        wname, _ = split_weapon(setup.weapon)
        return (f"<td class='v'><div class='vcell'>{_weapon_html(setup.weapon, store, 'weapon sm')}"
                f"<span>{html.escape(wname or '—')}</span></div></td>")
    arts = [a for a in (setup.artifacts or "").split("/") if a]
    return (f"<td class='v'><div class='vcell'>{_artifacts_html(setup.artifacts, store)}"
            f"<span>{html.escape(' + '.join(arts) or '—')}</span></div></td>")


# --------------------------------------------------------------------------- #
def render_roster(results: Sequence, title: str = "", key: str = "dps",
                  ascending: bool = False, store: Optional[IconStore] = None,
                  index: int = 0, notes: Sequence[str] = ()) -> str:
    """HTML одной карточки-рейтинга."""
    store = store or IconStore()
    if not results:
        return f"<section class='rcard'><h2>{html.escape(title)}</h2><p class='rot'>нет вариантов</p></section>"

    names, const, vary = analyze(results)
    units = "".join(_const_unit(n, const, vary, store) for n in names)

    if not vary:
        table = "<p class='rot'>Меняется: ничего — все варианты одинаковы.</p>"
    else:
        order = sorted(range(len(results)),
                       key=lambda i: getattr(results[i], key),
                       reverse=not ascending)
        best = max(getattr(r, key) for r in results) or 1.0
        head = "".join(
            "<th class='v'>"
            + f"<span class='who'>{store.img('characters', n, 'pic')}</span>"
            + f"{FIELD_LABEL[f]}</th>"
            for n, f in vary)

        rows, prev = [], None
        for rank, i in enumerate(order, start=1):
            r = results[i]
            value = getattr(r, key)
            cells = "".join(_cell(n, f, r.setup.get(n), store) for n, f in vary)
            step = f"{value / prev * 100:.1f}%" if prev else "—"
            prev = value
            is_best = value == best
            rows.append(
                f"<tr class='{'best' if is_best else ''}'><td class='rk'>{rank}</td>{cells}"
                f"<td class='num'>{fmt(r.dpr)}</td>"
                f"<td class='num bar'>{fmt(r.dps)}<i style='width:{value / best * 100:.1f}%'></i></td>"
                f"<td class='num'>{value / best * 100:.1f}%</td>"
                f"<td class='num'>{step}</td></tr>")
        table = (f"<table class='rt'><thead><tr><th class='rk'>#</th>{head}"
                 f"<th>DPR</th><th>{key.upper()}</th><th>% от лучшего</th>"
                 f"<th>% от предыдущего</th></tr></thead><tbody>{''.join(rows)}</tbody></table>")

    extra = "".join(f"<li>{html.escape(t)}</li>" for t in notes)
    rot = results[0].rotation
    foot = (f"<p class='rot'>{html.escape(rot)}</p>" if rot else "")
    notes_html = f"<ul class='rnotes'>{extra}</ul>" if extra else ""

    from .cards import HEADER_COLORS, HEADER_TEXT
    bg = HEADER_COLORS[index % len(HEADER_COLORS)]
    fg = HEADER_TEXT[index % len(HEADER_TEXT)]
    return f"""
<section class="card rcard">
  <h2 style="background:{bg};color:{fg}">{html.escape(title or results[0].team_name)}</h2>
  <div class="rbody">
    <div class="units">{units}</div>
    <div class="rtable">{table}{notes_html}</div>
  </div>
  {foot}
</section>"""


# --------------------------------------------------------------------------- #
ROSTER_CSS = """
.rgrid{display:grid;gap:14px;padding:16px 20px 28px;
  grid-template-columns:repeat(var(--cols,1),minmax(0,1fr))}
.rbody{display:flex;gap:14px;padding:10px;flex-wrap:wrap;align-items:flex-start}
.rtable{flex:0 1 auto;min-width:0;overflow-x:auto}
.unit.chg .portrait{border-color:#c9833a}
.ic.var{display:flex;align-items:center;justify-content:center;border-style:dashed;
  color:var(--mute);font-size:18px}
.ic.none{display:flex;align-items:center;justify-content:center;color:var(--mute)}
.ic.weapon.sm{width:40px;height:40px}
.rt th.v{text-align:left}
.rt th.rk,.rt td.rk{width:34px;text-align:center;color:var(--mute)}
.rt td.v{padding:4px 8px}
.rt th.v, .rt td.v{width:1%;white-space:nowrap}
.vcell{display:flex;align-items:center;gap:6px}
.vcell span{font-size:12px}
.vcell .ic.art{width:36px;height:36px}
.who{display:inline-block;width:20px;height:20px;border-radius:50%;overflow:hidden;
  vertical-align:middle;margin-right:6px}
.who .pic{width:100%;height:100%;object-fit:cover;display:block}
.chip{display:inline-block;padding:1px 8px;border-radius:3px;background:#2a2b33;font-weight:700}
.rt tr.best td{background:#2a1215}
.rt tr.best td.rk{color:var(--ink);font-weight:700}
.rt td.bar{position:relative}
.rt td.bar i{position:absolute;left:0;bottom:0;height:3px;background:var(--bar)}
.rnotes{margin:8px 0 0;padding:0 0 0 18px;font-size:12px;color:var(--mute)}
@media(max-width:900px){.rgrid{grid-template-columns:1fr}}
"""


def render_page(sections: Sequence, title: str = "Ростеры", columns: int = 1,
                store: Optional[IconStore] = None) -> str:
    """sections: [(заголовок, [TeamResult], key, ascending) | + notes]."""
    store = store or IconStore()
    cards = []
    for i, sec in enumerate(sections):
        sec_title, results, key, ascending = sec[:4]
        notes = sec[4] if len(sec) > 4 else ()
        cards.append(render_roster(results, sec_title, key, ascending, store, i, notes))
    return (f'<!doctype html><html lang="ru"><head><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>{html.escape(title)}</title><style>{CSS}{ROSTER_CSS}</style></head><body>'
            f'<h1>{html.escape(title)}</h1>'
            f'<div class="rgrid" style="--cols:{max(1, columns)}">{"".join(cards)}</div>'
            f'</body></html>')


# --------------------------------------------------------------------------- #
class RosterBook:
    """Копилка ростеров: считает, (по желанию) печатает старый текстовый отчёт
    и копит данные для HTML.

        book = RosterBook()
        book.add(roster, "оружие Мидзуки (C2)")
        book.save("rosters.html")
    """

    def __init__(self, store: Optional[IconStore] = None):
        self.store = store or IconStore()
        self.sections: List[tuple] = []

    def add(self, roster_or_results, title: str, key: str = "dps",
            ascending: bool = True, print_text: bool = True,
            notes: Sequence[str] = ()) -> List:
        results = (roster_or_results.run() if hasattr(roster_or_results, "run")
                   else list(roster_or_results))
        if print_text:
            from ..core.report import roster_report
            print("========================")
            print(f"=== Ростер: {title} ===")
            print(roster_report(results, key=key, title=title, ascending=ascending))
            print()
        self.sections.append((title, results, key, ascending, tuple(notes)))
        return results

    def save(self, path: str | Path, title: str = "Ростеры", columns: int = 1) -> Path:
        path = Path(path)
        path.write_text(render_page(self.sections, title, columns, self.store),
                        encoding="utf-8")
        return path


def save_rosters(sections: Sequence, path: str | Path, title: str = "Ростеры",
                 columns: int = 1, store: Optional[IconStore] = None) -> Path:
    path = Path(path)
    path.write_text(render_page(sections, title, columns, store), encoding="utf-8")
    return path