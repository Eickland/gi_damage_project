"""
Отряд звёздного проводника: Митя (ДД, перегрузка) / Одетта / Яэ Мико / Валера.

Ротация: Одетта EE / Яэ EEE / Митя hE CA / Валера E CA Q / Митя CA Q CA.
Реакций, наносящих урон, нет. Резонанс — электро (без бонуса урона).

Митя тратит стаки Offensive Directive Валеры: 13 на C0, 15 на C1+.
Артефакты Мити — лучший из двух вариантов: 2+2 на МС или 4 Разочарование
(выбирается автоматически по DPS для каждой вариации, см. best_team()).
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
from ...data.characters.odette import (odette_burst_buffs, ODETTE_BURST_TIME,
                                       ODETTE_COMBO_DICT, ODETTE_BURST_SOURCES)
from ...data.characters.yae import YAE_COMBO_DICT
from ...data.characters.valera import VALERA_COMBO_DICT
from ...data.characters.mitya import MITYA_COMBO_DICT, DD_TIME
from ...data.weapons import *

TEAM_BUFFS: tuple = ()

#: Время каждого персонажа в ротации (секунды)
TIMES = {"Митя": DD_TIME, "Валера": 3.5, "Одетта": 2.4, "Яэ Мико": 2.4}

ROTATION = "Одетта EE/Яэ EEE/Митя hE CA/Валера E CA Q/Митя CA Q CA"

#: Главные статы: пески/кубок/корона
MAIN_ATK = {S.ATK_PCT: 0.466 * 2, S.CRIT_VALUE: 0.622}                    # АТК/АТК/крит
MAIN_EM = {S.BASE_EM: 187.0 * 2, S.CRIT_VALUE: 0.622}                     # МС/МС/крит
MAIN_EM_ELECTRO = {S.BASE_EM: 187.0, "dmg_bonus.electro": 0.466,
                   S.CRIT_VALUE: 0.622}                                   # МС/электро/крит

MITYA_MAIN = MAIN_EM
YAE_MAIN = MAIN_ATK

#: Варианты артефактов Мити
MITYA_EM_2_2 = (AUBADE.at(2), GILDED.at(2))      # 2+2 на МС: +160 МС
MITYA_DISENCHANTMENT = (DISENCHANTMENT,)
MITYA_ARTIFACT_OPTIONS = (MITYA_EM_2_2, MITYA_DISENCHANTMENT)


def enemy() -> Enemy:
    return Enemy(res={"anemo": 0.10, "cryo": 0.10, "electro": 0.10},
                 def_mult=0.4875, elevation=0.0)


def mitya_build(constellation: int = 0, weapon=SPINDLELUTE, artifacts=MITYA_DISENCHANTMENT,
                main_stats=MITYA_MAIN, extra_buffs: Sequence[Buff] = ()) -> Build:
    return Build(
        character=MITYA_COMBO_DICT["dd_overload_valera"],
        constellation=constellation,
        weapon=weapon,
        artifacts=artifacts,
        extra_stats=merge_dicts(main_stats, STANDART_SUBSTAT_PRESET_EM_SCALE),
        extra_buffs=tuple(extra_buffs),
        time=TIMES["Митя"],
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


def yae_build(constellation: int = 1, weapon=ECHOES,
              artifacts=(DISENCHANTMENT,), main_stats=YAE_MAIN,
              extra_buffs: Sequence[Buff] = ()) -> Build:
    return Build(
        character=YAE_COMBO_DICT["yae_sc_short_combo"],
        constellation=constellation,
        weapon=weapon,
        artifacts=artifacts,
        extra_stats=merge_dicts(main_stats, STANDART_SUBSTAT_PRESET),
        extra_buffs=tuple(extra_buffs),
        time=TIMES["Яэ Мико"],
    )


def valera_build(constellation: int = 0, weapon=FINALE, artifacts=(NOBLESSE,),
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


def make_team(name: str, mitya_c: int = 0, mitya_weapon=SPINDLELUTE,
              odette_c: int = 0, odette_weapon=SILVER_LIGHT,
              yae_c: int = 1, yae_weapon=ECHOES,
              valera_c: int = 6, valera_weapon=FINALE,
              mitya_artifacts=MITYA_DISENCHANTMENT, odette_artifacts=(HEART_OF_FORGE,),
              yae_artifacts=(DISENCHANTMENT,), valera_artifacts=(NOBLESSE,),
              mitya_main_stats=MITYA_MAIN, yae_main_stats=YAE_MAIN) -> Team:
    return Team(
        name=name,
        builds=[
            mitya_build(mitya_c, mitya_weapon, mitya_artifacts, mitya_main_stats),
            odette_build(odette_c, odette_weapon, odette_artifacts),
            yae_build(yae_c, yae_weapon, yae_artifacts, yae_main_stats),
            valera_build(valera_c, valera_weapon, valera_artifacts),
        ],
        enemy=enemy(),
        buffs=TEAM_BUFFS,
        rotation=ROTATION,
        config=Config(),
    )


def _set_label(artifacts) -> str:
    return "2+2 МС" if len(artifacts) > 1 else artifacts[0].name


def best_team(name: str, **kw) -> Team:
    """Тот же отряд, но артефакты Мити — лучший по DPS вариант из
    MITYA_ARTIFACT_OPTIONS. Выбранный набор дописывается в имя отряда."""
    best = None
    for arts in MITYA_ARTIFACT_OPTIONS:
        team = make_team(f"{name} [Митя: {_set_label(arts)}]", mitya_artifacts=arts, **kw)
        dps = team.compute().dps
        if best is None or dps > best[0]:
            best = (dps, team)
    return best[1] # type: ignore


def team_name(mitya_c: int = 0, mitya_weapon=SPINDLELUTE, valera_c: int = 6,
              odette_c: int = 0, yae_c: int = 1) -> str:
    return (f"C{mitya_c} Митя ({mitya_weapon.name} R{mitya_weapon.refinement}), "
            f"C{odette_c} Одетта, C{yae_c} Яэ, C{valera_c} Валера")


#: Вариации: базовая, C2/C6 Валера, сигна Мити, C1/C2 Мити
VARIANTS = (
    {},
    {"valera_c": 2},
    {"valera_c": 6},
    {"mitya_weapon": STARSEALED},
    {"mitya_c": 1},
    {"mitya_c": 2},
)

BASE_NAME = team_name()


def all_teams() -> Dict[str, Team]:
    out: Dict[str, Team] = {}
    for kw in VARIANTS:
        team = best_team(team_name(**kw), **kw) # type: ignore
        out[team.name] = team
    return out
