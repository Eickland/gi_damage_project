"""
Отряд звёздного проводника: Анастасия (ДД, Слава) / Ци Ци / Сахароза / C6 Алеша.

Ротация: Алеша EQ / Ци Ци E / Сахароза EQ / Анастасия hEQ N5sE N5sE sE
(короткое комбо, 13.2 с). Реакций, наносящих урон, нет. Резонанс — крио.

Окна баффов на отрезках комбо Анастасии — ANASTASIA_COMBO_DICT["dd_sc_sucrose_qiqi"]:
Сахароза (Инструктор, A1/A4, Эпос) — hEQ и первая N5 sE; Изумрудная тень и
Ци Ци — до третьей. Бафф Ци Ци — только звёздное рассеивание, на проводник
Анастасии не влияет.
Артефакты: Анастасия — Разочарование, Ци Ци — Миллелит, Сахароза — Изумрудная
тень (Эпос R5), Алеша — Сердце горна.
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
from ...data.characters.anastasia import ANASTASIA_COMBO_DICT, DD_TIME, DD_TIME_SHORT
from ...data.characters.qiqi import QIQI_COMBO_DICT
from ...data.characters.sucrose import SUCROSE_COMBO_DICT
from ...data.characters.alyosha import ALYOSHA_COMBO_DICT
from ...data.weapons import *

TEAM_BUFFS = (
    Buff(S.CRIT_VALUE, 0.30, target=TEAM,
         source="Крио резонанс: +15% крит. шанса (0.30 крит-вэлью)"),
)

#: Время каждого персонажа в ротации (секунды)
TIMES = {"Анастасия": DD_TIME, "Ци Ци": 1.5, "Сахароза": 1.6, "Алеша": 1.9}

ROTATION = "Алеша EQ/Ци Ци E/Сахароза EQ/Анастасия hEQ (N5 sE)×3"
ROTATION_SHORT = "Алеша EQ/Ци Ци E/Сахароза EQ/Анастасия hEQ N5sE N5sE sE"

MAIN_ATK = {S.ATK_PCT: 0.466 * 2, S.CRIT_VALUE: 0.622}       # АТК/АТК/крит
MAIN_EM = {S.BASE_EM: 187.0 * 2, S.CRIT_VALUE: 0.622}        # МС/МС/крит

#: Комбо Анастасии-ДД: теги отрезков — ANASTASIA_COMBO_DICT["dd_sc_sucrose_qiqi"] (anastasia.py)
ANASTASIA = ANASTASIA_COMBO_DICT["dd_sc_sucrose_qiqi"]
ANASTASIA_SHORT = ANASTASIA_COMBO_DICT["dd_sc_sucrose_qiqi_short"]
SHORT_DEFAULT = True
ODETTE_ARTIFACTS = (DISENCHANTMENT,)


def enemy() -> Enemy:
    return Enemy(res={"anemo": 0.10, "cryo": 0.10, "electro": 0.10},
                 def_mult=0.4875, elevation=0.0)


def anastasia_build(constellation: int = 1, weapon=ARTEMISIA, artifacts=(DISENCHANTMENT,),
                    main_stats=MAIN_ATK, short: bool = SHORT_DEFAULT,
                    extra_buffs: Sequence[Buff] = ()) -> Build:
    """short=True — короткое комбо hEQ N5sE N5sE sE (13.2 с)."""
    return Build(
        character=ANASTASIA_SHORT if short else ANASTASIA,
        constellation=constellation,
        weapon=weapon,
        artifacts=artifacts,
        extra_stats=merge_dicts(main_stats, STANDART_SUBSTAT_PRESET),
        extra_buffs=tuple(extra_buffs),
        time=DD_TIME_SHORT if short else DD_TIME,
    )


def qiqi_build(constellation: int = 0, weapon=FAV_SWORD, artifacts=(MILLELITH,),
               main_stats={S.ATK_PCT: 0.466 * 1, S.CRIT_VALUE: 0.622},
               extra_buffs: Sequence[Buff] = ()) -> Build:
    return Build(
        character=QIQI_COMBO_DICT["off_field"],
        constellation=constellation,
        weapon=weapon,
        artifacts=artifacts,
        extra_stats=merge_dicts(main_stats, STANDART_SUBSTAT_PRESET),
        extra_buffs=tuple(extra_buffs),
        time=TIMES["Ци Ци"],
    )


def sucrose_build(constellation: int = 6, weapon=TTDS_FULL_CATALYSATOR, artifacts=(VIRIDESCENT,),
                  main_stats={S.BASE_EM: 187 * 3},
                  extra_buffs: Sequence[Buff] = ()) -> Build:
    return Build(
        character=SUCROSE_COMBO_DICT["cryo_burst_combo"],
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
        character=ALYOSHA_COMBO_DICT["sc_combo"],
        constellation=constellation,
        weapon=weapon,
        artifacts=artifacts,
        extra_stats=merge_dicts(main_stats, STANDART_SUBSTAT_PRESET),
        extra_buffs=tuple(extra_buffs),
        time=TIMES["Алеша"],
    )


def make_team(name: str, short: bool = SHORT_DEFAULT,
              anastasia_c: int = 0, anastasia_weapon=ARTEMISIA, anastasia_artifacts=(DISENCHANTMENT,),
              qiqi_c: int = 0, qiqi_weapon=FAV_SWORD, qiqi_artifacts=(MILLELITH,),
              sucrose_c: int = 6, sucrose_weapon=TTDS_FULL_CATALYSATOR, sucrose_artifacts=(VIRIDESCENT,),
              alyosha_c: int = 6, alyosha_weapon=FAV_LANCE, alyosha_artifacts=(HEART_OF_FORGE,)) -> Team:
    return Team(
        name=name,
        builds=[
            anastasia_build(anastasia_c, anastasia_weapon, anastasia_artifacts, short=short),
            qiqi_build(qiqi_c, qiqi_weapon, qiqi_artifacts),
            sucrose_build(sucrose_c, sucrose_weapon, sucrose_artifacts),
            alyosha_build(alyosha_c, alyosha_weapon, alyosha_artifacts),
        ],
        enemy=enemy(),
        buffs=TEAM_BUFFS,
        rotation=ROTATION_SHORT if short else ROTATION,
        config=Config(),
        dd="Анастасия",
    )


def team_name(short: bool = SHORT_DEFAULT, anastasia_c: int = 1, anastasia_weapon=ARTEMISIA, qiqi_c: int = 0, qiqi_weapon=FAV_SWORD, sucrose_c: int = 6, sucrose_weapon=TTDS_FULL_CATALYSATOR, alyosha_c: int = 6, alyosha_weapon=FAV_LANCE) -> str:
    return (f"C{anastasia_c}R{anastasia_weapon.refinement} Анастасия" + (" (ДД, короткое)" if short else " (ДД, полное)") + (f" ({anastasia_weapon.name})" if anastasia_weapon.name != ARTEMISIA.name else "") + ", " + f"C{qiqi_c}R{qiqi_weapon.refinement} Ци Ци" + ", " + f"C{sucrose_c}R{sucrose_weapon.refinement} Сахароза" + ", " + f"C{alyosha_c}R{alyosha_weapon.refinement} Алеша")


VARIANTS = ({}, {"short": False})

BASE_NAME = team_name()


def all_teams() -> Dict[str, Team]:
    out: Dict[str, Team] = {}
    for kw in VARIANTS:
        name = team_name(**{k: v for k, v in kw.items() if k in team_name.__code__.co_varnames})
        out[name] = make_team(name, **kw)
    return out
