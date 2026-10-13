"""Карточки отрядов: иконки, таблица урона, доп. информация.

Модуль читает только готовые TeamResult (см. core/engine.py), поэтому
подходит и для отрядов из all_teams(), и для результатов Roster.run().
Выход — один самодостаточный HTML-файл (картинки вшиты как data-URI).
"""

from __future__ import annotations

import html
import re
from pathlib import Path
from typing import Dict, List, Mapping, Optional, Sequence

from .icons import IconStore

#: цвета заголовков карточек — по кругу
HEADER_COLORS = ("#8b1119", "#c9833a", "#262626", "#2e9c97")
HEADER_TEXT = ("#f4e6c8", "#1d1204", "#f4e6c8", "#04201e")


# --------------------------------------------------------------------------- #
def fmt(x: float) -> str:
    return f"{x:,.0f}".replace(",", "\u00a0")


def split_weapon(label: str) -> tuple[str, Optional[int]]:
    """«Песнь странника R5» -> («Песнь странника», 5)."""
    m = re.match(r"^(.*?)\s+R(\d+)$", label or "")
    return (m.group(1), int(m.group(2))) if m else (label or "", None)


def top_sources(result, n: int = 4) -> List[tuple[str, float]]:
    """Самые «тяжёлые» источники урона по всему отряду (включая реакции)."""
    agg: Dict[str, float] = {}
    for ch in result.characters.values():
        for src, value in ch.by_source().items():
            agg[src] = agg.get(src, 0.0) + value
        for src, value in ch.reaction_breakdown.items():
            key = f"[реакция] {src}"
            agg[key] = agg.get(key, 0.0) + value
    return sorted(agg.items(), key=lambda kv: -kv[1])[:n]


# --------------------------------------------------------------------------- #
def _character_column(name: str, setup, store: IconStore) -> str:
    weapon, refinement = split_weapon(setup.weapon)
    artifacts = [a for a in (setup.artifacts or "").split("/") if a]

    badge_r = f'<span class="badge br">R{refinement}</span>' if refinement else ""
    arts = "".join(
        f'<div class="ic art">{store.img("artifacts", a, "pic")}</div>'
        for a in artifacts
    )
    return f"""
      <div class="unit">
        <div class="ic portrait">{store.img("characters", name, "pic")}
          <span class="badge bc">C{setup.constellation}</span></div>
        <div class="ic weapon">{store.img("weapons", weapon, "pic") if weapon else ""}{badge_r}</div>
        <div class="arts">{arts}</div>
        <div class="wname">{html.escape(weapon or "—")}</div>
        <div class="aname">{html.escape(" + ".join(artifacts) or "—")}</div>
      </div>"""


def render_card(result, store: Optional[IconStore] = None, index: int = 0,
                notes: Sequence[str] = ()) -> str:
    """HTML одной карточки отряда."""
    store = store or IconStore()
    dpr = result.dpr or 1.0

    units = "".join(_character_column(n, result.setup[n], store)
                    for n in result.characters if n in result.setup)

    rows = []
    for name, ch in result.characters.items():
        s = result.setup.get(name)
        share = ch.total / dpr * 100
        rows.append(
            f"<tr><td class='n'>{html.escape(name)}</td>"
            f"<td class='num'>{fmt(ch.total)}</td>"
            f"<td class='num'>{share:.0f}%"
            f"<i style='width:{min(share, 100):.0f}%'></i></td>"
            f"<td class='num'>{s.time:g}s</td></tr>" if s else "")
    table = "".join(rows)

    top = "".join(
        f"<li><span>{html.escape(n)}</span><b>{fmt(v)}</b></li>"
        for n, v in top_sources(result))
    extra = "".join(f"<li class='note'>{html.escape(t)}</li>" for t in notes)
    rotation = (f"<p class='rot'>{html.escape(result.rotation)}</p>"
                if result.rotation else "")

    bg = HEADER_COLORS[index % len(HEADER_COLORS)]
    fg = HEADER_TEXT[index % len(HEADER_TEXT)]
    return f"""
<section class="card">
  <h2 style="background:{bg};color:{fg}">{html.escape(result.team_name)}</h2>
  <div class="body">
    <div class="units">{units}</div>
    <div class="mid">
      <table>
        <thead><tr><th>Отряд</th><th>Урон</th><th>Доля</th><th>Поле</th></tr></thead>
        <tbody>{table}</tbody>
      </table>
      <div class="total">
        <div><span>DPR</span><b>{fmt(result.dpr)}</b></div>
        <div><span>Ротация</span><b>{result.rotation_time:g}s</b></div>
        <div><span>DPS</span><b>{fmt(result.dps)}</b></div>
      </div>
    </div>
    <aside class="info">
      <h3>Дополнительно</h3>
      <ul>{extra}</ul>
      <h4>Крупнейшие источники</h4>
      <ul class="top">{top}</ul>
    </aside>
  </div>
  {rotation}
</section>"""


# --------------------------------------------------------------------------- #
CSS = """
:root{--bg:#0f0f12;--panel:#17181d;--line:#e6d7a3;--ink:#f1e8d2;--mute:#a99f87;
      --bar:#b3202b;--cell:#1d1e24}
*{box-sizing:border-box}
html,body{margin:0;background:var(--bg);color:var(--ink);
  font:14px/1.35 "Segoe UI",system-ui,-apple-system,"Helvetica Neue",Arial,sans-serif}
h1{margin:18px 20px 0;font-size:20px;font-weight:600}
.grid{display:grid;gap:14px;padding:16px 20px 28px;
  grid-template-columns:repeat(var(--cols,2),minmax(0,1fr))}
.card{background:var(--panel);border:2px solid var(--line);border-radius:4px;overflow:hidden}
.card h2{margin:0;padding:6px 12px;font-size:14px;font-weight:700;text-align:center}
.body{display:flex;gap:10px;padding:10px;flex-wrap:wrap}
.units{display:flex;gap:6px;flex:0 0 auto}
.unit{width:76px;display:flex;flex-direction:column;align-items:center;gap:4px}
.ic{position:relative;width:64px;height:64px;border-radius:6px;overflow:hidden;
  background:var(--cell);border:1px solid #3a3b44}
.ic.weapon,.ic.art{width:48px;height:48px}
.ic .pic{width:100%;height:100%;object-fit:cover;display:block}
.arts{display:flex;gap:2px;justify-content:center}
.badge{position:absolute;padding:0 5px;font-size:11px;font-weight:700;border-radius:3px;
  background:#000c;color:var(--ink)}
.bc{left:2px;bottom:2px}.br{right:2px;bottom:2px}
.wname,.aname{font-size:10.5px;text-align:center;line-height:1.2;color:var(--mute);
  overflow-wrap:anywhere}
.wname{color:var(--ink)}
.mid{flex:1 1 230px;min-width:230px}
table{width:100%;border-collapse:collapse}
th{background:var(--bar);color:#f4e6c8;font-weight:600;padding:3px 8px;text-align:right}
th:first-child{text-align:left}
td{padding:5px 8px;border-bottom:1px solid #2a2b33}
td.n{font-weight:600}
td.num{text-align:right;font-variant-numeric:tabular-nums;position:relative}
td.num i{position:absolute;left:0;bottom:0;height:2px;background:var(--bar)}
.total{display:flex;margin-top:6px;background:var(--bar);color:#f4e6c8;border-radius:3px}
.total div{flex:1;padding:4px 8px;display:flex;flex-direction:column;align-items:center}
.total span{font-size:11px;opacity:.85}
.total b{font-size:15px;font-variant-numeric:tabular-nums}
.info{flex:1 1 200px;min-width:200px;background:#101116;border:1px solid #3a2a2c;
  border-radius:3px;padding:0 0 8px}
.info h3,.info h4{margin:0;padding:3px 8px;background:#5e0c13;color:#f4e6c8;
  font-size:12px;font-weight:600}
.info h4{margin-top:8px;background:#3b3d46}
.info ul{margin:6px 0 0;padding:0 8px;list-style:none}
.info li{font-size:12px;padding:1px 0}
.info li.note::before{content:"\\2022\\00a0"}
.top li{display:flex;justify-content:space-between;gap:8px;color:var(--mute)}
.top b{color:var(--ink);font-weight:600;font-variant-numeric:tabular-nums}
.rot{margin:0;padding:6px 10px;border-top:1px solid #2a2b33;text-align:center;
  font-size:12px;color:var(--mute)}
svg.ph{width:100%;height:100%;display:block}
@media(max-width:900px){.grid{grid-template-columns:1fr}}
"""


def render_page(results: Sequence, title: str = "Расчёт отрядов",
                columns: int = 2, store: Optional[IconStore] = None,
                notes: Optional[Mapping[str, Sequence[str]]] = None) -> str:
    """Полная HTML-страница. notes: {название отряда: [строки доп. информации]}."""
    store = store or IconStore()
    notes = notes or {}
    cards = "".join(render_card(r, store, i, notes.get(r.team_name, ()))
                    for i, r in enumerate(results))
    return (f'<!doctype html><html lang="ru"><head><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>{html.escape(title)}</title><style>{CSS}</style></head><body>'
            f'<h1>{html.escape(title)}</h1>'
            f'<div class="grid" style="--cols:{max(1, columns)}">{cards}</div>'
            f'</body></html>')


def save_cards(results: Sequence, path: str | Path, title: str = "Расчёт отрядов",
               columns: int = 2, store: Optional[IconStore] = None,
               notes: Optional[Mapping[str, Sequence[str]]] = None) -> Path:
    """Сохранить карточки в HTML-файл и вернуть путь."""
    path = Path(path)
    path.write_text(render_page(results, title, columns, store, notes),
                    encoding="utf-8")
    return path


def save_png(html_path: str | Path, png_path: str | Path, width: int = 1800) -> Path:
    """HTML -> PNG. Нужен playwright (pip install playwright && playwright install chromium)."""
    try:
        from playwright.sync_api import sync_playwright # type: ignore
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("Для PNG нужен playwright: "
                           "pip install playwright && playwright install chromium") from exc
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": width, "height": 900})
        page.goto(Path(html_path).resolve().as_uri())
        page.screenshot(path=str(png_path), full_page=True)
        browser.close()
    return Path(png_path)