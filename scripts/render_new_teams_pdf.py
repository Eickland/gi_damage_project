#!/usr/bin/env python3
"""PDF со всеми отрядами с Даникой и Анастасией (все вариации из all_teams()).

    python -m scripts.render_new_teams_pdf                     # new_teams.pdf (+ .html)
    python -m scripts.render_new_teams_pdf --out my.pdf --columns 1
    python -m scripts.render_new_teams_pdf --html-only         # только HTML
    python -m scripts.render_new_teams_pdf --one               # по одной команде из отряда (первой)
    python -m scripts.render_new_teams_pdf --pick -1           # … или любой по номеру (-1 — последняя)

Структура: титульная сводка (все отряды, DPS по группам), дальше —
по разделу на каждого основного ДД, в разделе — карточки всех вариаций.

PDF печатается через playwright (как PNG в scripts/render_cards):
    pip install playwright && playwright install chromium
Без playwright скрипт сохранит только HTML — его можно напечатать в PDF
из браузера (Ctrl+P, «Сохранить как PDF», включить фон).
"""

from __future__ import annotations

import argparse
import html
import importlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from gi_damage.visual import IconStore
from gi_damage.visual.cards import CSS, fmt, render_card

#: (заголовок раздела, [папки в gi_damage/teams]).
#: «папка:функция» — взять отряды не из all_teams(), а из этой функции
#: (например, ростер замен swap_teams()).
GROUPS = (
    ("Сандроне", [
        "sandrone_odette_yae_danika",
        "sandrone_odette_alyosha_danika",
        "sandrone_odette_mitya_danika",
        "sandrone_anastasia_danika_odette",
        "sandrone_yae_danika_anastasia",
        "sandrone_anastasia_danika_mitya",
        "sandrone_anastasia_danika_alyosha",
        "sandrone_odette_yae_anastasia",
        "sandrone_odette_sucrose_alyosha:swap_teams",
    ]),
    ("Сайно", [
        "cyno_danika_yae_odette",
        "cyno_anastasia_danika_odette",
        "cyno_yae_danika_anastasia",
    ]),
    ("Митя (ДД)", [
        "mitya_danika_yae_odette",
        "mitya_anastasia_danika_odette",
        "mitya_anastasia_yae_odette",
    ]),
    ("Крио ГГ (ДД)", [
        "cryo_mc_yae_danika_odette",
        "cryo_mc_anastasia_danika_odette",
        "cryo_mc_anastasia_mitya_odette",
        "cryo_mc_anastasia_mitya_danika",
        "cryo_mc_anastasia_yae_odette",
    ]),
    ("Анастасия (ДД)", [
        "anastasia_dd_danika_mitya_odette",
        "anastasia_dd_danika_yae_odette",
        "anastasia_dd_danika_alyosha_odette",
        "anastasia_dd_sucrose_alyosha_diona",
    ]),
    ("Ризли", [
        "wriothesley_anastasia_danika_odette",
    ]),
    ("Весна", [
        "vesna_anastasia_vodya_odette",
        "vesna_anastasia_odette_faruzan",
        "vesna_anastasia_cmc_vodya",
    ]),
    ("Мидзуки", [
        "mizuki_anastasia_vodya_odette",
        "mizuki_anastasia_vodya_cmc",
        "mizuki_anastasia_odette_faruzan_sacfrag",
    ]),
)

#: ширина страницы PDF (px). На ней помещаются 2 карточки в ряд.
PAGE_WIDTH = 1700
PAGE_HEIGHT = 1150

PRINT_CSS = """
@page{size:{W}px {H}px;margin:0}
html,body{-webkit-print-color-adjust:exact;print-color-adjust:exact}
.card{break-inside:avoid;page-break-inside:avoid}
.body{flex-wrap:nowrap}
.mid{flex:1 1 250px;min-width:250px}
.mid th,.mid td{padding:4px 5px;white-space:nowrap;font-size:12.5px}
.info{flex:0 0 180px;min-width:180px}
.group{break-before:page;page-break-before:always}
.group h1{margin:18px 20px 0;font-size:22px}
.group .sub{margin:4px 20px 0;color:var(--mute);font-size:12px}
.cover h1{font-size:26px}
.cover .meta{margin:6px 20px 14px;color:var(--mute)}
.summary{margin:0 20px 24px;border-collapse:collapse;width:calc(100% - 40px)}
.summary th{text-align:left;padding:5px 8px}
.summary td{padding:4px 8px;border-bottom:1px solid #2a2b33;font-size:13px}
.summary td.g{color:var(--line);font-weight:700;padding-top:10px;border-bottom:1px solid #4a4b55}
.summary td.dps{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap;width:110px}
.summary td.bar{width:34%}
.summary td.bar i{display:block;height:8px;background:var(--bar);border-radius:2px}
.summary td.t{color:var(--mute);text-align:right;width:70px}
"""


def pick_teams(teams: dict, pick: int | None = None) -> dict:
    """Отобрать команды отряда.

    pick=None — все вариации (как раньше);
    pick=0    — только первая; pick=-1 — только последняя; любой другой
                номер — по порядку в all_teams() (как в Python-списке).
    Номер за пределами списка берётся по краю (первая / последняя команда).
    """
    if pick is None or not teams:
        return teams
    items = list(teams.items())
    i = max(-len(items), min(pick, len(items) - 1))
    name, team = items[i]
    return {name: team}


def collect(pick: int | None = None):
    """[(группа, [(папка, [TeamResult...]), ...]), ...]

    pick — см. pick_teams(): None = все вариации, 0 = по одной (первой).
    Отбор идёт до расчёта, так что с pick скрипт работает быстрее.
    """
    out = []
    for title, folders in GROUPS:
        items = []
        for entry in folders:
            folder, _, func = entry.partition(":")
            module = importlib.import_module(f"gi_damage.teams.{folder}.builds")
            teams = pick_teams(getattr(module, func or "all_teams")(), pick)
            results = [team.compute() for team in teams.values()]
            items.append((entry, results))
            print(f"  {entry}: {len(results)} вар.")
        out.append((title, items))
    return out


def render(groups, columns: int, title: str) -> str:
    store = IconStore()
    best = max(r.dps for _, items in groups for _, rs in items for r in rs) or 1.0
    total = sum(len(rs) for _, items in groups for _, rs in items)

    rows = []
    for gtitle, items in groups:
        rows.append(f"<tr><td class='g' colspan='4'>{html.escape(gtitle)}</td></tr>")
        results = sorted((r for _, rs in items for r in rs), key=lambda r: -r.dps)
        for r in results:
            rows.append(
                f"<tr><td>{html.escape(r.team_name)}</td>"
                f"<td class='bar'><i style='width:{r.dps / best * 100:.1f}%'></i></td>"
                f"<td class='dps'>{fmt(r.dps)}</td>"
                f"<td class='t'>{r.rotation_time:g} с</td></tr>")
    cover = (f"<div class='cover'><h1>{html.escape(title)}</h1>"
             f"<p class='meta'>{total} вариаций в {sum(len(i) for _, i in groups)} отрядах. "
             f"Внутри разделов — по убыванию DPS.</p>"
             f"<table class='summary'><thead><tr><th>Отряд</th><th></th>"
             f"<th style='text-align:right'>DPS</th><th style='text-align:right'>Ротация</th>"
             f"</tr></thead><tbody>{''.join(rows)}</tbody></table></div>")

    sections = []
    index = 0
    for gtitle, items in groups:
        cards = []
        for folder, results in items:
            for r in results:
                cards.append(render_card(r, store, index))
                index += 1
        n = sum(len(rs) for _, rs in items)
        sections.append(
            f"<div class='group'><h1>{html.escape(gtitle)}</h1>"
            f"<p class='sub'>{n} вариаций: {html.escape(', '.join(f for f, _ in items))}</p>"
            f"<div class='grid' style='--cols:{max(1, columns)}'>{''.join(cards)}</div></div>")

    css = CSS + PRINT_CSS.replace("{W}", str(PAGE_WIDTH)).replace("{H}", str(PAGE_HEIGHT))
    return (f"<!doctype html><html lang='ru'><head><meta charset='utf-8'>"
            f"<title>{html.escape(title)}</title><style>{css}</style></head><body>"
            f"{cover}{''.join(sections)}</body></html>")


def to_pdf(html_path: Path, pdf_path: Path) -> Path:
    try:
        from playwright.sync_api import sync_playwright  # type: ignore
    except ImportError as exc:
        raise RuntimeError("Для PDF нужен playwright: "
                           "pip install playwright && playwright install chromium") from exc
    with sync_playwright() as p:
        try:
            browser = p.chromium.launch()
        except Exception as exc:  # браузер не скачан
            raise RuntimeError("playwright не нашёл Chromium: "
                               "python -m playwright install chromium") from exc
        page = browser.new_page(viewport={"width": PAGE_WIDTH, "height": PAGE_HEIGHT})
        page.goto(html_path.resolve().as_uri())
        page.pdf(path=str(pdf_path), width=f"{PAGE_WIDTH}px", height=f"{PAGE_HEIGHT}px",
                 print_background=True, prefer_css_page_size=True)
        browser.close()
    return pdf_path


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default="new_teams.pdf")
    ap.add_argument("--columns", type=int, default=2)
    ap.add_argument("--title", default="Отряды с Даникой и Анастасией")
    ap.add_argument("--html-only", action="store_true", help="не печатать PDF")
    sel = ap.add_mutually_exclusive_group()
    sel.add_argument("--one", action="store_const", const=0, dest="pick",
                     help="из каждого отряда только одна команда — первая")
    sel.add_argument("--pick", type=int, default=None, metavar="N",
                     help="из каждого отряда только команда номер N "
                          "(0 — первая, -1 — последняя)")
    args = ap.parse_args()

    print("Считаю отряды:")
    groups = collect(args.pick)
    pdf_path = Path(args.out)
    html_path = pdf_path.with_suffix(".html")
    html_path.write_text(render(groups, args.columns, args.title), encoding="utf-8")
    print(f"HTML: {html_path.resolve()}")
    if args.html_only:
        return 0
    try:
        print(f"PDF:  {to_pdf(html_path, pdf_path).resolve()}")
    except RuntimeError as exc:
        print(f"PDF не создан: {exc}")
        print("HTML можно напечатать в PDF из браузера (Ctrl+P, включить фон).")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())