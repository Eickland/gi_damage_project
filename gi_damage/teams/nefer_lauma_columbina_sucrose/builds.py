"""
Отряд лунных бутонов: Нефер / Лаума / Колумбина / Сахароза.

Ротация: Лаума hE Q / Колумбина E Q CA / Сахароза E (Q) / Нефер (E sCA sCA sCA) × 2.
Moonsign: Ascendant Gleam активен. Сахароза рассеивает гидро.
Урона реакции у лунных бутонов нет — только прямой урон.

Окна баффов:
    Отряду: бонус лунных реакций от МС Сахарозы (не из лунного региона).
    INST       (Инструктор + A4 Сахарозы) — все удары Нефер и одно срабатывание
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
from ...data.characters.sucrose import SUCROSE_COMBO_DICT
from ...data.weapons import *
from ...data.team_buffs import lunar_outsider_buff

TEAM_BUFFS = (
    Buff(S.BASE_EM, 80.0, target=TEAM, source="Дендро резонанс: +80 МС"),
    # Сахароза не из лунного региона: +2.25% урона лунных реакций за 100 МС (макс. 36%)
    lunar_outsider_buff("Сахароза", "anemo"),
)

SUCROSE_TIME = 2.95

ROTATION = "Лаума hE Q/Колумбина EQ CA/Сахароза E(Q)/Нефер (E sCA sCA sCA)×2"

MAIN_EM_EM_CRIT = {S.BASE_EM: 187.0 * 2, S.CRIT_VALUE: 0.622}


def enemy() -> Enemy:
    return Enemy(res={"dendro": 0.10, "hydro": 0.10, "anemo": 0.10},
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
                    main_stats={S.HP_PCT: 0.466 * 2, S.CRIT_VALUE: 0.622},
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


def sucrose_build(constellation: int = 6, weapon=SACFRAG, artifacts=(INSTRUCTOR,),
                  extra_buffs: Sequence[Buff] = ()) -> Build:
    return Build(
        character=SUCROSE_COMBO_DICT["hydro_burst_combo"],
        constellation=constellation,
        weapon=weapon,
        artifacts=artifacts,
        extra_stats=merge_dicts({S.BASE_EM: 139 * 2 + 187}, STANDART_SUBSTAT_PRESET),
        extra_buffs=tuple(extra_buffs),
        time=SUCROSE_TIME,
    )


def make_team(name: str, nefer_c: int = 2, lauma_c: int = 0, columbina_c: int = 0,
              nefer_weapon=BLACKMARROW, lauma_weapon=SPINDLELUTE,
              columbina_weapon=PROTOTYPE_AMBER, sucrose_weapon=SACFRAG,
              nefer_artifacts=(NIGHT_SKY,), lauma_artifacts=(DEEPWOOD,),
              columbina_artifacts=(SERENADE,), sucrose_artifacts=(INSTRUCTOR,)) -> Team:
    return Team(
        name=name,
        builds=[
            nefer_build(nefer_c, nefer_weapon, nefer_artifacts),
            lauma_build(lauma_c, lauma_weapon, lauma_artifacts),
            columbina_build(columbina_c, columbina_weapon, columbina_artifacts),
            sucrose_build(6, sucrose_weapon, sucrose_artifacts),
        ],
        enemy=enemy(),
        buffs=TEAM_BUFFS,
        rotation=ROTATION,
        config=Config(),
    )


def team_name(nefer_c=0, lauma_c=0, columbina_c=0) -> str:
    return (f"C{nefer_c} Нефер, C{lauma_c} Лаума, C{columbina_c} Колумбина, C6 Сахароза")


BASE_NAME = team_name()


def all_teams() -> Dict[str, Team]:
    return {BASE_NAME: make_team(BASE_NAME)}
