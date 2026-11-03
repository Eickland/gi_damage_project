"""
Отряд лунных бутонов: Нефер / Колумбина / Лаума / Нилу.

Ротация: Колумбина E Q CA / Лаума hE Q / Нилу E E E / Нефер (E sCA sCA sCA) × 2.
Moonsign: Ascendant Gleam активен (Нефер, Колумбина, Лаума).
Урона реакции у лунных бутонов нет — только прямой урон.

Отряду (постоянно):
    Дендро резонанс: +80 МС;
    Гидро резонанс: +25% HP;
    Нилу не из лунного региона: бонус лунных реакций 0.6% за 1000 HP (макс. 36%).

Окна баффов:
    INST       (Инструктор на Нилу) — все удары Нефер и одно срабатывание
               Gravity Interference Колумбины (5 ударов);
    PALE_HYMN  (Лаума, 36 стаков) — 18 ударов теней Нефер и 18 ударов бутонов
               Колумбины (15 Gravity Interference + 3 Moondew Cleanse).
"""

from __future__ import annotations

from typing import Dict, Sequence

from ...core.buffs import OTHERS, SELF, TEAM, Buff, temp
from ...core.engine import Config, Team
from ...core.entities import Build, Enemy, ArtifactSet
from ...core.stats import S
from ...core.utilits import merge_dicts
from ...data.artifacts import *
from ...data.artifacts_presets import *
from ...data.tags import *
from ...data.characters.nefer import NEFER_COMBO_DICT, NEFER_TIME
from ...data.characters.lauma import LAUMA_COMBO_DICT, LAUMA_TIME
from ...data.characters.columbina import (COLUMBINA_COMBO_DICT, COLUMBINA_TIME,
                                          MOONDEW_CLEANSE_TIME)
from ...data.characters.nilou import NILOU_COMBO_DICT, NILOU_NAME, NILOU_TIME
from ...data.weapons import *
from ...data.team_buffs import lunar_outsider_buff

TEAM_BUFFS = (
    Buff(S.BASE_EM, 80.0, target=TEAM, source="Дендро резонанс: +80 МС"),
    Buff(S.HP_PCT, 0.25, target=TEAM, source="Гидро резонанс: +25% HP"),
    # Нилу не из лунного региона: +0.6% урона лунных реакций за 1000 HP (макс. 36%)
    lunar_outsider_buff(NILOU_NAME, "hydro"),
)

ROTATION = "Колумбина EQ CA/Лаума hE Q/Нилу EEE/Нефер (E sCA sCA sCA)×2"

MAIN_EM_EM_CRIT = {S.BASE_EM: 187.0 * 2, S.CRIT_VALUE: 0.622}
MAIN_HP_HP_HP = {S.HP_PCT: 0.329 * 3}


def enemy() -> Enemy:
    return Enemy(res={"dendro": 0.10, "hydro": 0.10},
                 def_mult=0.4875, elevation=0.0)


def nefer_build(constellation: int = 0, weapon=BLACKMARROW, artifacts=(NIGHT_SKY,),
                main_stats=MAIN_EM_EM_CRIT, extra_buffs: Sequence[Buff] = ()) -> Build:
    return Build(
        character=NEFER_COMBO_DICT["lb_combo"],
        constellation=constellation,
        weapon=weapon,
        artifacts=artifacts,
        extra_stats=merge_dicts(main_stats, STANDART_SUBSTAT_PRESET_EM_SCALE),
        extra_buffs=tuple(extra_buffs),
        time=NEFER_TIME,
    )


def lauma_build(constellation: int = 0, weapon=SPINDLELUTE, artifacts=(DEEPWOOD,),
                main_stats={S.BASE_EM: 187.0 * 3}, extra_buffs: Sequence[Buff] = ()) -> Build:
    return Build(
        character=LAUMA_COMBO_DICT["hold_eq"],
        constellation=constellation,
        weapon=weapon,
        artifacts=artifacts,
        extra_stats=merge_dicts(main_stats, STANDART_SUBSTAT_PRESET_EM_SCALE),
        extra_buffs=tuple(extra_buffs),
        time=LAUMA_TIME,
    )


def columbina_build(constellation: int = 0, weapon=PROTOTYPE_AMBER, artifacts=(SERENADE,),
                    main_stats={S.HP_PCT: 0.466 * 1, S.CRIT_VALUE: 0.622},
                    extra_buffs: Sequence[Buff] = ()) -> Build:
    return Build(
        character=COLUMBINA_COMBO_DICT["lbloom_nefer_lauma"],
        constellation=constellation,
        weapon=weapon,
        artifacts=artifacts,
        extra_stats=merge_dicts(main_stats, STANDART_SUBSTAT_PRESET),
        extra_buffs=tuple(extra_buffs),
        time=COLUMBINA_TIME + MOONDEW_CLEANSE_TIME,   # E Q + CA (Moondew Cleanse)
    )


def nilou_build(constellation: int = 0, weapon=FAV_SWORD, artifacts=(INSTRUCTOR,),
                main_stats=MAIN_HP_HP_HP, extra_buffs: Sequence[Buff] = ()) -> Build:
    return Build(
        character=NILOU_COMBO_DICT["eee"],
        constellation=constellation,
        weapon=weapon,
        artifacts=artifacts,
        extra_stats=merge_dicts(main_stats, STANDART_SUBSTAT_PRESET),
        extra_buffs=tuple(extra_buffs),
        time=NILOU_TIME,
    )


def make_team(name: str, nefer_c: int = 0, columbina_c: int = 0, lauma_c: int = 0,
              nilou_c: int = 2,
              nefer_weapon=BLACKMARROW.at(5), columbina_weapon=PROTOTYPE_AMBER.at(5),
              lauma_weapon=SPINDLELUTE.at(5), nilou_weapon=FAV_SWORD.at(5),
              nefer_artifacts=(NIGHT_SKY,), columbina_artifacts=(SERENADE,),
              lauma_artifacts=(DEEPWOOD,), nilou_artifacts=(INSTRUCTOR,)) -> Team:
    return Team(
        name=name,
        builds=[
            # порядок = ротация: Колумбина → Лаума → Нилу → Нефер
            columbina_build(columbina_c, columbina_weapon, columbina_artifacts),
            lauma_build(lauma_c, lauma_weapon, lauma_artifacts),
            nilou_build(nilou_c, nilou_weapon, nilou_artifacts),
            nefer_build(nefer_c, nefer_weapon, nefer_artifacts),
        ],
        enemy=enemy(),
        buffs=TEAM_BUFFS,
        rotation=ROTATION,
        config=Config(),
    )


def team_name(nefer_c=6, columbina_c=6, lauma_c=6, nilou_c=2) -> str:
    return (f"C{nefer_c} Нефер, C{columbina_c} Колумбина, C{lauma_c} Лаума, "
            f"C{nilou_c} Нилу")


BASE_NAME = team_name()


def all_teams() -> Dict[str, Team]:
    return {BASE_NAME: make_team(BASE_NAME)}
