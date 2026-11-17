#!/usr/bin/env python3
"""Порядок инвестиций всех звёздных отрядов в одном HTML.

    python -m scripts.render_all_invest                    # «инвест звездных команд.html», кост 12
    python -m scripts.render_all_invest --budget 20
    python -m scripts.render_all_invest --only sandrone --text   # + текстовые таблицы в консоль

Отряды — из scripts/render_new_teams_pdf.py (GROUPS). Для каждого —
gi_damage/visual/standard_invest.standard_plan: старт с базовой линии (все
персонажи куплены на C0 / бесплатном созвездии, без сигн), платно —
созвездия и сигнатурное оружие (R1 = 1 кост, +1 за пробуждение).
На каждом косте показан ЛУЧШИЙ набор покупок этого коста — он не обязан
содержать набор предыдущего (бывает «продать сигну, взять C2»).
"""

from __future__ import annotations

import argparse
import html
import importlib
import json
import re
import time
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from gi_damage.core.search import plan_report
from gi_damage.visual.cards import CSS, SCROLL_JS, fmt
from gi_damage.visual.icons import IconStore
from gi_damage.visual.rosters import ROSTER_CSS
from gi_damage.visual.search import SEARCH_CSS
from gi_damage.visual.search import render_plan
from gi_damage.visual.standard_invest import standard_plan
from scripts.render_all_rosters import EXTRA_CSS, SharedIconStore, team_list

DEFAULT_OUT = "инвест звездных команд.html"


SRC = re.compile(r'src="(data:[^"]+)"')


def store_index(store: SharedIconStore, uri: str) -> int:
    if uri not in store.index:
        store.index[uri] = len(store.uris)
        store.uris.append(uri)
    return store.index[uri]


def compute_team(d: str, budget: int, text: bool) -> dict:
    """План отряда d → {name, dps, top, cost, card}; card — HTML с иконками внутри."""
    mod = importlib.import_module(f"gi_damage.teams.{d}.builds")
    plan, base = standard_plan(mod, budget=budget)
    r0 = base.compute()
    if text:
        print(r0.team_name)
        print(plan_report(plan))
    last = plan.levels[-1]
    card = render_plan(plan, f"Порядок инвестиций — {r0.team_name}", IconStore(),
                       sum(map(ord, d)) % 97)
    return {"name": r0.team_name, "dps": r0.dps, "top": last.best.result.dps,
            "cost": last.cost, "card": card}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=DEFAULT_OUT)
    ap.add_argument("--budget", type=int, default=12, help="максимальный кост (12)")
    ap.add_argument("--only", default=None, help="фильтр по имени папки отряда")
    ap.add_argument("--cache", default=".invest_cache",
                    help="папка кэша планов (повторный запуск досчитывает только новые; '' — без кэша)")
    ap.add_argument("--limit", type=float, default=0,
                    help="остановиться через N секунд (кэш сохранён, запустите ещё раз)")
    ap.add_argument("--text", action="store_true", help="печатать таблицы в консоль")
    args = ap.parse_args()

    cache = Path(args.cache) if args.cache else None
    if cache:
        cache.mkdir(exist_ok=True)
    t0, unfinished = time.time(), 0
    store = SharedIconStore()
    toc, body, n = [], [], 0
    for gtitle, folders in team_list(args.only):
        toc.append(f"<h3>{html.escape(gtitle)}</h3>")
        body.append(f"<h2 class='grp'>{html.escape(gtitle)}</h2>")
        for d in folders:
            print(f"  {d} ...", end="", flush=True)
            cfile = cache / f"{d}.b{args.budget}.v2.json" if cache else None
            try:
                if cfile and cfile.exists():
                    item = json.loads(cfile.read_text(encoding="utf-8"))
                elif args.limit and time.time() - t0 > args.limit:
                    print(" отложен (--limit)")
                    unfinished += 1
                    continue
                else:
                    item = compute_team(d, args.budget, args.text)
                    if cfile:
                        cfile.write_text(json.dumps(item, ensure_ascii=False), encoding="utf-8")
            except Exception as exc:
                print(f" ОШИБКА: {type(exc).__name__}: {exc}")
                body.append(f"<details class='team' id='{d}'><summary>{html.escape(d)}</summary>"
                            f"<p class='err'>{html.escape(type(exc).__name__)}: "
                            f"{html.escape(str(exc))}</p></details>")
                continue
            print(f" ×{item['top'] / item['dps']:.2f}")
            n += 1
            name = html.escape(item["name"])
            card = SRC.sub(lambda m: f'data-i="{store_index(store, m.group(1))}"', item["card"])
            toc.append(f"<a href='#{d}' onclick=\"document.getElementById('{d}').open=true\">"
                       f"{name}<span class='d'>{fmt(item['dps'])} → {fmt(item['top'])}</span></a>")
            body.append(
                f"<details class='team' id='{d}'><summary>{name}"
                f"<span class='folder'>{d}</span><span class='d'>DPS {fmt(item['dps'])} → "
                f"{fmt(item['top'])} (кост {item['cost']})</span></summary>"
                f"<div class='rgrid' style='--cols:1'>{card}</div></details>")

    title = "Порядок инвестиций звёздных команд"
    page = (f"<!doctype html><html lang='ru'><head><meta charset='utf-8'>"
            f"<meta name='viewport' content='width=device-width,initial-scale=1'>"
            f"<title>{title}</title><style>{CSS}{ROSTER_CSS}{SEARCH_CSS}{EXTRA_CSS}</style></head><body>"
            f"<h1>{title}</h1>"
            f"<p class='rot' style='margin:0 20px 8px'>{n} отрядов, кост до {args.budget}. "
            f"Старт — базовая линия (все персонажи куплены, без сигн и созвездий, кроме "
            f"бесплатных); 1 кост = созвездие или R1/пробуждение сигны. На каждом косте — "
            f"лучший набор этого коста; запасные варианты — во всплывающей подсказке строки.</p>"
            f"<div class='tools'><button onclick=\"document.querySelectorAll('details.team')"
            f".forEach(e=>e.open=true)\">Развернуть всё</button>"
            f"<button onclick=\"document.querySelectorAll('details.team')"
            f".forEach(e=>e.open=false)\">Свернуть всё</button></div>"
            f"<nav class='toc'>{''.join(toc)}</nav>{''.join(body)}"
            f"{store.script()}{SCROLL_JS}</body></html>")
    out = Path(args.out)
    out.write_text(page, encoding="utf-8")
    if unfinished:
        print(f"Не досчитано отрядов: {unfinished} — запустите ещё раз.")
    print(f"HTML: {out.resolve()}  ({out.stat().st_size / 1e6:.1f} МБ)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
