"""
Отряд звёздного проводника: Митя (ДД, перегрузка) / Одетта / Даника / C6 Валера.

Ротация: Одетта EE / Даника EQ / Митя hE CA / Валера E CA Q / Митя CA Q CA.
Комбо Мити — MITYA_COMBO_DICT["dd_overload"]: удары после Валеры — в окне
Знати, первые 13 (C1+: 15) тратят стаки Offensive Directive.
Реакций, наносящих урон, нет. Крио персонаж один — резонанса нет.
Артефакты: Митя — Разочарование, Одетта — Сердце горна, Даника — Миллелит,
Валера — Знать.
"""

from __future__ import annotations

from typing import Dict, Sequence

from ...core.buffs import OTHERS, SELF, TEAM, Buff, temp
from ...core.engine import Config, Team
from ...core.entities import Build, Enemy
from ...core.stats import S
from ...core.utilits import merge_dicts
from ...data.artifacts import *
from ...data.artifacts_presets import *
from ...data.tags import *
from ...data.characters.mitya import MITYA_COMBO_DICT, DD_TIME
from ...data.characters.odette import (odette_burst_buffs, ODETTE_BURST_TIME,
                                       ODETTE_COMBO_DICT, ODETTE_BURST_SOURCES)
from ...data.characters.danika import DANIKA_COMBO_DICT
from ...data.characters.valera import VALERA_COMBO_DICT
from ...data.weapons import *

TEAM_BUFFS: tuple = ()  # крио персонаж один — крио резонанса нет

#: Время каждого персонажа в ротации (секунды)
TIMES = {"Митя": DD_TIME, "Одетта": 2.4, "Даника": 3.25, "Валера": 3.5}

ROTATION = "Одетта EE/Даника EQ/Митя hE CA/Валера E CA Q/Митя CA Q CA"

MAIN_ATK = {S.ATK_PCT: 0.466 * 2, S.CRIT_VALUE: 0.622}       # АТК/АТК/крит
MAIN_EM = {S.BASE_EM: 187.0 * 2, S.CRIT_VALUE: 0.622}        # МС/МС/крит

#: Варианты артефактов Мити
MITYA_DISENCHANTMENT = (DISENCHANTMENT,)
ODETTE_ARTIFACTS = (HEART_OF_FORGE,)


def enemy() -> Enemy:
    return Enemy(res={"anemo": 0.10, "cryo": 0.10, "electro": 0.10},
                 def_mult=0.4875, elevation=0.0)


def mitya_build(constellation: int = 0, weapon=SPINDLELUTE, artifacts=MITYA_DISENCHANTMENT,
                main_stats=MAIN_EM, extra_buffs: Sequence[Buff] = ()) -> Build:
    return Build(
        character=MITYA_COMBO_DICT["dd_overload"],
        constellation=constellation,
        weapon=weapon,
        artifacts=artifacts,
        extra_stats=merge_dicts(main_stats, STANDART_SUBSTAT_PRESET_EM_SCALE),
        extra_buffs=tuple(extra_buffs),
        time=TIMES["Митя"],
    )


def odette_build(constellation: int = 0, weapon=SILVER_LIGHT, artifacts=ODETTE_ARTIFACTS,
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
        extra_stats=merge_dicts({S.ATK_PCT: 0.466 * 2, S.CRIT_VALUE: 0.622},
                                STANDART_SUBSTAT_PRESET),
        extra_sources=ODETTE_BURST_SOURCES if use_burst else (),
        extra_buffs=tuple(extra_buffs) + (odette_burst_buffs(constellation)
                                          if use_burst else ()),
        time=TIMES["Одетта"] + (ODETTE_BURST_TIME if use_burst else 0.0),
    )


def danika_build(constellation: int = 0, weapon=ATONEMENT, artifacts=(MILLELITH,),
                 main_stats={S.ATK_PCT: 0.466 * 3}, extra_buffs: Sequence[Buff] = ()) -> Build:
    return Build(
        character=DANIKA_COMBO_DICT["support_eq"],
        constellation=constellation,
        weapon=weapon,
        artifacts=artifacts,
        extra_stats=merge_dicts(main_stats, STANDART_SUBSTAT_FULL_ATK_PRESET),
        extra_buffs=tuple(extra_buffs),
        time=TIMES["Даника"],
    )


def valera_build(constellation: int = 6, weapon=FINALE, artifacts=(NOBLESSE,),
                 main_stats={S.ATK_PCT: 0.466 * 3},
                 extra_buffs: Sequence[Buff] = ()) -> Build:
    return Build(
        character=VALERA_COMBO_DICT["support_eq_ca"],
        constellation=constellation,
        weapon=weapon,
        artifacts=artifacts,
        extra_stats=merge_dicts(main_stats, STANDART_SUBSTAT_PRESET),
        extra_buffs=tuple(extra_buffs),
        time=TIMES["Валера"],
    )


def make_team(name: str,
              mitya_c: int = 0, mitya_weapon=SPINDLELUTE, mitya_artifacts=MITYA_DISENCHANTMENT,
              odette_c: int = 0, odette_weapon=SILVER_LIGHT, odette_artifacts=ODETTE_ARTIFACTS,
              danika_c: int = 0, danika_weapon=ATONEMENT, danika_artifacts=(MILLELITH,),
              valera_c: int = 6, valera_weapon=FINALE, valera_artifacts=(NOBLESSE,)) -> Team:
    return Team(
        name=name,
        builds=[
            mitya_build(mitya_c, mitya_weapon, mitya_artifacts),
            odette_build(odette_c, odette_weapon, odette_artifacts),
            danika_build(danika_c, danika_weapon, danika_artifacts),
            valera_build(valera_c, valera_weapon, valera_artifacts),
        ],
        enemy=enemy(),
        buffs=TEAM_BUFFS,
        rotation=ROTATION,
        config=Config(),
        dd="Митя",
    )


def team_name(mitya_c: int = 0, mitya_weapon=SPINDLELUTE, odette_c: int = 0, odette_weapon=SILVER_LIGHT, danika_c: int = 0, danika_weapon=ATONEMENT, valera_c: int = 6, valera_weapon=FINALE) -> str:
    return (f"C{mitya_c}R{mitya_weapon.refinement} Митя" + (f" ({mitya_weapon.name})" if mitya_weapon.name != SPINDLELUTE.name else "") + ", " + f"C{odette_c}R{odette_weapon.refinement} Одетта" + ", " + f"C{danika_c}R{danika_weapon.refinement} Даника" + ", " + f"C{valera_c}R{valera_weapon.refinement} Валера")


VARIANTS = ({},)

BASE_NAME = team_name()


def all_teams() -> Dict[str, Team]:
    out: Dict[str, Team] = {}
    for kw in VARIANTS:
        name = team_name(**{k: v for k, v in kw.items() if k in team_name.__code__.co_varnames})
        out[name] = make_team(name, **kw)
    return out
