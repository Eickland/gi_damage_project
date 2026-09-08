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

from ..core.buffs import OTHERS, SELF, TEAM, Buff, temp
from ..core.engine import Config, Team
from ..core.entities import Build, Enemy, ArtifactSet
from ..core.reactions import ssw_anemo, ssw_vortex
from ..core.stats import S
from ..core.utilits import merge_dicts
from ..data.artifacts import HEART_OF_FORGE, INSTRUCTOR, MILLELITH, VIRIDESCENT, SCARLET_PROOF
from ..data.artifacts_presets import STANDART_SUBSTAT_PRESET
from ..data.tags import DREAM, INST, OFF, ON
from ..data.teams.mizuki_faruzan_odette_cmc import CRYO_MC, MIZUKI, ODETTE, FARUZAN, ODETTE_BURST_SOURCES, odette_burst_buffs, ODETTE_BURST_TIME
from ..data.weapons import (EXAIPHANES, CEREMONIAL, SILVER_LIGHT,
                            SUNNY_MORNING_SLEEP_IN, WANDERER_SONG, FROSTFEATHER,FAV_BOW, BREEZEBORNE_BOW)

# =========================================================================== #
#  Баффы уровня ОТРЯДА                                                        #
# =========================================================================== #
TEAM_BUFFS = (
    Buff(S.CRIT_VALUE, 0.30, target=TEAM,
         source="Крио резонанс: +15% крит. шанса (0.30 крит-вэлью)"),
)

#: Время каждого персонажа в ротации (секунды)
TIMES = {"Мидзуки": 10.25, "Крио ГГ": 3.65, "Одетта": 2.4, "Фарузан": 2.7}

ROTATION = "CMC E CA Q/ Odette EE /Faruzan EQ /Midzuki EQ /Faruzan E"


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
def mizuki_build(constellation: int, weapon, artifacts, extra_buffs: Sequence[Buff] = ()) -> Build:

    
    if constellation == 6 and weapon.name != "Сон солнечным утром":
        main_stats = {S.BASE_EM: 187 * 3}
    else:
        main_stats = {S.BASE_EM: 187 * 2, S.CRIT_VALUE: 0.622}
    
    return Build(
        character=MIZUKI,
        constellation=constellation,
        weapon=weapon,
        artifacts=(artifacts,),
        extra_stats=merge_dicts(
            main_stats,
            STANDART_SUBSTAT_PRESET),
        extra_buffs=tuple(extra_buffs),
        time=TIMES["Мидзуки"],
    )


def cryo_mc_build(weapon=EXAIPHANES, extra_buffs: Sequence[Buff] = ()) -> Build:
    return Build(
        character=CRYO_MC,
        constellation=2,
        weapon=weapon,
        artifacts=(MILLELITH,),
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

def faruzan_build(weapon=BREEZEBORNE_BOW,artifacts:ArtifactSet=INSTRUCTOR, extra_buffs: Sequence[Buff] = ()) -> Build:
    if artifacts.name == 'Инструктор':
        main_stats = {S.BASE_EM: 139 * 2 + 187}
    else:
        main_stats = {S.BASE_EM: 187 * 3}
    return Build(
        character=FARUZAN,
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
        ssw_anemo("Мидзуки", 2, *d, name="SSW анемо (Мидзуки)"),
        ssw_anemo("Мидзуки", 8, INST, *d, name="SSW анемо (Мидзуки, Инструктор)"),
        # Фарузан триггерит со своего поля — Мидзуки в этот момент НЕ в Дрейфе.
        # Если по факту иначе, добавьте сюда *d.
        ssw_anemo("Фарузан", 4, INST, *d, name="SSW анемо (Фарузан, Инструктор)"),
        ssw_anemo("Фарузан", 3, INST, name="SSW анемо (Фарузан, Инструктор)"),
        # Детонации вихря: проверьте, попадают ли они в окно.
        ssw_vortex(3, 3, INST, *d, name="SSW вихрь ×3 стака"),
        ssw_vortex(3, 1, INST, name="SSW вихрь ×3 стака"),
    )


# =========================================================================== #
#  Отряды                                                                     #
# =========================================================================== #
def make_team(name: str, mizuki_c: int, mizuki_weapon, odette_c, odette_weapon, mizuki_artifacts = VIRIDESCENT, faruzan_artifacts = INSTRUCTOR,
              faruzan_weapon = FAV_BOW) -> Team:
    """Собрать отряд. mizuki_c — созвездие Мидзуки (0, 1 или 2).

    Ничего «отрядного» по условию здесь не добавляется, поэтому перебор
    созвездий через Roster/Variation даёт те же числа, что и этот пресет.
    """
    return Team(
        name=name,
        builds=[
            mizuki_build(constellation=mizuki_c, weapon=mizuki_weapon, artifacts=mizuki_artifacts),
            cryo_mc_build(),
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
        ("Мидзуки C0 (Песнь странника R5), C0 Одетта, C2R3 Крио ГГ, С6 Фарузан", 0, WANDERER_SONG.at(5), 0, SILVER_LIGHT,VIRIDESCENT,INSTRUCTOR,FAV_BOW),
        ("Мидзуки C1 (Песнь странника R5), C0 Одетта, C2R3 Крио ГГ, С6 Фарузан", 1, WANDERER_SONG.at(5), 0, SILVER_LIGHT,VIRIDESCENT,INSTRUCTOR,FAV_BOW),
        ("Мидзуки C2 (Песнь странника R5), C0 Одетта, C2R3 Крио ГГ, С6 Фарузан", 2, WANDERER_SONG.at(5), 0, SILVER_LIGHT,VIRIDESCENT,INSTRUCTOR,FAV_BOW),
        ("Мидзуки C2R1 (Сон солнечным утром R1), C0 Одетта, C2R3 Крио ГГ, С6R1 Фарузан", 2, SUNNY_MORNING_SLEEP_IN.at(1), 0, SILVER_LIGHT,SCARLET_PROOF,VIRIDESCENT,BREEZEBORNE_BOW),
        ("Мидзуки C2R1 (Сон солнечным утром R1), C1 Одетта, C2R3 Крио ГГ, С6R1 Фарузан", 2, SUNNY_MORNING_SLEEP_IN.at(1), 1, SILVER_LIGHT,SCARLET_PROOF,VIRIDESCENT,BREEZEBORNE_BOW),
        ("Мидзуки C2R1 (Сон солнечным утром R1), C2 Одетта, C2R3 Крио ГГ, С6R1 Фарузан", 2, SUNNY_MORNING_SLEEP_IN.at(1), 2, SILVER_LIGHT,SCARLET_PROOF,VIRIDESCENT,BREEZEBORNE_BOW),
        ("Мидзуки C2R1 (Сон солнечным утром R1), C2R1 Одетта, C2R3 Крио ГГ, С6R1 Фарузан", 2, SUNNY_MORNING_SLEEP_IN.at(1), 2, FROSTFEATHER,SCARLET_PROOF,VIRIDESCENT,BREEZEBORNE_BOW),
        ("Мидзуки C6R1 (Сон солнечным утром R1), C2R1 Одетта, C2R3 Крио ГГ, С6R1 Фарузан", 6, SUNNY_MORNING_SLEEP_IN.at(1), 2, FROSTFEATHER,SCARLET_PROOF,VIRIDESCENT,BREEZEBORNE_BOW),
        ("Мидзуки C6R1 (Сон солнечным утром R1), C6R1 Одетта, C2R3 Крио ГГ, С6R1 Фарузан", 6, SUNNY_MORNING_SLEEP_IN.at(1), 6, FROSTFEATHER,SCARLET_PROOF,VIRIDESCENT,BREEZEBORNE_BOW),
        ("Мидзуки C6R5 (Сон солнечным утром R5), C6R5 Одетта, C2R3 Крио ГГ, С6R5 Фарузан", 6, SUNNY_MORNING_SLEEP_IN.at(5), 6, FROSTFEATHER.at(5),SCARLET_PROOF,VIRIDESCENT,BREEZEBORNE_BOW.at(5)),
    )
    return {name: make_team(name, c, mizuki_w, c_odette, odette_w, mizuki_art, faruzan_art,faruzan_w) for name, c, mizuki_w, c_odette, odette_w, mizuki_art, faruzan_art, faruzan_w in variants}


#: Названия событий, относящихся к детонации вихря
VORTEX_EVENTS = ("SSW вихрь ×3 стака", "SSW вихрь ×1-2 стака")


