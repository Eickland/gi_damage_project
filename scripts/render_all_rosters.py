#!/usr/bin/env python3
"""Все ростеры звёздных отрядов в одном HTML.

    python -m scripts.render_all_rosters                  # «ростеры звездных команд.html»
    python -m scripts.render_all_rosters --out my.html
    python -m scripts.render_all_rosters --only sandrone  # только отряды, чьё имя содержит строку

Отряды и разделы — те же, что в scripts/render_new_teams_pdf.py (GROUPS).
Для каждого отряда — стандартные ростеры (созвездия / оружие / артефакты
каждого персонажа, gi_damage/visual/standard_rosters.py) и особые секции из
его rosters.py (функция extra, если есть).

Чтобы файл не раздувался, каждая иконка хранится в нём ОДИН раз (в конце
страницы), а картинки ссылаются на неё по номеру — без этого общий файл
весил бы сотни мегабайт. Отряды свёрнуты: раскрываются по клику, есть
оглавление и кнопки «развернуть/свернуть всё».
"""

from __future__ import annotations

import argparse
import contextlib
import html
import importlib
import io
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from gi_damage.visual.cards import CSS, fmt
from gi_damage.visual.icons import IconStore
from gi_damage.visual.rosters import ROSTER_CSS, RosterBook, render_roster, render_swaps
from gi_damage.visual.standard_rosters import add_standard_sections
from scripts.render_new_teams_pdf import GROUPS

DEFAULT_OUT = "ростеры звездных команд.html"


class SharedIconStore(IconStore):
    """Иконки по номеру: <img data-i="N">, сами картинки — один раз в конце."""

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self.uris: list[str] = []
        self.index: dict[str, int] = {}

    def img(self, kind: str, name: str, css_class: str = "") -> str:
        uri = self.data_uri(kind, name)
        if not uri:
            return super().img(kind, name, css_class)
        if uri not in self.index:
            self.index[uri] = len(self.uris)
            self.uris.append(uri)
        title = html.escape(name, quote=True)
        return (f'<img class="{css_class}" data-i="{self.index[uri]}" '
                f'alt="{title}" title="{title}">')

    def script(self) -> str:
        return ("<script>const ICONS=" + json.dumps(self.uris) + ";"
                "document.querySelectorAll('img[data-i]').forEach(e=>{e.src=ICONS[+e.dataset.i];});"
                "</script>")


EXTRA_CSS = """
.toc{margin:8px 20px 18px;columns:3 320px;font-size:13px}
.toc h3{margin:10px 0 4px;color:var(--line);font-size:14px;break-after:avoid}
.toc a{color:var(--ink);text-decoration:none;display:block;padding:1px 0}
.toc a:hover{color:var(--line)}
.toc .d{color:var(--mute);float:right;font-variant-numeric:tabular-nums}
.tools{margin:0 20px 10px}
.tools button{background:#2a2b33;color:var(--ink);border:1px solid #444;border-radius:4px;
  padding:4px 10px;margin-right:6px;cursor:pointer}
h2.grp{margin:28px 20px 6px;font-size:22px;color:var(--line)}
details.team{margin:8px 20px;border:1px solid #33343c;border-radius:6px;background:#141519}
details.team>summary{cursor:pointer;padding:8px 12px;font-weight:700;font-size:15px;list-style:none}
details.team>summary::-webkit-details-marker{display:none}
details.team>summary:before{content:"▸ ";color:var(--line)}
details.team[open]>summary:before{content:"▾ "}
details.team>summary .d{float:right;color:var(--mute);font-weight:400}
details.team .folder{color:var(--mute);font-weight:400;font-size:12px;margin-left:8px}
details.team .rgrid{padding:0 8px 8px}
.err{color:#f08080;margin:4px 12px 10px}
"""


def team_list(only: str | None):
    for title, folders in GROUPS:
        seen = []
        for entry in folders:
            d = entry.split(":")[0]
            if d not in seen and (not only or only in d):
                seen.append(d)
        if seen:
            yield title, seen


def build_team(d: str):
    """(база TeamResult, RosterBook) для отряда d."""
    builds = importlib.import_module(f"gi_damage.teams.{d}.builds")
    try:
        rosters = importlib.import_module(f"gi_damage.teams.{d}.rosters")
    except ImportError:
        rosters = None
    base = next(iter(builds.all_teams().values()))
    book = RosterBook()
    with contextlib.redirect_stdout(io.StringIO()):
        add_standard_sections(book, builds, base, skip=getattr(rosters, "SKIP", ()))
        extra = getattr(rosters, "extra", None)
        if extra is not None:
            extra(book, base)
    return base.compute(), book


def render_book(book: RosterBook, store: IconStore, start: int) -> str:
    cards = []
    for i, sec in enumerate(book.sections):
        title, results, key, ascending = sec[:4]
        notes = sec[4] if len(sec) > 4 else ()
        kind = sec[5] if len(sec) > 5 else "roster"
        if kind == "swap":
            cards.append(render_swaps(results, title, key, ascending, store, start + i, notes))
        else:
            base = sec[6] if len(sec) > 6 else 0
            cards.append(render_roster(results, title, key, ascending, store, start + i,
                                       notes, base))
    return "".join(cards)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=DEFAULT_OUT)
    ap.add_argument("--only", default=None, help="фильтр по имени папки отряда")
    ap.add_argument("--columns", type=int, default=2, help="ростеров в ряд внутри отряда")
    args = ap.parse_args()

    store = SharedIconStore()
    toc, body, n_teams, n_sections = [], [], 0, 0
    for gtitle, folders in team_list(args.only):
        toc.append(f"<h3>{html.escape(gtitle)}</h3>")
        body.append(f"<h2 class='grp' id='g{len(toc)}'>{html.escape(gtitle)}</h2>")
        for d in folders:
            print(f"  {d} ...", end="", flush=True)
            try:
                base, book = build_team(d)
            except Exception as exc:
                print(f" ОШИБКА: {type(exc).__name__}: {exc}")
                body.append(f"<details class='team' id='{d}'><summary>{html.escape(d)}</summary>"
                            f"<p class='err'>Не собирается: {html.escape(type(exc).__name__)}: "
                            f"{html.escape(str(exc))}</p></details>")
                continue
            print(f" {len(book.sections)} ростеров")
            n_teams += 1
            n_sections += len(book.sections)
            toc.append(f"<a href='#{d}' onclick=\"document.getElementById('{d}').open=true\">"
                       f"{html.escape(base.team_name)}<span class='d'>{fmt(base.dps)}</span></a>")
            body.append(
                f"<details class='team' id='{d}'><summary>{html.escape(base.team_name)}"
                f"<span class='folder'>{d}</span><span class='d'>DPS {fmt(base.dps)} · "
                f"{base.rotation_time:g} с</span></summary>"
                f"<div class='rgrid' style='--cols:{max(1, args.columns)}'>"
                f"{render_book(book, store, n_sections)}</div></details>")

    title = "Ростеры звёздных команд"
    page = (f"<!doctype html><html lang='ru'><head><meta charset='utf-8'>"
            f"<meta name='viewport' content='width=device-width,initial-scale=1'>"
            f"<title>{title}</title><style>{CSS}{ROSTER_CSS}{EXTRA_CSS}</style></head><body>"
            f"<h1>{title}</h1>"
            f"<p class='rot' style='margin:0 20px 8px'>{n_teams} отрядов, {n_sections} ростеров. "
            f"База каждого отряда — первая команда из all_teams(); «% от базы» — к ней.</p>"
            f"<div class='tools'><button onclick=\"document.querySelectorAll('details.team')"
            f".forEach(e=>e.open=true)\">Развернуть всё</button>"
            f"<button onclick=\"document.querySelectorAll('details.team')"
            f".forEach(e=>e.open=false)\">Свернуть всё</button></div>"
            f"<nav class='toc'>{''.join(toc)}</nav>{''.join(body)}"
            f"{store.script()}</body></html>")
    out = Path(args.out)
    out.write_text(page, encoding="utf-8")
    print(f"HTML: {out.resolve()}  ({out.stat().st_size / 1e6:.1f} МБ, "
          f"иконок: {len(store.uris)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
