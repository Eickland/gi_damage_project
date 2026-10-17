"""
Отряд Весна / Фарузан / Крио ГГ C2 / Одетта.

"""

from __future__ import annotations

from typing import Dict, Sequence

from ...core.buffs import OTHERS, SELF, TEAM, Buff, temp
from ...core.engine import Config, Team
from ...core.entities import Build, Enemy, ArtifactSet
from ...core.reactions import ssw_anemo, ssw_vortex
from ...core.stats import S
from ...core.utilits import merge_dicts
from ...data.artifacts import *
from ...data.artifacts_presets import STANDART_SUBSTAT_PRESET
from ...data.tags import *
from ...data.characters.odette import odette_burst_buffs, ODETTE_BURST_TIME, ODETTE_COMBO_DICT, ODETTE_BURST_SOURCES
from ...data.characters.diona import DIONA_COMBO_DICT
from ...data.characters.faruzan import FARUZAN_COMBO_DICT
from ...data.characters.cryo_mc import CMC_COMBO_DICT
from ...data.characters.vesna import VESNA_COMBO_DICT
from ...data.weapons import *

from dataclasses import replace
from gi_damage.core.cycle import Phase

VESNA_BASE_TIME = {"burst": 11.5, "no_burst": 11.5}
VESNA_C1_EXTRA = 0.5


def vesna_time(base: float, constellation: int) -> float:
    return base + (VESNA_C1_EXTRA if constellation > 0 else 0.0)


def vesna_combo(combo_key: str, base_time: float):
    """Правка сборки Весны: подставляет комбо и считает время по её созвездию."""
    return lambda b: replace(
        b,
        character=VESNA_COMBO_DICT[combo_key],
        time=vesna_time(base_time, b.constellation),
    )


def vesna_burst_cycle(burst_n: int, total_n: int):
    """взрыв в burst_n ротациях из total_n"""
    with_q = Phase(
        "Vesna (N1CE)2 QE (N1CE)2", burst_n,
        builds={"Весна": vesna_combo("vesna_ssw_burst_combo", VESNA_BASE_TIME["burst"])},
        reactions=reactions(),
    )
    without_q = Phase(
        "Vesna (N1CE)2 N3CE (N1CE)2", total_n - burst_n,
        builds={"Весна": vesna_combo("vesna_ssw_no_burst_combo", VESNA_BASE_TIME["no_burst"])},
        reactions=reactions(),
    )
    return (with_q, without_q)

# =========================================================================== #
#  Баффы уровня ОТРЯДА                                                        #
# =========================================================================== #
TEAM_BUFFS = (
    Buff(S.CRIT_VALUE, 0.30, target=TEAM,
         source="Крио резонанс: +15% крит. шанса (0.30 крит-вэлью)"),
)

#: Время каждого персонажа в ротации (секунды)
TIMES = {"Весна": 12.5, "Крио ГГ": 3.65, "Диона": 2.2, "Фарузан": 2.7}

ROTATION = "Faruzan EQ /CMC E Q CA/ Диона EQ/Vesna (N1CE)2 QE (N1CE)2"


# =========================================================================== #
#  Цель                                                                       #
# =========================================================================== #
def enemy() -> Enemy:
    """Базовое сопротивление цели.

    """
    return Enemy(res={"anemo": 0.10, "cryo": 0.10},
                 def_mult=0.4875, elevation=0.0)


# =========================================================================== #
#  Сборки                                                                     #
# =========================================================================== #
def vesna_build(constellation: int, weapon, artifacts, extra_buffs: Sequence[Buff] = ()) -> Build:

    return Build(
        character=VESNA_COMBO_DICT["vesna_ssw_burst_combo"],
        constellation=constellation,
        weapon=weapon,
        artifacts=(artifacts,),
        extra_stats=merge_dicts(
            {S.ATK_PCT: 0.466 * 2, S.CRIT_VALUE: 0.622},
            STANDART_SUBSTAT_PRESET),
        extra_buffs=tuple(extra_buffs),
        time=vesna_time(VESNA_BASE_TIME['burst'],constellation),
    )


def cryo_mc_build(constellation: int, artifacts, weapon=EXAIPHANES, extra_buffs: Sequence[Buff] = ()) -> Build:
    return Build(
        character=CMC_COMBO_DICT["cmc_ssw_mizuki_combo"],
        constellation=constellation,
        weapon=weapon,
        artifacts=(artifacts,),
        extra_stats=merge_dicts(
            {S.ATK_PCT: 0.466 * 2, S.CRIT_VALUE: 0.622},
            STANDART_SUBSTAT_PRESET),
        extra_buffs=tuple(extra_buffs),
        time=TIMES["Крио ГГ"],
    )


def diona_build(constellation: int, artifacts, weapon=FAV_BOW, extra_buffs: Sequence[Buff] = ()) -> Build:
    return Build(
        character=DIONA_COMBO_DICT["off_field"],
        constellation=constellation,
        weapon=weapon,
        artifacts=(artifacts,),
        extra_stats=merge_dicts(
            {S.ATK_PCT: 0.466 * 1, S.CRIT_VALUE: 0.622},
            STANDART_SUBSTAT_PRESET),
        extra_buffs=tuple(extra_buffs),
        time=TIMES["Диона"],
    )

def faruzan_build(weapon=FAV_BOW,artifacts:ArtifactSet=MILLELITH, extra_buffs: Sequence[Buff] = ()) -> Build:
    main_stats = {S.ATK_PCT: 0.446,S.CRIT_VALUE: 0.311,"dmg_bonus.anemo":0.466}
    return Build(
        character=FARUZAN_COMBO_DICT["ssw_combo"],
        constellation=6,
        weapon=weapon,
        artifacts=(artifacts,),
        extra_stats=merge_dicts(
            main_stats,
            STANDART_SUBSTAT_PRESET),
        extra_buffs=tuple(extra_buffs),
        time=TIMES["Фарузан"],
    )


# =========================================================================== #
#  Реакции                                                                    #
# =========================================================================== #
def reactions():
    """События звёздного рассеивания за одну ротацию.
    """
    return (
        ssw_anemo("Весна", 7,BREEZEBORNE,FROSTGLOW, name="SSW анемо (Весна)"),
        
        ssw_anemo("Фарузан", 7,BREEZEBORNE,FROSTGLOW, name="SSW анемо (Фарузан, Инструктор)"),
        
        # Детонации вихря
        ssw_vortex(2, 4, INST,BREEZEBORNE,FROSTGLOW,VV_CRYO, name="SSW вихрь ×3 стака"),
    )


# =========================================================================== #
#  Отряды                                                                     #
# =========================================================================== #
def make_team(name: str, vesna_c: int, vesna_weapon, diona_weapon,diona_artifacts, vesna_artifacts = SCARLET_PROOF, faruzan_artifacts = MILLELITH,
              faruzan_weapon = FAV_BOW, cmc_c=4, cmc_arts=HEART_OF_FORGE) -> Team:
    """Собрать отряд. vesna_c — созвездие Мидзуки (0, 1 или 2).

    Ничего «отрядного» по условию здесь не добавляется, поэтому перебор
    созвездий через Roster/Variation даёт те же числа, что и этот пресет.
    """
    return Team(
        name=name,
        builds=[
            vesna_build(constellation=vesna_c, weapon=vesna_weapon, artifacts=vesna_artifacts),
            cryo_mc_build(constellation=cmc_c,artifacts=cmc_arts),
            diona_build(constellation=6, weapon=diona_weapon,artifacts=diona_artifacts),
            faruzan_build(artifacts=faruzan_artifacts,weapon=faruzan_weapon),
        ],
        enemy=enemy(),
        reactions=reactions(),
        buffs=TEAM_BUFFS,
        rotation=ROTATION,
        config=Config(),
        phases=vesna_burst_cycle(1, 1)
    )


def all_teams() -> Dict[str, Team]:
    variants = (
        ("Весна C0R0, С6R0 диона, C4R3 Крио ГГ, С6R0 Фарузан", 0, EMBERWELL.at(5), FAV_BOW.at(5),NOBLESSE,SCARLET_PROOF,MILLELITH,FAV_BOW,4,HEART_OF_FORGE),
        ("Весна C0R0, С6R1 диона, C4R3 Крио ГГ, С6R0 Фарузан", 0, BOUGH.at(1), BREEZEBORNE_BOW.at(1),NOBLESSE,SCARLET_PROOF,MILLELITH,FAV_BOW,4,HEART_OF_FORGE),
        ("Весна C1R0, С6R5 диона, C4R3 Крио ГГ, С6R0 Фарузан", 1, BOUGH.at(5), BREEZEBORNE_BOW.at(5),NOBLESSE,SCARLET_PROOF,MILLELITH,FAV_BOW,4,HEART_OF_FORGE),
        ("Весна C0R1, С6R3 диона, C4R3 Крио ГГ, С6R0 Фарузан", 0, CHRYSALIS, BREEZEBORNE_BOW.at(3),NOBLESSE,SCARLET_PROOF,MILLELITH,FAV_BOW,4,HEART_OF_FORGE),
        ("Весна C1R1, С6R3 диона, C4R3 Крио ГГ, С6R0 Фарузан", 1, CHRYSALIS, BREEZEBORNE_BOW.at(3),NOBLESSE,SCARLET_PROOF,MILLELITH,FAV_BOW,4,HEART_OF_FORGE),
        ("Весна C2R1, С6R3 диона, C4R3 Крио ГГ, С6R0 Фарузан", 2, CHRYSALIS, BREEZEBORNE_BOW.at(3),NOBLESSE,SCARLET_PROOF,MILLELITH,FAV_BOW,4,HEART_OF_FORGE),
        ("Весна C6R1, С6R3 диона, C4R3 Крио ГГ, С6R0 Фарузан", 6, CHRYSALIS, BREEZEBORNE_BOW.at(3),NOBLESSE,SCARLET_PROOF,MILLELITH,FAV_BOW,4,HEART_OF_FORGE),


    )
    return {name: make_team(name, c, vesna_w, diona_w,diona_art, vesna_art, faruzan_art,faruzan_w,cmc_c,cmc_arts) 
            for name, c, vesna_w, diona_w, diona_art, vesna_art, faruzan_art, faruzan_w,cmc_c,cmc_arts in variants}


#: Названия событий, относящихся к детонации вихря
VORTEX_EVENTS = ("SSW вихрь ×3 стака", "SSW вихрь ×1-2 стака")


