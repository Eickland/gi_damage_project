"""
Отряд звёздного проводника: Митя (ДД, перегрузка) / Анастасия / Яэ Мико / Одетта.

Ротация: Одетта EE / Яэ EEE / Анастасия EQ / Митя hE CA Q CA CA (10.2 с).
Реакций, наносящих урон, нет. Резонанс — крио (2 крио + 2 электро).

Анастасия — саппорт (Милосердие): корона 10 атак вне поля, Triumph.
An Unfinished Requiem: +1 стак Polestar всем ударам SC отряда (polar_shift()).

Артефакты: Анастасия — Звёздный сет, Одетта — Сердце горна, Яэ —
Разочарование. Митя — лучший по DPS из 2+2 на МС и Разочарования
(выбирается автоматически, см. best_team()).
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
from ...data.characters.mitya import mitya_dd_rotation, DD_TIME
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
TIMES = {"Митя": DD_TIME, "Анастасия": 3.0, "Яэ Мико": 2.4, "Одетта": 2.4}

ROTATION = "Одетта EE/Яэ EEE/Анастасия EQ/Митя hE CA Q CA CA"

MAIN_ATK = {S.ATK_PCT: 0.466 * 2, S.CRIT_VALUE: 0.622}       # АТК/АТК/крит
MAIN_EM = {S.BASE_EM: 187.0 * 2, S.CRIT_VALUE: 0.622}        # МС/МС/крит (Митя)
FULL_ATK = {S.ATK_PCT: 0.466 * 3}
#: Варианты артефактов Мити
MITYA_EM_2_2 = (AUBADE.at(2), GILDED.at(2))      # 2+2 на МС: +160 МС
MITYA_DISENCHANTMENT = (DISENCHANTMENT,)
MITYA_ARTIFACT_OPTIONS = (MITYA_EM_2_2, MITYA_DISENCHANTMENT)

#: Комбо с +1 стаком Polestar (Requiem Анастасии). Митя без Валеры и Знати.
MITYA = polar_shift(mitya_dd_rotation(hit_tags=(ON,), hold_tags=(ON,)))
ODETTE = polar_shift(ODETTE_COMBO_DICT["odette_ssc_combo"])
YAE = polar_shift(YAE_COMBO_DICT["yae_sc_short_combo"])
ANASTASIA = polar_shift(anastasia_support("sc", [occ(CROWN_HITS, OFF)]))


def enemy() -> Enemy:
    return Enemy(res={"anemo": 0.10, "cryo": 0.10, "electro": 0.10},
                 def_mult=0.4875, elevation=0.0)


def mitya_build(constellation: int = 0, weapon=SPINDLELUTE, artifacts=MITYA_DISENCHANTMENT,
                main_stats=MAIN_EM,
                extra_buffs: Sequence[Buff] = ()) -> Build:
    return Build(
        character=MITYA,
        constellation=constellation,
        weapon=weapon,
        artifacts=artifacts,
        extra_stats=merge_dicts(main_stats, STANDART_SUBSTAT_PRESET_EM_SCALE),
        extra_buffs=tuple(extra_buffs),
        time=TIMES["Митя"],
    )


def anastasia_build(constellation: int = 0, weapon=ARTEMISIA, artifacts=(STELLAR_SET,),
                    main_stats=MAIN_ATK,
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


def yae_build(constellation: int = 1, weapon=ECHOES.at(5), artifacts=(DISENCHANTMENT,),
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


def make_team(name: str, mitya_c: int = 0, mitya_weapon=SPINDLELUTE,
              anastasia_c: int = 0, anastasia_weapon=ARTEMISIA,
              yae_c: int = 1, yae_weapon=ECHOES.at(5),
              odette_c: int = 0, odette_weapon=SILVER_LIGHT,
              mitya_artifacts=MITYA_DISENCHANTMENT, anastasia_artifacts=(STELLAR_SET,),
              yae_artifacts=(DISENCHANTMENT,), odette_artifacts=(HEART_OF_FORGE,)) -> Team:
    return Team(
        name=name,
        builds=[
            mitya_build(mitya_c, mitya_weapon, mitya_artifacts),
            anastasia_build(anastasia_c, anastasia_weapon, anastasia_artifacts),
            yae_build(yae_c, yae_weapon, yae_artifacts),
            odette_build(odette_c, odette_weapon, odette_artifacts),
        ],
        enemy=enemy(),
        buffs=TEAM_BUFFS,
        rotation=ROTATION,
        config=Config(),
    )


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


def team_name(mitya_c: int = 0, mitya_weapon=SPINDLELUTE,
              anastasia_c: int = 0, anastasia_weapon=ARTEMISIA,
              yae_c: int = 1, yae_weapon=ECHOES.at(5),
              odette_c: int = 0, odette_weapon=SILVER_LIGHT) -> str:
    return (f"C{mitya_c}R{mitya_weapon.refinement} Митя, "
            f"C{anastasia_c}R{anastasia_weapon.refinement} Анастасия, "
            f"C{yae_c}R{yae_weapon.refinement} Яэ, "
            f"C{odette_c}R{odette_weapon.refinement} Одетта")


VARIANTS = ({},)

BASE_NAME = team_name()


def all_teams() -> Dict[str, Team]:
    out: Dict[str, Team] = {}
    for kw in VARIANTS:
        team = best_team(team_name(**kw), **kw)
        out[team.name] = team
    return out
