"""
Отряд звёздного проводника: Сандроне / Одетта / Анастасия / C6 Алеша.

Ротация: Алеша EQ / Анастасия EQ / Одетта EE / Сандроне E CA EQ CA E CA E.
Реакций, наносящих урон, нет. Резонанс — крио (3 крио + 1 электро).

Сандроне: «Тень волны» R5 — в отряде один электро и есть лечение (Алеша),
как в базовой линии (gi_damage/data/baseline.py).
Анастасия — саппорт (Милосердие): корона 10 атак вне поля, Triumph.
An Unfinished Requiem: стаки Polestar — polar_always у Анастасии (Team.polar_plan()).
Алеша C6: баффы активному персонажу (на поле) — на ударах Сандроне.

Артефакты: Сандроне — Разочарование, Одетта — Звёздный сет,
Анастасия — Звёздный сет, Алеша — Сердце горна.
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
from ...data.characters.alyosha import ALYOSHA_COMBO_DICT
from ...data.weapons import *

TEAM_BUFFS = (
    Buff(S.CRIT_VALUE, 0.30, target=TEAM,
         source="Крио резонанс: +15% крит. шанса (0.30 крит-вэлью)"),
)

#: Время каждого персонажа в ротации (секунды)
TIMES = {"Сандроне": 14, "Алеша": 1.9, "Анастасия": 3.5, "Одетта": 2.4}

ROTATION = "Алеша EQ/Анастасия EQ/Одетта EE/Сандроне E CA EQ CA E"

MAIN_ATK = {S.ATK_PCT: 0.466 * 2, S.CRIT_VALUE: 0.622}       # АТК/АТК/крит

SANDRONE = SANDRONE_COMBO_DICT["sandrone_sc_combo"]
ODETTE = ODETTE_COMBO_DICT["odette_ssc_combo"]
ANASTASIA = ANASTASIA_COMBO_DICT["support_sc"]
ALYOSHA = ALYOSHA_COMBO_DICT["sc_combo"]


def enemy() -> Enemy:
    return Enemy(res={"anemo": 0.10, "cryo": 0.10, "electro": 0.10},
                 def_mult=0.4875, elevation=0.0)


def sandrone_build(constellation: int = 0, weapon=TIDAL_SHADOW.at(5), artifacts=(DISENCHANTMENT,),
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


def anastasia_build(constellation: int = 0, weapon=BREEZEBORNE_BOW.at(1), artifacts=(STELLAR_SET,),
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


def alyosha_build(constellation: int = 6, weapon=FAV_LANCE, artifacts=(HEART_OF_FORGE,),
                  extra_buffs: Sequence[Buff] = ()) -> Build:
    return Build(
        character=ALYOSHA,
        constellation=constellation,
        weapon=weapon,
        artifacts=artifacts,
        extra_stats=merge_dicts(
            {S.ATK_PCT: 0.466 * 1, S.CRIT_VALUE: 0.622},
            STANDART_SUBSTAT_PRESET),
        extra_buffs=tuple(extra_buffs),
        time=TIMES["Алеша"],
    )


def make_team(name: str, sandrone_c: int = 0, sandrone_weapon=TIDAL_SHADOW.at(5),
              odette_c: int = 0, odette_weapon=SILVER_LIGHT,
              anastasia_c: int = 0, anastasia_weapon=BREEZEBORNE_BOW.at(1),
              alyosha_c: int = 6, alyosha_weapon=FAV_LANCE,
              sandrone_artifacts=(DISENCHANTMENT,), odette_artifacts=(STELLAR_SET,),
              anastasia_artifacts=(MILLELITH,), alyosha_artifacts=(HEART_OF_FORGE,)) -> Team:
    return Team(
        name=name,
        builds=[
            sandrone_build(sandrone_c, sandrone_weapon, sandrone_artifacts),
            odette_build(odette_c, odette_weapon, odette_artifacts),
            anastasia_build(anastasia_c, anastasia_weapon, anastasia_artifacts),
            alyosha_build(alyosha_c, alyosha_weapon, alyosha_artifacts),
        ],
        enemy=enemy(),
        buffs=TEAM_BUFFS,
        rotation=ROTATION,
        config=Config(),
        dd="Сандроне",
    )


def team_name(sandrone_c: int = 0, sandrone_weapon=TIDAL_SHADOW.at(5),
              odette_c: int = 0, odette_weapon=SILVER_LIGHT,
              anastasia_c: int = 0, anastasia_weapon=BREEZEBORNE_BOW.at(1),
              alyosha_c: int = 6, alyosha_weapon=FAV_LANCE) -> str:
    return (f"C{sandrone_c}R{sandrone_weapon.refinement} Сандроне, "
            f"C{odette_c}R{odette_weapon.refinement} Одетта, "
            f"C{anastasia_c}R{anastasia_weapon.refinement} Анастасия, "
            f"C{alyosha_c}R{alyosha_weapon.refinement} Алеша")


VARIANTS = ({},)

BASE_NAME = team_name()


def all_teams() -> Dict[str, Team]:
    out: Dict[str, Team] = {}
    for kw in VARIANTS:
        name = team_name(**kw)
        out[name] = make_team(name, **kw)
    return out
