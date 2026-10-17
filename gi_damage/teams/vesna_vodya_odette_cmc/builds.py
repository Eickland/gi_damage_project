"""
Отряд Весна / Водяница / Крио ГГ C2 / Одетта.

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
TIMES = {"Весна": 11.5, "Крио ГГ": 3.65, "Одетта": 2.4, "Водяница": 1.6}

ROTATION = " Odette EE/CMC E Q CA/Водяница E /Vesna combo"


# =========================================================================== #
#  Цель                                                                       #
# =========================================================================== #
def enemy() -> Enemy:
    """Базовое сопротивление цели.

    Всё, что его снижает, — обычные баффы `res_reduction[.стихия]`:
      * Изумрудная тень 4ч   -40% крио   (постоянно)
      * C2 Мидзуки           -20% всем   (только внутри окна DREAM)
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
        character=CMC_COMBO_DICT["cmc_ssw_vesna_combo"],
        constellation=constellation,
        weapon=weapon,
        artifacts=artifacts,
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
        character=ODETTE_COMBO_DICT["odette_ssw_combo_vesna"],
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

def vodya_build(constellation: int = 0,weapon=TTDS_HALF_CATALYSATOR,artifacts:ArtifactSet=MILLELITH, extra_buffs: Sequence[Buff] = ()) -> Build:

    return Build(
        character=VODYA_COMBO_DICT["off_field"],
        constellation=constellation,
        weapon=weapon,
        artifacts=(artifacts,),
        extra_stats=merge_dicts(
            {S.HP_PCT: 0.466 * 3},
            STANDART_SUBSTAT_PRESET),
        extra_buffs=tuple(extra_buffs),
        time=TIMES["Водяница"],
    )


# =========================================================================== #
#  Реакции                                                                    #
# =========================================================================== #
def reactions():
    """События звёздного рассеивания за одну ротацию.
    """
    return (
        # Мидзуки на поле -> её реакции всегда внутри окна
        ssw_anemo("Весна", 2, INST, VODYA_LEAD,BREEZEBORNE,FROSTGLOW, name="SSW анемо (Весна, Весна)"),
        ssw_anemo("Весна", 6, INST, VODYA_LEAD,VODYA_CHORUS,BREEZEBORNE,FROSTGLOW, name="SSW анемо (Весна, Инструктор)"),
        ssw_vortex(2, 3, INST,BREEZEBORNE,FROSTGLOW,VV_CRYO, name="SSW вихрь ×3 стака"),
    )


# =========================================================================== #
#  Отряды                                                                     #
# =========================================================================== #
def make_team(name: str, vesna_c: int, vesna_weapon, odette_c, odette_weapon, vesna_artifacts = SCARLET_PROOF, vodya_artifacts = MILLELITH,
              vodya_weapon = TTDS_HALF_CATALYSATOR, vodya_c = 0, cmc_c=4,cmc_arts=(HEART_OF_FORGE.at(2),SCARLET_PROOF.at(2))) -> Team:
    """Собрать отряд. mizuki_c — созвездие Мидзуки (0, 1 или 2).

    Ничего «отрядного» по условию здесь не добавляется, поэтому перебор
    созвездий через Roster/Variation даёт те же числа, что и этот пресет.
    """
    return Team(
        name=name,
        builds=[
            vesna_build(constellation=vesna_c, weapon=vesna_weapon, artifacts=vesna_artifacts),
            cryo_mc_build(constellation=cmc_c,artifacts=cmc_arts),
            odette_build(constellation=odette_c, weapon=odette_weapon),
            vodya_build(artifacts=vodya_artifacts,weapon=vodya_weapon,constellation=vodya_c),
        ],
        enemy=enemy(),
        reactions=reactions(),
        buffs=TEAM_BUFFS,
        rotation=ROTATION,
        config=Config(),
        phases=vesna_burst_cycle(1, 2)
    )


def all_teams() -> Dict[str, Team]:
    variants = (
        ("Весна C0R0, C0R0 Одетта, C4R3 Крио ГГ, С0R0 Водяница", 0, EMBERWELL.at(5), 0, SILVER_LIGHT,SCARLET_PROOF,MILLELITH,TTDS_HALF_CATALYSATOR,0,4,(HEART_OF_FORGE.at(2),SCARLET_PROOF.at(2))),
        ("Весна C1R1, C0R0 Одетта, C4R3 Крио ГГ, С0R1 Водяница", 1, CHRYSALIS, 0, SILVER_LIGHT,SCARLET_PROOF,MILLELITH,MAELSTROM,0,4,(NOBLESSE,)),
        ("Весна C0R1, C0R0 Одетта, C4R3 Крио ГГ, С0R0 Водяница", 0, CHRYSALIS.at(1), 0, SILVER_LIGHT, SCARLET_PROOF, MILLELITH, TTDS_HALF_CATALYSATOR,0,4,(HEART_OF_FORGE.at(2),SCARLET_PROOF.at(2))),
        ("Весна C0R1, C0R0 Одетта, C4R3 Крио ГГ, С0R1 Водяница", 0, CHRYSALIS.at(1), 0, SILVER_LIGHT, SCARLET_PROOF, MILLELITH, MAELSTROM,0,4,(HEART_OF_FORGE.at(2),SCARLET_PROOF.at(2))),
        ("Весна C0R0, C2R0 Одетта, C4R3 Крио ГГ, С0R0 Водяница", 0, EMBERWELL.at(5), 2, SILVER_LIGHT,SCARLET_PROOF,MILLELITH,TTDS_HALF_CATALYSATOR,0,4,(HEART_OF_FORGE.at(2),SCARLET_PROOF.at(2))),
        ("Весна C0R1, C2R0 Одетта, C4R3 Крио ГГ, С0R0 Водяница", 0, CHRYSALIS, 2, SILVER_LIGHT,SCARLET_PROOF,MILLELITH,TTDS_HALF_CATALYSATOR,0,4,(HEART_OF_FORGE.at(2),SCARLET_PROOF.at(2))),


    )
    return {name: make_team(name, c, vesna_w, c_odette, odette_w, mizuki_art, vodya_art,vodya_w,vodya_c,cmc_c,cmc_arts) for name, 
            c, vesna_w, c_odette, odette_w, mizuki_art, vodya_art, vodya_w,vodya_c,cmc_c,cmc_arts in variants}


#: Названия событий, относящихся к детонации вихря
VORTEX_EVENTS = ("SSW вихрь ×3 стака", "SSW вихрь ×1-2 стака")


