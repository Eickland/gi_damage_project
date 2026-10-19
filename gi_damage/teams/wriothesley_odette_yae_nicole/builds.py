"""
Отряд звёздного проводника: Ризли / Одетта / Яэ Мико / Николь.

Реакций, наносящих урон, нет. Резонанс — крио (Ризли + Одетта).
"""

from __future__ import annotations

from typing import Dict, Sequence

from ...core.buffs import OTHERS, SELF, TEAM, Buff, temp
from ...core.engine import Config, Team
from ...core.entities import Build, Enemy, ArtifactSet
from ...core.stats import S
from ...core.utilits import merge_dicts
from ...data.artifacts import *
from ...data.artifacts_presets import *
from ...data.tags import *
from ...data.characters.wriothesley import WRIO_COMBO_DICT
from ...data.characters.odette import (odette_burst_buffs, ODETTE_BURST_TIME,
                                       ODETTE_COMBO_DICT, ODETTE_BURST_SOURCES)
from ...data.characters.yae import YAE_COMBO_DICT
from ...data.characters.nicole import NICOLE_COMBO_DICT
from ...data.weapons import *

TEAM_BUFFS = (
    Buff(S.CRIT_VALUE, 0.30, target=TEAM,
         source="Крио резонанс: +15% крит. шанса (0.30 крит-вэлью)"),
)

#: Время каждого персонажа в ротации (секунды)
TIMES = {"Ризли": 10.1, "Одетта": 2.4, "Яэ Мико": 2.4, "Николь": 1.4}

ROTATION = "Одетта EE/Яэ EEE/Николь E/Ризли 3×(N5 CA)"

#: Николь: 2+2 на АТК (по 18% АТК с каждой пары)
NICOLE_ARTIFACTS = (HEART_OF_FORGE.at(2), SCARLET_PROOF.at(2))


def enemy() -> Enemy:
    return Enemy(res={"anemo": 0.10, "cryo": 0.10, "electro": 0.10, "pyro": 0.10},
                 def_mult=0.4875, elevation=0.0)


def wriothesley_build(constellation: int = 1, weapon=WANDERER_SONG_CRYO.at(5),
                      artifacts=(DISENCHANTMENT,),
                      main_stats={S.ATK_PCT: 0.466 * 2, S.CRIT_VALUE: 0.622},
                      extra_buffs: Sequence[Buff] = ()) -> Build:
    return Build(
        character=WRIO_COMBO_DICT["sc_n5ca"],
        constellation=constellation,
        weapon=weapon,
        artifacts=artifacts,
        extra_stats=merge_dicts(main_stats, STANDART_SUBSTAT_PRESET),
        extra_buffs=tuple(extra_buffs),
        time=TIMES["Ризли"],
    )


def odette_build(constellation: int = 0, weapon=SILVER_LIGHT, artifacts=(HEART_OF_FORGE,),
                 use_burst: bool | None = None,
                 extra_buffs: Sequence[Buff] = ()) -> Build:
    """use_burst=None — авто: до C4 не применяем, с C4 применяем."""
    if use_burst is None:
        use_burst = constellation >= 4
    return Build(
        character=ODETTE_COMBO_DICT["odette_ssc_combo"],
        constellation=constellation,
        weapon=weapon,
        artifacts=artifacts,
        extra_stats=merge_dicts(
            {S.ATK_PCT: 0.466 * 2, S.CRIT_VALUE: 0.622},
            STANDART_SUBSTAT_PRESET),
        extra_sources=ODETTE_BURST_SOURCES if use_burst else (),
        extra_buffs=tuple(extra_buffs) + (odette_burst_buffs(constellation)
                                          if use_burst else ()),
        time=TIMES["Одетта"] + (ODETTE_BURST_TIME if use_burst else 0.0),
    )


def yae_build(constellation: int = 1, weapon=ECHOES.at(5), artifacts=(DISENCHANTMENT,),
              main_stats={S.ATK_PCT: 0.466 * 2, S.CRIT_VALUE: 0.622},
              extra_buffs: Sequence[Buff] = ()) -> Build:
    return Build(
        character=YAE_COMBO_DICT["yae_sc_wrio_combo"],
        constellation=constellation,
        weapon=weapon,
        artifacts=artifacts,
        extra_stats=merge_dicts(main_stats, STANDART_SUBSTAT_PRESET),
        extra_buffs=tuple(extra_buffs),
        time=TIMES["Яэ Мико"],
    )


def nicole_build(constellation: int = 0, weapon=ECHOES.at(5), artifacts=NICOLE_ARTIFACTS,
                 main_stats={S.ATK_PCT: 0.466 * 3},
                 extra_buffs: Sequence[Buff] = ()) -> Build:
    return Build(
        character=NICOLE_COMBO_DICT["support_e"],
        constellation=constellation,
        weapon=weapon,
        artifacts=artifacts,
        extra_stats=merge_dicts(main_stats, STANDART_SUBSTAT_PRESET),
        extra_buffs=tuple(extra_buffs),
        time=TIMES["Николь"],
    )


def make_team(name: str, wrio_c: int = 1, wrio_weapon=WANDERER_SONG_CRYO.at(5),
              odette_c: int = 0, odette_weapon=SILVER_LIGHT,
              yae_c: int = 2, yae_weapon=ECHOES.at(5),
              nicole_c: int = 0, nicole_weapon=ECHOES.at(5),
              wrio_artifacts=(DISENCHANTMENT,), odette_artifacts=(HEART_OF_FORGE,),
              yae_artifacts=(DISENCHANTMENT,), nicole_artifacts=NICOLE_ARTIFACTS) -> Team:
    return Team(
        name=name,
        builds=[
            wriothesley_build(wrio_c, wrio_weapon, wrio_artifacts),
            odette_build(odette_c, odette_weapon, odette_artifacts),
            yae_build(yae_c, yae_weapon, yae_artifacts),
            nicole_build(nicole_c, nicole_weapon, nicole_artifacts),
        ],
        enemy=enemy(),
        buffs=TEAM_BUFFS,
        rotation=ROTATION,
        config=Config(),
    )


BASE_NAME = "C1R5 Ризли, C0R5 Одетта, C1R5 Яэ, C0R5 Николь"


def all_teams() -> Dict[str, Team]:
    return {BASE_NAME: make_team(BASE_NAME)}
