"""Сигнатурные оружия персонажей и подписи «CxRy» в названиях отрядов.

В названии отряда R — пробуждение СИГНАТУРНОГО оружия персонажа; с любым
другим оружием — всегда R0. Подписи переписываются автоматически при расчёте
(core/engine.py → display_name), поэтому team_name() в файлах отрядов
можно оставить как есть.

Персонажи, которых нет ни в SIGNATURES, ни в NO_SIGNATURE, не трогаются
(подпись остаётся как в файле отряда) — для них сигна в проекте не задана.
"""

from __future__ import annotations

import re
from typing import Dict, Iterable, Set

from . import weapons as W

#: персонаж -> названия его сигнатурного оружия
SIGNATURES: Dict[str, Set[str]] = {
    "Анастасия": {W.SILVER_RADIANCE.name},
    "Весна": {W.CHRYSALIS.name},
    "Водяница": {W.MAELSTROM.name},
    "Даника": {W.SPRING_TIDE.name},
    "Мидзуки": {W.SUNNY_MORNING_SLEEP_IN.name},
    "Митя": {W.STARSEALED.name},
    "Одетта": {W.FROSTFEATHER.name},
    "Сайно": {W.SCARLET_SANDS.name},
    "Сандроне": {W.TEASPOON.name},
    "Яэ Мико": {W.KAGURA.name},
    "Крио ГГ": {W.EXAIPHANES.name},
    "Нефер": {W.RELIQUARY_OF_TRUTH_LUNAR.name},
    "Лаума": {W.NIGHTWEAVER_LUNAR.name},
    "Линея": {W.GOLDEN_OATH.name},
    "Нилу": {W.KEY_OF_KHAJ_NISUT.name},
    "Цзы Бай": {W.MOONSHARD.name},
    "Колумбина": {W.NOCTURNE.name},
    "Алеша": {W.SYMPHONIST.name},
    "Ризли": {W.TREASURY_OVERSIGHT.name},
}

#: у этих персонажей сигнатурного оружия нет — всегда R0
NO_SIGNATURE = {"Диона", "Валера", "Ци Ци", "Сахароза", "Фарузан", "Иллуги",
                # сигны ещё нет в проекте — любое их оружие не сигна
                "Николь", "Шилонен"}

#: этим персонажам «CxRy» дописывается, даже если в названии его не было
ALWAYS_LABEL = {"Сахароза", "Диона"}

#: как персонаж может быть записан в названии
_ALIASES = {"Яэ Мико": ("Яэ Мико", "Яэ")}


def signature_refinement(character: str, weapon) -> int | None:
    """R для подписи: пробуждение сигны, 0 — не сигна, None — неизвестно."""
    if character in NO_SIGNATURE:
        return 0
    sig = SIGNATURES.get(character)
    if sig is None:
        return None
    return weapon.refinement if weapon is not None and weapon.name in sig else 0


def _name_rx(name: str) -> str:
    alts = _ALIASES.get(name, (name,))
    return "(?:" + "|".join(re.escape(a).replace(r"\ ", r"\s*") for a in alts) + ")"


def display_name(team_name: str, builds: Iterable) -> str:
    """Переписать «CxRy» у персонажей по их фактическому созвездию и оружию."""
    out = team_name
    for b in builds:
        r = signature_refinement(b.name, b.weapon)
        if r is None:
            continue
        n = _name_rx(b.name)
        c = b.constellation
        # C2R1 Имя / С2 Имя
        out = re.sub(rf"(?<![\w])[CС]\d(?:R\d+)?(\s+)({n})(?![\w])",
                     lambda m: f"C{c}R{r}{m.group(1)}{m.group(2)}", out, flags=re.I)
        # Имя C2R1 / Имя С2
        out = re.sub(rf"(?<![\w])({n})(\s+)[CС]\d(?:R\d+)?(?![\w])",
                     lambda m: f"{m.group(1)}{m.group(2)}C{c}R{r}", out, flags=re.I)
        if b.name in ALWAYS_LABEL:
            # имя без подписи («Сахароза», «Сахароза (Эпос…)») — дописать CxRy
            out = re.sub(rf"(?<![\w])(?<![CС]\dR\d )(?<![CС]\d )({n})(?![\w])(?!\s+[CС]\d)",
                         lambda m: f"C{c}R{r} {b.name}", out, flags=re.I)
            # регистр имени — как в проекте («диона» → «Диона»)
            out = re.sub(rf"(?<![\w])({n})(?![\w])", b.name, out, flags=re.I)
    return out
