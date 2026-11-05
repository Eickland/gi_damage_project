"""
Отряд звёздного проводника: Сандроне / Анастасия / Даника / C6 Алеша.

Ротация: Алеша EQ / Даника EQ / Анастасия EQ / Сандроне E CA EQ CA E CA E.
Реакций, наносящих урон, нет. Резонанс — крио (2 крио + 2 электро).

Анастасия — саппорт (Милосердие): корона 10 атак вне поля, Triumph.
An Unfinished Requiem: +1 стак Polestar всем ударам SC отряда (polar_shift()).

Артефакты: Анастасия — Звёздный сет, Даника — Сердце горна, Алеша — Знать,
Сандроне — Разочарование.
Знать (окно NOBLE, 12 с после взрыва Алеши): у Сандроне окно размечено в её
комбо; все удары Даники, удары Анастасии на поле и первые 4 атаки короны —
в окне.

C2 Даники (если включить danika_c=2): стаки C2 — Сандроне 10, Анастасия 7,
Даника 7. У Алеши ударов SC нет.
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
from ...data.characters.alyosha import ALYOSHA_COMBO_DICT
from ...data.characters.danika import (DANIKA_COMBO_DICT, C2_ACTIVE_STACKS,
                                       C2_OTHER_STACKS, tag_stellar_conduct_hits)
from ...data.characters.anastasia import anastasia_support, polar_shift, CROWN_HITS
from ...data.weapons import *

TEAM_BUFFS = (
    Buff(S.CRIT_VALUE, 0.30, target=TEAM,
         source="Крио резонанс: +15% крит. шанса (0.30 крит-вэлью)"),
)

#: Время каждого персонажа в ротации (секунды)
TIMES = {"Сандроне": 14.5, "Алеша": 1.9, "Даника": 3.0, "Анастасия": 3.0}

ROTATION = "Алеша EQ/Даника EQ/Анастасия EQ/Сандроне E CA EQ CA E CA E"

MAIN_ATK = {S.ATK_PCT: 0.466 * 2, S.CRIT_VALUE: 0.622}       # АТК/АТК/крит
FULL_ATK = {S.ATK_PCT: 0.466 * 3}                            # АТК/АТК/АТК (Даника)

#: Комбо с +1 стаком Polestar (Requiem Анастасии)
SANDRONE = polar_shift(SANDRONE_COMBO_DICT["sandrone_sc_combo"])

DANIKA = polar_shift(DANIKA_COMBO_DICT["support_eq_noble"])
#: Атаки короны в окне Знати Алеши
CROWN_IN_NOBLE = 4
ANASTASIA = polar_shift(anastasia_support(
    "sc", [occ(CROWN_IN_NOBLE, OFF, NOBLE), occ(CROWN_HITS - CROWN_IN_NOBLE, OFF)],
    on_tags=(ON, NOBLE)))


def enemy() -> Enemy:
    return Enemy(res={"anemo": 0.10, "cryo": 0.10, "electro": 0.10},
                 def_mult=0.4875, elevation=0.0)


def _c2(build: Build, hits: int) -> Build:
    return tag_stellar_conduct_hits(build, DANIKA_C2, hits)


def sandrone_build(constellation: int = 0, weapon=ATONEMENT, artifacts=(DISENCHANTMENT,),
                   main_stats=MAIN_ATK, danika_c2_hits: int = 0,
                   extra_buffs: Sequence[Buff] = ()) -> Build:
    return _c2(Build(
        character=SANDRONE,
        constellation=constellation,
        weapon=weapon,
        artifacts=artifacts,
        extra_stats=merge_dicts(main_stats, STANDART_SUBSTAT_PRESET),
        extra_buffs=tuple(extra_buffs),
        time=TIMES["Сандроне"],
    ), danika_c2_hits)


def anastasia_build(constellation: int = 0, weapon=ARTEMISIA, artifacts=(STELLAR_SET,),
                    main_stats=MAIN_ATK, danika_c2_hits: int = 0,
                    extra_buffs: Sequence[Buff] = ()) -> Build:
    return _c2(Build(
        character=ANASTASIA,
        constellation=constellation,
        weapon=weapon,
        artifacts=artifacts,
        extra_stats=merge_dicts(main_stats, STANDART_SUBSTAT_PRESET),
        extra_buffs=tuple(extra_buffs),
        time=TIMES["Анастасия"],
    ), danika_c2_hits)


def danika_build(constellation: int = 0, weapon=ATONEMENT, artifacts=(HEART_OF_FORGE,),
                 main_stats=FULL_ATK, extra_buffs: Sequence[Buff] = ()) -> Build:
    return _c2(Build(
        character=DANIKA,
        constellation=constellation,
        weapon=weapon,
        artifacts=artifacts,
        extra_stats=merge_dicts(main_stats, STANDART_SUBSTAT_FULL_ATK_PRESET),
        extra_buffs=tuple(extra_buffs),
        time=TIMES["Даника"],
    ), C2_OTHER_STACKS if constellation >= 2 else 0)


def alyosha_build(constellation: int = 6, weapon=FAV_LANCE, artifacts=(NOBLESSE,),
                  extra_buffs: Sequence[Buff] = ()) -> Build:
    return Build(
        character=ALYOSHA_COMBO_DICT["sc_combo"],
        constellation=constellation,
        weapon=weapon,
        artifacts=artifacts,
        extra_stats=merge_dicts(
            {S.ATK_PCT: 0.466 * 1, S.CRIT_VALUE: 0.622},
            STANDART_SUBSTAT_PRESET),
        extra_buffs=tuple(extra_buffs),
        time=TIMES["Алеша"],
    )


def make_team(name: str, sandrone_c: int = 0, sandrone_weapon=ATONEMENT,
              anastasia_c: int = 0, anastasia_weapon=ARTEMISIA,
              danika_c: int = 0, danika_weapon=ATONEMENT,
              alyosha_c: int = 6, alyosha_weapon=FAV_LANCE,
              sandrone_artifacts=(DISENCHANTMENT,), anastasia_artifacts=(STELLAR_SET,),
              danika_artifacts=(HEART_OF_FORGE,), alyosha_artifacts=(NOBLESSE,)) -> Team:
    c2 = danika_c >= 2
    return Team(
        name=name,
        builds=[
            sandrone_build(sandrone_c, sandrone_weapon, sandrone_artifacts,
                           danika_c2_hits=C2_ACTIVE_STACKS if c2 else 0),
            anastasia_build(anastasia_c, anastasia_weapon, anastasia_artifacts,
                            danika_c2_hits=C2_OTHER_STACKS if c2 else 0),
            danika_build(danika_c, danika_weapon, danika_artifacts),
            alyosha_build(alyosha_c, alyosha_weapon, alyosha_artifacts),
        ],
        enemy=enemy(),
        buffs=TEAM_BUFFS,
        rotation=ROTATION,
        config=Config(),
    )


def team_name(sandrone_c: int = 0, sandrone_weapon=ATONEMENT,
              anastasia_c: int = 0, anastasia_weapon=ARTEMISIA,
              danika_c: int = 0, danika_weapon=ATONEMENT,
              alyosha_c: int = 6, alyosha_weapon=FAV_LANCE) -> str:
    _dw = (f" ({danika_weapon.name})" if danika_weapon.name != ATONEMENT.name else "")
    return (f"C{sandrone_c}R{sandrone_weapon.refinement} Сандроне, "
            f"C{anastasia_c}R{anastasia_weapon.refinement} Анастасия, "
            f"C{danika_c}R{danika_weapon.refinement} Даника{_dw}, "
            f"C{alyosha_c}R{alyosha_weapon.refinement} Алеша")


VARIANTS = ({},
            {"danika_c": 0, "danika_weapon": SPRING_TIDE},  # Даника с сигной (Весенний прилив R1)
)

BASE_NAME = team_name()


def all_teams() -> Dict[str, Team]:
    out: Dict[str, Team] = {}
    for kw in VARIANTS:
        name = team_name(**kw)
        out[name] = make_team(name, **kw)
    return out
