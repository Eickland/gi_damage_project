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
from ...data.characters.vodyanitsa import VODYA_COMBO_DICT
from ...data.characters.faruzan import FARUZAN_COMBO_DICT
from ...data.characters.cryo_mc import CMC_COMBO_DICT
from ...data.characters.vesna import VESNA_COMBO_DICT
from ...data.weapons import *

# =========================================================================== #
#  Баффы уровня ОТРЯДА                                                        #
# =========================================================================== #
TEAM_BUFFS = (
    Buff(S.CRIT_VALUE, 0.30, target=TEAM,
         source="Крио резонанс: +15% крит. шанса (0.30 крит-вэлью)"),
)

#: Время каждого персонажа в ротации (секунды)
TIMES = {"Весна": 11.5, "Крио ГГ": 3.65, "Одетта": 2.4, "Фарузан": 1.7}

ROTATION = "Faruzan EQ /CMC E CA Q/ Odette EE / /Vesna E sEsE N3CsE Q sE N3CsE"


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
        character=VESNA_COMBO_DICT["ssw_burst_combo"],
        constellation=constellation,
        weapon=weapon,
        artifacts=(artifacts,),
        extra_stats=merge_dicts(
            {S.ATK_PCT: 0.466 * 2, S.CRIT_VALUE: 0.622},
            STANDART_SUBSTAT_PRESET),
        extra_buffs=tuple(extra_buffs),
        time=TIMES["Весна"],
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


def odette_build(constellation: int = 0, weapon=SILVER_LIGHT,
                 use_burst: bool | None = None,
                 extra_buffs: Sequence[Buff] = ()) -> Build:
    """use_burst=None — авто: до C4 не применяем, с C4 применяем."""
    if use_burst is None:
        use_burst = constellation >= 4
        
    return Build(
        character=ODETTE_COMBO_DICT["odette_ssw_mizuki_combo"],
        constellation=constellation,
        weapon=weapon,
        artifacts=(HEART_OF_FORGE,),
        extra_stats=merge_dicts(
            {S.ATK_PCT: 0.466 * 2, S.CRIT_VALUE: 0.622},
            STANDART_SUBSTAT_PRESET),
        extra_sources=ODETTE_BURST_SOURCES if use_burst else (),
        extra_buffs=tuple(extra_buffs) + (odette_burst_buffs(constellation)
                                          if use_burst else ()),
        time=TIMES["Одетта"] + (ODETTE_BURST_TIME if use_burst else 0.0),
    )

def faruzan_build(weapon=BREEZEBORNE_BOW,artifacts:ArtifactSet=VIRIDESCENT, extra_buffs: Sequence[Buff] = ()) -> Build:
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
def make_team(name: str, vesna_c: int, vesna_weapon, odette_c, odette_weapon, vesna_artifacts = SCARLET_PROOF, faruzan_artifacts = VIRIDESCENT,
              faruzan_weapon = FAV_BOW, cmc_c=4) -> Team:
    """Собрать отряд. vesna_c — созвездие Мидзуки (0, 1 или 2).

    Ничего «отрядного» по условию здесь не добавляется, поэтому перебор
    созвездий через Roster/Variation даёт те же числа, что и этот пресет.
    """
    return Team(
        name=name,
        builds=[
            vesna_build(constellation=vesna_c, weapon=vesna_weapon, artifacts=vesna_artifacts),
            cryo_mc_build(constellation=cmc_c,artifacts=MILLELITH),
            odette_build(constellation=odette_c, weapon=odette_weapon),
            faruzan_build(artifacts=faruzan_artifacts,weapon=faruzan_weapon),
        ],
        enemy=enemy(),
        reactions=reactions(),
        buffs=TEAM_BUFFS,
        rotation=ROTATION,
        config=Config(),
    )


def all_teams() -> Dict[str, Team]:
    variants = (
        ("Весна C0R0, C0R0 Одетта, C4R3 Крио ГГ, С6R0 Фарузан", 0, EMBERWELL.at(5), 0, SILVER_LIGHT,SCARLET_PROOF,VIRIDESCENT,FAV_BOW,4),
        ("Весна C0R1, C0R0 Одетта, C4R3 Крио ГГ, С6R1 Фарузан", 0,  CHRYSALIS.at(1), 0, SILVER_LIGHT,SCARLET_PROOF,VIRIDESCENT,BREEZEBORNE_BOW.at(1),4),
        ("Весна C1R1, C0R0 Одетта, C4R3 Крио ГГ, С6R1 Фарузан", 1,  CHRYSALIS.at(1), 0, SILVER_LIGHT,SCARLET_PROOF,VIRIDESCENT,BREEZEBORNE_BOW.at(1),4),
        ("Весна C2R1, C0R0 Одетта, C4R3 Крио ГГ, С6R1 Фарузан", 2,  CHRYSALIS.at(1), 0, SILVER_LIGHT,SCARLET_PROOF,VIRIDESCENT,BREEZEBORNE_BOW.at(1),4),


    )
    return {name: make_team(name, c, vesna_w, c_odette, odette_w, vesna_art, faruzan_art,faruzan_w,cmc_c) for name, c, vesna_w, c_odette, odette_w, vesna_art, faruzan_art, faruzan_w,cmc_c in variants}


#: Названия событий, относящихся к детонации вихря
VORTEX_EVENTS = ("SSW вихрь ×3 стака", "SSW вихрь ×1-2 стака")


