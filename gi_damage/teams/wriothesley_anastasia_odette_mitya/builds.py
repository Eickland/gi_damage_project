"""
Отряд звёздного проводника: Ризли / Анастасия / Одетта / Митя.

Ротация: Одетта EE / Митя E / Анастасия EQ / Ризли 4×(N5 CA) (13.5 с),
как в отряде Ризли / Одетта / Митя / Николь, Николь заменена Анастасией.
Всего 20.6 с ≥ 20.5 — у Мити полный Эпос (TTDS_FULL).
Реакций, наносящих урон, нет. Резонанс — крио (3 крио + Митя).

Анастасия — саппорт (Милосердие): корона 10 атак вне поля, Triumph.

Артефакты: Ризли и Анастасия — Звёздный сет, Одетта — Сердце горна,
Митя — Миллелит.
"""

from __future__ import annotations

from typing import Dict, Sequence

from ...core.buffs import TEAM, Buff
from ...core.engine import Config, Team
from ...core.entities import Build, Enemy
from ...core.sources import occ
from ...core.stats import S
from ...core.utilits import merge_dicts
from ...data.artifacts import *
from ...data.artifacts_presets import *
from ...data.tags import *
from ...data.characters.wriothesley import WRIO_COMBO_DICT,WRIO_4N5CA_N3_TIME
from ...data.characters.odette import (odette_burst_buffs, ODETTE_BURST_TIME,
                                       ODETTE_COMBO_DICT, ODETTE_BURST_SOURCES)
from ...data.characters.mitya import MITYA_COMBO_DICT
from ...data.characters.anastasia import anastasia_support, CROWN_HITS
from ...data.weapons import *

TEAM_BUFFS = (
    Buff(S.CRIT_VALUE, 0.30, target=TEAM,
         source="Крио резонанс: +15% крит. шанса (0.30 крит-вэлью)"),
)

#: Время каждого персонажа в ротации (секунды)
TIMES = {"Ризли": WRIO_4N5CA_N3_TIME, "Анастасия": 3.5, "Одетта": 2.4, "Митя": 1.2}

ROTATION = "Одетта EE/Митя E/Анастасия EQ/Ризли 4×(N5 CA) N3"

MAIN_ATK = {S.ATK_PCT: 0.466 * 2, S.CRIT_VALUE: 0.622}       # АТК/АТК/крит

WRIO = WRIO_COMBO_DICT["sc_4n5ca_n3"]
ODETTE = ODETTE_COMBO_DICT["odette_ssc_combo"]
MITYA = MITYA_COMBO_DICT["support_steady"]
ANASTASIA = anastasia_support("sc", [occ(CROWN_HITS, OFF)])


def enemy() -> Enemy:
    return Enemy(res={"anemo": 0.10, "cryo": 0.10, "electro": 0.10},
                 def_mult=0.4875, elevation=0.0)


def wriothesley_build(constellation: int = 1, weapon=WANDERER_SONG_CRYO.at(5),
                      artifacts=(STELLAR_SET,), main_stats=MAIN_ATK,
                      extra_buffs: Sequence[Buff] = ()) -> Build:
    return Build(
        character=WRIO,
        constellation=constellation,
        weapon=weapon,
        artifacts=artifacts,
        extra_stats=merge_dicts(main_stats, STANDART_SUBSTAT_PRESET),
        extra_buffs=tuple(extra_buffs),
        time=TIMES["Ризли"],
    )


def anastasia_build(constellation: int = 0, weapon=BREEZEBORNE_BOW.at(1),
                    artifacts=(STELLAR_SET,), main_stats=MAIN_ATK,
                    extra_buffs: Sequence[Buff] = ()) -> Build:
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
        character=ODETTE,
        constellation=constellation,
        weapon=weapon,
        artifacts=artifacts,
        extra_stats=merge_dicts(MAIN_ATK, STANDART_SUBSTAT_PRESET),
        extra_sources=ODETTE_BURST_SOURCES if use_burst else (),
        extra_buffs=tuple(extra_buffs) + (odette_burst_buffs(constellation)
                                          if use_burst else ()),
        time=TIMES["Одетта"] + (ODETTE_BURST_TIME if use_burst else 0.0),
    )


def mitya_build(constellation: int = 0, weapon=TTDS_FULL_CATALYSATOR, artifacts=(MILLELITH,),
                main_stats={S.BASE_EM: 187.0 * 3},
                extra_buffs: Sequence[Buff] = ()) -> Build:
    return Build(
        character=MITYA,
        constellation=constellation,
        weapon=weapon,
        artifacts=artifacts,
        extra_stats=merge_dicts(main_stats, STANDART_SUBSTAT_PRESET),
        extra_buffs=tuple(extra_buffs),
        time=TIMES["Митя"],
    )


def make_team(name: str, wrio_c: int = 1, wrio_weapon=WANDERER_SONG_CRYO.at(5),
              anastasia_c: int = 0, anastasia_weapon=BREEZEBORNE_BOW.at(1),
              odette_c: int = 0, odette_weapon=SILVER_LIGHT,
              mitya_c: int = 0, mitya_weapon=TTDS_FULL_CATALYSATOR,
              wrio_artifacts=(STELLAR_SET,), anastasia_artifacts=(HEART_OF_FORGE,),
              odette_artifacts=(STELLAR_SET,), mitya_artifacts=(MILLELITH,)) -> Team:
    return Team(
        name=name,
        builds=[
            wriothesley_build(wrio_c, wrio_weapon, wrio_artifacts),
            anastasia_build(anastasia_c, anastasia_weapon, anastasia_artifacts),
            odette_build(odette_c, odette_weapon, odette_artifacts),
            mitya_build(mitya_c, mitya_weapon, mitya_artifacts),
        ],
        enemy=enemy(),
        buffs=TEAM_BUFFS,
        rotation=ROTATION,
        config=Config(),
    )


def team_name(wrio_c: int = 1, anastasia_c: int = 0, odette_c: int = 0,
              mitya_c: int = 0) -> str:
    return (f"C{wrio_c}R0 Ризли, C{anastasia_c}R0 Анастасия, "
            f"C{odette_c}R0 Одетта, C{mitya_c}R0 Митя")


VARIANTS = ({},)

BASE_NAME = team_name()


def all_teams() -> Dict[str, Team]:
    out: Dict[str, Team] = {}
    for kw in VARIANTS:
        name = team_name(**kw)
        out[name] = make_team(name, **kw)
    return out
