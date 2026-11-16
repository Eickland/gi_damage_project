"""Стандартный порядок инвестиций для отряда.

    from gi_damage.visual.standard_invest import standard_plan
    plan, base = standard_plan(mod, budget=12)

Старт — базовая линия отряда (data/baseline.baseline_team): все персонажи
уже куплены (C0, у KEEP_CONSTELLATIONS — их созвездие бесплатно), оружие без
сигн. Платно: каждое следующее созвездие (до C6) и сигнатурное оружие
персонажа (data/signatures.SIGNATURES): R1 — 1 кост, каждое пробуждение — +1.
Персонаж с C6 в базе (Алеша, Крио ГГ, Диона…) докупает только сигну.
"""

from __future__ import annotations

import inspect
from dataclasses import replace
from typing import Callable, Dict, List, Optional, Tuple

from ..core.engine import Build, Team
from ..core.search import Investable, SignatureWeapon, plan_investments
from ..data import weapons as W
from ..data.baseline import baseline_team
from ..data.signatures import SIGNATURES
from .standard_rosters import _build_fn, _dps, _flat, _same, _swap

_BY_NAME: Dict[str, object] = {}
for _v in vars(W).values():
    if hasattr(_v, "name") and hasattr(_v, "at"):
        _BY_NAME.setdefault(_v.name, _v)


def first_team(mod) -> Team:
    return next(iter(mod.all_teams().values()))


def _maker(mod, base: Team, b: Build) -> Callable[[int], Build]:
    """C -> Build, сохраняя оружие и артефакты базы. Если у отряда есть
    `<ключ>_build` и он воспроизводит базу — им (ротация может зависеть от C)."""
    fn = _build_fn(mod, b.name)
    if fn is not None:
        params = inspect.signature(fn).parameters

        def call(c: int) -> Build:
            args = {"constellation": c, "weapon": b.weapon, "artifacts": _flat(b.artifacts)}
            args = {k: v for k, v in args.items() if k in params}
            try:
                return fn(**args)
            except Exception:
                if len(args.get("artifacts", ())) == 1:
                    args["artifacts"] = args["artifacts"][0]
                    return fn(**args)
                raise
        try:
            if _same(_dps(_swap(base, b.name, call(b.constellation))), _dps(base)):
                return call
        except Exception:
            pass
    return lambda c: replace(b, constellation=c)


def standard_plan(mod, budget: int = 12, team: Optional[Team] = None, beam=200, **kw):
    """(InvestmentPlan, базовый отряд).

    beam=200: узкий луч (40) теряет «дорогие» покупки, которые окупаются
    только целиком — например C3→C6 Одетты (C3–C5 почти ничего не дают).
    """
    base, _ = baseline_team(team or first_team(mod))
    inv: List[Investable] = []
    wps: List[SignatureWeapon] = []
    for b in base.builds:
        name = b.name
        if b.constellation < 6:
            inv.append(Investable(name, name, _maker(mod, base, b),
                                  owned=True, start_constellation=b.constellation))
        sig = sorted(SIGNATURES.get(name, ()))
        weapon = _BY_NAME.get(sig[0]) if sig else None
        if weapon is None:
            continue
        r0 = b.weapon.refinement if b.weapon is not None and b.weapon.name == weapon.name else 0
        if r0 >= 5:
            continue
        if r0:                         # сигна уже в базе (Крио ГГ R5) — тут не бывает
            continue
        wps.append(SignatureWeapon(name, weapon))
    plan = plan_investments(base, inv, wps, budget=budget, beam=beam, **kw)
    return plan, base
