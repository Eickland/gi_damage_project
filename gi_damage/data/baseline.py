"""Базовая линия отряда: без сигнатурных оружий и созвездий.

    from gi_damage.data.baseline import baseline_team
    team, changes = baseline_team(team)

Правила (см. scripts/render_new_teams_pdf.py --one):

1. Сандроне: «Клинок искупления» — только если в отряде 2+ электро;
   иначе «Тень волны» — если есть лечение (Ци Ци / Алеша / Диона);
   иначе «Магический супермеч».
2. Сигнатурные оружия заменяются на базовые (SIGNATURE_FALLBACK),
   созвездия сбрасываются в C0, кроме KEEP_CONSTELLATIONS
   (C6 Алеша, C6 Валера, C1 Яэ, C1 Ризли, C1 Сайно, C2 Мидзуки, C6 Крио ГГ, C6 Фарузан,
   C6 Диона, C6 Сахароза).
3. Анастасия с «Артемизией»: R1, «Звёздный сет» → «Разочарование».
4. Одетта: «Серебряный свет» R5.
5. Крио ГГ: C6 и «Пробуждение» R5.
"""

from __future__ import annotations

from dataclasses import replace
from typing import List, Tuple

from ..core.engine import Team
from . import weapons as W
from .artifacts import DISENCHANTMENT, HEART_OF_FORGE, SCARLET_PROOF, STELLAR_SET

#: созвездие, которое остаётся на базовой линии (остальные — C0)
KEEP_CONSTELLATIONS = {
    "Алеша": 6, "Валера": 6, "Яэ Мико": 1, "Ризли": 1, "Сайно": 1, "Мидзуки": 2,"Крио ГГ":6,"Фарузан":6, "Диона": 6, "Сахароза": 6
}

ELECTRO_FOR_ATONEMENT = 2
HEALERS = ("Ци Ци", "Алеша", "Диона")

#: (персонаж, сигна) -> базовое оружие. Ключ "*" — для любого персонажа.
SIGNATURE_FALLBACK = {
    ("Водяница", W.MAELSTROM.name): W.TTDS_HALF_CATALYSATOR.at(5),
    ("Одетта", W.FROSTFEATHER.name): W.SILVER_LIGHT.at(5),
    ("Весна", W.CHRYSALIS.name): W.BOUGH.at(1),
    ("Митя", W.STARSEALED.name): W.SPINDLELUTE.at(5),
    ("Анастасия", W.SILVER_RADIANCE.name): W.ARTEMISIA.at(1),
    ("Анастасия", W.ELEGY_BOW.name): W.ARTEMISIA.at(1),
    ("Даника", W.SPRING_TIDE.name): W.ATONEMENT.at(5),
    ("Яэ Мико", W.KAGURA.name): W.ECHOES.at(5),
    ("Сайно", W.SCARLET_SANDS.name): W.DEATHMATCH.at(1),
    ("Мидзуки", W.SUNNY_MORNING_SLEEP_IN.name): W.WANDERER_SONG.at(5),
    ("Алеша", W.SYMPHONIST.name): W.FAV_LANCE.at(5),
    ("Ризли", W.TREASURY_OVERSIGHT.name): W.WANDERER_SONG_CRYO.at(5),
}
SIGNATURES = {w for _, w in SIGNATURE_FALLBACK} | {W.TEASPOON.name}


def _fallback(char: str, weapon):
    return SIGNATURE_FALLBACK.get((char, weapon.name))


def sandrone_weapon(team: Team):
    electro = sum(1 for b in team.builds if b.element == "electro")
    if electro >= ELECTRO_FOR_ATONEMENT:
        return W.ATONEMENT.at(5)
    if any(b.character.name in HEALERS for b in team.builds):
        return W.TIDAL_SHADOW.at(5)
    return W.FLOWER


def _is_ssw(team: Team) -> bool:
    """Отряд звёздного рассеивания (есть удары SSW или реакции)."""
    from ..core.sources import STELLAR_SWIRL
    return bool(team.reactions) or any(s.model == STELLAR_SWIRL
                                       for b in team.builds for s in b.all_sources())


def _wr(w) -> str:
    return f"{w.name} R{w.refinement}" if w else "—"


def baseline_team(team: Team, suffix: str = "") -> Tuple[Team, List[str]]:
    """Вернуть (новая команда, список изменений «Персонаж: было → стало»)."""
    builds, changes = [], []
    for b in team.builds:
        name = b.character.name
        new = b
        # --- созвездие
        c = KEEP_CONSTELLATIONS.get(name, 0)
        if b.constellation != c:
            changes.append(f"{name}: C{b.constellation} → C{c}")
            new = replace(new, constellation=c)
        # --- оружие
        w = new.weapon
        if name == "Сандроне":
            w = sandrone_weapon(team)
        elif w is not None:
            w = _fallback(name, w) or w
        if name == "Анастасия" and w is not None and w.name == W.ARTEMISIA.name:
            w = w.at(1)
        if name == "Одетта" and w is not None and w.name == W.SILVER_LIGHT.name:
            w = w.at(5)
        if name == "Крио ГГ" and w is not None and w.name == W.EXAIPHANES.name:
            w = w.at(5)
        assert w is not None
        assert new.weapon is not None
        if w is not new.weapon and (w.name, w.refinement) != (new.weapon.name, new.weapon.refinement):
            changes.append(f"{name}: {_wr(new.weapon)} → {_wr(w)}")
            if name == "Сайно":   # главстаты зависят от сигны (МС/АТК)
                from .characters.cyno import cyno_main_stats
                old_m, new_m = cyno_main_stats(new.weapon), cyno_main_stats(w)
                st = dict(new.extra_stats)
                for k, v in old_m.items():
                    st[k] = st.get(k, 0.0) - v
                for k, v in new_m.items():
                    st[k] = st.get(k, 0.0) + v
                new = replace(new, extra_stats={k: v for k, v in st.items() if abs(v) > 1e-12})
            new = replace(new, weapon=w)
        # --- артефакты
        arts = tuple(new.artifacts)
        if name == "Анастасия" and new.weapon is not None and new.weapon.name == W.ARTEMISIA.name:
            arts = tuple(DISENCHANTMENT if a.name == STELLAR_SET.name else a for a in arts)
        if [a.name for a in arts] != [a.name for a in new.artifacts]:
            changes.append(f"{name}: {'/'.join(a.name for a in new.artifacts)} → "
                           f"{'/'.join(a.name for a in arts)}")
            new = replace(new, artifacts=arts)
        builds.append(new)
    label = ", ".join(f"C{b.constellation}R{b.weapon.refinement if b.weapon else 0} {b.name}"
                      for b in builds)
    return replace(team, builds=tuple(builds), name=label + suffix), changes
