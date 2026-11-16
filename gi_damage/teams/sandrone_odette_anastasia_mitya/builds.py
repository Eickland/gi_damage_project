"""
Отряд звёздного проводника: Сандроне / Одетта / Анастасия / Митя (саппорт).

Ротация: Анастасия EQ / Одетта EE / Митя E / Сандроне E CA EQ CA E CA E
(обычное комбо sandrone_sc_combo, 14.5 с). Реакций, наносящих урон, нет.
Резонанс — крио (3 крио + 1 электро).

Сандроне: «Цветок в латах» — в отряде один электро и нет лечения (как в
базовой линии gi_damage/data/baseline.py).
Митя — саппорт (Steady State), Эпос с полным баффом (ротация ≥ 20.5 с).
An Unfinished Requiem: стаки Polestar — polar_always у Анастасии (Team.polar_plan()).

Артефакты: Сандроне — Разочарование, Одетта — Звёздный сет,
Анастасия — Сердце горна, Митя — Миллелит.
"""

from __future__ import annotations

from typing import Dict, Sequence

from ...core.buffs import OTHERS, SELF, TEAM, Buff, temp
from ...core.engine import Config, Team
from ...core.entities import Build, Enemy
from ...core.stats import S
from ...core.utilits import merge_dicts
from ...data.artifacts import *
from ...data.artifacts_presets import *
from ...data.tags import *
from ...data.characters.sandrone import SANDRONE_COMBO_DICT
from ...data.characters.odette import (odette_burst_buffs, ODETTE_BURST_TIME,
                                       ODETTE_COMBO_DICT, ODETTE_BURST_SOURCES)
from ...data.characters.anastasia import ANASTASIA_COMBO_DICT
from ...data.characters.mitya import MITYA_COMBO_DICT
from ...data.weapons import *

TEAM_BUFFS = (
    Buff(S.CRIT_VALUE, 0.30, target=TEAM,
         source="Крио резонанс: +15% крит. шанса (0.30 крит-вэлью)"),
)

#: Время каждого персонажа в ротации (секунды)
TIMES = {"Сандроне": 14.5, "Митя": 1.5, "Анастасия": 3.5, "Одетта": 2.4}

ROTATION = "Анастасия EQ/Одетта EE/Митя E/Сандроне E CA EQ CA E CA E"

MAIN_ATK = {S.ATK_PCT: 0.466 * 2, S.CRIT_VALUE: 0.622}       # АТК/АТК/крит
MAIN_EM = {S.BASE_EM: 187.0 * 2, S.CRIT_VALUE: 0.622}        # МС/МС/крит (Митя)

SANDRONE = SANDRONE_COMBO_DICT["sandrone_sc_combo"]
ODETTE = ODETTE_COMBO_DICT["odette_ssc_combo"]
ANASTASIA = ANASTASIA_COMBO_DICT["support_sc"]
MITYA = MITYA_COMBO_DICT["support_steady"]


def enemy() -> Enemy:
    return Enemy(res={"anemo": 0.10, "cryo": 0.10, "electro": 0.10},
                 def_mult=0.4875, elevation=0.0)


def sandrone_build(constellation: int = 0, weapon=FLOWER, artifacts=(DISENCHANTMENT,),
                   main_stats=MAIN_ATK, extra_buffs: Sequence[Buff] = ()) -> Build:
    return Build(
        character=SANDRONE,
        constellation=constellation,
        weapon=weapon,
        artifacts=artifacts,
        extra_stats=merge_dicts(main_stats, STANDART_SUBSTAT_PRESET),
        extra_buffs=tuple(extra_buffs),
        time=TIMES["Сандроне"],
    )


def odette_build(constellation: int = 0, weapon=SILVER_LIGHT, artifacts=(STELLAR_SET,),
                 use_burst: bool | None = None,
                 extra_buffs: Sequence[Buff] = ()) -> Build:
    """use_burst=None — авто: до C4 не применяем, с C4 применяем."""
    if use_burst is None:
        use_burst = constellation >= 4
    return Build(
        character=ODETTE,
        constellation=constellation,
        weapon=weapon,
        artifacts=artifacts,
        extra_stats=merge_dicts(MAIN_ATK, STANDART_SUBSTAT_PRESET),
        extra_sources=ODETTE_BURST_SOURCES if use_burst else (),
        extra_buffs=tuple(extra_buffs) + (odette_burst_buffs(constellation)
                                          if use_burst else ()),
        time=TIMES["Одетта"] + (ODETTE_BURST_TIME if use_burst else 0.0),
    )


def anastasia_build(constellation: int = 0, weapon=BREEZEBORNE_BOW.at(1), artifacts=(HEART_OF_FORGE,),
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


def mitya_build(constellation: int = 0, weapon=TTDS_FULL_CATALYSATOR, artifacts=(MILLELITH,),
                main_stats=MAIN_EM, extra_buffs: Sequence[Buff] = ()) -> Build:
    return Build(
        character=MITYA,
        constellation=constellation,
        weapon=weapon,
        artifacts=artifacts,
        extra_stats=merge_dicts(main_stats, STANDART_SUBSTAT_PRESET),
        extra_buffs=tuple(extra_buffs),
        time=TIMES["Митя"],
    )


def make_team(name: str, sandrone_c: int = 0, sandrone_weapon=FLOWER,
              odette_c: int = 0, odette_weapon=SILVER_LIGHT,
              anastasia_c: int = 0, anastasia_weapon=BREEZEBORNE_BOW.at(1),
              mitya_c: int = 0, mitya_weapon=TTDS_FULL_CATALYSATOR,
              sandrone_artifacts=(DISENCHANTMENT,), odette_artifacts=(STELLAR_SET,),
              anastasia_artifacts=(HEART_OF_FORGE,), mitya_artifacts=(MILLELITH,)) -> Team:
    return Team(
        name=name,
        builds=[
            sandrone_build(sandrone_c, sandrone_weapon, sandrone_artifacts),
            odette_build(odette_c, odette_weapon, odette_artifacts),
            anastasia_build(anastasia_c, anastasia_weapon, anastasia_artifacts),
            mitya_build(mitya_c, mitya_weapon, mitya_artifacts),
        ],
        enemy=enemy(),
        buffs=TEAM_BUFFS,
        rotation=ROTATION,
        config=Config(),
        dd="Сандроне",
    )


def team_name(sandrone_c: int = 0, sandrone_weapon=FLOWER,
              odette_c: int = 0, odette_weapon=SILVER_LIGHT,
              anastasia_c: int = 0, anastasia_weapon=BREEZEBORNE_BOW.at(1),
              mitya_c: int = 0, mitya_weapon=TTDS_FULL_CATALYSATOR) -> str:
    return (f"C{sandrone_c}R{sandrone_weapon.refinement} Сандроне, "
            f"C{odette_c}R{odette_weapon.refinement} Одетта, "
            f"C{anastasia_c}R{anastasia_weapon.refinement} Анастасия, "
            f"C{mitya_c}R0 Митя")


VARIANTS = ({},)

BASE_NAME = team_name()


def all_teams() -> Dict[str, Team]:
    out: Dict[str, Team] = {}
    for kw in VARIANTS:
        name = team_name(**kw)
        out[name] = make_team(name, **kw)
    return out
