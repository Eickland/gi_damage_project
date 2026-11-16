"""
Отряд звёздного проводника: Крио ГГ (ДД на поле) / Анастасия / Даника / Ци Ци.

Ротация: Даника EQ / Анастасия EQ / Ци Ци E / Крио ГГ E N2 N2 C Q N2.
Крио ГГ — короткое ДД-комбо cmc_sc_dd_e_combo (E N2 N2 C Q N2, 6.4 с).
Реакций, наносящих урон, нет. Резонанс — крио (3 крио + 1 электро).

C6 Крио ГГ (окно FROSTGLOW, 15 с после взрыва): все удары остальных — с FROSTGLOW.
An Unfinished Requiem: стаки Polestar — polar_always у Анастасии (Team.polar_plan()).
Бафф Ци Ци (SEVEN_SACRED) — только звёздное рассеивание, на проводник не влияет.
Даника — единственный электро: Двуручный меч фавония, часы на ВЭ (АТК/АТК/ВЭ).
C2 Даники (danika_c=2): стаки — Крио ГГ 10, Анастасия 7.

Артефакты: Анастасия — Звёздный сет, Даника — Сердце горна, Ци Ци — Миллелит,
Крио ГГ — Разочарование.
"""

from __future__ import annotations

from typing import Dict, Sequence

from ...core.buffs import OTHERS, SELF, TEAM, Buff, temp
from ...core.engine import Config, Team
from ...core.entities import Build, Enemy
from ...core.sources import occ
from ...core.stats import S
from ...core.utilits import merge_dicts
from ...data.artifacts import *
from ...data.artifacts_presets import *
from ...data.tags import *
from ...data.characters.cryo_mc import CMC_COMBO_DICT, CMC_SC_DD_TIME, CMC_SC_DD_E_TIME
from ...data.characters.odette import (odette_burst_buffs, ODETTE_BURST_TIME,
                                       ODETTE_COMBO_DICT, ODETTE_BURST_SOURCES)
from ...data.characters.danika import (DANIKA_COMBO_DICT, C2_ACTIVE_STACKS,
                                       C2_OTHER_STACKS, tag_stellar_conduct_hits, add_tags)
from ...data.characters.anastasia import ANASTASIA_COMBO_DICT
from ...data.characters.qiqi import QIQI_COMBO_DICT
from ...data.weapons import *

TEAM_BUFFS = (
    Buff(S.CRIT_VALUE, 0.30, target=TEAM,
         source="Крио резонанс: +15% крит. шанса (0.30 крит-вэлью)"),
)

#: Время каждого персонажа в ротации (секунды)
TIMES = {"Крио ГГ": CMC_SC_DD_TIME-1, "Анастасия": 3.5, "Даника": 3.25, "Ци Ци": 1.5}

ROTATION = "Даника EQ/Анастасия EQ/Ци Ци E/Крио ГГ E N2 N2 C Q N2"

MAIN_ATK = {S.ATK_PCT: 0.466 * 2, S.CRIT_VALUE: 0.622}       # АТК/АТК/крит
MAIN_EM = {S.BASE_EM: 187.0 * 2, S.CRIT_VALUE: 0.622}        # МС/МС/крит
#: Даника — единственный электро в отряде: часы на ВЭ вместо АТК
#: (штраф по требованию энергии) — АТК/АТК/ВЭ.
DANIKA_MAIN_ER = {S.ATK_PCT: 0.466 * 2}

#: Короткое ДД-комбо Крио ГГ: E N2 N2 C Q N2 (6.4 с)
CMC = CMC_COMBO_DICT["cmc_sc_dd_combo"]
ANASTASIA = ANASTASIA_COMBO_DICT['support_sc_short']
DANIKA = DANIKA_COMBO_DICT["support_eq"]
QIQI = QIQI_COMBO_DICT["off_field"]


def enemy() -> Enemy:
    return Enemy(res={"anemo": 0.10, "cryo": 0.10, "electro": 0.10},
                 def_mult=0.4875, elevation=0.0)


def _c2(build: Build, hits: int) -> Build:
    return tag_stellar_conduct_hits(build, DANIKA_C2, hits)


def _frostglow(build: Build) -> Build:
    """C6 Крио ГГ: удар остальных под +40% урона звёздных реакций."""
    return add_tags(build, FROSTGLOW)


def cryo_mc_build(constellation: int = 6, weapon=EXAIPHANES.at(5), artifacts=(DISENCHANTMENT,),
                  main_stats=MAIN_ATK, danika_c2_hits: int = 0,
                  extra_buffs: Sequence[Buff] = ()) -> Build:
    return _c2(Build(
        character=CMC,
        constellation=constellation,
        weapon=weapon,
        artifacts=artifacts,
        extra_stats=merge_dicts(main_stats, STANDART_SUBSTAT_PRESET),
        extra_buffs=tuple(extra_buffs),
        time=TIMES["Крио ГГ"],
    ), danika_c2_hits)

def anastasia_build(constellation: int = 0, weapon=BREEZEBORNE_BOW.at(1), artifacts=(STELLAR_SET,),
                    main_stats=MAIN_ATK, danika_c2_hits: int = 0,
                    extra_buffs: Sequence[Buff] = ()) -> Build:
    return _c2(_frostglow(Build(
        character=ANASTASIA,
        constellation=constellation,
        weapon=weapon,
        artifacts=artifacts,
        extra_stats=merge_dicts(main_stats, STANDART_SUBSTAT_PRESET),
        extra_buffs=tuple(extra_buffs),
        time=TIMES["Анастасия"],
    )), danika_c2_hits)


def danika_build(constellation: int = 0, weapon=FAV_GREATSWORD, artifacts=(HEART_OF_FORGE,),
                 main_stats=DANIKA_MAIN_ER, extra_buffs: Sequence[Buff] = ()) -> Build:
    return _c2(_frostglow(Build(
        character=DANIKA,
        constellation=constellation,
        weapon=weapon,
        artifacts=artifacts,
        extra_stats=merge_dicts(main_stats, STANDART_SUBSTAT_FULL_ATK_PRESET),
        extra_buffs=tuple(extra_buffs),
        time=TIMES["Даника"],
    )), C2_OTHER_STACKS if constellation >= 2 else 0)


def qiqi_build(constellation: int = 0, weapon=FAV_SWORD, artifacts=(MILLELITH,),
               main_stats={S.ATK_PCT: 0.466 * 1, S.CRIT_VALUE: 0.622},
               extra_buffs: Sequence[Buff] = ()) -> Build:
    return _frostglow(Build(
        character=QIQI,
        constellation=constellation,
        weapon=weapon,
        artifacts=artifacts,
        extra_stats=merge_dicts(main_stats, STANDART_SUBSTAT_PRESET),
        extra_buffs=tuple(extra_buffs),
        time=TIMES["Ци Ци"],
    ))


def make_team(name: str, cmc_c: int = 6, cmc_weapon=EXAIPHANES.at(5),
              cmc_artifacts=(DISENCHANTMENT,),
              anastasia_c: int = 0, anastasia_weapon=BREEZEBORNE_BOW.at(1), anastasia_artifacts=(DISENCHANTMENT,),
              danika_c: int = 0, danika_weapon=FAV_GREATSWORD, danika_artifacts=(HEART_OF_FORGE,),
              qiqi_c: int = 0, qiqi_weapon=FAV_SWORD, qiqi_artifacts=(MILLELITH,)) -> Team:
    c2 = danika_c >= 2
    return Team(
        name=name,
        builds=[
            cryo_mc_build(cmc_c, cmc_weapon, cmc_artifacts,
                          danika_c2_hits=C2_ACTIVE_STACKS if c2 else 0),
            anastasia_build(anastasia_c, anastasia_weapon, anastasia_artifacts, danika_c2_hits=C2_OTHER_STACKS if c2 else 0),
            danika_build(danika_c, danika_weapon, danika_artifacts),
            qiqi_build(qiqi_c, qiqi_weapon, qiqi_artifacts),
        ],
        enemy=enemy(),
        buffs=TEAM_BUFFS,
        rotation=ROTATION,
        config=Config(),
    )


def team_name(cmc_c: int = 6, cmc_weapon=EXAIPHANES.at(5),
              anastasia_c: int = 0, anastasia_weapon=BREEZEBORNE_BOW.at(1),
              danika_c: int = 0, danika_weapon=FAV_GREATSWORD,
              qiqi_c: int = 0, qiqi_weapon=FAV_SWORD) -> str:
    _dw = (f" ({danika_weapon.name})" if danika_weapon.name != FAV_GREATSWORD.name else "")
    return (f"C{cmc_c}R{cmc_weapon.refinement} Крио ГГ, "
            + f"C{anastasia_c}R{anastasia_weapon.refinement} Анастасия" + ", "
            + f"C{danika_c}R{danika_weapon.refinement} Даника{_dw}" + ", "
            + f"C{qiqi_c}R0 Ци Ци")


VARIANTS = ({"danika_c": 0}, {"danika_c": 1}, {"danika_c": 2},
            {"danika_c": 0, "danika_weapon": SPRING_TIDE},  # Даника с сигной (Весенний прилив R1)
)

BASE_NAME = team_name()


def all_teams() -> Dict[str, Team]:
    out: Dict[str, Team] = {}
    for kw in VARIANTS:
        name = team_name(**kw) # pyright: ignore[reportArgumentType]
        out[name] = make_team(name, **kw) # pyright: ignore[reportArgumentType]
    return out
