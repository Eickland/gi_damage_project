"""
Отряд звёздного проводника: Митя / Даника / Яэ Мико / Одетта.

Митя — ДД (перегрузка), без Валеры и Знати. Ротация: Одетта EE / Яэ EEE / Даника EQ / Митя hE CA Q CA CA (10.2 с).
Реакций, наносящих урон, нет. Резонанс — электро (3 электро + 1 крио),
бонуса урона нет — отрядных баффов нет.

Артефакты: Даника — Сердце горна (полная АТК: АТК/АТК/АТК +
STANDART_SUBSTAT_FULL_ATK_PRESET), Одетта и Яэ — Разочарование. Митя — лучший по DPS из 2+2 на МС и Разочарования (best_team()).

C2 Даники (если включить danika_c=2): стаки C2 — Митя 10, Яэ 7,
Одетта 7, Даника 7.
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
from ...data.characters.mitya import mitya_dd_rotation, DD_TIME
from ...data.characters.odette import (odette_burst_buffs, ODETTE_BURST_TIME,
                                       ODETTE_COMBO_DICT, ODETTE_BURST_SOURCES)
from ...data.characters.yae import YAE_COMBO_DICT
from ...data.characters.danika import (DANIKA_COMBO_DICT, C2_ACTIVE_STACKS,
                                       C2_OTHER_STACKS, tag_stellar_conduct_hits)
from ...data.weapons import *

#: Электро резонанс (3 электро) — без бонуса урона
TEAM_BUFFS: tuple = ()

#: Время каждого персонажа в ротации (секунды)
TIMES = {"Митя": DD_TIME, "Даника": 3.0, "Яэ Мико": 2.4, "Одетта": 2.4}

ROTATION = "Одетта EE/Яэ EEE/Даника EQ/Митя hE CA Q CA CA"

MAIN_ATK = {S.ATK_PCT: 0.466 * 2, S.CRIT_VALUE: 0.622}       # АТК/АТК/крит
MAIN_EM = {S.BASE_EM: 187.0 * 2, S.CRIT_VALUE: 0.622}        # МС/МС/крит
FULL_ATK = {S.ATK_PCT: 0.466 * 3}                            # АТК/АТК/АТК (Даника)

#: Варианты артефактов Мити
MITYA_EM_2_2 = (AUBADE.at(2), GILDED.at(2))      # 2+2 на МС: +160 МС
MITYA_DISENCHANTMENT = (DISENCHANTMENT,)
MITYA_ARTIFACT_OPTIONS = (MITYA_EM_2_2, MITYA_DISENCHANTMENT)

MITYA = mitya_dd_rotation(hit_tags=(ON,), hold_tags=(ON,))


def enemy() -> Enemy:
    return Enemy(res={"anemo": 0.10, "cryo": 0.10, "electro": 0.10},
                 def_mult=0.4875, elevation=0.0)


def _c2(build: Build, hits: int) -> Build:
    return tag_stellar_conduct_hits(build, DANIKA_C2, hits)


def mitya_build(constellation: int = 0, weapon=SPINDLELUTE, artifacts=MITYA_DISENCHANTMENT,
                main_stats=MAIN_EM, danika_c2_hits: int = 0,
                extra_buffs: Sequence[Buff] = ()) -> Build:
    return _c2(Build(
        character=MITYA,
        constellation=constellation,
        weapon=weapon,
        artifacts=artifacts,
        extra_stats=merge_dicts(main_stats, STANDART_SUBSTAT_PRESET_EM_SCALE),
        extra_buffs=tuple(extra_buffs),
        time=TIMES["Митя"],
    ), danika_c2_hits)


def danika_build(constellation: int = 0, weapon=ATONEMENT, artifacts=(HEART_OF_FORGE,),
                 main_stats=FULL_ATK, extra_buffs: Sequence[Buff] = ()) -> Build:
    return _c2(Build(
        character=DANIKA_COMBO_DICT["support_eq"],
        constellation=constellation,
        weapon=weapon,
        artifacts=artifacts,
        extra_stats=merge_dicts(main_stats, STANDART_SUBSTAT_FULL_ATK_PRESET),
        extra_buffs=tuple(extra_buffs),
        time=TIMES["Даника"],
    ), C2_OTHER_STACKS if constellation >= 2 else 0)


def yae_build(constellation: int = 1, weapon=ECHOES.at(5), artifacts=(DISENCHANTMENT,),
              main_stats=MAIN_ATK, danika_c2_hits: int = 0,
              extra_buffs: Sequence[Buff] = ()) -> Build:
    return _c2(Build(
        character=YAE_COMBO_DICT["yae_sc_short_combo"],
        constellation=constellation,
        weapon=weapon,
        artifacts=artifacts,
        extra_stats=merge_dicts(main_stats, STANDART_SUBSTAT_PRESET),
        extra_buffs=tuple(extra_buffs),
        time=TIMES["Яэ Мико"],
    ), danika_c2_hits)


def odette_build(constellation: int = 0, weapon=SILVER_LIGHT, artifacts=(DISENCHANTMENT,),
                 use_burst: bool | None = None, danika_c2_hits: int = 0,
                 extra_buffs: Sequence[Buff] = ()) -> Build:
    """use_burst=None — авто: до C4 не применяем, с C4 применяем."""
    if use_burst is None:
        use_burst = constellation >= 4
    return _c2(Build(
        character=ODETTE_COMBO_DICT["odette_ssc_combo"],
        constellation=constellation,
        weapon=weapon,
        artifacts=artifacts,
        extra_stats=merge_dicts(MAIN_ATK, STANDART_SUBSTAT_PRESET),
        extra_sources=ODETTE_BURST_SOURCES if use_burst else (),
        extra_buffs=tuple(extra_buffs) + (odette_burst_buffs(constellation)
                                          if use_burst else ()),
        time=TIMES["Одетта"] + (ODETTE_BURST_TIME if use_burst else 0.0),
    ), danika_c2_hits)


def make_team(name: str, mitya_c: int = 0, mitya_weapon=SPINDLELUTE,
              danika_c: int = 0, danika_weapon=ATONEMENT,
              yae_c: int = 1, yae_weapon=ECHOES.at(5),
              odette_c: int = 0, odette_weapon=SILVER_LIGHT,
              mitya_artifacts=MITYA_DISENCHANTMENT, danika_artifacts=(HEART_OF_FORGE,),
              yae_artifacts=(DISENCHANTMENT,), odette_artifacts=(DISENCHANTMENT,)) -> Team:
    c2 = danika_c >= 2
    return Team(
        name=name,
        builds=[
            mitya_build(mitya_c, mitya_weapon, mitya_artifacts,
                           danika_c2_hits=C2_ACTIVE_STACKS if c2 else 0),
            danika_build(danika_c, danika_weapon, danika_artifacts),
            yae_build(yae_c, yae_weapon, yae_artifacts,
                      danika_c2_hits=C2_OTHER_STACKS if c2 else 0),
            odette_build(odette_c, odette_weapon, odette_artifacts,
                         danika_c2_hits=C2_OTHER_STACKS if c2 else 0),
        ],
        enemy=enemy(),
        buffs=TEAM_BUFFS,
        rotation=ROTATION,
        config=Config(),
    )


def team_name(mitya_c: int = 0, mitya_weapon=SPINDLELUTE,
              danika_c: int = 0, danika_weapon=ATONEMENT,
              yae_c: int = 1, yae_weapon=ECHOES.at(5),
              odette_c: int = 0, odette_weapon=SILVER_LIGHT) -> str:
    _dw = (f" ({danika_weapon.name})" if danika_weapon.name != ATONEMENT.name else "")
    return (f"C{mitya_c}R{mitya_weapon.refinement} Митя, "
            f"C{danika_c}R{danika_weapon.refinement} Даника{_dw}, "
            f"C{yae_c}R{yae_weapon.refinement} Яэ, "
            f"C{odette_c}R{odette_weapon.refinement} Одетта")


#: Вариации: C0 / C1 / C2 Даники
VARIANTS = ({"danika_c": 0}, {"danika_c": 1}, {"danika_c": 2},
            {"danika_c": 0, "danika_weapon": SPRING_TIDE},  # Даника с сигной (Весенний прилив R1)
)

BASE_NAME = team_name()

def _set_label(artifacts) -> str:
    return "2+2 МС" if len(artifacts) > 1 else artifacts[0].name


def best_team(name: str, **kw) -> Team:
    """Артефакты Мити — лучший по DPS вариант из MITYA_ARTIFACT_OPTIONS."""
    best = None
    for arts in MITYA_ARTIFACT_OPTIONS:
        team = make_team(f"{name} [Митя: {_set_label(arts)}]", mitya_artifacts=arts, **kw)
        dps = team.compute().dps
        if best is None or dps > best[0]:
            best = (dps, team)
    return best[1]  # type: ignore


def all_teams() -> Dict[str, Team]:
    out: Dict[str, Team] = {}
    for kw in VARIANTS:
        team = best_team(team_name(**kw), **kw)
        out[team.name] = team
    return out

