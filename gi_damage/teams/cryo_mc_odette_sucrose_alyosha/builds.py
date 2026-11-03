"""
Отряд звёздного проводника: Крио ГГ (ДД на поле) / Одетта / Сахароза / Алеша.

Ротация: Алеша EQ / Одетта EE Q / Сахароза EQ / Крио ГГ N2 P N2 N2 C N2 Q N2 N2.
Реакций, наносящих урон, нет (звёздный проводник).

Отряду (постоянно):
    Крио резонанс (Крио ГГ + Одетта): +15% крит. шанса.

Окна баффов:
    INST    (A4 Сахарозы) и VV_CRYO (Изумрудная тень, рассеивание крио) —
            все удары Крио ГГ и удары Одетты, как в отряде с Сандроне.
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
from ...data.characters.cryo_mc import CMC_COMBO_DICT, CMC_SC_DD_TIME
from ...data.characters.odette import (odette_burst_buffs, ODETTE_BURST_TIME,
                                       ODETTE_COMBO_DICT, ODETTE_BURST_SOURCES)
from ...data.characters.sucrose import SUCROSE_COMBO_DICT
from ...data.characters.alyosha import ALYOSHA_COMBO_DICT
from ...data.weapons import *

TEAM_BUFFS = (
    Buff(S.CRIT_VALUE, 0.30, target=TEAM,
         source="Крио резонанс: +15% крит. шанса (0.30 крит-вэлью)"),
)

#: Время каждого персонажа в ротации (секунды)
TIMES = {"Крио ГГ": CMC_SC_DD_TIME, "Одетта": 2.4 + ODETTE_BURST_TIME,   # 3.9 с с взрывом
         "Сахароза": 3.5, "Алеша": 1.9}

ROTATION = "Алеша EQ/Крио ГГ N2/Сахароза Ed/Одетта EQE/Сахароза N1E(Q)/Крио ГГ N2 P N2 C N2 Q N2 N2"

CMC_MAIN_ATK = {S.ATK_PCT: 0.466 * 2, S.CRIT_VALUE: 0.622}       # АТК/АТК/крит


def enemy() -> Enemy:
    return Enemy(res={"anemo": 0.10, "cryo": 0.10, "electro": 0.10},
                 def_mult=0.4875, elevation=0.0)


def cryo_mc_build(constellation: int = 4, weapon=EXAIPHANES.at(3),
                  artifacts=(DISENCHANTMENT,), main_stats=CMC_MAIN_ATK,
                  extra_buffs: Sequence[Buff] = ()) -> Build:
    return Build(
        character=CMC_COMBO_DICT["cmc_sc_dd_combo"],
        constellation=constellation,
        weapon=weapon,
        artifacts=artifacts,
        extra_stats=merge_dicts(main_stats, HIGH_SUBSTAT_PRESET),
        extra_buffs=tuple(extra_buffs),
        time=TIMES["Крио ГГ"],
    )


def odette_build(constellation: int = 0, weapon=SILVER_LIGHT, artifacts=(DISENCHANTMENT,),
                 extra_buffs: Sequence[Buff] = ()) -> Build:
    """Одетта в этом отряде всегда применяет взрыв стихии."""
    return Build(
        character=ODETTE_COMBO_DICT["odette_ssc_combo_sucrose_cmc"],
        constellation=constellation,
        weapon=weapon,
        artifacts=artifacts,
        extra_stats=merge_dicts(
            {S.ATK_PCT: 0.466 * 2, S.CRIT_VALUE: 0.622},
            HIGH_SUBSTAT_PRESET),
        extra_sources=ODETTE_BURST_SOURCES,
        extra_buffs=tuple(extra_buffs) + tuple(odette_burst_buffs(constellation)),
        time=TIMES["Одетта"],
    )


def sucrose_build(constellation: int = 6, weapon=CODEX_FAVONIUS, artifacts=(VIRIDESCENT,),
                  extra_buffs: Sequence[Buff] = ()) -> Build:
    return Build(
        character=SUCROSE_COMBO_DICT["cryo_burst_combo"],
        constellation=constellation,
        weapon=weapon,
        artifacts=artifacts,
        extra_stats=merge_dicts({S.BASE_EM: 187 * 3}, STANDART_SUBSTAT_PRESET),
        extra_buffs=tuple(extra_buffs),
        time=TIMES["Сахароза"],
    )


def alyosha_build(constellation: int = 6, weapon=FAV_LANCE, artifacts=(HEART_OF_FORGE,),
                  extra_buffs: Sequence[Buff] = ()) -> Build:
    return Build(
        character=ALYOSHA_COMBO_DICT["sc_combo"],
        constellation=constellation,
        weapon=weapon,
        artifacts=artifacts,
        extra_stats=merge_dicts(
            {S.ATK_PCT: 0.466 * 1, S.CRIT_VALUE: 0.622},
            STANDART_SUBSTAT_PRESET),
        extra_buffs=tuple(extra_buffs),
        time=TIMES["Алеша"],
    )


def make_team(name: str, cmc_c: int = 6, cmc_weapon=EXAIPHANES.at(5),
              odette_c: int = 2, odette_weapon=FROSTFEATHER,
              alyosha_c: int = 6, alyosha_weapon=FAV_LANCE,
              sucrose_weapon=CODEX_FAVONIUS.at(5),
              cmc_artifacts=(DISENCHANTMENT,), odette_artifacts=(DISENCHANTMENT,),
              sucrose_artifacts=(VIRIDESCENT,), alyosha_artifacts=(HEART_OF_FORGE,),
              cmc_main_stats=CMC_MAIN_ATK) -> Team:
    return Team(
        name=name,
        builds=[
            cryo_mc_build(cmc_c, cmc_weapon, cmc_artifacts, cmc_main_stats),
            odette_build(odette_c, odette_weapon, odette_artifacts),
            sucrose_build(6, sucrose_weapon, sucrose_artifacts),
            alyosha_build(alyosha_c, alyosha_weapon, alyosha_artifacts),
        ],
        enemy=enemy(),
        buffs=TEAM_BUFFS,
        rotation=ROTATION,
        config=Config(),
    )


def team_name(cmc_c=6, cmc_r=5, odette_c=0, alyosha_c=6) -> str:
    return (f"C{cmc_c}R{cmc_r} Крио ГГ, C{odette_c}R0 Одетта, C6 Сахароза, "
            f"C{alyosha_c}R0 Алеша")


BASE_NAME = team_name()


def all_teams() -> Dict[str, Team]:
    return {BASE_NAME: make_team(BASE_NAME)}
