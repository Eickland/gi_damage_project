"""
Отряд Весна / Анастасия / Водяница / Одетта (звёздное рассеивание).

Анастасия — саппорт (Милосердие), заменяет Крио ГГ из
vesna_vodya_odette_cmc. Ротация: Одетта EE / Анастасия EQ / Водяница E /
Весна (комбо). Корона Анастасии: 10 атак вне поля.

An Unfinished Requiem: базовый множитель реакций SSW ×1.15 и +4 вихря
2 уровня (см. reactions()).
"""

from __future__ import annotations

from dataclasses import replace
from typing import Dict, Sequence

from ...core.buffs import OTHERS, SELF, TEAM, Buff, temp
from ...core.cycle import Phase
from ...core.engine import Config, Team
from ...core.entities import Build, Enemy
from ...core.reactions import ssw_anemo, ssw_vortex
from ...core.sources import occ
from ...core.stats import S
from ...core.utilits import merge_dicts
from ...data.artifacts import *
from ...data.artifacts_presets import STANDART_SUBSTAT_PRESET
from ...data.tags import *
from ...data.characters.odette import (odette_burst_buffs, ODETTE_BURST_TIME,
                                       ODETTE_COMBO_DICT, ODETTE_BURST_SOURCES)
from ...data.characters.vodyanitsa import VODYA_COMBO_DICT
from ...data.characters.vesna import VESNA_COMBO_DICT
from ...data.characters.anastasia import (anastasia_support, requiem_reactions,
                                          requiem_vortex, CROWN_HITS)
from ...data.weapons import *

VESNA_BASE_TIME = {"burst": 11.5, "no_burst": 11.5}
VESNA_C1_EXTRA = 0.5

TEAM_BUFFS = (
    Buff(S.CRIT_VALUE, 0.30, target=TEAM,
         source="Крио резонанс: +15% крит. шанса (0.30 крит-вэлью)"),
)

#: Время каждого персонажа в ротации (секунды)
TIMES = {"Весна": 11.5, "Анастасия": 3.0, "Одетта": 2.4, "Водяница": 1.6}

ROTATION = "Odette EE/Анастасия EQ/Водяница E/Vesna combo"

MAIN_ATK = {S.ATK_PCT: 0.466 * 2, S.CRIT_VALUE: 0.622}       # АТК/АТК/крит

#: Корона следует за активным персонажем — все 10 атак вне поля Анастасии
ANASTASIA = anastasia_support("ssw", [occ(CROWN_HITS, OFF)])


def vesna_time(base: float, constellation: int) -> float:
    return base + (VESNA_C1_EXTRA if constellation > 0 else 0.0)


def vesna_combo(combo_key: str, base_time: float):
    return lambda b: replace(b, character=VESNA_COMBO_DICT[combo_key],
                             time=vesna_time(base_time, b.constellation))


def vesna_burst_cycle(burst_n: int, total_n: int):
    """Взрыв Весны в burst_n ротациях из total_n."""
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


def enemy() -> Enemy:
    return Enemy(res={"anemo": 0.10, "cryo": 0.10}, def_mult=0.4875, elevation=0.0)


def vesna_build(constellation: int = 0, weapon=CHRYSALIS, artifacts=SCARLET_PROOF,
                extra_buffs: Sequence[Buff] = ()) -> Build:
    return Build(
        character=VESNA_COMBO_DICT["vesna_ssw_burst_combo"],
        constellation=constellation,
        weapon=weapon,
        artifacts=(artifacts,),
        extra_stats=merge_dicts(MAIN_ATK, STANDART_SUBSTAT_PRESET),
        extra_buffs=tuple(extra_buffs),
        time=vesna_time(VESNA_BASE_TIME["burst"], constellation),
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
        character=ODETTE_COMBO_DICT["odette_ssw_combo_vesna"],
        constellation=constellation,
        weapon=weapon,
        artifacts=artifacts,
        extra_stats=merge_dicts(MAIN_ATK, STANDART_SUBSTAT_PRESET),
        extra_sources=ODETTE_BURST_SOURCES if use_burst else (),
        extra_buffs=tuple(extra_buffs) + (odette_burst_buffs(constellation)
                                          if use_burst else ()),
        time=TIMES["Одетта"] + (ODETTE_BURST_TIME if use_burst else 0.0),
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


def reactions():
    """События SSW за ротацию: как в отряде с Крио ГГ + Requiem Анастасии."""
    return requiem_reactions((
        ssw_anemo("Весна", 2, INST, VODYA_LEAD, BREEZEBORNE, name="SSW анемо (Весна, Весна)"),
        ssw_anemo("Весна", 6, INST, VODYA_LEAD, VODYA_CHORUS, BREEZEBORNE,
                  name="SSW анемо (Весна, Инструктор)"),
        ssw_vortex(2, 3, INST, BREEZEBORNE, VV_CRYO, name="SSW вихрь ×3 стака"),
        requiem_vortex(INST, BREEZEBORNE, VV_CRYO),
    ))


def make_team(name: str, vesna_c: int = 0, vesna_weapon=BOUGH,
              odette_c: int = 0, odette_weapon=SILVER_LIGHT,
              vesna_artifacts=SCARLET_PROOF, vodya_artifacts=(MILLELITH,),
              vodya_weapon=TTDS_HALF_CATALYSATOR, vodya_c: int = 0,
              anastasia_c: int = 0, anastasia_weapon=ARTEMISIA,
              anastasia_artifacts=(STELLAR_SET,),odette__artifacts=(HEART_OF_FORGE,)) -> Team:
    return Team(
        name=name,
        builds=[
            vesna_build(vesna_c, vesna_weapon, vesna_artifacts),
            anastasia_build(anastasia_c, anastasia_weapon, anastasia_artifacts),
            odette_build(odette_c, odette_weapon,odette__artifacts),
            vodya_build(vodya_c, vodya_weapon, vodya_artifacts),
        ],
        enemy=enemy(),
        reactions=reactions(),
        buffs=TEAM_BUFFS,
        rotation=ROTATION,
        config=Config(),
        phases=vesna_burst_cycle(1, 2),
    )


#: Те же вариации, что у отряда с Крио ГГ (без него)
VARIANTS = (
    ("Весна C0R0, C2R1 Одетта, C0R0 Анастасия, С0R0 Водяница",
     dict(vesna_c=0)),
    ("Весна C0R1, C2R1 Одетта, C0R0 Анастасия, С0R0 Водяница",
     dict(vesna_weapon = CHRYSALIS,odette_c=2,odette_weapon=FROSTFEATHER,anastasia_weapon=BREEZEBORNE_BOW.at(3),anastasia_artifacts=(HEART_OF_FORGE,),
          odette__artifacts=(STELLAR_SET,))),
    ("Весна C0R0, C2R1 Одетта, C0R0 Анастасия, С0R1 Водяница",
     dict(vesna_c=0, vodya_weapon=MAELSTROM)),
    ("Весна C1R1, C0R0 Одетта, C0R0 Анастасия, С0R1 Водяница",
     dict(vesna_c=1,vesna_weapon = CHRYSALIS,odette_c=0,odette_weapon=SILVER_LIGHT,anastasia_weapon=BREEZEBORNE_BOW.at(1),anastasia_artifacts=(HEART_OF_FORGE,),
          odette__artifacts=(STELLAR_SET,), vodya_weapon=MAELSTROM)),
)

BASE_NAME = VARIANTS[0][0]


def all_teams() -> Dict[str, Team]:
    return {name: make_team(name, **kw) for name, kw in VARIANTS} # pyright: ignore[reportArgumentType]
