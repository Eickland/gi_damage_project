"""
Отряд Мидзуки / Анастасия / Водяница / Крио ГГ (звёздное рассеивание).

Как mizuki_vodya_odette_cmc, но вместо Одетты — Анастасия (саппорт,
Милосердие). Ротация: Крио ГГ E CA Q / Анастасия EQ / Водяница E / Мидзуки EQ.
Корона следует за активным персонажем: 6 атак из 10 — пока Мидзуки на поле
(окно DREAM, Изумрудная тень, C6 Крио ГГ), 4 — вне его.

An Unfinished Requiem: базовый множитель реакций SSW ×1.15 и +4 вихря
2 уровня (см. reactions()). Стак Chorus Водяницы — у Крио ГГ, как в исходном
отряде.
"""

from __future__ import annotations

from typing import Dict, Sequence

from ...core.buffs import OTHERS, SELF, TEAM, Buff, temp
from ...core.engine import Config, Team
from ...core.entities import Build, Enemy
from ...core.reactions import ssw_anemo, ssw_vortex
from ...core.sources import occ
from ...core.stats import S
from ...core.utilits import merge_dicts
from ...data.artifacts import *
from ...data.artifacts_presets import STANDART_SUBSTAT_PRESET
from ...data.tags import *
from ...data.weapons import *
from ...data.characters.cryo_mc import CMC_COMBO_DICT
from ...data.characters.mizuki import MIZUKI_COMBO_DICT
from ...data.characters.vodyanitsa import VODYA_COMBO_DICT
from ...data.characters.anastasia import (anastasia_support, requiem_reactions,
                                          requiem_vortex)

TEAM_BUFFS = (
    Buff(S.CRIT_VALUE, 0.30, target=TEAM,
         source="Крио резонанс: +15% крит. шанса (0.30 крит-вэлью)"),
)

#: Время каждого персонажа в ротации (секунды)
TIMES = {"Мидзуки": 10.5, "Анастасия": 3.0, "Крио ГГ": 3.65, "Водяница": 1.35}

ROTATION = "CMC E CA Q/Анастасия EQ/Водяница E/Midzuki EQ"

MAIN_ATK = {S.ATK_PCT: 0.466 * 2, S.CRIT_VALUE: 0.622}       # АТК/АТК/крит

#: Атаки короны: 6 — пока Мидзуки на поле, 4 — до неё
CROWN_IN_DREAM = 6
ANASTASIA = anastasia_support("ssw", [occ(CROWN_IN_DREAM, OFF, DREAM, VV_CRYO, FROSTGLOW),
                                      occ(10 - CROWN_IN_DREAM, OFF)])


def enemy() -> Enemy:
    return Enemy(res={"anemo": 0.10, "cryo": 0.10}, def_mult=0.4875, elevation=0.0)


def mizuki_build(constellation: int = 2, weapon=WANDERER_SONG.at(5), artifacts=(VIRIDESCENT,),
                 extra_buffs: Sequence[Buff] = ()) -> Build:
    if constellation == 6 and weapon.name != "Сон солнечным утром":
        main_stats = {S.BASE_EM: 187 * 3}
    else:
        main_stats = {S.BASE_EM: 187 * 2, S.CRIT_VALUE: 0.622}
    return Build(
        character=MIZUKI_COMBO_DICT["mizuki_long_combo"],
        constellation=constellation,
        weapon=weapon,
        artifacts=artifacts,
        extra_stats=merge_dicts(main_stats, STANDART_SUBSTAT_PRESET),
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


def cryo_mc_build(constellation: int = 4, artifacts=(HEART_OF_FORGE.at(2), SCARLET_PROOF.at(2)),
                  weapon=EXAIPHANES, extra_buffs: Sequence[Buff] = ()) -> Build:
    return Build(
        character=CMC_COMBO_DICT["cmc_ssw_mizuki_combo"],
        constellation=constellation,
        weapon=weapon,
        artifacts=artifacts,
        extra_stats=merge_dicts(MAIN_ATK, STANDART_SUBSTAT_PRESET),
        extra_buffs=tuple(extra_buffs),
        time=TIMES["Крио ГГ"],
    )


def vodya_build(constellation: int = 0, weapon=TTDS_HALF_CATALYSATOR, artifacts=(MILLELITH,),
                extra_buffs: Sequence[Buff] = ()) -> Build:
    return Build(
        character=VODYA_COMBO_DICT["off_field"],
        constellation=constellation,
        weapon=weapon,
        artifacts=artifacts,
        extra_stats=merge_dicts({S.HP_PCT: 0.466 * 3}, STANDART_SUBSTAT_PRESET),
        extra_buffs=tuple(extra_buffs),
        time=TIMES["Водяница"],
    )


def reactions(in_dreamdrifter: bool = True):
    """События SSW за ротацию: как в mizuki_vodya_odette_cmc + Requiem Анастасии."""
    d = (DREAM,) if in_dreamdrifter else ()
    return requiem_reactions((
        ssw_anemo("Мидзуки", 1, *d, BREEZEBORNE, FROSTGLOW, trigger_tags=(VODYA_LEAD,),
                  name="SSW анемо (Мидзуки)"),
        ssw_anemo("Мидзуки", 10, *d, BREEZEBORNE, FROSTGLOW, trigger_tags=(VODYA_LEAD,),
                  char_tags={"Крио ГГ": (VODYA_CHORUS,)}, name="SSW анемо (Мидзуки)"),
        ssw_vortex(3, 3, *d, BREEZEBORNE, FROSTGLOW, VV_CRYO, name="SSW вихрь ×3 стака"),
        requiem_vortex(*d, BREEZEBORNE, FROSTGLOW, VV_CRYO),
    ))


def make_team(name: str, mizuki_c: int = 2, mizuki_weapon=WANDERER_SONG.at(5),
              cmc_c: int = 4, cmc_weapon=EXAIPHANES,
              cmc_artifacts=(HEART_OF_FORGE.at(2), SCARLET_PROOF.at(2)),
              mizuki_artifacts=(VIRIDESCENT,), vodya_artifacts=(MILLELITH,),
              vodya_weapon=TTDS_HALF_CATALYSATOR, vodya_c: int = 0,
              anastasia_c: int = 0, anastasia_weapon=ARTEMISIA,
              anastasia_artifacts=(STELLAR_SET,)) -> Team:
    return Team(
        name=name,
        builds=[
            mizuki_build(mizuki_c, mizuki_weapon, mizuki_artifacts),
            anastasia_build(anastasia_c, anastasia_weapon, anastasia_artifacts),
            cryo_mc_build(cmc_c, cmc_artifacts, cmc_weapon),
            vodya_build(vodya_c, vodya_weapon, vodya_artifacts),
        ],
        enemy=enemy(),
        reactions=reactions(),
        buffs=TEAM_BUFFS,
        rotation=ROTATION,
        config=Config(),
    )


#: Первые вариации mizuki_vodya_odette_cmc (Одетта -> Анастасия)
VARIANTS = (
    ("Мидзуки C1, C0R1 Анастасия, C4R3 Крио ГГ, С0R0 Водяница (Мил)",
     dict(mizuki_c=1, mizuki_artifacts=(GILDED,))),
    ("Мидзуки C2, C0R1 Анастасия, C4R3 Крио ГГ, С0R0 Водяница (Мил)",
     dict(mizuki_c=2, mizuki_artifacts=(VIRIDESCENT,))),
    ("Мидзуки C2, C0R1 Анастасия, C4R3 Крио ГГ, С0R0 Водяница (2+2)",
     dict(mizuki_c=2, vodya_artifacts=(MILLELITH.at(2), VOURUKASHA.at(2)))),
)

BASE_NAME = VARIANTS[1][0]


def all_teams() -> Dict[str, Team]:
    return {name: make_team(name, **kw) for name, kw in VARIANTS}
