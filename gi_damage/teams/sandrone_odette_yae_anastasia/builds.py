"""
Отряд звёздного проводника: Сандроне / Одетта / Яэ Мико / Анастасия.

Ротация: Анастасия EQ / Одетта EE / Яэ EEE / Сандроне E CA EQ CA E CA E.
Реакций, наносящих урон, нет. Резонанс — крио (3 крио + 1 электро).
Ротация ~22.3 с — у Яэ длинное комбо.

Анастасия — саппорт (Милосердие): корона 10 атак вне поля, Triumph.
An Unfinished Requiem: +1 стак Polestar всем ударам SC отряда (polar_shift()).

Напевы ветра Анастасии (окно BREEZEBORNE): в комбо Сандроне оно уже стоит
на всех ударах SC, кроме последней заряженной атаки и последнего навыка.

Артефакты: Сандроне — Разочарование, Одетта — Звёздный сет, Яэ — Сердце
горна, Анастасия — Миллелит.
"""

from __future__ import annotations

from typing import Dict, Sequence

from ...core.buffs import OTHERS, SELF, TEAM, Buff, temp
from ...core.engine import Config, Team
from ...core.entities import Build, Enemy
from ...core.sources import occ
from ...core.stats import S
from ...core.utilits import merge_dicts
from ...data.artifacts import *
from ...data.artifacts_presets import *
from ...data.tags import *
from ...data.characters.sandrone import SANDRONE_COMBO_DICT
from ...data.characters.odette import (odette_burst_buffs, ODETTE_BURST_TIME,
                                       ODETTE_COMBO_DICT, ODETTE_BURST_SOURCES)
from ...data.characters.yae import YAE_COMBO_DICT
from ...data.characters.anastasia import anastasia_support, polar_shift, CROWN_HITS
from ...data.weapons import *

TEAM_BUFFS = (
    Buff(S.CRIT_VALUE, 0.30, target=TEAM,
         source="Крио резонанс: +15% крит. шанса (0.30 крит-вэлью)"),
)

#: Время каждого персонажа в ротации (секунды)
TIMES = {"Сандроне": 14.5, "Одетта": 2.4, "Яэ Мико": 2.4, "Анастасия": 3.0}

ROTATION = "Анастасия EQ/Одетта EE/Яэ EEE/Сандроне E CA EQ CA E CA E"

MAIN_ATK = {S.ATK_PCT: 0.466 * 2, S.CRIT_VALUE: 0.622}       # АТК/АТК/крит

#: Комбо с +1 стаком Polestar (Requiem Анастасии)
SANDRONE = polar_shift(SANDRONE_COMBO_DICT["sandrone_sc_combo"])
ODETTE = polar_shift(ODETTE_COMBO_DICT["odette_ssc_combo"])
YAE = polar_shift(YAE_COMBO_DICT["yae_sc_long_combo"])
ANASTASIA = polar_shift(anastasia_support("sc", [occ(CROWN_HITS, OFF)]))


def enemy() -> Enemy:
    return Enemy(res={"anemo": 0.10, "cryo": 0.10, "electro": 0.10},
                 def_mult=0.4875, elevation=0.0)


def sandrone_build(constellation: int = 0, weapon=ATONEMENT, artifacts=(DISENCHANTMENT,),
                   main_stats=MAIN_ATK, extra_buffs: Sequence[Buff] = ()) -> Build:
    return Build(
        character=SANDRONE,
        constellation=constellation,
        weapon=weapon,
        artifacts=artifacts,
        extra_stats=merge_dicts(main_stats, STANDART_SUBSTAT_PRESET),
        extra_buffs=tuple(extra_buffs),
        time=TIMES["Сандроне"],
    )


def odette_build(constellation: int = 0, weapon=SILVER_LIGHT, artifacts=(STELLAR_SET,),
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


def yae_build(constellation: int = 1, weapon=ECHOES.at(5), artifacts=(HEART_OF_FORGE,),
              main_stats=MAIN_ATK, extra_buffs: Sequence[Buff] = ()) -> Build:
    return Build(
        character=YAE,
        constellation=constellation,
        weapon=weapon,
        artifacts=artifacts,
        extra_stats=merge_dicts(main_stats, STANDART_SUBSTAT_PRESET),
        extra_buffs=tuple(extra_buffs),
        time=TIMES["Яэ Мико"],
    )


def anastasia_build(constellation: int = 0, weapon=BREEZEBORNE_BOW.at(1), artifacts=(MILLELITH,),
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


def make_team(name: str, sandrone_c: int = 0, sandrone_weapon=ATONEMENT,
              odette_c: int = 0, odette_weapon=SILVER_LIGHT,
              yae_c: int = 1, yae_weapon=ECHOES.at(5),
              anastasia_c: int = 0, anastasia_weapon=ARTEMISIA.at(1),
              sandrone_artifacts=(DISENCHANTMENT,), odette_artifacts=(STELLAR_SET,),
              yae_artifacts=(HEART_OF_FORGE,), anastasia_artifacts=(MILLELITH,)) -> Team:
    return Team(
        name=name,
        builds=[
            sandrone_build(sandrone_c, sandrone_weapon, sandrone_artifacts),
            odette_build(odette_c, odette_weapon, odette_artifacts),
            yae_build(yae_c, yae_weapon, yae_artifacts),
            anastasia_build(anastasia_c, anastasia_weapon, anastasia_artifacts),
        ],
        enemy=enemy(),
        buffs=TEAM_BUFFS,
        rotation=ROTATION,
        config=Config(),
    )


def team_name(sandrone_c: int = 0, sandrone_weapon=ATONEMENT,
              odette_c: int = 0, odette_weapon=SILVER_LIGHT,
              yae_c: int = 1, yae_weapon=ECHOES.at(5),
              anastasia_c: int = 0, anastasia_weapon=BREEZEBORNE_BOW.at(1)) -> str:
    a = ("R0 Анастасия" if anastasia_weapon.name == BREEZEBORNE_BOW.name
         else f"R{anastasia_weapon.refinement} Анастасия ({anastasia_weapon.name})")
    return (f"C{sandrone_c}R{sandrone_weapon.refinement} Сандроне, "
            f"C{odette_c}R{odette_weapon.refinement} Одетта, "
            f"C{yae_c}R{yae_weapon.refinement} Яэ, "
            f"C{anastasia_c}{a}")


#: Анастасия: C0R0, C0 с сигной, C1R0, C2R0 (R0 = Напевы ветра R1)
VARIANTS = (
    {"anastasia_c": 0},
    {"anastasia_c": 0, "anastasia_weapon": SILVER_RADIANCE},
    {"anastasia_c": 1},
    {"anastasia_c": 2},
)

BASE_NAME = team_name()


def all_teams() -> Dict[str, Team]:
    out: Dict[str, Team] = {}
    for kw in VARIANTS:
        name = team_name(**kw)
        out[name] = make_team(name, **kw)
    return out
