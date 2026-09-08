"""
Отряд Весна / Водяница / Крио ГГ C2 / Одетта.

"""

from __future__ import annotations

from typing import Dict, Sequence

from ..core.buffs import OTHERS, SELF, TEAM, Buff, temp
from ..core.engine import Config, Team
from ..core.entities import Build, Enemy, ArtifactSet
from ..core.reactions import ssw_anemo, ssw_vortex
from ..core.stats import S
from ..core.utilits import merge_dicts
from ..data.artifacts import HEART_OF_FORGE, INSTRUCTOR, MILLELITH, VIRIDESCENT, SCARLET_PROOF,ATK_2_2_SET
from ..data.artifacts_presets import STANDART_SUBSTAT_PRESET
from ..data.tags import DREAM, INST, OFF, ON, VODYA_CHORUS, VODYA_LEAD
from ..data.teams.vesna_vodya_odette_cmc import CRYO_MC, VESNA, ODETTE, VODYANITSA, ODETTE_BURST_SOURCES, odette_burst_buffs, ODETTE_BURST_TIME
from ..data.weapons import *

# =========================================================================== #
#  Баффы уровня ОТРЯДА                                                        #
# =========================================================================== #
TEAM_BUFFS = (
    Buff(S.CRIT_VALUE, 0.30, target=TEAM,
         source="Крио резонанс: +15% крит. шанса (0.30 крит-вэлью)"),
)

#: Время каждого персонажа в ротации (секунды)
TIMES = {"Весна": 10.25, "Крио ГГ": 3.65, "Одетта": 2.4, "Водяница": 1.7}

ROTATION = "CMC E CA Q/ Odette EE /Водяница E /Vesna E sEsE N3CsE Q sE N3CsE"


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
        character=VESNA,
        constellation=constellation,
        weapon=weapon,
        artifacts=(artifacts,),
        extra_stats=merge_dicts(
            {S.ATK_PCT: 0.466 * 2, S.CRIT_VALUE: 0.622},
            STANDART_SUBSTAT_PRESET),
        extra_buffs=tuple(extra_buffs),
        time=TIMES["Весна"],
    )


def cryo_mc_build(weapon=EXAIPHANES, extra_buffs: Sequence[Buff] = ()) -> Build:
    return Build(
        character=CRYO_MC,
        constellation=2,
        weapon=weapon,
        artifacts=(ATK_2_2_SET,),
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
        character=ODETTE,
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
        character=VODYANITSA,
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
        ssw_vortex(2, 3, INST, name="SSW вихрь ×3 стака"),
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
            cryo_mc_build(),
            odette_build(constellation=odette_c, weapon=odette_weapon),
            vodya_build(artifacts=vodya_artifacts,weapon=vodya_weapon,constellation=vodya_c),
        ],
        enemy=enemy(),
        reactions=reactions(),
        buffs=TEAM_BUFFS,
        rotation=ROTATION,
        config=Config(),
    )


def all_teams() -> Dict[str, Team]:
    variants = (
        ("Весна C0 (Источник пламени R5), C0 Одетта, C2R3 Крио ГГ, С0 Водяница", 0, EMBERWELL.at(5), 0, SILVER_LIGHT,SCARLET_PROOF,MILLELITH,TTDS_HALF_CATALYSATOR,0),
        ("Весна C6R5 (Beyond the Chrysalis R5), C6R5 Одетта, C2R3 Крио ГГ, С6R5 Водяница", 6, CHRYSALIS.at(5), 6, FROSTFEATHER.at(5),SCARLET_PROOF,MILLELITH,MAELSTROM.at(5),6),
    )
    return {name: make_team(name, c, vesna_w, c_odette, odette_w, mizuki_art, vodya_art,vodya_w,vodya_c) for name, c, vesna_w, c_odette, odette_w, mizuki_art, vodya_art, vodya_w,vodya_c in variants}


#: Названия событий, относящихся к детонации вихря
VORTEX_EVENTS = ("SSW вихрь ×3 стака", "SSW вихрь ×1-2 стака")


