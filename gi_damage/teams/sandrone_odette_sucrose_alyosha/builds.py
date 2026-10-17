from __future__ import annotations

from typing import Dict, Sequence

from ...core.buffs import OTHERS, SELF, TEAM, Buff, temp
from ...core.engine import Config, Team
from ...core.entities import Build, Enemy, ArtifactSet
from ...core.reactions import ssw_anemo, ssw_vortex
from ...core.stats import S
from ...core.utilits import merge_dicts
from ...data.artifacts import *
from ...data.artifacts_presets import *
from ...data.tags import DREAM, INST, OFF, ON, MIZUKI_C1
from ...data.characters.odette import odette_burst_buffs, ODETTE_BURST_TIME, ODETTE_COMBO_DICT, ODETTE_BURST_SOURCES
from ...data.characters.sucrose import SUCROSE_COMBO_DICT
from ...data.characters.alyosha import ALYOSHA_COMBO_DICT
from ...data.characters.sandrone import SANDRONE_COMBO_DICT
from ...data.weapons import *

TEAM_BUFFS = (
    Buff(S.CRIT_VALUE, 0.30, target=TEAM,
         source="Крио резонанс: +15% крит. шанса (0.30 крит-вэлью)"),
)

#: Время каждого персонажа в ротации (секунды)
TIMES = {"Сандроне": 14.5, "Алеша": 1.65, "Одетта": 2.4, "Сахароза": 2.95}

ROTATION = "Алеша EQ/Одетта EE/Сахароза Ed(Q)/Сандроне E CA EQ CA/Сахароза Ed/Сандроне E CA E"

def enemy() -> Enemy:
    """Базовое сопротивление цели.
    """
    return Enemy(res={"anemo": 0.10, "cryo": 0.10},
                 def_mult=0.4875, elevation=0.0)
    
def sandrone_build(constellation: int, weapon, artifacts, extra_buffs: Sequence[Buff] = (),
                 main_stats={S.ATK_PCT: 0.466 * 2, S.CRIT_VALUE: 0.622}) -> Build:

    return Build(
        character=SANDRONE_COMBO_DICT["sandrone_sc_sucrose_combo"],
        constellation=constellation,
        weapon=weapon,
        artifacts=artifacts,
        extra_stats=merge_dicts(
            main_stats,
            STANDART_SUBSTAT_PRESET),
        extra_buffs=tuple(extra_buffs),
        time=TIMES["Сандроне"],
    )
    
def odette_build(constellation: int, weapon,artifacts=(MILLELITH,),
                 use_burst: bool | None = None,
                 extra_buffs: Sequence[Buff] = ()) -> Build:
    """use_burst=None — авто: до C4 не применяем, с C4 применяем."""
    if use_burst is None:
        use_burst = constellation >= 4
        
    return Build(
        character=ODETTE_COMBO_DICT["odette_ssc_combo_sucrose"],
        constellation=constellation,
        weapon=weapon,
        artifacts=artifacts,
        extra_stats=merge_dicts(
            {S.ATK_PCT: 0.466 * 2, S.CRIT_VALUE: 0.622},
            STANDART_SUBSTAT_PRESET),
        extra_sources=ODETTE_BURST_SOURCES if use_burst else (),
        extra_buffs=tuple(extra_buffs) + (odette_burst_buffs(constellation)
                                          if use_burst else ()),
        time=TIMES["Одетта"] + (ODETTE_BURST_TIME if use_burst else 0.0),
    )
    
def sucrose_build(artifacts, weapon=TTDS_FULL_CATALYSATOR, extra_buffs: Sequence[Buff] = ()) -> Build:
    
    main_stats = {S.BASE_EM: 187 * 3}
    
    return Build(
        character=SUCROSE_COMBO_DICT["cryo_burst_combo"],
        constellation=6,
        weapon=weapon,
        artifacts=artifacts,
        extra_stats=merge_dicts(
            main_stats,
            STANDART_SUBSTAT_PRESET),
        extra_buffs=tuple(extra_buffs),
        time=TIMES["Сахароза"],
    )
    
def alyosha_build(constellation: int, artifacts, weapon=FAV_LANCE, extra_buffs: Sequence[Buff] = ()) -> Build:
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
    
def make_team(name: str, sandrone_c: int, sandrone_weapon, odette_c, odette_weapon, sandrone_artifacts = (DISENCHANTMENT,), alyosha_artifacts = (HEART_OF_FORGE,),
              alyosha_weapon = FAV_LANCE, alyosha_c = 2, sucrose_art=(VIRIDESCENT,),odette_art=(MILLELITH,)) -> Team:
    """

    """
    return Team(
        name=name,
        builds=[
            sandrone_build(constellation=sandrone_c, weapon=sandrone_weapon, artifacts=sandrone_artifacts),
            sucrose_build(artifacts=sucrose_art),
            odette_build(constellation=odette_c, weapon=odette_weapon,artifacts=odette_art),
            alyosha_build(artifacts=alyosha_artifacts,weapon=alyosha_weapon,constellation=alyosha_c),
        ],
        enemy=enemy(),
        buffs=TEAM_BUFFS,
        rotation=ROTATION,
        config=Config(),
    )

def all_teams() -> Dict[str, Team]:
    variants = (
        ("C0R0 Сандроне, C0R0 Одетта, Сахароза, С2R0 Алеша", 0, TIDAL_SHADOW, 0, SILVER_LIGHT,(DISENCHANTMENT,),(HEART_OF_FORGE,),FAV_LANCE,2,(VIRIDESCENT,),(MILLELITH,)),
        ("C0R0 Сандроне, C0R0 Одетта, Сахароза, С6R0 Алеша", 0, TIDAL_SHADOW, 0, SILVER_LIGHT,(DISENCHANTMENT,),(HEART_OF_FORGE,),FAV_LANCE,6,(VIRIDESCENT,),(MILLELITH,)),
        ("C0R1 Сандроне, C0R0 Одетта, Сахароза, С6R0 Алеша", 0, TEASPOON, 0, SILVER_LIGHT,(DISENCHANTMENT,),(HEART_OF_FORGE,),FAV_LANCE,6,(VIRIDESCENT,),(MILLELITH,)),
        ("C0R0 Сандроне, C2R1 Одетта, Сахароза, С6R0 Алеша", 0, THOUSAND_SUNS, 2, FROSTFEATHER,(DISENCHANTMENT,),(HEART_OF_FORGE,),FAV_LANCE,6,(VIRIDESCENT,),(DISENCHANTMENT,)),



    )
    return {name: make_team(name, c, sandrone_w, c_odette, odette_w, sandrone_art, alyosha_art,alyosha_w,alyosha_c,sucr_art,odette_art) 
            for name, c, sandrone_w, c_odette, odette_w, sandrone_art, alyosha_art, alyosha_w,alyosha_c,sucr_art,odette_art in variants}
