"""Карточки для поиска по отрядам: замены персонажей и порядок инвестиций.

    from gi_damage.visual import SearchBook

    book = SearchBook()
    book.add_alternatives(report, "Замены Крио ГГ")
    book.add_plan(plan, "Порядок инвестиций")
    book.save("search.html")
"""

from __future__ import annotations

import html
from pathlib import Path
from typing import List, Optional, Sequence

from .cards import (CSS, HEADER_COLORS, HEADER_TEXT, _character_column, fmt,
                    split_weapon)
from .icons import IconStore
from .rosters import ROSTER_CSS, _artifacts_html, _weapon_html

SEARCH_CSS = """
.ic.sm{width:32px;height:32px;border-radius:5px}
.ic.sm .badge{font-size:9px;padding:0 3px}
.ic.md{width:44px;height:44px}
.hold{display:flex;gap:4px;flex-wrap:wrap;max-width:300px}
.chgs{display:flex;flex-direction:column;gap:2px;font-size:12px}
.chgs span{display:flex;align-items:center;gap:6px;white-space:nowrap}
.pos{color:#7ed39a}.neg{color:#e5766f}
.rt tr.base td{background:#17202a}
.tag{font-size:10px;padding:0 5px;border-radius:3px;background:#2a3a4a;color:#bcd}
.who2{display:flex;align-items:center;gap:8px;font-weight:600}
"""


def _pct(x: float) -> str:
    return f"{x:+.1f}%"


def _colors(index: int):
    return (HEADER_COLORS[index % len(HEADER_COLORS)],
            HEADER_TEXT[index % len(HEADER_TEXT)])


# --------------------------------------------------------------------------- #
#  Замены                                                                     #
# --------------------------------------------------------------------------- #
def render_alternatives(report, title: str = "", store: Optional[IconStore] = None,
                        index: int = 0, ascending: bool = False,
                        notes: Sequence[str] = ()) -> str:
    store = store or IconStore()
    key = report.key
    base_name = report.base_build.name
    units = "".join(_character_column(n, s, store)
                    for n, s in report.baseline.setup.items() if n != base_name)

    ranked = report.ranked(ascending)
    best = max(r.value(key) for r in ranked) or 1.0
    base = report.baseline_value
    rows, prev = [], None
    for rank, r in enumerate(ranked, start=1):
        s = r.result.setup.get(r.build.name)
        v = r.value(key)
        d = (v / base - 1) * 100 if base else 0.0
        step = f"{v / prev * 100:.1f}%" if prev else "—"
        prev = v
        cls = "base" if r.is_baseline else ("best" if v == best else "")
        tag = " <span class='tag'>база</span>" if r.is_baseline else ""
        if s is None:
            continue
        weapon_name, _ = split_weapon(s.weapon)
        arts = " + ".join(a for a in (s.artifacts or "").split("/") if a) or "—"
        rows.append(
            f"<tr class='{cls}'><td class='rk'>{rank}</td>"
            f"<td class='v'><div class='who2'><div class='ic md'>"
            f"{store.img('characters', r.build.name, 'pic')}"
            f"<span class='badge bc'>C{s.constellation}</span></div>"
            f"{html.escape(r.build.name)}{tag}</div></td>"
            f"<td class='v'><div class='vcell'>{_weapon_html(s.weapon, store, 'weapon sm')}"
            f"<span>{html.escape(weapon_name or '—')}</span></div></td>"
            f"<td class='v'><div class='vcell'>{_artifacts_html(s.artifacts, store)}"
            f"<span>{html.escape(arts)}</span></div></td>"
            f"<td class='num'>{fmt(r.result.dpr)}</td>"
            f"<td class='num bar'>{fmt(r.result.dps)}<i style='width:{v / best * 100:.1f}%'></i></td>"
            f"<td class='num'>{v / best * 100:.1f}%</td>"
            f"<td class='num {'pos' if d > 0.05 else 'neg' if d < -0.05 else ''}'>{_pct(d)}</td>"
            f"<td class='num'>{step}</td></tr>")
    table = ("<table class='rt'><thead><tr><th class='rk'>#</th><th class='v'>Персонаж</th>"
             "<th class='v'>Оружие</th><th class='v'>Артефакты</th><th>DPR</th>"
             f"<th>{key.upper()}</th><th>% от лучшего</th><th>к базе</th>"
             f"<th>% от предыдущего</th></tr></thead><tbody>{''.join(rows)}</tbody></table>")

    extra = "".join(f"<li>{html.escape(t)}</li>" for t in notes)
    notes_html = f"<ul class='rnotes'>{extra}</ul>" if extra else ""
    rot = (f"<p class='rot'>{html.escape(report.baseline.rotation)}</p>"
           if report.baseline.rotation else "")
    bg, fg = _colors(index)
    head = title or f"Замены слота «{report.slot}»"
    return f"""
<section class="card rcard">
  <h2 style="background:{bg};color:{fg}">{html.escape(head)}</h2>
  <div class="rbody">
    <div class="units">{units}</div>
    <div class="rtable">{table}{notes_html}</div>
  </div>
  {rot}
</section>"""


# --------------------------------------------------------------------------- #
#  Порядок инвестиций                                                         #
# --------------------------------------------------------------------------- #
def _holding_html(h, store: IconStore) -> str:
    if h.kind == "character":
        img, badge = store.img("characters", h.name, "pic"), f"<span class='badge bc'>C{h.level}</span>"
    else:
        img, badge = store.img("weapons", h.name, "pic"), f"<span class='badge br'>R{h.level}</span>"
    return f"<div class='ic sm' title='{html.escape(h.label, quote=True)}'>{img}{badge}</div>"


def _change_html(c, store: IconStore) -> str:
    kind = "characters" if c.kind == "character" else "weapons"
    p = "C" if c.kind == "character" else "R"
    f = lambda x: "—" if x is None else f"{p}{x}"
    return (f"<span><div class='ic sm'>{store.img(kind, c.name, 'pic')}</div>"
            f"{html.escape(c.name)}: {f(c.old)} → <b>{f(c.new)}</b></span>")


def render_plan(plan, title: str = "", store: Optional[IconStore] = None,
                index: int = 0, notes: Sequence[str] = ()) -> str:
    store = store or IconStore()
    top = plan.best_value or 1.0
    rows = []
    for lv in plan.levels:
        a = lv.best
        hold = "".join(_holding_html(h, store) for h in plan.holdings(a.state))
        step = ("".join(_change_html(c, store) for c in lv.changes)
                or "<span>базовая линия</span>")
        tip = " | ".join(
            f"{', '.join(h.label for h in plan.holdings(r.state))}: {fmt(r.value)}"
            for r in lv.runners_up)
        tip_attr = f" title='{html.escape('Запасные: ' + tip, quote=True)}'" if tip else ""
        delta = ("—" if lv.cost == 0 else
                 f"<span class='{'pos' if lv.delta_pct > 0.05 else 'neg' if lv.delta_pct < -0.05 else ''}'>"
                 f"{_pct(lv.delta_pct)}</span>")
        rows.append(
            f"<tr{tip_attr}><td class='rk'>{lv.cost}</td>"
            f"<td class='v'><div class='chgs'>{step}</div></td>"
            f"<td class='v'><div class='hold'>{hold}</div></td>"
            f"<td class='num'>{fmt(a.result.dpr)}</td>"
            f"<td class='num bar'>{fmt(a.result.dps)}<i style='width:{a.value / top * 100:.1f}%'></i></td>"
            f"<td class='num'>{delta}</td>"
            f"<td class='num'>{a.value / top * 100:.1f}%</td></tr>")
    key = plan.key.upper()
    table = ("<table class='rt'><thead><tr><th class='rk'>Кост</th><th class='v'>Что докупить</th>"
             f"<th class='v'>Всего куплено</th><th>DPR</th><th>{key}</th>"
             "<th>к предыдущему</th><th>% от макс.</th></tr></thead>"
             f"<tbody>{''.join(rows)}</tbody></table>")
    extra = "".join(f"<li>{html.escape(t)}</li>" for t in notes)
    notes_html = f"<ul class='rnotes'>{extra}</ul>" if extra else ""
    bg, fg = _colors(index)
    return f"""
<section class="card rcard">
  <h2 style="background:{bg};color:{fg}">{html.escape(title or 'Порядок инвестиций')}</h2>
  <div class="rbody"><div class="rtable">{table}{notes_html}</div></div>
</section>"""


# --------------------------------------------------------------------------- #
class SearchBook:
    """Копилка карточек поиска: печатает текстовый отчёт и копит HTML."""

    def __init__(self, store: Optional[IconStore] = None):
        self.store = store or IconStore()
        self._cards: List[str] = []

    def add_alternatives(self, report, title: str = "", ascending: bool = False,
                         print_text: bool = True, notes: Sequence[str] = ()):
        if print_text:
            from ..core.search import alternatives_report
            print(alternatives_report(report, ascending=ascending))
            print()
        self._cards.append(render_alternatives(report, title, self.store,
                                               len(self._cards), ascending, notes))
        return report

    def add_plan(self, plan, title: str = "", print_text: bool = True,
                 notes: Sequence[str] = ()):
        if print_text:
            from ..core.search import plan_report
            print(plan_report(plan))
            print()
        self._cards.append(render_plan(plan, title, self.store, len(self._cards), notes))
        return plan

    def render(self, title: str = "Поиск по отрядам", columns: int = 1) -> str:
        return (f'<!doctype html><html lang="ru"><head><meta charset="utf-8">'
                f'<meta name="viewport" content="width=device-width,initial-scale=1">'
                f'<title>{html.escape(title)}</title>'
                f'<style>{CSS}{ROSTER_CSS}{SEARCH_CSS}</style></head><body>'
                f'<h1>{html.escape(title)}</h1>'
                f'<div class="rgrid" style="--cols:{max(1, columns)}">{"".join(self._cards)}</div>'
                f'</body></html>')

    def save(self, path: str | Path, title: str = "Поиск по отрядам", columns: int = 1) -> Path:
        path = Path(path)
        path.write_text(self.render(title, columns), encoding="utf-8")
        return path