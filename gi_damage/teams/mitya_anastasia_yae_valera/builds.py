"""
Отряд звёздного проводника: Митя (ДД, перегрузка) / Анастасия / Яэ Мико / C6 Валера.

Ротация: Анастасия EQ / Яэ EEE / Митя hE CA / Валера E CA Q / Митя CA Q CA.
Комбо Мити — MITYA_COMBO_DICT["dd_overload"]: удары после Валеры — в окне
Знати, первые 13 (C1+: 15) тратят стаки Offensive Directive.
Анастасия — единственный крио: часы на ВЭ вместо АТК (штраф по энергии),
главные статы АТК/ВЭ/крит. Крио резонанса нет.
Артефакты: Митя — Разочарование, Анастасия — Звёздный сет, Яэ — Разочарование,
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
from ...data.characters.anastasia import ANASTASIA_COMBO_DICT
from ...data.characters.yae import YAE_COMBO_DICT
from ...data.characters.valera import VALERA_COMBO_DICT
from ...data.weapons import *

TEAM_BUFFS: tuple = ()  # крио персонаж один — крио резонанса нет

#: Время каждого персонажа в ротации (секунды)
TIMES = {"Митя": DD_TIME, "Анастасия": 3.5, "Яэ Мико": 2.4, "Валера": 3.5}

ROTATION = "Анастасия EQ/Яэ EEE/Митя hE CA/Валера E CA Q/Митя CA Q CA"

MAIN_ATK = {S.ATK_PCT: 0.466 * 2, S.CRIT_VALUE: 0.622}       # АТК/АТК/крит
MAIN_EM = {S.BASE_EM: 187.0 * 2, S.CRIT_VALUE: 0.622}        # МС/МС/крит

#: Варианты артефактов Мити
MITYA_DISENCHANTMENT = (DISENCHANTMENT,)
ODETTE_ARTIFACTS = (HEART_OF_FORGE,)
#: Анастасия — единственный крио: часы на ВЭ (штраф по энергии) — АТК/ВЭ/крит
ANASTASIA_MAIN = {S.ATK_PCT: 0.466, S.CRIT_VALUE: 0.622}


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


def anastasia_build(constellation: int = 0, weapon=BREEZEBORNE_BOW.at(1), artifacts=(HEART_OF_FORGE,),
                    main_stats=ANASTASIA_MAIN, extra_buffs: Sequence[Buff] = ()) -> Build:
    return Build(
        character=ANASTASIA_COMBO_DICT["support_sc"],
        constellation=constellation,
        weapon=weapon,
        artifacts=artifacts,
        extra_stats=merge_dicts(main_stats, STANDART_SUBSTAT_PRESET),
        extra_buffs=tuple(extra_buffs),
        time=TIMES["Анастасия"],
    )


def yae_build(constellation: int = 1, weapon=ECHOES, artifacts=(DISENCHANTMENT,),
              main_stats=MAIN_ATK, extra_buffs: Sequence[Buff] = ()) -> Build:
    return Build(
        character=YAE_COMBO_DICT["yae_sc_short_combo"],
        constellation=constellation,
        weapon=weapon,
        artifacts=artifacts,
        extra_stats=merge_dicts(main_stats, STANDART_SUBSTAT_PRESET),
        extra_buffs=tuple(extra_buffs),
        time=TIMES["Яэ Мико"],
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
              anastasia_c: int = 0, anastasia_weapon=BREEZEBORNE_BOW.at(1), anastasia_artifacts=(HEART_OF_FORGE,),
              yae_c: int = 1, yae_weapon=ECHOES, yae_artifacts=(DISENCHANTMENT,),
              valera_c: int = 6, valera_weapon=FINALE, valera_artifacts=(NOBLESSE,)) -> Team:
    return Team(
        name=name,
        builds=[
            mitya_build(mitya_c, mitya_weapon, mitya_artifacts),
            anastasia_build(anastasia_c, anastasia_weapon, anastasia_artifacts),
            yae_build(yae_c, yae_weapon, yae_artifacts),
            valera_build(valera_c, valera_weapon, valera_artifacts),
        ],
        enemy=enemy(),
        buffs=TEAM_BUFFS,
        rotation=ROTATION,
        config=Config(),
        dd="Митя",
    )


def team_name(mitya_c: int = 0, mitya_weapon=SPINDLELUTE, anastasia_c: int = 0, anastasia_weapon=BREEZEBORNE_BOW.at(1), yae_c: int = 1, yae_weapon=ECHOES, valera_c: int = 6, valera_weapon=FINALE) -> str:
    return (f"C{mitya_c}R{mitya_weapon.refinement} Митя" + (f" ({mitya_weapon.name})" if mitya_weapon.name != SPINDLELUTE.name else "") + ", " + f"C{anastasia_c}R{anastasia_weapon.refinement} Анастасия" + ", " + f"C{yae_c}R{yae_weapon.refinement} Яэ Мико" + ", " + f"C{valera_c}R{valera_weapon.refinement} Валера")


VARIANTS = ({},)

BASE_NAME = team_name()


def all_teams() -> Dict[str, Team]:
    out: Dict[str, Team] = {}
    for kw in VARIANTS:
        name = team_name(**{k: v for k, v in kw.items() if k in team_name.__code__.co_varnames})
        out[name] = make_team(name, **kw)
    return out
