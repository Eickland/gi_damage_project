"""
Отряд Весна / Анастасия / Одетта / Фарузан (звёздное рассеивание).

Как vesna_faruzan_odette_cmc, но вместо Крио ГГ — Анастасия (саппорт,
Милосердие). Ротация: Фарузан EQ / Анастасия EQ / Одетта EE / Весна.
Корона: 6 атак из 10 — в окне Напевов ветра и Изумрудной тени Фарузан,
4 — вне.

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
from ...data.artifacts_presets import STANDART_SUBSTAT_PRESET
from ...data.tags import *
from ...data.characters.odette import (odette_burst_buffs, ODETTE_BURST_TIME,
                                       ODETTE_COMBO_DICT, ODETTE_BURST_SOURCES)
from ...data.characters.faruzan import FARUZAN_COMBO_DICT
from ...data.characters.vesna import VESNA_COMBO_DICT
from ...data.characters.anastasia import (anastasia_support, requiem_reactions,
                                          requiem_vortex, CROWN_HITS)
from ...data.weapons import *

TEAM_BUFFS = (
    Buff(S.CRIT_VALUE, 0.30, target=TEAM,
         source="Крио резонанс: +15% крит. шанса (0.30 крит-вэлью)"),
)

#: Время каждого персонажа в ротации (секунды)
TIMES = {"Весна": 11.5, "Анастасия": 3.0, "Одетта": 2.4, "Фарузан": 2.1}

ROTATION = "Faruzan EQ/Odette EE/Анастасия EQ/Vesna E sEsE N3CsE Q sE N3CsE"

MAIN_ATK = {S.ATK_PCT: 0.466 * 2, S.CRIT_VALUE: 0.622}       # АТК/АТК/крит

#: Атаки короны в окне Напевов ветра / Изумрудной тени Фарузан
CROWN_IN_WINDOW = 6
ANASTASIA = anastasia_support("ssw", [occ(CROWN_IN_WINDOW, OFF, BREEZEBORNE, VV_CRYO),
                                      occ(CROWN_HITS - CROWN_IN_WINDOW, OFF)])


def enemy() -> Enemy:
    return Enemy(res={"anemo": 0.10, "cryo": 0.10}, def_mult=0.4875, elevation=0.0)


def vesna_build(constellation: int = 0, weapon=CHRYSALIS.at(1), artifacts=SCARLET_PROOF,
                extra_buffs: Sequence[Buff] = ()) -> Build:
    return Build(
        character=VESNA_COMBO_DICT["vesna_ssw_burst_combo"],
        constellation=constellation,
        weapon=weapon,
        artifacts=(artifacts,),
        extra_stats=merge_dicts(MAIN_ATK, STANDART_SUBSTAT_PRESET),
        extra_buffs=tuple(extra_buffs),
        time=TIMES["Весна"],
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


def faruzan_build(weapon=BREEZEBORNE_BOW.at(1), artifacts: ArtifactSet = VIRIDESCENT,
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


def reactions():
    """События SSW за ротацию: как в vesna_faruzan_odette_cmc + Requiem Анастасии."""
    return requiem_reactions((
        ssw_anemo("Весна", 7, BREEZEBORNE, name="SSW анемо (Весна)"),
        ssw_anemo("Фарузан", 7, BREEZEBORNE, name="SSW анемо (Фарузан, Инструктор)"),
        ssw_vortex(2, 4, INST, BREEZEBORNE, VV_CRYO, name="SSW вихрь ×3 стака"),
        requiem_vortex(INST, BREEZEBORNE, VV_CRYO),
    ))


def make_team(name: str, vesna_c: int = 0, vesna_weapon=CHRYSALIS.at(1),
              odette_c: int = 0, odette_weapon=SILVER_LIGHT,
              vesna_artifacts=SCARLET_PROOF, faruzan_artifacts=VIRIDESCENT,
              faruzan_weapon=FAV_BOW.at(5),
              anastasia_c: int = 0, anastasia_weapon=BREEZEBORNE_BOW,
              anastasia_artifacts=(STELLAR_SET,)) -> Team:
    return Team(
        name=name,
        builds=[
            vesna_build(vesna_c, vesna_weapon, vesna_artifacts),
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


#: Те же вариации, что у vesna_faruzan_odette_cmc (Крио ГГ -> Анастасия C0)
VARIANTS = (
    ("Весна C0R0, C0R0 Одетта, C0R1 Анастасия, С6R0 Фарузан",
     dict(vesna_weapon=BOUGH.at(1), faruzan_weapon=FAV_BOW)),
    ("Весна C0R1, C0R0 Одетта, C0R1 Анастасия, С6R1 Фарузан",
     dict(vesna_weapon=CHRYSALIS.at(1), faruzan_weapon=FAV_BOW.at(1))),
    ("Весна C1R1, C0R0 Одетта, C0R1 Анастасия, С6R1 Фарузан",
     dict(vesna_c=1, vesna_weapon=CHRYSALIS.at(1), faruzan_weapon=FAV_BOW.at(1))),
    ("Весна C2R1, C0R0 Одетта, C0R1 Анастасия, С6R5 Фарузан",
     dict(vesna_c=2, vesna_weapon=CHRYSALIS.at(1), faruzan_weapon=FAV_BOW.at(5))),
)

BASE_NAME = VARIANTS[1][0]


def all_teams() -> Dict[str, Team]:
    return {name: make_team(name, **kw) for name, kw in VARIANTS} # pyright: ignore[reportArgumentType]
