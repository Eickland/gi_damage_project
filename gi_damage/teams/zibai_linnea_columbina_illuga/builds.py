"""
Отряд лунной кристаллизации: Цзы Бай / Линея / Колумбина / Иллуги.

Все четверо — Moonsign, поэтому эффекты Ascendant Gleam активны.

Реакции лунной кристаллизации (Moondrift Harmony — удары лунных клеток):
    18 — пока Цзы Бай на поле, 6 — в остальное время;
    C2 Линеи: ещё 12 (6 + 6) от Heavy Overdrive Hammer.
    A4 Колумбины (Law of the New Moon): в среднем ×1.33 к числу ударов.

Окна баффов:
    NIGHTINGALE (взрыв Иллуги) — все удары Цзы Бай и удар Колумбины от C1;
    FIELD_CATALOG (C1 Линеи)   — удары LC Линеи (4), Цзы Бай (9, с C1 — 10),
                                 Колумбины (3).
"""

from __future__ import annotations

from typing import Dict, Sequence

from ...core.buffs import OTHERS, SELF, TEAM, Buff, temp
from ...core.engine import Config, Team
from ...core.entities import Build, Enemy, ArtifactSet
from ...core.reactions import lunar_crystallize_reaction
from ...core.stats import S
from ...core.utilits import merge_dicts
from ...data.artifacts import *
from ...data.artifacts_presets import *
from ...data.tags import *
from ...data.characters.zibai import ZIBAI_COMBO_DICT, ZIBAI_NAME, zibai_time
from ...data.characters.linnea import LINNEA_COMBO_DICT, LINNEA_NAME, LINNEA_TIME
from ...data.characters.columbina import (COLUMBINA_COMBO_DICT, COLUMBINA_NAME,
                                          COLUMBINA_TIME, MOONDRIFT_EXTRA)
from ...data.characters.illuga import ILLUGA_COMBO_DICT, ILLUGA_NAME, ILLUGA_TIME
from ...data.weapons import *

TEAM_BUFFS: tuple = (Buff("res_reduction.geo", 0.10, target=TEAM,
         source="Гео резонанс: -10% гео сопротивления"),)

ROTATION = "Линея E/Колумбина EQ/Иллуги EQ/Цзы Бай E N4sE N4sE Q N4sE N4sE"

#: Реакции за ротацию (до множителя A4 Колумбины)
LC_ON_ZIBAI = 12
LC_OFF_ZIBAI = 6
LC_LINNEA_C2_ON, LC_LINNEA_C2_OFF = 6, 6


def enemy() -> Enemy:
    return Enemy(res={"geo": 0.10, "hydro": 0.10}, def_mult=0.4875, elevation=0.0)


def reactions(linnea_c: int, with_columbina: bool = True):
    """Удары лунных клеток за ротацию."""
    k = 1.0 + (MOONDRIFT_EXTRA if with_columbina else 0.0)
    on = LC_ON_ZIBAI + (LC_LINNEA_C2_ON if linnea_c >= 2 else 0)
    off = LC_OFF_ZIBAI + (LC_LINNEA_C2_OFF if linnea_c >= 2 else 0)
    return (
        lunar_crystallize_reaction(on * k, name="Лунная кристаллизация (Цзы Бай на поле)"),
        lunar_crystallize_reaction(off * k, name="Лунная кристаллизация (Цзы Бай вне поля)",
                                   field_override={ZIBAI_NAME: OFF}),
    )


def zibai_build(constellation: int = 0, weapon=FLUTE_OF_EZPITZAL, artifacts=(NIGHT_SKY,),
                main_stats={S.DEF_PCT: 0.583 * 2, S.CRIT_VALUE: 0.622},
                extra_buffs: Sequence[Buff] = ()) -> Build:
    return Build(
        character=ZIBAI_COMBO_DICT["lc_combo"],
        constellation=constellation,
        weapon=weapon,
        artifacts=artifacts,
        extra_stats=merge_dicts(main_stats, STANDART_SUBSTAT_PRESET),
        extra_buffs=tuple(extra_buffs),
        time=zibai_time(constellation),
    )


def linnea_build(constellation: int = 0, weapon=COVENANT_FROST_SNOW, artifacts=(AUBADE,),
                 main_stats={S.DEF_PCT: 0.583 * 2, S.CRIT_VALUE: 0.622},
                 extra_buffs: Sequence[Buff] = ()) -> Build:
    return Build(
        character=LINNEA_COMBO_DICT["super_power"],
        constellation=constellation,
        weapon=weapon,
        artifacts=artifacts,
        extra_stats=merge_dicts(main_stats, STANDART_SUBSTAT_PRESET),
        extra_buffs=tuple(extra_buffs),
        time=LINNEA_TIME,
    )


def columbina_build(constellation: int = 0, weapon=PROTOTYPE_AMBER, artifacts=(AUBADE,),
                    main_stats={S.HP_PCT: 0.466 * 2, S.CRIT_VALUE: 0.622},
                    extra_buffs: Sequence[Buff] = ()) -> Build:
    return Build(
        character=COLUMBINA_COMBO_DICT["lc_support"],
        constellation=constellation,
        weapon=weapon,
        artifacts=artifacts,
        extra_stats=merge_dicts(main_stats, STANDART_SUBSTAT_PRESET),
        extra_buffs=tuple(extra_buffs),
        time=COLUMBINA_TIME,
    )


def illuga_build(constellation: int = 6, weapon=DRAGONS_BANE, artifacts=(SERENADE,),
                 main_stats={S.BASE_EM: 187.0 * 3},
                 extra_buffs: Sequence[Buff] = ()) -> Build:
    return Build(
        character=ILLUGA_COMBO_DICT["eq"],
        constellation=constellation,
        weapon=weapon,
        artifacts=artifacts,
        extra_stats=merge_dicts(main_stats, STANDART_SUBSTAT_PRESET),
        extra_buffs=tuple(extra_buffs),
        time=ILLUGA_TIME,
    )


def make_team(name: str, zibai_c: int = 0, linnea_c: int = 0,
              columbina_c: int = 0, illuga_c: int = 6,
              zibai_weapon=HARBINGER, linnea_weapon=COVENANT_FROST_SNOW,
              columbina_weapon=PROTOTYPE_AMBER, illuga_weapon=DRAGONS_BANE,
              zibai_artifacts=(NIGHT_SKY,), linnea_artifacts=(AUBADE,),
              columbina_artifacts=(SERENADE,), illuga_artifacts=(INSTRUCTOR,)) -> Team:
    return Team(
        name=name,
        builds=[
            zibai_build(zibai_c, zibai_weapon, zibai_artifacts),
            linnea_build(linnea_c, linnea_weapon, linnea_artifacts),
            columbina_build(columbina_c, columbina_weapon, columbina_artifacts),
            illuga_build(illuga_c, illuga_weapon, illuga_artifacts),
        ],
        enemy=enemy(),
        reactions=reactions(linnea_c),
        buffs=TEAM_BUFFS,
        rotation=ROTATION,
        config=Config(),
    )


def team_name(zibai_c=0, linnea_c=0, columbina_c=0, illuga_c=6) -> str:
    return (f"C{zibai_c}R5 Цзы Бай, C{linnea_c}R5 Линея, "
            f"C{columbina_c}R5 Колумбина, C{illuga_c}R5 Иллуги")


BASE_NAME = team_name()


def all_teams() -> Dict[str, Team]:
    return {BASE_NAME: make_team(BASE_NAME)}
