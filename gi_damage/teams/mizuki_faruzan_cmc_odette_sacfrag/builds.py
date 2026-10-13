"""
Отряд Мидзуки / Сахароза / Крио ГГ C2 / Одетта.

Короткая ротация с 3 проками A4 Мидзуки, Сахароза в Инструкторе,
Мидзуки в Изумрудной тени.

Расчёт ведётся строго по формулам — режима совместимости с исходной
таблицей Excel здесь больше нет.

ОКНО «ДРЕЙФ ГРЁЗ» (тег DREAM)
-----------------------------
Внутри него работают эффекты C2 Мидзуки: бонус пиро/гидро/крио/электро урона
отряду и -20% сопротивления цели. Окно живёт, пока Мидзуки на поле.

Разметка окна — ТОЛЬКО в occurrences источников (файл data/teams/…) и в тегах
событий реакций ниже. Никакого «навесить DREAM на всё» здесь нет: иначе
пропала бы разница между ударами внутри окна и вне его.
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
from ...data.tags import DREAM, INST, OFF, ON
from ...data.weapons import *
from ...data.characters.odette import odette_burst_buffs, ODETTE_BURST_TIME, ODETTE_COMBO_DICT, ODETTE_BURST_SOURCES
from ...data.characters.sucrose import SUCROSE_COMBO_DICT
from ...data.characters.faruzan import FARUZAN_COMBO_DICT
from ...data.characters.cryo_mc import CMC_COMBO_DICT
from ...data.characters.mizuki import MIZUKI_COMBO_DICT
# =========================================================================== #
#  Баффы уровня ОТРЯДА                                                        #
# =========================================================================== #
TEAM_BUFFS = (
    Buff(S.CRIT_VALUE, 0.30, target=TEAM,
         source="Крио резонанс: +15% крит. шанса (0.30 крит-вэлью)"),
)

#: Время каждого персонажа в ротации (секунды)
TIMES = {"Мидзуки": 10.25, "Крио ГГ": 3.65, "Одетта": 2.4, "Фарузан": 2.7}

ROTATION = "CMC E CA Q /Faruzan EQ /Midzuki E/ Odette EE/ Midzuki EQ /Faruzan E"


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
def mizuki_build(constellation: int, weapon, artifacts, extra_buffs: Sequence[Buff] = (),
                 main_stats={S.BASE_EM: 187 * 2, S.CRIT_VALUE: 0.622}) -> Build:

    return Build(
        character=MIZUKI_COMBO_DICT["mizuki_sacfrag_combo"],
        constellation=constellation,
        weapon=weapon,
        artifacts=artifacts,
        extra_stats=merge_dicts(
            main_stats,
            STANDART_SUBSTAT_PRESET),
        extra_buffs=tuple(extra_buffs),
        time=TIMES["Мидзуки"],
    )


def cryo_mc_build(constellation: int, artifacts, weapon=EXAIPHANES, extra_buffs: Sequence[Buff] = ()) -> Build:
    return Build(
        character=CMC_COMBO_DICT["cmc_ssw_combo"],
        constellation=constellation,
        weapon=weapon,
        artifacts=(artifacts,),
        extra_stats=merge_dicts(
            {S.ATK_PCT: 0.466 * 2, S.CRIT_VALUE: 0.622},
            STANDART_SUBSTAT_PRESET),
        extra_buffs=tuple(extra_buffs),
        time=TIMES["Крио ГГ"],
    )


def odette_build(constellation: int, weapon,
                 use_burst: bool | None = None,
                 extra_buffs: Sequence[Buff] = ()) -> Build:
    """use_burst=None — авто: до C4 не применяем, с C4 применяем."""
    if use_burst is None:
        use_burst = constellation >= 4
        
    return Build(
        character=ODETTE_COMBO_DICT["odette_ssw_combo_vv_full_uptime_mizuki"],
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

def faruzan_build(weapon=FAV_BOW,artifacts:ArtifactSet=VIRIDESCENT, extra_buffs: Sequence[Buff] = ()) -> Build:
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
def reactions(in_dreamdrifter: bool = True):
    """События звёздного рассеивания за одну ротацию.

    Теги события добавляются к «полевому» состоянию КАЖДОГО персонажа, то есть
    описывают момент времени, а не конкретного бойца. Поэтому DREAM здесь —
    это «реакция произошла, пока Мидзуки была в Дрейфе грёз», и он влияет на
    сопротивление цели для всех участников распределения.

    in_dreamdrifter=False — если реакции происходят вне окна.
    """
    d = (DREAM,) if in_dreamdrifter else ()
    return (
        # Мидзуки на поле -> её реакции всегда внутри окна
        ssw_anemo("Мидзуки", 2, *d,BREEZEBORNE,FROSTGLOW, name="SSW анемо (Мидзуки)"),
        ssw_anemo("Мидзуки", 8, INST,BREEZEBORNE,FROSTGLOW, *d, name="SSW анемо (Мидзуки, Инструктор)"),
        # Фарузан триггерит со своего поля — Мидзуки в этот момент НЕ в Дрейфе.
        # Если по факту иначе, добавьте сюда *d.
        ssw_anemo("Фарузан", 4, INST,BREEZEBORNE,FROSTGLOW, *d, name="SSW анемо (Фарузан, Инструктор)"),
        ssw_anemo("Фарузан", 3, INST,BREEZEBORNE,FROSTGLOW, name="SSW анемо (Фарузан, Инструктор)"),
        # Детонации вихря: проверьте, попадают ли они в окно.
        ssw_vortex(3, 3, INST,BREEZEBORNE,FROSTGLOW,VV_CRYO, *d, name="SSW вихрь ×3 стака"),
        ssw_vortex(3, 1, INST,BREEZEBORNE,FROSTGLOW,VV_CRYO, name="SSW вихрь ×3 стака"),
    )


# =========================================================================== #
#  Отряды                                                                     #
# =========================================================================== #
def make_team(name: str, mizuki_c: int, mizuki_weapon, odette_c, odette_weapon, mizuki_artifacts, faruzan_artifacts,
              faruzan_weapon, cmc_artifacts, cmc_c) -> Team:
    """Собрать отряд. mizuki_c — созвездие Мидзуки (0, 1 или 2).

    Ничего «отрядного» по условию здесь не добавляется, поэтому перебор
    созвездий через Roster/Variation даёт те же числа, что и этот пресет.
    """
    return Team(
        name=name,
        builds=[
            mizuki_build(constellation=mizuki_c, weapon=mizuki_weapon, artifacts=mizuki_artifacts),
            cryo_mc_build(constellation=cmc_c, artifacts=cmc_artifacts),
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
        ("Мидзуки C2 (Церемон), C0 Одетта (Серебряный свет R5), C4R3 Крио ГГ, С6R0 Фарузан", 2, SACFRAG.at(5), 0, SILVER_LIGHT,(NIGHT_SKY.at(2),AUBADE.at(2)),VIRIDESCENT,FAV_BOW, MILLELITH,4),
        ("Мидзуки C2 (Церемон), C2 Одетта (Серебряный свет R5), C4R3 Крио ГГ, С6R3 Фарузан", 2, SACFRAG.at(5), 2, SILVER_LIGHT,(NIGHT_SKY.at(2),AUBADE.at(2)),VIRIDESCENT,BREEZEBORNE_BOW.at(3), MILLELITH,4),
        ("Мидзуки C3 (Церемон), C2R1 Одетта, C4R3 Крио ГГ, С6R3 Фарузан", 3, SACFRAG.at(5), 2, FROSTFEATHER,(NIGHT_SKY.at(2),AUBADE.at(2)),VIRIDESCENT,BREEZEBORNE_BOW.at(3), MILLELITH,4),
        ("Мидзуки C3 (Церемон), C2R1 Одетта, C6R3 Крио ГГ, С6R3 Фарузан", 3, SACFRAG.at(5), 2, FROSTFEATHER,(NIGHT_SKY.at(2),AUBADE.at(2)),VIRIDESCENT,BREEZEBORNE_BOW.at(3), MILLELITH,6),
    )
    return {name: make_team(name, c, mizuki_w, c_odette, odette_w, mizuki_art, faruzan_art,faruzan_w,
                            cmc_art, c_cmc) for name, c, mizuki_w, c_odette, odette_w, mizuki_art, faruzan_art, faruzan_w, cmc_art, c_cmc in variants}


#: Названия событий, относящихся к детонации вихря
VORTEX_EVENTS = ("SSW вихрь ×3 стака", "SSW вихрь ×1-2 стака")


