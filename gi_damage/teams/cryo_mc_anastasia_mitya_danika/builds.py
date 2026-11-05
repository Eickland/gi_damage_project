"""
Отряд звёздного проводника: Крио ГГ (ДД на поле) / Анастасия / Митя / Даника.

Ротация: Анастасия EQ / Одетта EE / Митя E / Крио ГГ N2 P N2 N2 C N2 Q N2 N2.
Реакций, наносящих урон, нет. Резонанс — крио.

Крио ГГ: C6R5 (Пробуждение R5), Разочарование, комбо как в
cryo_mc_odette_sucrose_alyosha: N2 P N2 N2 C N2 Q N2 N2 (9.2 с).
C6 Крио ГГ (окно FROSTGLOW, 15 с после взрыва): ротация ~16.1 с, окно
перекрывает почти всю её, поэтому все удары остальных — с FROSTGLOW.
An Unfinished Requiem: +1 стак Polestar всем ударам SC отряда (polar_shift()).
Эпос Мити (окно TTDS_FULL) — на всех ударах Крио ГГ: он идёт сразу после Мити.

Артефакты: Анастасия — Звёздный сет, Митя — Миллелит (Эпос R5), Одетта — Звёздный сет, Крио ГГ — Разочарование.
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
from ...data.characters.cryo_mc import CMC_COMBO_DICT, CMC_SC_DD_TIME
from ...data.characters.danika import (DANIKA_COMBO_DICT, C2_ACTIVE_STACKS,
                                       C2_OTHER_STACKS, tag_stellar_conduct_hits, add_tags)
from ...data.characters.danika import (C2_ACTIVE_STACKS, C2_OTHER_STACKS,
                                       tag_stellar_conduct_hits, add_tags)
from ...data.characters.anastasia import anastasia_support, polar_shift, CROWN_HITS
from ...data.characters.mitya import MITYA_COMBO_DICT
from ...data.weapons import *

TEAM_BUFFS = (
    Buff(S.CRIT_VALUE, 0.30, target=TEAM,
         source="Крио резонанс: +15% крит. шанса (0.30 крит-вэлью)"),
)

#: Время каждого персонажа в ротации (секунды)
TIMES = {"Крио ГГ": CMC_SC_DD_TIME+1.3, "Анастасия": 3.0, "Митя": 1.5, "Даника": 3}

ROTATION = "Анастасия EQ/Даника EQ/Митя E/Крио ГГ N2 P N2 N2 C N2 Q N2 N2"

MAIN_ATK = {S.ATK_PCT: 0.466 * 2, S.CRIT_VALUE: 0.622}       # АТК/АТК/крит
MAIN_EM = {S.BASE_EM: 187.0 * 2, S.CRIT_VALUE: 0.622}        # МС/МС/крит
FULL_ATK = {S.ATK_PCT: 0.466 * 3}                            # АТК/АТК/АТК (Даника)

#: Комбо с +1 стаком Polestar (Requiem Анастасии)
CMC = polar_shift(CMC_COMBO_DICT["cmc_sc_dd_combo"])
ANASTASIA = polar_shift(anastasia_support("sc", [occ(CROWN_HITS, OFF)]))
MITYA = polar_shift(MITYA_COMBO_DICT["support_steady"])
DANIKA = DANIKA_COMBO_DICT["support_eq"]


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
    return _c2(add_tags(Build(
        character=CMC,
        constellation=constellation,
        weapon=weapon,
        artifacts=artifacts,
        extra_stats=merge_dicts(main_stats, STANDART_SUBSTAT_PRESET),
        extra_buffs=tuple(extra_buffs),
        time=TIMES["Крио ГГ"],
    ), TTDS_FULL), danika_c2_hits)

def anastasia_build(constellation: int = 0, weapon=ARTEMISIA, artifacts=(STELLAR_SET,),
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


def mitya_build(constellation: int = 0, weapon=TTDS_FULL_CATALYSATOR, artifacts=(MILLELITH,),
                main_stats=MAIN_EM, danika_c2_hits: int = 0,
                extra_buffs: Sequence[Buff] = ()) -> Build:
    return _c2(_frostglow(Build(
        character=MITYA,
        constellation=constellation,
        weapon=weapon,
        artifacts=artifacts,
        extra_stats=merge_dicts(main_stats, STANDART_SUBSTAT_PRESET),
        extra_buffs=tuple(extra_buffs),
        time=TIMES["Митя"],
    )), danika_c2_hits)


def danika_build(constellation: int = 0, weapon=ATONEMENT, artifacts=(HEART_OF_FORGE,),
                 main_stats=FULL_ATK, extra_buffs: Sequence[Buff] = ()) -> Build:
    return _c2(_frostglow(Build(
        character=DANIKA,
        constellation=constellation,
        weapon=weapon,
        artifacts=artifacts,
        extra_stats=merge_dicts(main_stats, STANDART_SUBSTAT_FULL_ATK_PRESET),
        extra_buffs=tuple(extra_buffs),
        time=TIMES["Даника"],
    )), C2_OTHER_STACKS if constellation >= 2 else 0)


def make_team(name: str, cmc_c: int = 6, cmc_weapon=EXAIPHANES.at(5),
              cmc_artifacts=(DISENCHANTMENT,),
              anastasia_c: int = 0, anastasia_weapon=ARTEMISIA, anastasia_artifacts=(STELLAR_SET,),
              mitya_c: int = 0, mitya_weapon=TTDS_FULL_CATALYSATOR, mitya_artifacts=(MILLELITH,),
              odette_c: int = 0, odette_weapon=ATONEMENT, odette_artifacts=(HEART_OF_FORGE,)) -> Team:
    c2 = False
    return Team(
        name=name,
        builds=[
            cryo_mc_build(cmc_c, cmc_weapon, cmc_artifacts,
                          danika_c2_hits=C2_ACTIVE_STACKS if c2 else 0),
            anastasia_build(anastasia_c, anastasia_weapon, anastasia_artifacts, danika_c2_hits=0),
            mitya_build(mitya_c, mitya_weapon, mitya_artifacts),
            danika_build(odette_c, odette_weapon, odette_artifacts),
        ],
        enemy=enemy(),
        buffs=TEAM_BUFFS,
        rotation=ROTATION,
        config=Config(),
    )


def team_name(cmc_c: int = 6, cmc_weapon=EXAIPHANES.at(5),
              anastasia_c: int = 0, anastasia_weapon=ARTEMISIA,
              mitya_c: int = 0, mitya_weapon=TTDS_FULL_CATALYSATOR,
              odette_c: int = 0, odette_weapon=SILVER_LIGHT) -> str:
    _dw = (f" ({odette_weapon.name})" if odette_weapon.name != ATONEMENT.name else "")
    return (f"C{cmc_c}R{cmc_weapon.refinement} Крио ГГ, "
            + f"C{anastasia_c}R{anastasia_weapon.refinement} Анастасия" + ", "
            + f"C{mitya_c}R{mitya_weapon.refinement} Митя" + ", "
            + f"C{odette_c}R{odette_weapon.refinement} Даника{_dw}")


VARIANTS = ({},
            {"odette_weapon": SPRING_TIDE},  # Даника с сигной (Весенний прилив R1)
)

BASE_NAME = team_name()


def all_teams() -> Dict[str, Team]:
    out: Dict[str, Team] = {}
    for kw in VARIANTS:
        name = team_name(**kw)
        out[name] = make_team(name, **kw)
    return out
