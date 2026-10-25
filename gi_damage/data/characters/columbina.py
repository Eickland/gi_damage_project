"""
Колумбина — гидро, катализатор. Саппорт лунных реакций (Moonsign).
Масштабируется от HP. Навык работает из кармана. Ротация: E Q, 3.1 с.

Комбо (за ротацию отряда), одинаковое по числу ударов для всех реакций:
    E                      — 1 удар навыка (гидро)
    Gravity Ripple         — 10 ударов (гидро, вне поля)
    Gravity Interference   — 3 срабатывания (вне поля, раз в 6 с)
        C1: +1 сразу при E (с поля);  C2: ещё +1 (вне поля)
    Q                      — 1 удар взрыва (гидро)

Тип Gravity Interference зависит от лунной реакции отряда — три комбо:
    "lc_support"       — лунная кристаллизация: 15.88% HP (гео)
    "lcharged_support" — лунный заряд:          8.47% HP (электро)
    "lbloom_support"   — лунные бутоны:         2.53% HP × 5 (дендро)
От типа зависят и C2 / C4 / C6 (см. ниже) — эти баффы добавляет комбо.

Баффы (постоянные):
    Q   Lunar Domain: +40% урона лунных реакций отряду (C5: 49%)
    A1  Lunacy: +15% КШ (3 стака)
    A4  Law of the New Moon (считается в отряде, в среднем ×1.33):
        кристаллизация — каждый Moondrift с шансом 33% наносит доп. атаку
        (MOONDRIFT_EXTRA); заряд — каждая молния Thundercloud с шансом 33%
        бьёт ещё раз (THUNDERCLOUD_EXTRA)
    Moonsign Benediction: +0.2% базового урона лунных реакций за 1000 HP (макс. 7%)
    C1, C3, C4, C5: +1.5% возвышения лунных реакций отряду каждое
    C2, C6: +7% возвышения лунных реакций отряду каждое
    C2  Lunar Brilliance: +40% HP; активному персонажу по типу реакции:
        кристаллизация +ЗЩ = 1% HP, заряд +АТК = 1% HP, бутоны +МС = 0.35% HP
    C4  Gravity Interference от C1: доп. базовый урон по типу реакции:
        кристаллизация / заряд +12.5% HP, бутоны +2.5% HP (к каждому из 5 ударов)
    C6  +80% КУ урона стихий реакции отряду:
        кристаллизация — гео и гидро, заряд — электро и гидро, бутоны — дендро и гидро
"""

from __future__ import annotations
from dataclasses import replace  # noqa: F401 — для patches= в файлах отрядов

from ...core.buffs import OTHERS, SELF, TEAM, Buff, temp
from ...core.entities import Character, Constellation, with_rotation
from ...core.stats import S
from ...core.sources import (elemental, occ, lunar_crystallize, lunar_charged,
                             lunar_bloom)
from ..tags import *

COLUMBINA_NAME = "Колумбина"

# --------------------------------------------------------------------------- #
#  Множители (в долях Max HP)                                                  #
# --------------------------------------------------------------------------- #
SKILL_MV, SKILL_MV_C3 = 0.301, 0.3553
RIPPLE_MV, RIPPLE_MV_C3 = 0.1685, 0.1989
INTERFERENCE_MV, INTERFERENCE_MV_C3 = 0.1588, 0.1875              # кристаллизация
INTERFERENCE_CHARGED_MV, INTERFERENCE_CHARGED_MV_C3 = 0.0847, 0.10  # заряд
INTERFERENCE_BLOOM_MV, INTERFERENCE_BLOOM_MV_C3 = 0.0253, 0.0299    # бутоны, × 5
INTERFERENCE_BLOOM_HITS = 5
BURST_MV, BURST_MV_C5 = 0.5803, 0.6851
DOMAIN_LUNAR_BONUS, DOMAIN_LUNAR_BONUS_C5 = 0.40, 0.49

RIPPLE_HITS = 10
INTERFERENCE_HITS = 3          # C0, раз в 6 с
C2_EXTRA_INTERFERENCE = 1

A1_CRIT_RATE = 0.05 * 3        # Lunacy: +5% КШ × 3
MOONDRIFT_EXTRA = 0.33         # A4: шанс доп. атаки каждого Moondrift (кристаллизация)
THUNDERCLOUD_EXTRA = 0.33      # A4: шанс доп. молнии Thundercloud (заряд)
MOONSIGN_PER_1000_HP = 0.002   # +0.2% базового урона за 1000 HP
MOONSIGN_CAP = 0.07
SMALL_ELEVATION = 0.015        # C1/C3/C4/C5
BIG_ELEVATION = 0.07           # C2/C6
C2_HP = 0.40
C2_DEF_PER_HP = 0.01           # кристаллизация: ЗЩ активному
C2_ATK_PER_HP = 0.01           # заряд: АТК активному
C2_EM_PER_HP = 0.0035          # бутоны: МС активному
C4_FLAT_HP = 0.125             # кристаллизация / заряд
C4_FLAT_HP_BLOOM = 0.025       # бутоны
C6_CRIT_DMG = 0.80

COLUMBINA_TIME = 3.1

#: Тег источника: Gravity Interference от C1 (C4 добавляет ему доп. урон)
INTERFERENCE_C1 = "columbina_gi_c1"


def _columbina_hp(ctx) -> float:
    return ctx.stat(COLUMBINA_NAME, "hp", frozenset({OFF}))


COLUMBINA_KIT = Character(
    name=COLUMBINA_NAME,
    element="hydro",
    weapon_type="catalyst",
    default_field=OFF,
    crit_mode="balance",
    stats={
        S.BASE_HP: 14695.0,
        S.CRIT_VALUE: 0.988,
    },
    buffs=(
        Buff(S.LUNAR_BONUS, DOMAIN_LUNAR_BONUS, target=TEAM,
             source="Lunar Domain: +40% урона лунных реакций отряду"),
        Buff(S.CRIT_VALUE, A1_CRIT_RATE * 2, target=SELF,
             source="Lunacy's Lure: +15% КШ (3 стака)"),
        Buff(S.LUNAR_BASE_INC,
             lambda ctx: min(MOONSIGN_CAP, MOONSIGN_PER_1000_HP * _columbina_hp(ctx) / 1000.0),
             target=TEAM,
             source="Moonsign Benediction: +0.2% базового урона лунных реакций за 1000 HP (макс. 7%)"),
    ),
    sources=(),
    constellations={
        1: Constellation(
            number=1, name="C1",
            buffs=(Buff("elevation.lunar", SMALL_ELEVATION, target=TEAM,
                        source="C1 Колумбины: +1.5% возвышения лунных реакций"),),
        ),
        2: Constellation(
            number=2, name="C2",
            buffs=(
                Buff(S.HP_PCT, C2_HP, target=SELF,
                     source="C2 Колумбины: Lunar Brilliance, +40% HP"),
                Buff("elevation.lunar", BIG_ELEVATION, target=TEAM,
                     source="C2 Колумбины: +7% возвышения лунных реакций"),
            ),
        ),
        3: Constellation(
            number=3, name="C3",
            buffs=(Buff("elevation.lunar", SMALL_ELEVATION, target=TEAM,
                        source="C3 Колумбины: +1.5% возвышения лунных реакций"),),
            patches={
                "Навык": lambda s: replace(s, mv=SKILL_MV_C3),
                "Gravity Ripple": lambda s: replace(s, mv=RIPPLE_MV_C3),
                "Gravity Interference (LC)": lambda s: replace(s, mv=INTERFERENCE_MV_C3),
                "C1: Gravity Interference при E (LC)": lambda s: replace(s, mv=INTERFERENCE_MV_C3),
                "C2: доп. Gravity Interference (LC)": lambda s: replace(s, mv=INTERFERENCE_MV_C3),
                "Gravity Interference (заряд)": lambda s: replace(s, mv=INTERFERENCE_CHARGED_MV_C3),
                "C1: Gravity Interference при E (заряд)": lambda s: replace(s, mv=INTERFERENCE_CHARGED_MV_C3),
                "C2: доп. Gravity Interference (заряд)": lambda s: replace(s, mv=INTERFERENCE_CHARGED_MV_C3),
                "Gravity Interference (бутоны)": lambda s: replace(s, mv=INTERFERENCE_BLOOM_MV_C3),
                "C1: Gravity Interference при E (бутоны)": lambda s: replace(s, mv=INTERFERENCE_BLOOM_MV_C3),
                "C2: доп. Gravity Interference (бутоны)": lambda s: replace(s, mv=INTERFERENCE_BLOOM_MV_C3),
            },
        ),
        4: Constellation(
            number=4, name="C4",
            buffs=(
                Buff("elevation.lunar", SMALL_ELEVATION, target=TEAM,
                     source="C4 Колумбины: +1.5% возвышения лунных реакций"),
            ),
        ),
        5: Constellation(
            number=5, name="C5",
            buffs=(
                Buff(S.LUNAR_BONUS, DOMAIN_LUNAR_BONUS_C5 - DOMAIN_LUNAR_BONUS, target=TEAM,
                     source="C5 Колумбины: Lunar Domain до 49%"),
                Buff("elevation.lunar", SMALL_ELEVATION, target=TEAM,
                     source="C5 Колумбины: +1.5% возвышения лунных реакций"),
            ),
            patches={"Взрыв стихии": lambda s: replace(s, mv=BURST_MV_C5)},
        ),
        6: Constellation(
            number=6, name="C6",
            buffs=(
                Buff("elevation.lunar", BIG_ELEVATION, target=TEAM,
                     source="C6 Колумбины: +7% возвышения лунных реакций"),
            ),
        ),
    },
    note="Саппорт лунных реакций (Moonsign).",
)

# --------------------------------------------------------------------------- #
#  Баффы, зависящие от типа лунной реакции (C2 / C4 / C6)                      #
# --------------------------------------------------------------------------- #
_ELEMENT_RU = {"geo": "гео", "hydro": "гидро", "electro": "электро", "dendro": "дендро"}


def _reaction_constellation_buffs(c2_stat: str, c2_ratio: float, c2_label: str,
                                  c4_ratio: float, c6_elements):
    """C2: стат активному от HP; C4: доп. урон удару от C1; C6: КУ стихий реакции."""
    return {
        2: (Buff(c2_stat, lambda ctx: c2_ratio * _columbina_hp(ctx),
                 target=TEAM, requires=(ON,),
                 source=f"C2 Колумбины: активному +{c2_label} = {c2_ratio:.2%} HP Колумбины"),),
        4: (Buff(f"{S.FLAT_BASE_DMG}.{INTERFERENCE_C1}",
                 lambda ctx: c4_ratio * ctx.own("hp"), target=SELF,
                 source=f"C4 Колумбины: Gravity Interference от C1 +{c4_ratio:.1%} HP"),),
        6: tuple(Buff(f"crit_value.{el}", C6_CRIT_DMG, target=TEAM,
                      source=f"C6 Колумбины: +80% КУ {_ELEMENT_RU[el]} урона")
                 for el in c6_elements),
    }


def _support_combo(make_interference, label: str, hits_per_trigger: int,
                   main_tags=(OFF,), c1_tags=(ON,),
                   main_occs=None, c1_occs=None, c2_occs=None):
    """Комбо саппорта: одинаковые удары, разный тип Gravity Interference.

    make_interference(name, mv, occurrences, **kw) — lunar_crystallize / lunar_charged /
    lunar_bloom; hits_per_trigger — инстансов за одно срабатывание (бутоны — 5).
    main_occs / c1_occs / c2_occs — свои списки вхождений вместо стандартных
    (когда удары одного срабатывания попадают в разные окна отряда).
    """
    n = hits_per_trigger
    if main_occs is None:
        main_occs = [occ(INTERFERENCE_HITS * n, *main_tags)]
    if c1_occs is None:
        c1_occs = [occ(n, *c1_tags)]
    if c2_occs is None:
        c2_occs = [occ(C2_EXTRA_INTERFERENCE * n, OFF)]
    return (
        (
            elemental("Навык", "hp", SKILL_MV, "hydro", "skill", [occ(1, ON)]),
            elemental("Gravity Ripple", "hp", RIPPLE_MV, "hydro", "skill",
                      [occ(RIPPLE_HITS, OFF)]),
            make_interference(f"Gravity Interference ({label})", main_occs),
            elemental("Взрыв стихии", "hp", BURST_MV, "hydro", "burst", [occ(1, ON)]),
        ),
        {
            1: (make_interference(f"C1: Gravity Interference при E ({label})",
                                  c1_occs, extra_tags=(INTERFERENCE_C1,)),),
            2: (make_interference(f"C2: доп. Gravity Interference ({label})", c2_occs),),
        },
    )


# Лунная кристаллизация. Окна отряда Цзы Бай: 3 обычных срабатывания тратят
# Field Catalog Линеи (C1), удар от C1 (с поля) — Nightingale's Song Иллуги.
_LC_SOURCES, _LC_CONST_SOURCES = _support_combo(
    lambda name, occs, **kw: lunar_crystallize(name, "hp", INTERFERENCE_MV, occs,
                                               kind="skill", **kw),
    "LC", 1, main_tags=(OFF, FIELD_CATALOG), c1_tags=(ON, NIGHTINGALE))

_CHARGED_SOURCES, _CHARGED_CONST_SOURCES = _support_combo(
    lambda name, occs, **kw: lunar_charged(name, "hp", INTERFERENCE_CHARGED_MV, occs,
                                           kind="skill", **kw),
    "заряд", 1)

_BLOOM_SOURCES, _BLOOM_CONST_SOURCES = _support_combo(
    lambda name, occs, **kw: lunar_bloom(name, "hp", INTERFERENCE_BLOOM_MV, occs,
                                         kind="skill", **kw),
    "бутоны", INTERFERENCE_BLOOM_HITS)

# Лунные бутоны в отряде Нефер / Лаума / Сахароза:
#   одно срабатывание (5 ударов) — под Сахарозой и Инструктором (INST);
#   18 стаков Pale Hymn Лаумы — на удары бутонов Колумбины: 15 основных + 3 из C1.
_BLOOM_LAUMA_SOURCES, _BLOOM_LAUMA_CONST_SOURCES = _support_combo(
    lambda name, occs, **kw: lunar_bloom(name, "hp", INTERFERENCE_BLOOM_MV, occs,
                                         kind="skill", **kw),
    "бутоны", INTERFERENCE_BLOOM_HITS,
    main_occs=[occ(INTERFERENCE_BLOOM_HITS, OFF, INST, PALE_HYMN),
               occ((INTERFERENCE_HITS - 1) * INTERFERENCE_BLOOM_HITS, OFF, PALE_HYMN)],
    c1_occs=[occ(3, ON, PALE_HYMN), occ(INTERFERENCE_BLOOM_HITS - 3, ON)],
)

COLUMBINA_COMBO_DICT = {
    "lc_support": with_rotation(
        COLUMBINA_KIT,
        sources=_LC_SOURCES,
        constellation_sources=_LC_CONST_SOURCES,
        constellation_extra_buffs=_reaction_constellation_buffs(
            S.FLAT_DEF, C2_DEF_PER_HP, "ЗЩ", C4_FLAT_HP, ("geo", "hydro")),
    ),
    "lcharged_support": with_rotation(
        COLUMBINA_KIT,
        sources=_CHARGED_SOURCES,
        constellation_sources=_CHARGED_CONST_SOURCES,
        constellation_extra_buffs=_reaction_constellation_buffs(
            S.FLAT_ATK, C2_ATK_PER_HP, "АТК", C4_FLAT_HP, ("electro", "hydro")),
    ),
    "lbloom_support": with_rotation(
        COLUMBINA_KIT,
        sources=_BLOOM_SOURCES,
        constellation_sources=_BLOOM_CONST_SOURCES,
        constellation_extra_buffs=_reaction_constellation_buffs(
            S.FLAT_EM, C2_EM_PER_HP, "МС", C4_FLAT_HP_BLOOM, ("dendro", "hydro")),
    ),
    "lbloom_nefer_lauma": with_rotation(
        COLUMBINA_KIT,
        sources=_BLOOM_LAUMA_SOURCES,
        constellation_sources=_BLOOM_LAUMA_CONST_SOURCES,
        constellation_extra_buffs=_reaction_constellation_buffs(
            S.FLAT_EM, C2_EM_PER_HP, "МС", C4_FLAT_HP_BLOOM, ("dendro", "hydro")),
    ),
}
