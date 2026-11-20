"""
Анастасия — крио, лук. Пока только САППОРТ-режим («Милосердие»: навык
нажатием + взрыв «To a New World»). Режим «Слава» (копьё, Annihilation)
не реализован — неизвестно число ударов за ротацию.

База: 350 базовой АТК, 0.984 крит-вэлью.
(Бета: стат возвышения 19.2% КШ → 38.4% КУ. В режиме крита «balance» это
те же 0.384 крит-вэлью, поэтому 0.984 не меняется.)

Удары (за ротацию отряда)
    * навык нажатием — крио 212.76% (ур. 10), 1 раз;
    * взрыв «To a New World» — крио 360.7%, 1 раз;
    * Корона (Azure Star Crown), 10 атак:
        - крио 115.2% × 10;
        - Radiance: второй удар — SC 72% или SSW 108% × 10;
        - доп. удар от взрыва — SC 20.2% или SSW 30.2% × 10.
      Взрыв замораживает корону — все 10 атак идут под ним.
    * Triumph (Azure Star Decree) — выход на поле после конца запечатывания:
      SC 400.8% или SSW 601.2%, 1 раз.
    SC или SSW — по режиму отряда (anastasia_support(mode="sc" | "ssw")).

Баффы
    * Взрыв: +30% урона звёздных реакций (SC и SSW) всему отряду — постоянно.
    * Stellar Benediction: +0.7% базового урона SC и SSW отряду за каждые
      100 АТК Анастасии, максимум 14%.
    * Glory of the Radiant Night: +12% крит. урона отряду. Анастасия после
      взрыва запечатывает себя — её Слава делится на остальных троих
      (+16% им), у самой — только в ударах на поле.
    * An Unfinished Requiem:
        - SC: +1 стак Polestar отряду всегда (polar_always=1, стаки считает
          Team.polar_plan(); бета-хотфикс: было 2);
        - SSW: базовый множитель реакций SSW ×1.10 (requiem_reactions(); бета, было ×1.15) и
          +4 вихря 2 уровня (requiem_vortex()).

Созвездия (саппорт-режим)
    C1  Слава: +30% АТК другим крио персонажам (сама Анастасия крио), +15% АТК
        ей самой, +60 МС персонажам других стихий; Анастасия свою
        Славу не теряет. Каждому остальному — одна Слава: 12% КУ + 30% АТК
        (крио) или +60 МС (иные стихии); доля от Анастасии (+4% КУ на C0)
        и множитель ×3 не применяются.
    C2  Милосердие: +50% крит. урона звёздных реакций отряду (бета; было 60%); +5% возвышения
        звёздных реакций отряду.
    C3  Взрыв +3 ур.: To a New World 425.85%, +35.4% урона звёздных реакций,
        доп. удар короны 23.8%/35.7%, Triumph 473.17%/709.75%; ДД — Evernight
        662.43%/993.65%, Annihilation 56.78%×5 и 141.95/189.27/236.58% (SC),
        212.93/283.9/354.87% (SSW).
    C4  Все эффекты Славы ×1.3.
    C5  Навык +3 ур.: нажатие 251.17%, удержание 334.9%, корона крио 136%,
        корона 71.4%/107.1%, копьё (крио и SC/SSW) — по таблице C5_SPEAR_*.
    C6  Милосердие: Triumph при выходе следующего персонажа, 200% урона
        (SC 400.8% / SSW 601.2% × 2.0; бета, было 250%), 1 раз; +10% возвышения звёздных
        реакций отряду.
"""

from __future__ import annotations
from dataclasses import replace
from typing import Sequence

from ...core.buffs import OTHERS, SELF, TEAM, Buff, temp
from ...core.entities import Character, Constellation, with_rotation
from ...core.reactions import REACTION_SSW, ssw_vortex
from ...core.sources import (Occurrence, elemental, occ,
                             stellar_conduct, stellar_swirl)
from ...core.stats import S
from ..tags import *

ANASTASIA_NAME = "Анастасия"

# --------------------------------------------------------------------------- #
#  Множители (в долях)                                                         #
# --------------------------------------------------------------------------- #
TAP_MV = 2.1276                   # навык нажатием, начальный урон (ур. 10)
BURST_MV = 3.607                  # «To a New World», начальный урон
CROWN_CRYO_MV = 1.152             # корона: крио удар (ур. 10)
CROWN_MV = {"sc": 0.6048, "ssw": 0.9072}      # корона: второй удар в Radiance (ур. 10; бета: 60.48% / 90.72%)
CROWN_BURST_MV = {"sc": 0.202, "ssw": 0.302}  # корона: доп. удар во время взрыва
TRIUMPH_MV = {"sc": 4.008, "ssw": 6.012}      # Azure Star Decree — Triumph
CROWN_HITS = 10

BURST_SG_BONUS = 0.30             # +30% урона звёздных реакций отряду (бета; было 50%)
BASE_INC_PER_100_ATK = 0.007      # +0.7% базового урона за 100 АТК
BASE_INC_CAP = 0.14

GLORY_CD = 0.12                   # Слава: +12% КУ
GLORY_ATK = 0.15                  # C1: +15% АТК крио персонажам (самой Анастасии)
#: C1: остальные крио персонажи получают 30% АТК — сама Анастасия тоже крио
GLORY_ATK_OTHERS_CRYO = 0.30
GLORY_EM = 60.0                   # C1: +60 МС персонажам других стихий
C1_SEALED_FACTOR = 1.0            # C1: остальным — одна Слава (12% КУ + 15% АТК крио / 60 МС), без ×3
C4_FACTOR = 1.3                   # C4: эффекты Славы ×1.3

C2_SG_CRIT_DMG = 0.50             # C2: +50% КУ звёздных реакций (бета; было 60%)
C2_SG_ELEVATION = 0.05            # C2: +5% возвышения звёздных реакций
C6_SG_ELEVATION = 0.10            # C6: +10% возвышения звёздных реакций
C6_TRIUMPH_FACTOR = 2.0           # C6: Triumph на 200% урона (бета; было 250%)

# C3: взрыв +3 ур. (оба режима)
C3_BURST_MV = 4.2585
C3_BURST_SG_BONUS = 0.354
C3_CROWN_BURST_MV = {"sc": 0.238, "ssw": 0.357}
C3_TRIUMPH_MV = {"sc": 4.7317, "ssw": 7.0975}
C3_DD_BURST_MV = {"sc": 6.6243, "ssw": 9.9365}
C3_DOOM1_CRYO_MV = 0.5678
#: бета: новые множители × прежнее соотношение C3 / ур. 10 (≈1.1806)
C3_DOOM_SG = {"sc": (2.3658, 2.8393, 3.3126), "ssw": (3.5488, 4.2583, 4.9677)}
# C5: навык +3 ур.
C5_TAP_MV = 2.5117
C5_DD_HOLD_MV = 3.349
C5_CROWN_CRYO_MV = 1.36
C5_CROWN_MV = {"sc": 0.714, "ssw": 1.071}
C5_SPEAR_CRYO = {1: 1.3323, 2: 0.698, 3: 1.6947, 4: 0.6251, 5: 0.7529}
#: бета: новые множители × прежнее соотношение C5 / ур. 10 (≈1.1805)
C5_SPEAR_SG = {"sc": {1: 1.0967, 2: 1.1487, 3: 1.3943, 4: 1.5217, 5: 1.8559},
               "ssw": {1: 1.6446, 2: 1.7236, 3: 2.0921, 4: 2.2819, 5: 2.7849}}

REQUIEM_SSW_MULT = 1.10           # Requiem (SSW): базовый множитель реакций ×1.10 (бета; было ×1.15)

#: Откат взрыва (бета: 15 → 18 с; стоимость не изменилась). Ротация отряда
#: с Анастасией не должна быть короче.
BURST_CD = 18.0
REQUIEM_VORTEX_LEVEL = 2          # Requiem (SSW): вихри сразу 2 уровня
REQUIEM_VORTEX_HITS = 4           # доп. вихрей 2 уровня за ротацию


_SG = ("stellar_conduct", "stellar_swirl")
_LABEL = {"sc": "SC", "ssw": "SSW"}


def _mv(v):
    return lambda src: replace(src, mv=v)


def _c3_patches_support():
    p = {"Взрыв «To a New World» — начальный урон": _mv(C3_BURST_MV)}
    for m, l in _LABEL.items():
        p[f"Корона — доп. удар взрыва ({l})"] = _mv(C3_CROWN_BURST_MV[m])
        p[f"Triumph ({l})"] = _mv(C3_TRIUMPH_MV[m])
        p[f"C6: Triumph ×200% ({l})"] = _mv(C3_TRIUMPH_MV[m] * C6_TRIUMPH_FACTOR)
    return p


def _c5_patches_support():
    p = {"Навык нажатием — начальный урон": _mv(C5_TAP_MV),
         "Корона — крио": _mv(C5_CROWN_CRYO_MV)}
    for m, l in _LABEL.items():
        p[f"Корона — {l}"] = _mv(C5_CROWN_MV[m])
    return p


def _anastasia_atk(ctx) -> float:
    return ctx.stat(ANASTASIA_NAME, "atk", frozenset({OFF}))


def _is_cryo(ctx) -> bool:
    return ctx.recipient_element() == "cryo"


def _glory_buffs(factor_self: float, factor_others: float, with_c1: bool, tag: str):
    """Слава: себе (factor_self единиц) и остальным (factor_others единиц)."""
    out = []
    if factor_self:
        out.append(Buff(S.CRIT_VALUE, GLORY_CD * factor_self, target=SELF,
                        source=f"{tag}: Слава, +{GLORY_CD * factor_self:.1%} КУ себе"))
        if with_c1:
            out.append(Buff(S.ATK_PCT, GLORY_ATK * factor_self, target=SELF,
                            source=f"{tag}: Слава, +{GLORY_ATK * factor_self:.1%} АТК себе"))
    if factor_others:
        out.append(Buff(S.CRIT_VALUE, GLORY_CD * factor_others, target=OTHERS,
                        source=f"{tag}: Слава, +{GLORY_CD * factor_others:.1%} КУ отряду"))
        if with_c1:
            atk, em = GLORY_ATK_OTHERS_CRYO * factor_others, GLORY_EM * factor_others
            out.append(Buff(S.ATK_PCT, lambda ctx, v=atk: v if _is_cryo(ctx) else 0.0,
                            target=OTHERS,
                            source=f"{tag}: Слава, +{atk:.1%} АТК крио персонажам"))
            out.append(Buff(S.BASE_EM, lambda ctx, v=em: 0.0 if _is_cryo(ctx) else v,
                            target=OTHERS,
                            source=f"{tag}: Слава, +{em:g} МС персонажам других стихий"))
    return tuple(out)


def _sg_buffs(stat: str, value: float, tag: str):
    return tuple(Buff(f"{stat}.{m}", value, target=TEAM, source=f"{tag} ({m})") for m in _SG)


# C0: сама — 1 единица Славы только на поле; остальным — своя + 1/3 её.
_C0_SELF_ON = Buff(S.CRIT_VALUE, GLORY_CD, target=SELF, requires=(ON,),
                   source="Glory of the Radiant Night: +12% КУ себе (на поле)")
_C0_OTHERS = 1.0 + 1.0 / 3.0
# C1: остальным ×3 от исходной; сама Славу не теряет (и вне поля).
_C1_OTHERS = C1_SEALED_FACTOR

ANASTASIA_KIT = Character(
    name=ANASTASIA_NAME,
    element="cryo",
    weapon_type="bow",
    default_field=OFF,
    polar_always=1.0,   # стаки Polestar отряду: An Unfinished Requiem, +1 всегда
    crit_mode="balance",
    stats={
        S.BASE_ATK: 356.0,
        S.CRIT_VALUE: 0.984,
    },
    buffs=(
        Buff(S.SC_BONUS, BURST_SG_BONUS, target=TEAM,
             source=f"To a New World: +{BURST_SG_BONUS:.0%} урона звёздного проводника отряду"),
        Buff(S.SSW_BONUS, BURST_SG_BONUS, target=TEAM,
             source=f"To a New World: +{BURST_SG_BONUS:.0%} урона звёздного рассеивания отряду"),
        Buff(S.SC_BASE_INC,
             lambda ctx: min(BASE_INC_CAP, BASE_INC_PER_100_ATK * _anastasia_atk(ctx) / 100.0),
             target=TEAM,
             source="Stellar Benediction: +0.7% базового урона SC за 100 АТК (макс. 14%)"),
        Buff(S.SSW_BASE_INC,
             lambda ctx: min(BASE_INC_CAP, BASE_INC_PER_100_ATK * _anastasia_atk(ctx) / 100.0),
             target=TEAM,
             source="Stellar Benediction: +0.7% базового урона SSW за 100 АТК (макс. 14%)"),
        _C0_SELF_ON,
    ) + _glory_buffs(0.0, _C0_OTHERS, False, "Glory of the Radiant Night"),
    sources=(),
    constellations={
        1: Constellation(
            number=1, name="C1",
            buffs=(
                # Себе: Слава и вне поля + АТК крио на поле и вне его
                Buff(S.CRIT_VALUE, GLORY_CD, target=SELF, requires=(OFF,),
                     source="C1: Слава не пропадает при запечатывании (+12% КУ себе)"),
                Buff(S.ATK_PCT, GLORY_ATK, target=SELF,
                     source="C1: Слава, +15% АТК себе"),
                # Остальным: добираем КУ с 4/3 до 3 единиц, плюс АТК/МС ×3
                Buff(S.CRIT_VALUE, GLORY_CD * (_C1_OTHERS - _C0_OTHERS), target=OTHERS,
                     source="C1: остальным одна Слава — 12% КУ (без доли Анастасии)"),
            ) + tuple(b for b in _glory_buffs(0.0, _C1_OTHERS, True, "C1")
                      if b.stat != S.CRIT_VALUE),
        ),
        2: Constellation(
            number=2, name="C2",
            buffs=_sg_buffs("crit_value", C2_SG_CRIT_DMG,
                            "C2 Милосердие: +50% КУ звёздных реакций отряду")
                  + _sg_buffs("elevation", C2_SG_ELEVATION,
                              "C2: +5% возвышения звёздных реакций отряду"),
        ),
        # C4: +30% ко всем эффектам Славы (C1 уже взят)
        4: Constellation(
            number=4, name="C4",
            buffs=(
                Buff(S.CRIT_VALUE, GLORY_CD * (C4_FACTOR - 1), target=SELF,
                     source="C4: Слава ×1.3 (КУ себе)"),
                Buff(S.ATK_PCT, GLORY_ATK * (C4_FACTOR - 1), target=SELF,
                     source="C4: Слава ×1.3 (АТК себе)"),
            ) + _glory_buffs(0.0, _C1_OTHERS * (C4_FACTOR - 1), True, "C4 (Слава ×1.3)"),
        ),
        3: Constellation(
            number=3, name="C3",
            buffs=(Buff(S.SC_BONUS, C3_BURST_SG_BONUS - BURST_SG_BONUS, target=TEAM,
                        source="C3: To a New World +35.4% урона звёздного проводника отряду"),
                   Buff(S.SSW_BONUS, C3_BURST_SG_BONUS - BURST_SG_BONUS, target=TEAM,
                        source="C3: To a New World +35.4% урона звёздного рассеивания отряду")),
            patches=_c3_patches_support(),
        ),
        5: Constellation(number=5, name="C5", patches=_c5_patches_support()),
        6: Constellation(
            number=6, name="C6",
            buffs=_sg_buffs("elevation", C6_SG_ELEVATION,
                            "C6 Милосердие: +10% возвышения звёздных реакций отряду"),
        ),
    },
    note="Саппорт (Милосердие). Режим «Слава» не реализован.",
)


def anastasia_support(mode: str, crown_occ: Sequence[Occurrence],
                      on_tags: Sequence[str] = (ON,), off_tags: Sequence[str] = (OFF,),
                      triumph_tags: Sequence[str] = (ON,)) -> Character:
    """Анастасия-саппорт под конкретный отряд.

    mode      — "sc" (звёздный проводник) или "ssw" (звёздное рассеивание);
    crown_occ — вхождения 10 атак короны (теги окон отряда), например
                [occ(6, OFF, DREAM),
                 occ(4, OFF)];
    on_tags   — теги навыка и взрыва (Анастасия на поле);
    off_tags  — теги Triumph от C6;
    triumph_tags — теги Triumph при выходе на поле после запечатывания.
    """
    if mode not in ("sc", "ssw"):
        raise ValueError(f"mode должен быть 'sc' или 'ssw', а не {mode!r}")
    direct = stellar_conduct if mode == "sc" else stellar_swirl
    label = "SC" if mode == "sc" else "SSW"
    crown_occ = list(crown_occ)
    on_tags, off_tags = tuple(on_tags), tuple(off_tags)
    return with_rotation(
        ANASTASIA_KIT,
        sources=(
            elemental("Навык нажатием — начальный урон", "atk", TAP_MV, "cryo", "skill",
                      [occ(1, *on_tags)]),
            elemental("Взрыв «To a New World» — начальный урон", "atk", BURST_MV, "cryo",
                      "burst", [occ(1, *on_tags)]),
            elemental("Корона — крио", "atk", CROWN_CRYO_MV, "cryo", "skill", crown_occ),
            direct(f"Корона — {label}", "atk", CROWN_MV[mode], "cryo", crown_occ,
                   kind="skill"),
            direct(f"Корона — доп. удар взрыва ({label})", "atk", CROWN_BURST_MV[mode],
                   "cryo", crown_occ, kind="burst"),
            direct(f"Triumph ({label})", "atk", TRIUMPH_MV[mode], "cryo",
                   [occ(1, *triumph_tags)], kind="skill"),
        ),
        constellation_sources={
            6: (
                direct(f"C6: Triumph ×200% ({label})", "atk",
                       TRIUMPH_MV[mode] * C6_TRIUMPH_FACTOR, "cryo",
                       [occ(1, *off_tags)], kind="skill"),
            ),
        },
    )


# --------------------------------------------------------------------------- #
#  An Unfinished Requiem — эффекты на отряд                                    #
# --------------------------------------------------------------------------- #

def requiem_reactions(events):
    """Базовый множитель реакций SSW ×1.15."""
    return tuple(replace(e, multiplier=e.multiplier * REQUIEM_SSW_MULT)
                 if e.model == REACTION_SSW else e for e in events)


def requiem_vortex(*tags: str, count: float = REQUIEM_VORTEX_HITS, **kwargs):
    """Доп. детонации вихря 2 уровня (Requiem: вихри сразу 2 уровня)."""
    return ssw_vortex(REQUIEM_VORTEX_LEVEL, count, *tags,
                      name=kwargs.pop("name", "SSW вихрь 2 ур. (Requiem Анастасии)"),
                      **kwargs)


ANASTASIA_COMBO_DICT = {
    # корона — 10 атак вне поля
    "support_sc": anastasia_support("sc", [
        occ(6, OFF,NOBLE,VV_CRYO,SUCROSE_PASSIVE,SEVEN_SACRED,DECODING),
        occ(2, OFF,NOBLE,SEVEN_SACRED),
        occ(2, OFF),
    ]),
    "support_ssw": anastasia_support("ssw", [
        occ(6, OFF,NOBLE,VV_CRYO,SUCROSE_PASSIVE,SEVEN_SACRED,DECODING),
        occ(2, OFF,NOBLE,SEVEN_SACRED),
        occ(2, OFF),
    ]),
    # укороченные: корона — 8 атак вместо 10
    "support_sc_short": anastasia_support("sc", [
        occ(6, OFF,NOBLE,VV_CRYO,SUCROSE_PASSIVE,SEVEN_SACRED,DECODING),
        occ(2, OFF,NOBLE,SEVEN_SACRED),
    ]),
    "support_ssw_short": anastasia_support("ssw", [
        occ(6, OFF,NOBLE,VV_CRYO,SUCROSE_PASSIVE,SEVEN_SACRED,DECODING),
        occ(2, OFF,NOBLE,SEVEN_SACRED),
    ]),
}


# =========================================================================== #
#  ДД-режим: благословение «Слава» (навык удержанием + копьё)                 #
# =========================================================================== #
# Комбо: hEQ (N5 sE)×3 — 3.1 + 3 × (2.8 + 1.5) = 16.0 с;
# короткое: hEQ N5sE N5sE sE — 3.1 + 2 × 2.8 + 3 × 1.5 = 13.2 с.
#   hE  — начальный урон удержанием, крио 283.68%;
#   Q   — «The Evernight Yields to Dawn», SC 561.12% / SSW 841.68%;
#   N5  — 5 ударов копья (обычная атака, крио) + на каждом ударе ещё один
#         инстанс SC / SSW (идёт сверху, не заменяет крио);
#   sE  — Annihilation: 3 стадии по очереди, по одной после каждой N5:
#         1-я — крио 48.1% × 5 (урон навыка) + SC 200.4% / SSW 300.6%,
#         2-я — SC 240.5% / SSW 360.7%, 3-я — SC 280.6% / SSW 420.8% (бета).
# Бета: в усиленном режиме на поле — повышенная устойчивость к прерыванию и
# ходьба по воде (на урон не влияет).
# В ДД-режиме нет короны и бафа +30% урона звёздных реакций отряду.
#
# Слава (A1): Анастасия запечатывает троих — их Слава уходит ей:
#   себе 4 × 12% КУ, остальным — ничего.
#   C1: остальные Славу не теряют (12% КУ, +15% АТК крио / +60 МС иным),
#       Анастасия (крио) получает 4 × (12% КУ + 15% АТК);
#   C2: копьё, взрыв Славы и Annihilation — 125% урона; +5% возвышения
#       звёздных реакций отряду;
#   C4: эффекты Славы ×1.3;
#   C6: нажатие навыка вызывает 3-ю стадию Annihilation с 250% урона (бета; было 200%)
#       (1 раз, на первом sE); +20% урона звёздных реакций самой Анастасии.

DD_HOLD_MV = 2.8368                                  # навык удержанием (ур. 10)
DD_BURST_MV = {"sc": 5.6112, "ssw": 8.4168}          # The Evernight Yields to Dawn
#: Копьё: (крио множитель, инстансов) и звёздный инстанс на удар
SPEAR_CRYO = {1: (1.1286, 1), 2: (0.5913, 2), 3: (1.4355, 1), 4: (0.5295, 3), 5: (0.6378, 3)}
#: бета: SC 70.6/74/89.8/97.9/119.5% → 92.9/97.3/118.1/128.9/157.2%,
#:       SSW 105.9/110.9/134.7/146.9/179.2% → 139.3/146/177.2/193.3/235.9%
SPEAR_SG = {"sc": {1: 0.929, 2: 0.973, 3: 1.181, 4: 1.289, 5: 1.572},
            "ssw": {1: 1.393, 2: 1.46, 3: 1.772, 4: 1.933, 5: 2.359}}
#: бета: SC 120.2/160.3/200.4% → 200.4/240.5/280.6%,
#:       SSW 180.4/240.5/300.6% → 300.6/360.7/420.8%
DOOM_SG = {"sc": (2.004, 2.405, 2.806), "ssw": (3.006, 3.607, 4.208)}
DOOM1_CRYO_MV, DOOM1_CRYO_HITS = 0.481, 5            # 1-я стадия: крио 48.1% × 5
DD_LOOPS = 3                                         # (N5 sE) × 3
DD_HEQ_TIME, DD_N5_TIME, DD_SE_TIME = 3.1, 2.8, 1.5


def dd_time(n5: int = DD_LOOPS) -> float:
    """Время комбо: hEQ + n5 × N5 + 3 × sE (Annihilation — всегда 3 стадии)."""
    return round(DD_HEQ_TIME + n5 * DD_N5_TIME + DD_LOOPS * DD_SE_TIME, 2)


DD_TIME = dd_time(3)          # hEQ (N5 sE)×3      — 16.0 с
DD_TIME_SHORT = dd_time(2)    # hEQ N5sE N5sE sE   — 13.2 с

C2_GLORY_MULT = 1.25                                 # C2 Слава: 125% урона
C6_GLORY_DOOM3 = 2.5                                 # C6 Слава: 3-я стадия ×250% (бета; было ×200%)
C6_GLORY_SG_BONUS = 0.20                             # C6 Слава: +20% урона SG себе
DD_GLORY_UNITS = 4                                   # своя Слава + Слава троих запечатанных



def _c3_patches_dd():
    p = {}
    for m, l in _LABEL.items():
        p[f"Взрыв «The Evernight Yields to Dawn» ({l})"] = _mv(C3_DD_BURST_MV[m])
        for i in range(3):
            p[f"Annihilation {i + 1} — {l}"] = _mv(C3_DOOM_SG[m][i])
        p[f"C6: Annihilation 3 ×250% ({l})"] = _mv(C3_DOOM_SG[m][2] * C6_GLORY_DOOM3)
    p["Annihilation 1 — крио"] = _mv(C3_DOOM1_CRYO_MV)
    return p


def _c5_patches_dd():
    p = {"Навык удержанием — начальный урон": _mv(C5_DD_HOLD_MV)}
    for n in range(1, 6):
        p[f"Копьё {n}-й удар — крио"] = _mv(C5_SPEAR_CRYO[n])
        for m, l in _LABEL.items():
            p[f"Копьё {n}-й удар — {l}"] = _mv(C5_SPEAR_SG[m][n])
    return p


def _dd_glory_others(factor: float, tag: str):
    """C1 в ДД-режиме: остальные сохраняют свою Славу (factor единиц)."""
    return _glory_buffs(0.0, factor, True, tag)


ANASTASIA_DD_KIT = replace(
    ANASTASIA_KIT,
    default_field=ON,
    polar_on_field=3.0,    # стаки Polestar: +3 на поле (и +1 всегда от Requiem)
    buffs=(
        # Stellar Benediction — как в саппорт-режиме
        ANASTASIA_KIT.buffs[2],
        ANASTASIA_KIT.buffs[3],
        Buff(S.CRIT_VALUE, GLORY_CD * DD_GLORY_UNITS, target=SELF,
             source="Слава: своя + 3 запечатанных, +48% КУ себе"),
    ),
    multipliers={"glory_c2": lambda stats: 1.0},
    constellations={
        1: Constellation(
            number=1, name="C1",
            buffs=(Buff(S.ATK_PCT, GLORY_ATK * DD_GLORY_UNITS, target=SELF,
                        source="C1: Слава, +15% АТК × 4 себе"),)
                  + _dd_glory_others(1.0, "C1 (Слава остаётся у отряда)"),
        ),
        2: Constellation(
            number=2, name="C2",
            buffs=_sg_buffs("elevation", C2_SG_ELEVATION,
                            "C2: +5% возвышения звёздных реакций отряду"),
            multipliers={"glory_c2": lambda stats: C2_GLORY_MULT},
        ),
        3: Constellation(number=3, name="C3", patches=_c3_patches_dd()),
        5: Constellation(number=5, name="C5", patches=_c5_patches_dd()),
        4: Constellation(
            number=4, name="C4",
            buffs=(
                Buff(S.CRIT_VALUE, GLORY_CD * DD_GLORY_UNITS * (C4_FACTOR - 1), target=SELF,
                     source="C4: Слава ×1.3 (КУ себе)"),
                Buff(S.ATK_PCT, GLORY_ATK * DD_GLORY_UNITS * (C4_FACTOR - 1), target=SELF,
                     source="C4: Слава ×1.3 (АТК себе)"),
            ) + _dd_glory_others(C4_FACTOR - 1, "C4 (Слава ×1.3)"),
        ),
        6: Constellation(
            number=6, name="C6",
            buffs=(
                Buff(S.SC_BONUS, C6_GLORY_SG_BONUS, target=SELF,
                     source="C6 Слава: +20% урона звёздного проводника себе"),
                Buff(S.SSW_BONUS, C6_GLORY_SG_BONUS, target=SELF,
                     source="C6 Слава: +20% урона звёздного рассеивания себе"),
            ),
        ),
    },
    note="ДД на поле (Слава).",
)


def anastasia_dd(mode: str = "sc", seg_tags: Sequence[Sequence[str]] = ((ON,),) * 4,
                 n5: int = DD_LOOPS) -> Character:
    """Анастасия-ДД: hEQ (N5 sE)×3 (n5=3) или hEQ N5sE N5sE sE (n5=2).

    n5       — сколько цепочек N5 в комбо; стадий Annihilation всегда 3,
               отрезки без N5 (последние) — только sE;

    mode     — "sc" или "ssw";
    seg_tags — теги 4 отрезков комбо: [hEQ, N5 sE №1, N5 sE №2, N5 sE №3]
               (окна баффов отряда: Эпос, Сахароза, Изумрудная тень, C6 Дионы…);
    """
    if mode not in ("sc", "ssw"):
        raise ValueError(f"mode должен быть 'sc' или 'ssw', а не {mode!r}")
    segs = [tuple(t) for t in seg_tags]
    assert len(segs) == 1 + DD_LOOPS, "нужно 4 набора тегов: hEQ и три N5 sE"
    direct = stellar_conduct if mode == "sc" else stellar_swirl
    label = "SC" if mode == "sc" else "SSW"
    g = ("glory_c2",)
    loops = segs[1:]
    assert 1 <= n5 <= DD_LOOPS, n5
    spear = loops[:n5]

    sources = [
        elemental("Навык удержанием — начальный урон", "atk", DD_HOLD_MV, "cryo", "skill",
                  [occ(1, *segs[0])]),
        direct(f"Взрыв «The Evernight Yields to Dawn» ({label})", "atk", DD_BURST_MV[mode],
               "cryo", [occ(1, *segs[0])], kind="burst", multipliers=g),
    ]
    for n in range(1, 6):
        mv, inst = SPEAR_CRYO[n]
        sources.append(elemental(f"Копьё {n}-й удар — крио", "atk", mv, "cryo", "normal",
                                 [occ(inst, *t) for t in spear], multipliers=g))
        sources.append(direct(f"Копьё {n}-й удар — {label}", "atk", SPEAR_SG[mode][n], "cryo",
                              [occ(1, *t) for t in spear], kind="normal", multipliers=g))
    sources.append(elemental("Annihilation 1 — крио", "atk", DOOM1_CRYO_MV, "cryo", "skill",
                             [occ(DOOM1_CRYO_HITS, *loops[0])], multipliers=g))
    for i, t in enumerate(loops):
        sources.append(direct(f"Annihilation {i + 1} — {label}", "atk", DOOM_SG[mode][i], "cryo",
                              [occ(1, *t)], kind="skill", multipliers=g))
    return with_rotation(
        ANASTASIA_DD_KIT,
        sources=tuple(sources),
        constellation_sources={
            6: (direct(f"C6: Annihilation 3 ×250% ({label})", "atk",
                       DOOM_SG[mode][2] * C6_GLORY_DOOM3, "cryo", [occ(1, *loops[2])],
                       kind="skill", multipliers=g),),
        },
    )


# --------------------------------------------------------------------------- #
#  ДД-комбо под отряды. Теги — по отрезкам комбо:                              #
#    0: hEQ (навык удержанием + взрыв)                                        #
#    1: N5 sE №1 (копьё + Annihilation 1)                                     #
#    2: N5 sE №2 (копьё + Annihilation 2)                                     #
#    3: N5 sE №3 (копьё + Annihilation 3; в коротком комбо — только sE)        #
#  Каждая строка — окна баффов отряда на этом отрезке.                         #
# --------------------------------------------------------------------------- #

#: Без временных баффов отряда (Даника/Алеша/Одетта, Даника/Яэ/Одетта)
ANASTASIA_COMBO_DICT["dd_sc"] = anastasia_dd("sc", (
    (ON,NOBLE,CATS_TAIL,SEVEN_SACRED,INST,TTDS_FULL,TTDS_HALF,VV_CRYO, SUCROSE_PASSIVE),
    (ON,NOBLE,CATS_TAIL,SEVEN_SACRED,INST,TTDS_FULL,TTDS_HALF,VV_CRYO, SUCROSE_PASSIVE),
    (ON,CATS_TAIL,SEVEN_SACRED),
    (ON,SEVEN_SACRED),
))
ANASTASIA_COMBO_DICT["dd_sc_short"] = anastasia_dd("sc", (
    (ON,NOBLE,CATS_TAIL,SEVEN_SACRED,INST,TTDS_FULL,TTDS_HALF,VV_CRYO, SUCROSE_PASSIVE),
    (ON,NOBLE,CATS_TAIL,SEVEN_SACRED,INST,TTDS_FULL,TTDS_HALF,VV_CRYO, SUCROSE_PASSIVE),
    (ON,CATS_TAIL,SEVEN_SACRED),
    (ON,SEVEN_SACRED),
), n5=2)

#: Отряд Даника / Митя / Одетта: Эпос Мити на первых трёх отрезках
_SEG_MITYA = (
    (ON, TTDS_FULL, TTDS_HALF),
    (ON, TTDS_FULL, TTDS_HALF),
    (ON,),
    (ON,),
)
ANASTASIA_COMBO_DICT["dd_sc_mitya"] = anastasia_dd("sc", _SEG_MITYA)
ANASTASIA_COMBO_DICT["dd_sc_mitya_short"] = anastasia_dd("sc", _SEG_MITYA, n5=2)

#: Отряд Сахароза / Алеша / Диона: окна Сахарозы (Инструктор, A1/A4, Эпос) —
#: на hEQ и первой N5 sE; Изумрудная тень и Диона — до третьей N5 sE
_SEG_SUCROSE_DIONA = (
    (ON, INST, SUCROSE_PASSIVE, TTDS_FULL, TTDS_HALF, VV_CRYO, CATS_TAIL),
    (ON, SUCROSE_PASSIVE, TTDS_FULL, TTDS_HALF, VV_CRYO, CATS_TAIL),
    (ON, VV_CRYO, CATS_TAIL),
    (ON,),
)
ANASTASIA_COMBO_DICT["dd_sc_sucrose_diona"] = anastasia_dd("sc", _SEG_SUCROSE_DIONA)
ANASTASIA_COMBO_DICT["dd_sc_sucrose_diona_short"] = anastasia_dd("sc", _SEG_SUCROSE_DIONA, n5=2)

#: Отряд Ци Ци / Одетта / Алеша: окно Ци Ци (SEVEN_SACRED) — до третьей N5 sE.
#: Бафф Ци Ци — урон звёздного рассеивания, на проводник Анастасии не влияет.
_SEG_QIQI = (
    (ON, SEVEN_SACRED),
    (ON, SEVEN_SACRED),
    (ON, SEVEN_SACRED),
    (ON,),
)
ANASTASIA_COMBO_DICT["dd_sc_qiqi"] = anastasia_dd("sc", _SEG_QIQI)
ANASTASIA_COMBO_DICT["dd_sc_qiqi_short"] = anastasia_dd("sc", _SEG_QIQI, n5=2)

#: Отряд Ци Ци / Сахароза / Алеша: окна Сахарозы — hEQ и первая N5 sE;
#: Изумрудная тень и Ци Ци — до третьей N5 sE
_SEG_SUCROSE_QIQI = (
    (ON, INST, SUCROSE_PASSIVE, TTDS_FULL, TTDS_HALF, VV_CRYO, SEVEN_SACRED),
    (ON, INST, SUCROSE_PASSIVE, TTDS_FULL, TTDS_HALF, VV_CRYO, SEVEN_SACRED),
    (ON, VV_CRYO, SEVEN_SACRED),
    (ON,),
)
ANASTASIA_COMBO_DICT["dd_sc_sucrose_qiqi"] = anastasia_dd("sc", _SEG_SUCROSE_QIQI)
ANASTASIA_COMBO_DICT["dd_sc_sucrose_qiqi_short"] = anastasia_dd("sc", _SEG_SUCROSE_QIQI, n5=2)

#: Отряд Диона / Одетта / Алеша: C6 Дионы (CATS_TAIL) — до третьей N5 sE
_SEG_DIONA = (
    (ON, CATS_TAIL),
    (ON, CATS_TAIL),
    (ON, CATS_TAIL),
    (ON,),
)
ANASTASIA_COMBO_DICT["dd_sc_diona"] = anastasia_dd("sc", _SEG_DIONA)
ANASTASIA_COMBO_DICT["dd_sc_diona_short"] = anastasia_dd("sc", _SEG_DIONA, n5=2)
