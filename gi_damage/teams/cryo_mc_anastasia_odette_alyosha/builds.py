"""
Отряд звёздного проводника: Крио ГГ (ДД на поле) / Анастасия / Одетта / C6 Алеша.

Ротация: Алеша EQ / Анастасия EQ / Одетта EE / Крио ГГ N2 P N2 N2 C N2 Q N2 N2.
Реакций, наносящих урон, нет. Резонанс — крио.

Крио ГГ: C6R5 (Пробуждение R5), Разочарование, комбо cmc_sc_dd_combo (9.2 с).
Время ротации: 18.5 с — не короче отката взрыва Анастасии (бета, 18 с),
доп. N2 у Крио ГГ не нужны.
C6 Крио ГГ (окно FROSTGLOW, 15 с после взрыва): как в остальных отрядах
Крио ГГ-ДД, все удары остальных — с FROSTGLOW.
An Unfinished Requiem: стаки Polestar — polar_always у Анастасии (Team.polar_plan()).
Алеша C6: баффы активному персонажу (на поле) — на ударах Крио ГГ.

Артефакты: Анастасия — Звёздный сет, Одетта — Звёздный сет,
Алеша — Сердце горна, Крио ГГ — Разочарование.
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
from ...data.characters.odette import (odette_burst_buffs, ODETTE_BURST_TIME,
                                       ODETTE_COMBO_DICT, ODETTE_BURST_SOURCES)
from ...data.characters.danika import add_tags
from ...data.characters.anastasia import ANASTASIA_COMBO_DICT
from ...data.characters.alyosha import ALYOSHA_COMBO_DICT
from ...data.weapons import *

TEAM_BUFFS = (
    Buff(S.CRIT_VALUE, 0.30, target=TEAM,
         source="Крио резонанс: +15% крит. шанса (0.30 крит-вэлью)"),
)

#: Время каждого персонажа в ротации (секунды)
TIMES = {"Крио ГГ": CMC_SC_DD_TIME , "Анастасия": 3.5,
         "Одетта": 2.4, "Алеша": 1.9}

ROTATION = "Алеша EQ/Анастасия EQ/Одетта EQE/Крио ГГ N2 N2 N2 C N2 Q N2 N2"

MAIN_ATK = {S.ATK_PCT: 0.466 * 2, S.CRIT_VALUE: 0.622}       # АТК/АТК/крит

CMC = CMC_COMBO_DICT["cmc_sc_dd_combo"]
ANASTASIA = ANASTASIA_COMBO_DICT["support_sc"]
ODETTE = ODETTE_COMBO_DICT["odette_ssc_combo"]
ALYOSHA = ALYOSHA_COMBO_DICT["sc_combo"]


def enemy() -> Enemy:
    return Enemy(res={"anemo": 0.10, "cryo": 0.10, "electro": 0.10},
                 def_mult=0.4875, elevation=0.0)


def _frostglow(build: Build) -> Build:
    """C6 Крио ГГ: удар остальных под +40% урона звёздных реакций."""
    return add_tags(build, FROSTGLOW)


def cryo_mc_build(constellation: int = 6, weapon=EXAIPHANES.at(5), artifacts=(DISENCHANTMENT,),
                  main_stats=MAIN_ATK, extra_buffs: Sequence[Buff] = ()) -> Build:
    return Build(
        character=CMC,
        constellation=constellation,
        weapon=weapon,
        artifacts=artifacts,
        extra_stats=merge_dicts(main_stats, STANDART_SUBSTAT_PRESET),
        extra_buffs=tuple(extra_buffs),
        time=TIMES["Крио ГГ"],
    )


def anastasia_build(constellation: int = 0, weapon=BREEZEBORNE_BOW.at(1), artifacts=(STELLAR_SET,),
                    main_stats=MAIN_ATK, extra_buffs: Sequence[Buff] = ()) -> Build:
    return _frostglow(Build(
        character=ANASTASIA,
        constellation=constellation,
        weapon=weapon,
        artifacts=artifacts,
        extra_stats=merge_dicts(main_stats, STANDART_SUBSTAT_PRESET),
        extra_buffs=tuple(extra_buffs),
        time=TIMES["Анастасия"],
    ))


def odette_build(constellation: int = 0, weapon=SILVER_LIGHT, artifacts=(STELLAR_SET,),
                 use_burst: bool | None = None,
                 extra_buffs: Sequence[Buff] = ()) -> Build:
    """use_burst=None — авто: до C4 не применяем, с C4 применяем."""
    if use_burst is None:
        use_burst = constellation >= 4
    return _frostglow(Build(
        character=ODETTE,
        constellation=constellation,
        weapon=weapon,
        artifacts=artifacts,
        extra_stats=merge_dicts(MAIN_ATK, STANDART_SUBSTAT_PRESET),
        extra_sources=ODETTE_BURST_SOURCES if use_burst else (),
        extra_buffs=tuple(extra_buffs) + (odette_burst_buffs(constellation)
                                          if use_burst else ()),
        time=TIMES["Одетта"] + (ODETTE_BURST_TIME if use_burst else 0.0),
    ))


def alyosha_build(constellation: int = 6, weapon=FAV_LANCE, artifacts=(HEART_OF_FORGE,),
                  extra_buffs: Sequence[Buff] = ()) -> Build:
    return _frostglow(Build(
        character=ALYOSHA,
        constellation=constellation,
        weapon=weapon,
        artifacts=artifacts,
        extra_stats=merge_dicts(
            {S.ATK_PCT: 0.466 * 1, S.CRIT_VALUE: 0.622},
            STANDART_SUBSTAT_PRESET),
        extra_buffs=tuple(extra_buffs),
        time=TIMES["Алеша"],
    ))


def make_team(name: str, cmc_c: int = 6, cmc_weapon=EXAIPHANES.at(5),
              cmc_artifacts=(DISENCHANTMENT,),
              anastasia_c: int = 0, anastasia_weapon=BREEZEBORNE_BOW.at(1),
              anastasia_artifacts=(DISENCHANTMENT,),
              odette_c: int = 0, odette_weapon=SILVER_LIGHT, odette_artifacts=(STELLAR_SET,),
              alyosha_c: int = 6, alyosha_weapon=FAV_LANCE,
              alyosha_artifacts=(HEART_OF_FORGE,)) -> Team:
    return Team(
        name=name,
        builds=[
            cryo_mc_build(cmc_c, cmc_weapon, cmc_artifacts),
            anastasia_build(anastasia_c, anastasia_weapon, anastasia_artifacts),
            odette_build(odette_c, odette_weapon, odette_artifacts,use_burst=True),
            alyosha_build(alyosha_c, alyosha_weapon, alyosha_artifacts),
        ],
        enemy=enemy(),
        buffs=TEAM_BUFFS,
        rotation=ROTATION,
        config=Config(),
        dd="Крио ГГ",
    )


def team_name(cmc_c: int = 6, cmc_weapon=EXAIPHANES.at(5),
              anastasia_c: int = 0, anastasia_weapon=BREEZEBORNE_BOW.at(1),
              odette_c: int = 0, odette_weapon=SILVER_LIGHT,
              alyosha_c: int = 6, alyosha_weapon=FAV_LANCE) -> str:
    return (f"C{cmc_c}R{cmc_weapon.refinement} Крио ГГ, "
            f"C{anastasia_c}R{anastasia_weapon.refinement} Анастасия, "
            f"C{odette_c}R{odette_weapon.refinement} Одетта, "
            f"C{alyosha_c}R{alyosha_weapon.refinement} Алеша")


VARIANTS = ({},)

BASE_NAME = team_name()


def all_teams() -> Dict[str, Team]:
    out: Dict[str, Team] = {}
    for kw in VARIANTS:
        name = team_name(**kw)
        out[name] = make_team(name, **kw)
    return out
