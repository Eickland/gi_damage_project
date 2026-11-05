"""
Отряд Весна / Анастасия / C6R5 Крио ГГ / Водяница (звёздное рассеивание).

Анастасия — саппорт (Милосердие), Сердце горна. Крио ГГ — C6, Пробуждение R5,
Знать (комбо cmc_ssw_vesna_combo, как в vesna_vodya_odette_cmc).
Ротация: Анастасия EQ / Крио ГГ E Q CA / Водяница E / Весна (комбо).

Окна: Знать и C6 Крио ГГ (FROSTGLOW, 15 с после взрыва) — на ударах Весны
(уже размечены в её комбо), на 6 атаках короны из 10 и в реакциях.

An Unfinished Requiem: базовый множитель реакций SSW ×1.15 и +4 вихря
2 уровня (см. reactions()).
"""

from __future__ import annotations

from dataclasses import replace
from typing import Dict, Sequence

from ...core.buffs import OTHERS, SELF, TEAM, Buff, temp
from ...core.cycle import Phase
from ...core.engine import Config, Team
from ...core.entities import Build, Enemy
from ...core.reactions import ssw_anemo, ssw_vortex
from ...core.sources import occ
from ...core.stats import S
from ...core.utilits import merge_dicts
from ...data.artifacts import *
from ...data.artifacts_presets import STANDART_SUBSTAT_PRESET
from ...data.tags import *
from ...data.characters.cryo_mc import CMC_COMBO_DICT
from ...data.characters.vodyanitsa import VODYA_COMBO_DICT
from ...data.characters.vesna import VESNA_COMBO_DICT
from ...data.characters.anastasia import (anastasia_support, requiem_reactions,
                                          requiem_vortex, CROWN_HITS)
from ...data.weapons import *

VESNA_BASE_TIME = {"burst": 11.5, "no_burst": 11.5}
VESNA_C1_EXTRA = 0.5

TEAM_BUFFS = (
    Buff(S.CRIT_VALUE, 0.30, target=TEAM,
         source="Крио резонанс: +15% крит. шанса (0.30 крит-вэлью)"),
)

#: Время каждого персонажа в ротации (секунды)
TIMES = {"Весна": 11.5, "Анастасия": 3.0, "Крио ГГ": 3.65, "Водяница": 1.6}

ROTATION = "Анастасия EQ/CMC E Q CA/Водяница E/Vesna combo"

MAIN_ATK = {S.ATK_PCT: 0.466 * 2, S.CRIT_VALUE: 0.622}       # АТК/АТК/крит

#: Корона: 6 атак из 10 — после взрыва Крио ГГ (Знать + C6), 4 — до него
CROWN_IN_WINDOW = 6
ANASTASIA = anastasia_support("ssw", [occ(CROWN_IN_WINDOW, OFF, NOBLE, FROSTGLOW, BREEZEBORNE),
                                      occ(CROWN_HITS - CROWN_IN_WINDOW, OFF)])


def vesna_time(base: float, constellation: int) -> float:
    return base + (VESNA_C1_EXTRA if constellation > 0 else 0.0)


def vesna_combo(combo_key: str, base_time: float):
    return lambda b: replace(b, character=VESNA_COMBO_DICT[combo_key],
                             time=vesna_time(base_time, b.constellation))


def vesna_burst_cycle(burst_n: int, total_n: int):
    """Взрыв Весны в burst_n ротациях из total_n."""
    with_q = Phase(
        "Vesna (N1CE)2 QE (N1CE)2", burst_n,
        builds={"Весна": vesna_combo("vesna_ssw_burst_combo", VESNA_BASE_TIME["burst"])},
        reactions=reactions(),
    )
    without_q = Phase(
        "Vesna (N1CE)2 N3CE (N1CE)2", total_n - burst_n,
        builds={"Весна": vesna_combo("vesna_ssw_no_burst_combo", VESNA_BASE_TIME["no_burst"])},
        reactions=reactions(),
    )
    return (with_q, without_q)


def enemy() -> Enemy:
    return Enemy(res={"anemo": 0.10, "cryo": 0.10}, def_mult=0.4875, elevation=0.0)


def vesna_build(constellation: int = 0, weapon=CHRYSALIS, artifacts=SCARLET_PROOF,
                extra_buffs: Sequence[Buff] = ()) -> Build:
    return Build(
        character=VESNA_COMBO_DICT["vesna_ssw_burst_combo"],
        constellation=constellation,
        weapon=weapon,
        artifacts=(artifacts,),
        extra_stats=merge_dicts(MAIN_ATK, STANDART_SUBSTAT_PRESET),
        extra_buffs=tuple(extra_buffs),
        time=vesna_time(VESNA_BASE_TIME["burst"], constellation),
    )


def anastasia_build(constellation: int = 0, weapon=ARTEMISIA, artifacts=(HEART_OF_FORGE,),
                    main_stats=MAIN_ATK, extra_buffs: Sequence[Buff] = ()) -> Build:
    return Build(
        character=ANASTASIA,
        constellation=constellation,
        weapon=weapon,
        artifacts=artifacts,
        extra_stats=merge_dicts(main_stats, STANDART_SUBSTAT_PRESET),
        extra_buffs=tuple(extra_buffs),
        time=TIMES["Анастасия"],
    )


def cryo_mc_build(constellation: int = 6, weapon=EXAIPHANES.at(5), artifacts=(NOBLESSE,),
                  extra_buffs: Sequence[Buff] = ()) -> Build:
    return Build(
        character=CMC_COMBO_DICT["cmc_ssw_vesna_combo"],
        constellation=constellation,
        weapon=weapon,
        artifacts=artifacts,
        extra_stats=merge_dicts(MAIN_ATK, STANDART_SUBSTAT_PRESET),
        extra_buffs=tuple(extra_buffs),
        time=TIMES["Крио ГГ"],
    )


def vodya_build(constellation: int = 0, weapon=TTDS_HALF_CATALYSATOR, artifacts=(MILLELITH,),
                extra_buffs: Sequence[Buff] = ()) -> Build:
    return Build(
        character=VODYA_COMBO_DICT["off_field"],
        constellation=constellation,
        weapon=weapon,
        artifacts=artifacts,
        extra_stats=merge_dicts({S.HP_PCT: 0.466 * 3}, STANDART_SUBSTAT_PRESET),
        extra_buffs=tuple(extra_buffs),
        time=TIMES["Водяница"],
    )


def reactions():
    """События SSW за ротацию: как в vesna_vodya_odette_cmc (с C6 Крио ГГ)
    + Requiem Анастасии."""
    return requiem_reactions((
        ssw_anemo("Весна", 2, INST, VODYA_LEAD, BREEZEBORNE, FROSTGLOW, name="SSW анемо (Весна, Весна)"),
        ssw_anemo("Весна", 6, INST, VODYA_LEAD, VODYA_CHORUS, BREEZEBORNE, FROSTGLOW,
                  name="SSW анемо (Весна, Инструктор)"),
        ssw_vortex(2, 3, INST, BREEZEBORNE, FROSTGLOW, VV_CRYO, name="SSW вихрь ×3 стака"),
        requiem_vortex(INST, BREEZEBORNE, FROSTGLOW, VV_CRYO),
    ))


def make_team(name: str, vesna_c: int = 0, vesna_weapon=BOUGH,
              cmc_c: int = 6, cmc_weapon=EXAIPHANES.at(5), cmc_artifacts=(NOBLESSE,),
              vesna_artifacts=SCARLET_PROOF, vodya_artifacts=(MILLELITH,),
              vodya_weapon=MAELSTROM, vodya_c: int = 0,
              anastasia_c: int = 0, anastasia_weapon=SILVER_RADIANCE,
              anastasia_artifacts=(HEART_OF_FORGE,)) -> Team:
    return Team(
        name=name,
        builds=[
            vesna_build(vesna_c, vesna_weapon, vesna_artifacts),
            anastasia_build(anastasia_c, anastasia_weapon, anastasia_artifacts),
            cryo_mc_build(cmc_c, cmc_weapon, cmc_artifacts),
            vodya_build(vodya_c, vodya_weapon, vodya_artifacts),
        ],
        enemy=enemy(),
        reactions=reactions(),
        buffs=TEAM_BUFFS,
        rotation=ROTATION,
        config=Config(),
        phases=vesna_burst_cycle(1, 2),
    )


#: Вариации (как первые две у отряда с Одеттой)
VARIANTS = (
    ("Весна C0R1, C0R1 Анастасия (СГ), C6R5 Крио ГГ (Знать), С0R1 Водяница",
     dict(vesna_weapon=CHRYSALIS,)),
    ("Весна C0R1, C0R3 Анастасия (Напевы ветра, СГ), C6R5 Крио ГГ (Знать), С0R1 Водяница",
     dict(vesna_weapon=CHRYSALIS, anastasia_weapon=BREEZEBORNE_BOW.at(3))),
)

BASE_NAME = VARIANTS[0][0]


def all_teams() -> Dict[str, Team]:
    return {name: make_team(name, **kw) for name, kw in VARIANTS} # pyright: ignore[reportArgumentType]
