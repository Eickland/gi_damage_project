"""
Отряд звёздного проводника: Анастасия (ДД, Слава) / Сахароза / Алеша / Диона.

Ротация: Алеша EQ / Диона EQ / Сахароза EQ / Анастасия hEQ (N5 sE)×3.
Комбо Анастасии: hEQ (N5 sE)×3 — 3.1 + 3 × (2.8 + 1.5) = 16 с;
короткое (short=True): hEQ N5sE N5sE sE — 13.2 с, без третьей N5.
Реакций, наносящих урон, нет. Резонанс — крио.

Окна баффов на отрезках комбо Анастасии [hEQ, N5 sE, N5 sE, N5 sE]:
    МС Сахарозы (A4, +50 МС) и её Эпос — hEQ, N5 sE;
    Изумрудная тень (−40% крио) — hEQ, N5 sE, N5 sE;
    C6 Дионы (+200 МС, +40% урона звёздных реакций) — hEQ, N5 sE, N5 sE.
An Unfinished Requiem: +1 стак Polestar всем ударам SC отряда (polar_shift());
у ударов Анастасии итого 8 стаков.

Артефакты: Анастасия — Звёздный сет, Сахароза — Изумрудная тень (Эпос R5), Алеша — Сердце горна, Диона — Миллелит.
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
from ...data.characters.danika import C2_ACTIVE_STACKS, C2_OTHER_STACKS, tag_stellar_conduct_hits
from ...data.characters.anastasia import anastasia_dd, polar_shift, DD_TIME, DD_TIME_SHORT, DD_POLAR_STACKS_SUCROSE
from ...data.characters.sucrose import SUCROSE_COMBO_DICT
from ...data.characters.alyosha import ALYOSHA_COMBO_DICT
from ...data.characters.diona import DIONA_COMBO_DICT
from ...data.weapons import *

TEAM_BUFFS = (
    Buff(S.CRIT_VALUE, 0.30, target=TEAM,
         source="Крио резонанс: +15% крит. шанса (0.30 крит-вэлью)"),
)

#: Время каждого персонажа в ротации (секунды)
TIMES = {"Анастасия": DD_TIME, "Сахароза": 2.95, "Алеша": 1.9, "Диона": 2.2}

ROTATION = "Алеша EQ/Диона EQ/Сахароза EQ/Анастасия hEQ (N5 sE)×3"
ROTATION_SHORT = ROTATION.replace("hEQ (N5 sE)×3", "hEQ N5sE N5sE sE")

MAIN_ATK = {S.ATK_PCT: 0.466 * 2, S.CRIT_VALUE: 0.622}       # АТК/АТК/крит
MAIN_EM = {S.BASE_EM: 187.0 * 2, S.CRIT_VALUE: 0.622}        # МС/МС/крит
FULL_ATK = {S.ATK_PCT: 0.466 * 3}                            # АТК/АТК/АТК (Даника)

#: Теги отрезков комбо Анастасии: hEQ, N5 sE №1, №2, №3
SEG_TAGS = ((ON, INST, SUCROSE_PASSIVE, TTDS_FULL, VV_CRYO, CATS_TAIL), (ON, INST, SUCROSE_PASSIVE, TTDS_FULL, VV_CRYO, CATS_TAIL), (ON, VV_CRYO, CATS_TAIL), (ON,))

#: Комбо с +1 стаком Polestar (Requiem Анастасии): полное и короткое
ANASTASIA = polar_shift(anastasia_dd("sc", SEG_TAGS, polar_stacks=DD_POLAR_STACKS_SUCROSE - 1))
ANASTASIA_SHORT = polar_shift(anastasia_dd("sc", SEG_TAGS, polar_stacks=DD_POLAR_STACKS_SUCROSE - 1, n5=2))
SUCROSE = SUCROSE_COMBO_DICT["cryo_burst_combo"]
ALYOSHA = ALYOSHA_COMBO_DICT["sc_combo"]
DIONA = DIONA_COMBO_DICT["off_field"]


def enemy() -> Enemy:
    return Enemy(res={"anemo": 0.10, "cryo": 0.10, "electro": 0.10},
                 def_mult=0.4875, elevation=0.0)


def _c2(build: Build, hits: int) -> Build:
    return tag_stellar_conduct_hits(build, DANIKA_C2, hits)


def anastasia_build(constellation: int = 0, weapon=ARTEMISIA, artifacts=(STELLAR_SET,),
                    main_stats=MAIN_ATK, danika_c2_hits: int = 0, short: bool = False,
                    extra_buffs: Sequence[Buff] = ()) -> Build:
    """short=True — короткое комбо hEQ N5sE N5sE sE (13.2 с)."""
    return _c2(Build(
        character=ANASTASIA_SHORT if short else ANASTASIA,
        constellation=constellation,
        weapon=weapon,
        artifacts=artifacts,
        extra_stats=merge_dicts(main_stats, STANDART_SUBSTAT_PRESET),
        extra_buffs=tuple(extra_buffs),
        time=DD_TIME_SHORT if short else TIMES["Анастасия"],
    ), danika_c2_hits)

def sucrose_build(constellation: int = 6, weapon=TTDS_FULL_CATALYSATOR, artifacts=(VIRIDESCENT,),
                  main_stats={S.BASE_EM: 187 * 3},
                  extra_buffs: Sequence[Buff] = ()) -> Build:
    return Build(
        character=SUCROSE,
        constellation=constellation,
        weapon=weapon,
        artifacts=artifacts,
        extra_stats=merge_dicts(main_stats, STANDART_SUBSTAT_PRESET),
        extra_buffs=tuple(extra_buffs),
        time=TIMES["Сахароза"],
    )


def alyosha_build(constellation: int = 6, weapon=FAV_LANCE, artifacts=(HEART_OF_FORGE,),
                  main_stats={S.ATK_PCT: 0.466 * 1, S.CRIT_VALUE: 0.622},
                  extra_buffs: Sequence[Buff] = ()) -> Build:
    return Build(
        character=ALYOSHA,
        constellation=constellation,
        weapon=weapon,
        artifacts=artifacts,
        extra_stats=merge_dicts(main_stats, STANDART_SUBSTAT_PRESET),
        extra_buffs=tuple(extra_buffs),
        time=TIMES["Алеша"],
    )


def diona_build(constellation: int = 6, weapon=FAV_BOW.at(5), artifacts=(MILLELITH,),
                main_stats={S.ATK_PCT: 0.466 * 1, S.CRIT_VALUE: 0.622},
                extra_buffs: Sequence[Buff] = ()) -> Build:
    return Build(
        character=DIONA,
        constellation=constellation,
        weapon=weapon,
        artifacts=artifacts,
        extra_stats=merge_dicts(main_stats, STANDART_SUBSTAT_PRESET),
        extra_buffs=tuple(extra_buffs),
        time=TIMES["Диона"],
    )


def make_team(name: str, anastasia_c: int = 1, anastasia_weapon=ARTEMISIA,
              anastasia_artifacts=(STELLAR_SET,), short: bool = False,
              sucrose_c: int = 6, sucrose_weapon=TTDS_FULL_CATALYSATOR, sucrose_artifacts=(VIRIDESCENT,),
              alyosha_c: int = 6, alyosha_weapon=FAV_LANCE, alyosha_artifacts=(HEART_OF_FORGE,),
              diona_c: int = 6, diona_weapon=FAV_BOW.at(5), diona_artifacts=(MILLELITH,)) -> Team:
    c2 = False
    return Team(
        name=name,
        builds=[
            anastasia_build(anastasia_c, anastasia_weapon, anastasia_artifacts,
                            danika_c2_hits=C2_ACTIVE_STACKS if c2 else 0, short=short),
            sucrose_build(sucrose_c, sucrose_weapon, sucrose_artifacts),
            alyosha_build(alyosha_c, alyosha_weapon, alyosha_artifacts),
            diona_build(diona_c, diona_weapon, diona_artifacts),
        ],
        enemy=enemy(),
        buffs=TEAM_BUFFS,
        rotation=ROTATION_SHORT if short else ROTATION,
        config=Config(),
    )


def team_name(anastasia_c: int = 1, anastasia_weapon=ARTEMISIA, short: bool = False,
              sucrose_c: int = 6, sucrose_weapon=TTDS_FULL_CATALYSATOR,
              alyosha_c: int = 6, alyosha_weapon=FAV_LANCE,
              diona_c: int = 6, diona_weapon=FAV_BOW.at(5)) -> str:
    combo = "короткое" if short else "полное"
    if anastasia_weapon.name != ARTEMISIA.name:
        combo += f", {anastasia_weapon.name}"
    return (f"C{anastasia_c}R{anastasia_weapon.refinement} Анастасия (ДД, {combo}), "
            + f"C{sucrose_c}R{sucrose_weapon.refinement} Сахароза" + ", "
            + f"C{alyosha_c}R{alyosha_weapon.refinement} Алеша" + ", "
            + f"C{diona_c}R{diona_weapon.refinement} Диона")


VARIANTS = ({}, {"short": True},
            {"anastasia_weapon": SILVER_RADIANCE})  # сигна Анастасии

BASE_NAME = team_name()


def all_teams() -> Dict[str, Team]:
    out: Dict[str, Team] = {}
    for kw in VARIANTS:
        name = team_name(**kw)
        out[name] = make_team(name, **kw)
    return out
