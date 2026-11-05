"""
Отряд звёздного проводника: Крио ГГ (ДД на поле) / Яэ Мико / Даника / Одетта.

Ротация: Даника EQ / Одетта EE / Яэ EEE / Крио ГГ N2 P N2 N2 C N2 Q N2 N2.
Реакций, наносящих урон, нет. Резонанс — крио.

Крио ГГ: C6R5 (Пробуждение R5), Разочарование, комбо как в
cryo_mc_odette_sucrose_alyosha: N2 P N2 N2 C N2 Q N2 N2 (9.2 с).
C6 Крио ГГ (окно FROSTGLOW, 15 с после взрыва): ротация ~17.0 с, окно
перекрывает почти всю её, поэтому все удары остальных — с FROSTGLOW.
C2 Даники (danika_c=2): стаки — Крио ГГ 10 (у него 7 ударов SC), остальные по 7.

Артефакты: Яэ — Разочарование, Даника — Сердце горна (полная АТК), Одетта — Звёздный сет, Крио ГГ — Разочарование.
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
from ...data.characters.cryo_mc import CMC_COMBO_DICT, CMC_SC_DD_TIME
from ...data.characters.odette import (odette_burst_buffs, ODETTE_BURST_TIME,
                                       ODETTE_COMBO_DICT, ODETTE_BURST_SOURCES)
from ...data.characters.danika import (DANIKA_COMBO_DICT, C2_ACTIVE_STACKS,
                                       C2_OTHER_STACKS, tag_stellar_conduct_hits, add_tags)
from ...data.characters.yae import YAE_COMBO_DICT
from ...data.weapons import *

TEAM_BUFFS = (
    Buff(S.CRIT_VALUE, 0.30, target=TEAM,
         source="Крио резонанс: +15% крит. шанса (0.30 крит-вэлью)"),
)

#: Время каждого персонажа в ротации (секунды)
TIMES = {"Крио ГГ": CMC_SC_DD_TIME+1, "Яэ Мико": 2.4, "Даника": 3.0, "Одетта": 2.4}

ROTATION = "Даника EQ/Одетта EE/Яэ EEE/Крио ГГ N2 P N2 N2 C N2 Q N2 N2"

MAIN_ATK = {S.ATK_PCT: 0.466 * 2, S.CRIT_VALUE: 0.622}       # АТК/АТК/крит
MAIN_EM = {S.BASE_EM: 187.0 * 2, S.CRIT_VALUE: 0.622}        # МС/МС/крит
FULL_ATK = {S.ATK_PCT: 0.466 * 3}                            # АТК/АТК/АТК (Даника)

CMC = CMC_COMBO_DICT["cmc_sc_dd_combo"]
YAE = YAE_COMBO_DICT["yae_sc_short_combo"]   # ротация ~18 с — короткое комбо
DANIKA = DANIKA_COMBO_DICT["support_eq"]
ODETTE = ODETTE_COMBO_DICT["odette_ssc_combo"]


def enemy() -> Enemy:
    return Enemy(res={"anemo": 0.10, "cryo": 0.10, "electro": 0.10},
                 def_mult=0.4875, elevation=0.0)


def _c2(build: Build, hits: int) -> Build:
    return tag_stellar_conduct_hits(build, DANIKA_C2, hits)


def _frostglow(build: Build) -> Build:
    """C6 Крио ГГ: удар остальных под +40% урона звёздных реакций."""
    return add_tags(build, FROSTGLOW)


def cryo_mc_build(constellation: int = 6, weapon=EXAIPHANES.at(5), artifacts=(DISENCHANTMENT,),
                  main_stats=MAIN_ATK, danika_c2_hits: int = 0,
                  extra_buffs: Sequence[Buff] = ()) -> Build:
    return _c2(Build(
        character=CMC,
        constellation=constellation,
        weapon=weapon,
        artifacts=artifacts,
        extra_stats=merge_dicts(main_stats, STANDART_SUBSTAT_PRESET),
        extra_buffs=tuple(extra_buffs),
        time=TIMES["Крио ГГ"],
    ), danika_c2_hits)

def yae_build(constellation: int = 1, weapon=ECHOES.at(5), artifacts=(DISENCHANTMENT,),
              main_stats=MAIN_ATK, danika_c2_hits: int = 0,
              extra_buffs: Sequence[Buff] = ()) -> Build:
    return _c2(_frostglow(Build(
        character=YAE,
        constellation=constellation,
        weapon=weapon,
        artifacts=artifacts,
        extra_stats=merge_dicts(main_stats, STANDART_SUBSTAT_PRESET),
        extra_buffs=tuple(extra_buffs),
        time=TIMES["Яэ Мико"],
    )), danika_c2_hits)


def danika_build(constellation: int = 0, weapon=ATONEMENT, artifacts=(HEART_OF_FORGE,),
                 main_stats=FULL_ATK, extra_buffs: Sequence[Buff] = ()) -> Build:
    return _c2(_frostglow(Build(
        character=DANIKA,
        constellation=constellation,
        weapon=weapon,
        artifacts=artifacts,
        extra_stats=merge_dicts(main_stats, STANDART_SUBSTAT_FULL_ATK_PRESET),
        extra_buffs=tuple(extra_buffs),
        time=TIMES["Даника"],
    )), C2_OTHER_STACKS if constellation >= 2 else 0)


def odette_build(constellation: int = 0, weapon=SILVER_LIGHT, artifacts=(STELLAR_SET,),
                 use_burst: bool | None = None, danika_c2_hits: int = 0,
                 extra_buffs: Sequence[Buff] = ()) -> Build:
    """use_burst=None — авто: до C4 не применяем, с C4 применяем."""
    if use_burst is None:
        use_burst = constellation >= 4
    return _c2(_frostglow(Build(
        character=ODETTE,
        constellation=constellation,
        weapon=weapon,
        artifacts=artifacts,
        extra_stats=merge_dicts(MAIN_ATK, STANDART_SUBSTAT_PRESET),
        extra_sources=ODETTE_BURST_SOURCES if use_burst else (),
        extra_buffs=tuple(extra_buffs) + (odette_burst_buffs(constellation)
                                          if use_burst else ()),
        time=TIMES["Одетта"] + (ODETTE_BURST_TIME if use_burst else 0.0),
    )), danika_c2_hits)


def make_team(name: str, cmc_c: int = 6, cmc_weapon=EXAIPHANES.at(5),
              cmc_artifacts=(DISENCHANTMENT,),
              yae_c: int = 1, yae_weapon=ECHOES.at(5), yae_artifacts=(DISENCHANTMENT,),
              danika_c: int = 0, danika_weapon=ATONEMENT, danika_artifacts=(HEART_OF_FORGE,),
              odette_c: int = 0, odette_weapon=SILVER_LIGHT, odette_artifacts=(STELLAR_SET,)) -> Team:
    c2 = danika_c >= 2
    return Team(
        name=name,
        builds=[
            cryo_mc_build(cmc_c, cmc_weapon, cmc_artifacts,
                          danika_c2_hits=C2_ACTIVE_STACKS if c2 else 0),
            yae_build(yae_c, yae_weapon, yae_artifacts, danika_c2_hits=C2_OTHER_STACKS if c2 else 0),
            danika_build(danika_c, danika_weapon, danika_artifacts),
            odette_build(odette_c, odette_weapon, odette_artifacts, danika_c2_hits=C2_OTHER_STACKS if c2 else 0),
        ],
        enemy=enemy(),
        buffs=TEAM_BUFFS,
        rotation=ROTATION,
        config=Config(),
    )


def team_name(cmc_c: int = 6, cmc_weapon=EXAIPHANES.at(5),
              yae_c: int = 1, yae_weapon=ECHOES.at(5),
              danika_c: int = 0, danika_weapon=ATONEMENT,
              odette_c: int = 0, odette_weapon=SILVER_LIGHT) -> str:
    _dw = (f" ({danika_weapon.name})" if danika_weapon.name != ATONEMENT.name else "")
    return (f"C{cmc_c}R{cmc_weapon.refinement} Крио ГГ, "
            + f"C{yae_c}R{yae_weapon.refinement} Яэ" + ", "
            + f"C{danika_c}R{danika_weapon.refinement} Даника{_dw}" + ", "
            + f"C{odette_c}R{odette_weapon.refinement} Одетта")


VARIANTS = ({"danika_c": 0}, {"danika_c": 1}, {"danika_c": 2},
            {"danika_c": 0, "danika_weapon": SPRING_TIDE},  # Даника с сигной (Весенний прилив R1)
)

BASE_NAME = team_name()


def all_teams() -> Dict[str, Team]:
    out: Dict[str, Team] = {}
    for kw in VARIANTS:
        name = team_name(**kw) # pyright: ignore[reportArgumentType]
        out[name] = make_team(name, **kw) # pyright: ignore[reportArgumentType]
    return out
