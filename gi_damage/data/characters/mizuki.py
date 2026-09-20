"""
Мидзуки — анемо, main dps. Часть кита, НЕ зависящая от ротации/отряда.

Источники урона (в т.ч. по созвездиям C1) сюда не входят — они подставляются
per-team через core.entities.with_rotation(), см. data/teams/*.py.
"""

from __future__ import annotations
from dataclasses import replace  # noqa: F401 — для patches= в файлах отрядов

from ...core.buffs import OTHERS, SELF, TEAM, Buff
from ...core.entities import Character, Constellation, with_rotation
from ...core.stats import S
from ..tags import DREAM, INST, OFF, ON, MIZUKI_C1, FROSTGLOW, BREEZEBORNE
from ...core.sources import elemental, occ, stellar_swirl

SSW_EM_RATE = 0.045          # прирост урона SSW за 100 МС (базовый уровень)
SSW_EM_RATE_C3 = 0.054       # то же с C3
C6_EM_THRESHOLD = 500        # МС сверх этого порога конвертируется в крит
C6_RATE_PER_EM = 0.0004      # +0.04% крит. шанса за 1 МС, максимум +20%
C6_DMG_PER_EM = 0.0016       # +0.16% крит. урона за 1 МС, максимум +80%
C6_MAX_EXCESS = 500          # обе планки упираются ровно на 1000 МС


def _c6_crit_value(em: float) -> float:
    """Прибавка к крит-вэлью от C6. CV = 2*шанс + крит.урон."""
    excess = min(max(em - C6_EM_THRESHOLD, 0.0), C6_MAX_EXCESS)
    return (2 * C6_RATE_PER_EM + C6_DMG_PER_EM) * excess


MIZUKI_KIT = Character(
    name="Мидзуки",
    element="anemo",
    weapon_type="catalyst",
    default_field=ON,
    crit_mode="balance",
    stats={
        S.BASE_ATK: 215.0,
        S.BASE_EM: 115,
        S.CRIT_VALUE: 0.6,
    },
    buffs=(
        Buff(S.EM_PCT, 0.10, target=SELF, source="Мидзуки A4"),

        # Талант: бонус урона звёздного рассеивания = 4.5% за каждые 100 МС Мидзуки.
        # Себе — считается по своему же МС в текущем окне.
        Buff(S.SSW_BONUS,
             lambda ctx: 0.045 * ctx.own("em") / 100.0,
             target=SELF, requires=(ON,),
             source="Мидзуки: 4.5% урона SSW за 100 МС (себе)"),

        # Отряду — по МС Мидзуки на поле, в том же окне Инструктора.
        Buff(S.SSW_BONUS,
             lambda ctx: 0.045 * ctx.stat("Мидзуки", "em",
                                          ctx.mirror(ON, keep=[INST])) / 100.0,
             target=OTHERS, requires=(OFF,),
             source="Мидзуки: 4.5% урона SSW за 100 МС (отряду)"),

        # Отряду: +10% от «голого» МС Мидзуки, пока она на поле.
        Buff(S.BASE_EM,
             lambda ctx: 0.10 * ctx.stat("Мидзуки", S.BASE_EM,
                                         ctx.mirror(ON, keep=[INST])),
             target=OTHERS, requires=(OFF,),
             source="Мидзуки A4"),
    ),
    sources=(),
    constellations={
        1: Constellation(number=1, name="C1",
                             buffs=(Buff(S.FLAT_BASE_DMG,lambda ctx: 5.5*ctx.own("em"),
         target=TEAM, requires=(MIZUKI_C1,),
         source="С1 мидзуки"),)),

        2: Constellation(
            number=2,
            name="C2",
            buffs=tuple(
                Buff(f"dmg_bonus.{element}",
                     lambda ctx: 0.0004 * ctx.stat("Мидзуки", "em",
                                                   ctx.mirror(ON, keep=[INST, DREAM])),
                     target=TEAM, requires=(DREAM,), temporary=True,
                     source=f"C2 Мидзуки: +0.04% {element} урона за 1 МС")
                for element in ("pyro", "hydro", "cryo", "electro")
            ) + tuple(
                Buff(f"res_reduction.{element}", 0.20,
                     target=TEAM, requires=(DREAM,), temporary=True,
                     source=f"C2 Мидзуки: -20% сопротивления к {element}")
                for element in ("pyro", "hydro", "cryo", "electro", "anemo")
            ),
        ),
        3: Constellation(
            number=3,
            name="C3",
            patches={
                "Использование навыка (АТК)": lambda s: replace(s, mv=1.2271),
                "Навык (АТК)":                lambda s: replace(s, mv=0.9544),
            },
            # Талант «за 100 МС» усиливается с 4.5% до 5.4%. Базовый бафф никуда
            buffs=(
                Buff(S.SSW_BONUS,
                    lambda ctx: (SSW_EM_RATE_C3 - SSW_EM_RATE) * ctx.own("em") / 100.0,
                    target=SELF, requires=(ON,),
                    source="C3: SSW за 100 МС 4.5% -> 5.4% (себе)"),
                Buff(S.SSW_BONUS,
                    lambda ctx: (SSW_EM_RATE_C3 - SSW_EM_RATE)
                                * ctx.stat("Мидзуки", "em",
                                            ctx.mirror(ON, keep=[INST])) / 100.0,
                    target=OTHERS, requires=(OFF,),
                    source="C3: SSW за 100 МС 4.5% -> 5.4% (отряду)"),
            ),
        ),
        6: Constellation(
            number=6,
            name="C6",
            buffs=(
                # Внутри Дрейфа грёз весь урон звёздного рассеивания отряда
                # получает +10% крит. шанса и +20% крит. урона.
                Buff("crit_value.stellar_swirl", 2 * 0.10 + 0.20,
                    target=TEAM, requires=(DREAM,), temporary=True,
                    source="C6: крит по урону SSW (+10% шанс, +20% урон)"),

                # МС сверх 500 конвертируется в крит самой Мидзуки.
                Buff(S.CRIT_VALUE,
                    lambda ctx: _c6_crit_value(ctx.own("em")),
                    target=SELF,
                    source="C6: МС сверх 500 -> крит (до +20% шанса, +80% урона)"),
            ),
        ),
    },
    note="Анемо, main dps",
)

MIZUKI_COMBO_DICT = {
    "mizuki_short_combo" : with_rotation(
    MIZUKI_KIT,
    sources=(
        elemental("Использование навыка (АТК)", "atk", 1.0394, "anemo", "skill",
                  [occ(1, ON, DREAM)]),
        elemental("Навык (АТК)", "atk", 0.8084, "anemo", "skill",
                  [occ(10, ON, DREAM)]),
        elemental("Использование взрыва (АТК)", "atk", 1.6934, "anemo", "burst",
                  [occ(1, ON, DREAM)]),
        elemental("Взрыв (АТК)", "atk", 1.2701, "anemo", "burst",
                  [occ(8, ON, DREAM)]),
        elemental("Перья (МС)", "em", 10.0, "anemo", "passive",
                  [occ(1, ON, DREAM), occ(2, ON, INST, DREAM)],
                  note="Дополнительный базовый урон для инстанции навыка"),
        stellar_swirl("Навык — звёздное рассеивание (МС)", "em", 10.0, "anemo",
                      [occ(1, ON, DREAM, FROSTGLOW), occ(2, ON, INST, DREAM, FROSTGLOW)],
                      note="Строка «Skill EM SSW MV%» = 1000%"),
    ),
    constellation_sources={
        1: (
            stellar_swirl("C1: доп. звёздное рассеивание (МС)", "em", 4.0,
                          "anemo", [occ(1, ON, DREAM, FROSTGLOW),
                                    occ(2, ON, INST, DREAM, FROSTGLOW)]),
        ),
    },
),

    "mizuki_sacfrag_combo" : with_rotation(
    MIZUKI_KIT,
    sources=(
        elemental("Использование навыка (АТК)", "atk", 1.0394, "anemo", "skill",
                  [occ(2, ON, DREAM)]),
        elemental("Навык (АТК)", "atk", 0.8084, "anemo", "skill",
                  [occ(11, ON, DREAM)]),
        elemental("Использование взрыва (АТК)", "atk", 1.6934, "anemo", "burst",
                  [occ(1, ON, DREAM)]),
        elemental("Взрыв (АТК)", "atk", 1.2701, "anemo", "burst",
                  [occ(8, ON, DREAM)]),
        elemental("Перья (МС)", "em", 10.0, "anemo", "passive",
                  [occ(1, ON, DREAM), occ(3, ON, INST, DREAM)],
                  note="Дополнительный базовый урон для инстанции навыка"),
        stellar_swirl("Навык — звёздное рассеивание (МС)", "em", 10.0, "anemo",
                      [occ(1, ON, DREAM, FROSTGLOW), occ(3, ON, INST, DREAM, FROSTGLOW, BREEZEBORNE)],
                      note="Строка «Skill EM SSW MV%» = 1000%"),
    ),
    constellation_sources={
        1: (
            stellar_swirl("C1: доп. звёздное рассеивание (МС)", "em", 4.0,
                          "anemo", [occ(1, ON, DREAM, FROSTGLOW),
                                    occ(3, ON, INST, DREAM, FROSTGLOW, BREEZEBORNE)]),
        ),
    },
),
    
    "mizuki_long_combo" : with_rotation(
    MIZUKI_KIT,
    sources=(
        elemental("Использование навыка (АТК)", "atk", 1.0394, "anemo", "skill",
                  [occ(1, ON, DREAM)]),
        elemental("Навык (АТК)", "atk", 0.8084, "anemo", "skill",
                  [occ(13, ON, DREAM)]),
        elemental("Использование взрыва (АТК)", "atk", 1.6934, "anemo", "burst",
                  [occ(1, ON, DREAM)]),
        elemental("Взрыв (АТК)", "atk", 1.2701, "anemo", "burst",
                  [occ(8, ON, DREAM)]),
        elemental("Перья (МС)", "em", 10.0, "anemo", "passive",
                  [occ(2, ON, DREAM), occ(2, ON, INST, DREAM)],
                  note="Дополнительный базовый урон для инстанции навыка"),
        stellar_swirl("Навык — звёздное рассеивание (МС)", "em", 10.0, "anemo",
                      [occ(1, ON, DREAM, FROSTGLOW, BREEZEBORNE), occ(2, ON, INST, DREAM, FROSTGLOW, BREEZEBORNE),
                       occ(1, ON, FROSTGLOW),],
                      note="Строка «Skill EM SSW MV%» = 1000%"),
    ),
    constellation_sources={
        1: (
            stellar_swirl("C1: доп. звёздное рассеивание (МС)", "em", 4.0,
                          "anemo", [occ(1, ON, DREAM, FROSTGLOW, BREEZEBORNE),
                                    occ(2, ON, INST, DREAM, FROSTGLOW, BREEZEBORNE)]),
        ),
    },
)
}