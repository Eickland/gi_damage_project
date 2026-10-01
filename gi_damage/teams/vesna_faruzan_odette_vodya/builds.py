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
from ...data.artifacts import HEART_OF_FORGE, INSTRUCTOR, MILLELITH, VIRIDESCENT, SCARLET_PROOF,ATK_2_2_SET
from ...data.artifacts_presets import STANDART_SUBSTAT_PRESET
from ...data.tags import DREAM, INST, OFF, ON, VODYA_CHORUS, VODYA_LEAD
from ...data.characters.odette import odette_burst_buffs, ODETTE_BURST_TIME, ODETTE_COMBO_DICT, ODETTE_BURST_SOURCES
from ...data.characters.vodyanitsa import VODYA_COMBO_DICT
from ...data.characters.faruzan import FARUZAN_COMBO_DICT
from ...data.characters.cryo_mc import CMC_COMBO_DICT
from ...data.characters.vesna import VESNA_COMBO_DICT
from ...data.weapons import *

# =========================================================================== #
#  Баффы уровня ОТРЯДА                                                        #
# =========================================================================== #

#: Время каждого персонажа в ротации (секунды)
TIMES = {"Весна": 13.6, "Фарузан": 1.5, "Одетта": 2.4, "Водяница": 1.5}

ROTATION = "Водяница E /Фарузан E Q/ Odette EE /Vesna E sEsE N3CsE Q sE N3CsE"


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


def faruzan_build(weapon=BREEZEBORNE_BOW,artifacts:ArtifactSet=VIRIDESCENT, extra_buffs: Sequence[Buff] = ()) -> Build:
    if artifacts.name == 'Инструктор':
        main_stats = {S.BASE_EM: 139 * 2 + 187}
    else:
        main_stats = {S.BASE_EM: 187 * 3}
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


def odette_build(constellation: int = 0, weapon=SILVER_LIGHT,
                 use_burst: bool | None = None,
                 extra_buffs: Sequence[Buff] = ()) -> Build:
    """use_burst=None — авто: до C4 не применяем, с C4 применяем."""
    if use_burst is None:
        use_burst = constellation >= 4
        
    return Build(
        character=ODETTE_COMBO_DICT["odette_short_mizuki_combo_no_burst"],
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
def reactions(in_dreamdrifter: bool = True):
    """События звёздного рассеивания за одну ротацию.

    Теги события добавляются к «полевому» состоянию КАЖДОГО персонажа, то есть
    описывают момент времени, а не конкретного бойца. Поэтому DREAM здесь —
    это «реакция произошла, пока Мидзуки была в Дрейфе грёз», и он влияет на
    сопротивление цели для всех участников распределения.

    in_dreamdrifter=False — если реакции происходят вне окна.
    """
    return (
        # Мидзуки на поле -> её реакции всегда внутри окна
        ssw_anemo("Весна", 2, INST, VODYA_LEAD, name="SSW анемо (Весна, Весна)"),
        ssw_anemo("Весна", 6, INST, VODYA_LEAD,VODYA_CHORUS, name="SSW анемо (Весна, Инструктор)"),
        ssw_anemo("Фарузан", 6, name="SSW анемо (Фарузан)"),
        ssw_vortex(3, 3, INST, name="SSW вихрь ×3 стака"),
    )


# =========================================================================== #
#  Отряды                                                                     #
# =========================================================================== #
def make_team(name: str, vesna_c: int, vesna_weapon, odette_c, odette_weapon, vesna_artifacts = SCARLET_PROOF, vodya_artifacts = MILLELITH,
              vodya_weapon = TTDS_HALF_CATALYSATOR, vodya_c = 0) -> Team:
    """Собрать отряд. mizuki_c — созвездие Мидзуки (0, 1 или 2).

    Ничего «отрядного» по условию здесь не добавляется, поэтому перебор
    созвездий через Roster/Variation даёт те же числа, что и этот пресет.
    """
    return Team(
        name=name,
        builds=[
            vesna_build(constellation=vesna_c, weapon=vesna_weapon, artifacts=vesna_artifacts),
            faruzan_build(),
            odette_build(constellation=odette_c, weapon=odette_weapon),
            vodya_build(artifacts=vodya_artifacts,weapon=vodya_weapon,constellation=vodya_c),
        ],
        enemy=enemy(),
        reactions=reactions(),
        rotation=ROTATION,
        config=Config(),
    )


def all_teams() -> Dict[str, Team]:
    variants = (
        ("Весна C2R1, C2R1 Одетта, С6 Фарузан, С6R1 Водяница", 2, CHRYSALIS, 2, FROSTFEATHER, SCARLET_PROOF, MILLELITH, MAELSTROM,6),
    )
    return {name: make_team(name, c, vesna_w, c_odette, odette_w, mizuki_art, vodya_art,vodya_w,vodya_c) for name, c, vesna_w, c_odette, odette_w, mizuki_art, vodya_art, vodya_w,vodya_c in variants}


#: Названия событий, относящихся к детонации вихря
VORTEX_EVENTS = ("SSW вихрь ×3 стака", "SSW вихрь ×1-2 стака")


