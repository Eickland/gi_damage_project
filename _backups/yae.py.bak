"""
Яэ Мико — карманный саб-ДД, катализатор. Всегда в отрядах звёздного
проводника (Radiance: Stellar-Conduct). Ротация: EEE, 2.4 с, без взрыва.

C1 — базовая линия. Все её баффы считаются постоянными.

ВНИМАНИЕ: множители молний Сесшо Сакуры в задании не даны — взяты
значения 10 уровня навыка (60.67/75.84/94.80/118.50 % на 1 ур. × 1.8).
Поправьте SAKURA_MV, если нужен другой уровень таланта.
"""

from __future__ import annotations
from dataclasses import replace  # noqa: F401 — для patches= в файлах отрядов

from ...core.buffs import OTHERS, SELF, TEAM, Buff, temp
from ...core.entities import Character, Constellation, with_rotation
from ...core.stats import S
from ..tags import *
from ...core.sources import elemental, occ, stellar_conduct

# --------------------------------------------------------------------------- #
#  Множители (в долях)                                                         #
# --------------------------------------------------------------------------- #
#: Урон молнии Сесшо Сакуры по уровню сакуры (талант 10)
SAKURA_MV = {1: 1.0921, 2: 1.3651, 3: 1.7064, 4: 2.1330}
SAKURA_LEVEL_C0 = 3      # 3 сакуры рядом, максимум 3 ур.
SAKURA_LEVEL_C2 = 4      # C2: максимум 4 ур.

EM_SAKURA_BONUS = 0.0015      # A4 Enlightened Blessing: +0.15% урона сакуры за 1 МС
ENHANCED_ATK = 0.80           # Edict of Cleansing: усиленная молния +80% АТК
ENHANCED_SC_ATK = 2.00        # Radiance: доп. инстанс 200% АТК (звёздный проводник)
A1_SC_ATK = 0.50              # Radiance A1: доп. молния 50% АТК (звёздный проводник)

C1_BONUS = 0.50               # C1: +50% электро урона и урона SC отряду
C2_EM = 200.0                 # C2: +200 МС при сакуре 4 ур.
C6_DEF_IGNORE = 0.60          # C6: молнии сакуры игнорируют 60% защиты
C6_SC_CRIT_DMG = 2.00         # C6: +200% крит. урона звёздного проводника

#: Количество ударов за ротацию отряда
ENHANCED_HITS = 7             # усиленных молний (раз в ~3 с)
NORMAL_HITS = 15              # обычных: 3 сакуры × ~22 с / 2.9 с ≈ 22 удара, минус 7 усиленных
A1_STRIKES = 3                # доп. молний A1 (по одной на каждое E при 3 сакурах рядом)

#: Стаки «полярности» для звёздного проводника Яэ (как у Одетты вне поля)
YAE_POLAR_STACKS = 8
YAE_POLAR_STACKS_WRIO = 5


YAE_KIT = Character(
    name="Яэ Мико",
    element="electro",
    weapon_type="catalyst",
    default_field=OFF,
    crit_mode="balance",
    stats={
        S.BASE_ATK: 340.0,
        # 24.2% КШ × 2 + 50% КУ
        S.CRIT_VALUE: 0.242 * 2 + 0.50,
    },
    buffs=(
        Buff(f"{S.DMG_BONUS}.{SESSHOU_SAKURA}",
             lambda ctx: EM_SAKURA_BONUS * ctx.own("em"), target=SELF,
             source="Enlightened Blessing: +0.15% урона сакуры за 1 МС"),
    ),
    sources=(),
    constellations={
        1: Constellation(
            number=1,
            name="C1",
            buffs=(
                Buff("dmg_bonus.electro", C1_BONUS, target=TEAM,
                     source="C1 Яэ: +50% электро урона отряду"),
                Buff(S.SC_BONUS, C1_BONUS, target=TEAM,
                     source="C1 Яэ: +50% урона звёздного проводника отряду"),
            ),
        ),
        2: Constellation(
            number=2,
            name="C2",
            buffs=(
                Buff(S.BASE_EM, C2_EM, target=SELF,
                     source="C2 Яэ: +200 МС (сакура 4 ур.)"),
                Buff(S.BASE_EM, C2_EM, target=OTHERS, requires=(ON,),
                     source="C2 Яэ: +200 МС активному персонажу"),
            ),
            patches={
                "Сесшо Сакура — молния":
                    lambda s: replace(s, mv=SAKURA_MV[SAKURA_LEVEL_C2]),
                "Сесшо Сакура — усиленная молния":
                    lambda s: replace(s, mv=SAKURA_MV[SAKURA_LEVEL_C2] + ENHANCED_ATK),
            },
        ),
        6: Constellation(
            number=6,
            name="C6",
            buffs=(
                Buff(f"{S.DEF_IGNORE}.{SESSHOU_SAKURA}", C6_DEF_IGNORE, target=SELF,
                     source="C6 Яэ: молнии сакуры игнорируют 60% защиты"),
                Buff("crit_value.stellar_conduct", C6_SC_CRIT_DMG, target=SELF,
                     source="C6 Яэ: +200% крит. урона звёздного проводника"),
            ),
        ),
    },
    note="Только отряды звёздного проводника.",
)

#: Окна отряда, в которых находится Яэ (вне поля). Расставляйте, как нужно.
_YAE_TAGS = (OFF, NOBLE,ELEGY)

YAE_COMBO_DICT = {
    "yae_sc_long_combo": with_rotation(
        YAE_KIT,
        sources=(
            elemental("Сесшо Сакура — молния", "atk", SAKURA_MV[SAKURA_LEVEL_C0],
                      "electro", "skill", [occ(NORMAL_HITS, *_YAE_TAGS)],
                      extra_tags=(SESSHOU_SAKURA,)),
            elemental("Сесшо Сакура — усиленная молния", "atk",
                      SAKURA_MV[SAKURA_LEVEL_C0] + ENHANCED_ATK,
                      "electro", "skill", [occ(ENHANCED_HITS, *_YAE_TAGS)],
                      extra_tags=(SESSHOU_SAKURA,)),
            stellar_conduct("Усиленная молния — звёздный проводник", "atk",
                            ENHANCED_SC_ATK, "electro",
                            [occ(ENHANCED_HITS-3, *_YAE_TAGS),
                             occ(3, OFF)], kind="skill",
                            polar_stacks=YAE_POLAR_STACKS),
            stellar_conduct("A1: доп. молния — звёздный проводник", "atk",
                            A1_SC_ATK, "electro",
                            [occ(A1_STRIKES, ON, NOBLE)], kind="skill",
                            polar_stacks=YAE_POLAR_STACKS),
        ),
    ),
    "yae_sc_wrio_combo": with_rotation(
        YAE_KIT,
        sources=(
            elemental("Сесшо Сакура — молния", "atk", SAKURA_MV[SAKURA_LEVEL_C0],
                      "electro", "skill", [occ(NORMAL_HITS, *_YAE_TAGS)],
                      extra_tags=(SESSHOU_SAKURA,)),
            elemental("Сесшо Сакура — усиленная молния", "atk",
                      SAKURA_MV[SAKURA_LEVEL_C0] + ENHANCED_ATK,
                      "electro", "skill", [occ(ENHANCED_HITS, *_YAE_TAGS)],
                      extra_tags=(SESSHOU_SAKURA,)),
            stellar_conduct("Усиленная молния — звёздный проводник", "atk",
                            ENHANCED_SC_ATK, "electro",
                            [occ(ENHANCED_HITS-3, *_YAE_TAGS),
                             occ(1, OFF)], kind="skill",
                            polar_stacks=YAE_POLAR_STACKS_WRIO),
            stellar_conduct("A1: доп. молния — звёздный проводник", "atk",
                            A1_SC_ATK, "electro",
                            [occ(A1_STRIKES, ON, NOBLE)], kind="skill",
                            polar_stacks=YAE_POLAR_STACKS_WRIO),
        ),
    ),
}
