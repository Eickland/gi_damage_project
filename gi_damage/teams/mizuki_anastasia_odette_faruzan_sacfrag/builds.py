"""
Отряд Мидзуки / Анастасия / Одетта / Фарузан, ротация sacfrag
(звёздное рассеивание).

Как mizuki_faruzan_cmc_odette_sacfrag, но вместо Крио ГГ — Анастасия
(саппорт, Милосердие). Ротация:
Анастасия EQ / Фарузан EQ / Мидзуки E / Одетта EE / Мидзуки EQ / Фарузан E.

Длительность ротации — не меньше MIN_ROTATION (19 с). Анастасия короче
Крио ГГ (3.0 с против 3.65 с), недостающее время добавлено Мидзуки
(mizuki_time()).

Корона: 6 атак из 10 — пока Мидзуки на поле (окно DREAM, Изумрудная тень
Фарузан), 4 — вне его.

An Unfinished Requiem: базовый множитель реакций SSW ×1.15 и +4 вихря
2 уровня (см. reactions()).
"""

from __future__ import annotations

from typing import Dict, Sequence

from ...core.buffs import OTHERS, SELF, TEAM, Buff, temp
from ...core.engine import Config, Team
from ...core.entities import Build, Enemy, ArtifactSet
from ...core.reactions import ssw_anemo, ssw_vortex
from ...core.sources import occ
from ...core.stats import S
from ...core.utilits import merge_dicts
from ...data.artifacts import *
from ...data.artifacts_presets import STANDART_SUBSTAT_PRESET, STANDART_SUBSTAT_PRESET_EM_SCALE
from ...data.tags import *
from ...data.weapons import *
from ...data.characters.odette import (odette_burst_buffs, ODETTE_BURST_TIME,
                                       ODETTE_COMBO_DICT, ODETTE_BURST_SOURCES)
from ...data.characters.faruzan import FARUZAN_COMBO_DICT
from ...data.characters.mizuki import MIZUKI_COMBO_DICT
from ...data.characters.anastasia import (anastasia_support, requiem_reactions,
                                          requiem_vortex, CROWN_HITS)

TEAM_BUFFS = (
    Buff(S.CRIT_VALUE, 0.30, target=TEAM,
         source="Крио резонанс: +15% крит. шанса (0.30 крит-вэлью)"),
)

#: Минимальная длительность ротации (секунды)
MIN_ROTATION = 19.0
#: Время Мидзуки в исходной ротации sacfrag (с Крио ГГ)
MIZUKI_BASE_TIME = 10.25
OTHERS_TIMES = {"Анастасия": 3.0, "Одетта": 2.4, "Фарузан": 2.7}


def mizuki_time() -> float:
    """Время Мидзуки: исходное, но так, чтобы ротация была не короче MIN_ROTATION."""
    return max(MIZUKI_BASE_TIME, round(MIN_ROTATION - sum(OTHERS_TIMES.values()), 2))


#: Время каждого персонажа в ротации (секунды)
TIMES = {"Мидзуки": mizuki_time(), **OTHERS_TIMES}

ROTATION = "Анастасия EQ/Faruzan EQ/Midzuki E/Odette EE/Midzuki EQ/Faruzan E"

MAIN_ATK = {S.ATK_PCT: 0.466 * 2, S.CRIT_VALUE: 0.622}       # АТК/АТК/крит

#: Атаки короны: 6 — пока Мидзуки на поле, 4 — вне его
CROWN_IN_DREAM = 6
ANASTASIA = anastasia_support("ssw", [occ(CROWN_IN_DREAM, OFF, DREAM, VV_CRYO),
                                      occ(CROWN_HITS - CROWN_IN_DREAM, OFF)])


def enemy() -> Enemy:
    return Enemy(res={"anemo": 0.10, "cryo": 0.10}, def_mult=0.4875, elevation=0.0)


def mizuki_build(constellation: int = 0, weapon=SACFRAG.at(5),
                 artifacts=(NIGHT_SKY.at(2), AUBADE.at(2)),
                 main_stats={S.BASE_EM: 187 * 2, S.CRIT_VALUE: 0.622},
                 extra_buffs: Sequence[Buff] = ()) -> Build:
    return Build(
        character=MIZUKI_COMBO_DICT["mizuki_sacfrag_combo"],
        constellation=constellation,
        weapon=weapon,
        artifacts=artifacts,
        extra_stats=merge_dicts(main_stats, STANDART_SUBSTAT_PRESET_EM_SCALE),
        extra_buffs=tuple(extra_buffs),
        time=TIMES["Мидзуки"],
    )


def anastasia_build(constellation: int = 0, weapon=ARTEMISIA, artifacts=(STELLAR_SET,),
                    main_stats=MAIN_ATK, extra_buffs: Sequence[Buff] = ()) -> Build:
    return Build(
        character=ANASTASIA,
        constellation=constellation,
        weapon=weapon,
        artifacts=artifacts,
        extra_stats=merge_dicts(main_stats, STANDART_SUBSTAT_PRESET),
        extra_buffs=tuple(extra_buffs),
        time=TIMES["Анастасия"],
    )


def odette_build(constellation: int = 0, weapon=SILVER_LIGHT, artifacts=(HEART_OF_FORGE,),
                 use_burst: bool | None = None,
                 extra_buffs: Sequence[Buff] = ()) -> Build:
    """use_burst=None — авто: до C4 не применяем, с C4 применяем."""
    if use_burst is None:
        use_burst = constellation >= 4
    return Build(
        character=ODETTE_COMBO_DICT["odette_ssw_mizuki_combo"],
        constellation=constellation,
        weapon=weapon,
        artifacts=artifacts,
        extra_stats=merge_dicts(MAIN_ATK, STANDART_SUBSTAT_PRESET),
        extra_sources=ODETTE_BURST_SOURCES if use_burst else (),
        extra_buffs=tuple(extra_buffs) + (odette_burst_buffs(constellation)
                                          if use_burst else ()),
        time=TIMES["Одетта"] + (ODETTE_BURST_TIME if use_burst else 0.0),
    )


def faruzan_build(weapon=FAV_BOW, artifacts: ArtifactSet = VIRIDESCENT,
                  extra_buffs: Sequence[Buff] = ()) -> Build:
    main_stats = {S.ATK_PCT: 0.446, S.CRIT_VALUE: 0.311, "dmg_bonus.anemo": 0.466}
    return Build(
        character=FARUZAN_COMBO_DICT["ssw_combo"],
        constellation=6,
        weapon=weapon,
        artifacts=(artifacts,),
        extra_stats=merge_dicts(main_stats, STANDART_SUBSTAT_PRESET),
        extra_buffs=tuple(extra_buffs),
        time=TIMES["Фарузан"],
    )


def reactions(in_dreamdrifter: bool = True):
    """События SSW за ротацию: как в mizuki_faruzan_cmc_odette_sacfrag
    (без окна C6 Крио ГГ) + Requiem Анастасии."""
    d = (DREAM,) if in_dreamdrifter else ()
    return requiem_reactions((
        ssw_anemo("Мидзуки", 2, *d, BREEZEBORNE, name="SSW анемо (Мидзуки)"),
        ssw_anemo("Мидзуки", 8, INST, BREEZEBORNE, *d, name="SSW анемо (Мидзуки, Инструктор)"),
        ssw_anemo("Фарузан", 4, INST, BREEZEBORNE, *d, name="SSW анемо (Фарузан, Инструктор)"),
        ssw_anemo("Фарузан", 3, INST, BREEZEBORNE, name="SSW анемо (Фарузан, Инструктор)"),
        ssw_vortex(3, 3, INST, BREEZEBORNE, VV_CRYO, *d, name="SSW вихрь ×3 стака"),
        ssw_vortex(3, 1, INST, BREEZEBORNE, VV_CRYO, name="SSW вихрь ×3 стака"),
        requiem_vortex(INST, BREEZEBORNE, VV_CRYO, *d),
    ))


def make_team(name: str, mizuki_c: int = 0, mizuki_weapon=SACFRAG.at(5),
              odette_c: int = 0, odette_weapon=SILVER_LIGHT,
              mizuki_artifacts=(NIGHT_SKY.at(2), AUBADE.at(2)),
              faruzan_artifacts=VIRIDESCENT, faruzan_weapon=FAV_BOW,
              anastasia_c: int = 0, anastasia_weapon=ARTEMISIA,
              anastasia_artifacts=(STELLAR_SET,)) -> Team:
    return Team(
        name=name,
        builds=[
            mizuki_build(mizuki_c, mizuki_weapon, mizuki_artifacts),
            anastasia_build(anastasia_c, anastasia_weapon, anastasia_artifacts),
            odette_build(odette_c, odette_weapon),
            faruzan_build(faruzan_weapon, faruzan_artifacts),
        ],
        enemy=enemy(),
        reactions=reactions(),
        buffs=TEAM_BUFFS,
        rotation=ROTATION,
        config=Config(),
    )


#: Те же вариации, что у mizuki_faruzan_cmc_odette_sacfrag (Крио ГГ -> Анастасия C0)
VARIANTS = (
    ("Мидзуки C0 (Церемон), C0 Одетта (Серебряный свет R5), C0R1 Анастасия, С6R0 Фарузан",
     dict(mizuki_c=0)),
    ("Мидзуки C2 (Церемон), C0 Одетта (Серебряный свет R5), C0R1 Анастасия, С6R0 Фарузан",
     dict(mizuki_c=2)),
)

BASE_NAME = VARIANTS[0][0]


def all_teams() -> Dict[str, Team]:
    return {name: make_team(name, **kw) for name, kw in VARIANTS}
