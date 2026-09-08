"""
ШАБЛОНЫ для добавления своих персонажей, оружия, артефактов и отрядов.

Скопируйте нужный блок в свой файл (или прямо сюда) и заполните.
Ничего из этого файла не используется в расчётах — он только для примера.

Содержание:
    1. Персонаж
    2. Созвездия
    3. Оружие
    4. Набор артефактов
    5. Сборка (Build)
    6. Отряд (Team)
    7. Ростер (массовый перебор)
    8. Шпаргалка по статам и тегам
"""

from __future__ import annotations

from ..core.buffs import OTHERS, SELF, TEAM, Buff, temp
from ..core.engine import Config, Team
from ..core.entities import (ArtifactSet, Build, Character, Constellation,
                             Enemy, Weapon)
from ..core.reactions import ssw_anemo, ssw_vortex
from ..core.roster import Roster, Variation
from ..core.sources import elemental, occ, stellar_swirl
from ..core.stats import S
from .tags import INST, OFF, ON

# =========================================================================== #
# 1. ПЕРСОНАЖ                                                                 #
# =========================================================================== #
TEMPLATE_CHARACTER = Character(
    name="Имя персонажа",
    element="anemo",              # anemo / cryo / pyro / hydro / electro / geo / dendro
    weapon_type="catalyst",
    level=90,
    default_field=OFF,            # ON, если персонаж находится на поле во время реакций
    crit_mode="expected",         # expected | always | none | balance

    # --- база персонажа (без оружия и артефактов) --------------------------- #
    stats={
        S.BASE_ATK: 300.0,
        # S.BASE_HP: 15000.0,
        # S.BASE_DEF: 800.0,
        # S.BASE_EM: 115.0,       # например прибавка за возвышение
    },

    # --- постоянные и псевдопостоянные усиления ----------------------------- #
    buffs=(
        # Постоянный бафф — без requires:
        Buff(S.ATK_PCT, 0.20, target=SELF, source="Пассивка: +20% АТК"),

        # Временный бафф — работает только в своём окне (теге состояния):
        temp(S.DMG_BONUS, 0.30, INST, target=TEAM,
             source="Взрыв стихии: +30% урона отряду"),

        # Бафф, зависящий от стата другого персонажа:
        Buff(S.FLAT_EM,
             lambda ctx: 0.25 * ctx.own("em"),
             target=OTHERS,
             source="A4: +25% своего МС отряду"),

        # Бонус только для конкретной стихии или типа атаки:
        Buff("dmg_bonus.cryo", 0.15, target=SELF, source="+15% крио урона"),
        Buff("dmg_bonus.burst", 0.10, target=SELF, source="+10% урона взрыва"),

        # Снижение сопротивления цели — тоже обычный бафф (0.20 = -20% RES).
        # Постоянное:
        Buff("res_reduction.cryo", 0.40, target=TEAM, source="4ч набора: -40% крио сопр."),
        # Временное — работает только внутри своего окна:
        temp("res_reduction", 0.20, INST, target=TEAM, source="C2: -20% сопр. в окне"),
    ),

    # --- источники урона ---------------------------------------------------- #
    sources=(
        # Обычный элементальный урон.
        # mv — множитель таланта в ДОЛЯХ: 103.94% -> 1.0394
        elemental(
            name="Навык",
            scaling="atk",             # atk | hp | def | em
            mv=1.0394 + 0.8084 * 20,   # можно писать формулой, как в таблице
            element="cryo",
            kind="skill",              # normal | charged | plunge | skill | burst | ...
            occurrences=[
                occ(1, ON),            # 1 раз, пока персонаж на поле
                occ(3, ON, INST),      # ещё 3 раза внутри окна INST
            ],
        ),

        # Прямой урон звёздного рассеивания (защита цели не учитывается).
        stellar_swirl(
            name="Навык — SSW",
            scaling="em",
            mv=10.0,
            element="anemo",
            occurrences=[occ(1, ON), occ(3, ON, INST)],
        ),
    ),

    # --- дополнительные множители (пассивки вида «×(1 + f(АТК))») ------------ #
    multipliers={
        "my_passive": lambda stats: min(stats.atk - 1000.0, 3000.0) * 0.00015 + 1.0,
    },

    # --- созвездия ---------------------------------------------------------- #
    constellations={
        1: Constellation(
            number=1, name="C1",
            stats={S.CRIT_DMG: 0.20},
            buffs=(Buff(S.DMG_BONUS, 0.10, target=SELF),),
            sources=(  # C1 может добавлять новые источники урона
                stellar_swirl("C1: доп. рассеивание", "em", 4.0, "anemo",
                              [occ(1, ON)]),
            ),
            # ...либо менять существующие:
            # patches={"Навык": lambda src: replace(src, mv=src.mv * 1.5)},
        ),
    },
)


# =========================================================================== #
# 3. ОРУЖИЕ                                                                   #
# =========================================================================== #
TEMPLATE_WEAPON = Weapon(
    name="Название оружия",
    base_atk=510.0,
    refinement=1,
    # статы, одинаковые на всех рангах:
    stats={S.CRIT_DMG: 0.882},
    # статы, зависящие от ранга пробуждения:
    stats_by_refinement={
        1: {S.ATK_PCT: 0.20},
        5: {S.ATK_PCT: 0.40, S.BASE_EM: 160.0},
    },
    buffs_by_refinement={
        5: (temp(S.DMG_BONUS, 0.20, INST, target=SELF,
                 source="Оружие R5: +20% урона после навыка"),),
    },
)
# использование: TEMPLATE_WEAPON.at(5)


# =========================================================================== #
# 4. НАБОР АРТЕФАКТОВ                                                         #
# =========================================================================== #
TEMPLATE_ARTIFACT_SET = ArtifactSet(
    name="Название набора",
    pieces=4,
    stats_by_pieces={
        2: {S.ATK_PCT: 0.18},
    },
    buffs_by_pieces={
        4: (temp(S.BASE_EM, 120.0, INST, target=OTHERS,
                 source="4ч: +120 МС отряду"),),
    },
)


# =========================================================================== #
# 5. СБОРКА                                                                   #
# =========================================================================== #
TEMPLATE_BUILD = Build(
    character=TEMPLATE_CHARACTER,
    constellation=1,
    weapon=TEMPLATE_WEAPON.at(5),
    artifacts=(TEMPLATE_ARTIFACT_SET,),
    # всё, что не разложено по источникам: главстаты, сабстаты, ручные правки
    extra_stats={
        S.ATK_PCT: 0.466 * 2,
        S.FLAT_ATK: 350.0,
        S.BASE_EM: 187.0,
        S.CRIT_RATE: 0.75,
        S.CRIT_DMG: 1.60,
        S.CRIT_VALUE: 3.40,
    },
    extra_buffs=(),
    extra_sources=(),
    time=8.5,                   # сколько секунд ротации занимает персонаж
    # label="Мидзуки #2",       # если в отряде два персонажа с одним именем
)


# =========================================================================== #
# 6. ОТРЯД                                                                    #
# =========================================================================== #
def template_team() -> Team:
    return Team(
        name="Мой отряд",
        builds=[TEMPLATE_BUILD],           # обычно четыре сборки
        enemy=Enemy(
            # БАЗОВОЕ сопротивление цели в долях (0.10 = 10%).
            # Всё, что его снижает, задаётся баффами "res_reduction[.стихия]" —
            # тогда снижение может быть временным и разным для разных ударов.
            res={"anemo": 0.10, "cryo": 0.10},
            # Альтернатива — ГОТОВЫЕ множители (как в таблице). Берутся как есть,
            # снижения сопротивления к ним НЕ применяются:
            # res_mult={"anemo": 0.90, "cryo": 1.15},
            def_mult=0.4875,               # множитель защиты цели
            elevation=0.0,                 # «Возвышение», итог = 1 + elevation
        ),
        reactions=(
            ssw_anemo("Имя персонажа", 3),
            ssw_anemo("Имя персонажа", 7, INST),
            ssw_vortex(3, 2, INST),
        ),
        rotation="Описание ротации",
        config=Config(excel_compat=False),
    )


# =========================================================================== #
# 7. РОСТЕР (массовые расчёты)                                                #
# =========================================================================== #
def template_roster() -> Roster:
    team = template_team()
    return Roster(
        base_team=team,
        variations=[
            # перебрать оружие у одного персонажа
            Variation(slot="Имя персонажа",
                      weapons=[TEMPLATE_WEAPON.at(1), TEMPLATE_WEAPON.at(5)]),
            # можно добавить вторую ось — будет декартово произведение
            # Variation(slot="Другой персонаж", constellations=[0, 1, 2]),
            # или полная замена персонажа:
            # Variation(slot="Другой персонаж", builds=[build_a, build_b]),
        ],
    )
# roster.ranked("dps") -> список TeamResult, отсортированный по DPS


# =========================================================================== #
# 8. ШПАРГАЛКА                                                                #
# =========================================================================== #
CHEATSHEET = """
СТАТЫ (gi_damage.core.stats.S)
    base_atk / atk_pct / flat_atk      итог = base*(1+pct) + flat
    base_hp  / hp_pct  / flat_hp
    base_def / def_pct / flat_def
    base_em  / em_pct  / flat_em       flat_em прибавляется ПОСЛЕ процентов
    crit_rate, crit_dmg                для crit_mode="expected"
    crit_value                         для crit_mode="balance"
    dmg_bonus                          общий бонус урона
    dmg_bonus.<стихия|тип>             например dmg_bonus.cryo, dmg_bonus.burst
    res_reduction[.<стихия>]           снижение сопротивления цели (0.2 = -20% RES)
    ssw_bonus                          «Stellar Swirl DMG Bonus%»
    ssw_base_inc                       «Base DMG Increase%» звёздного рассеивания
    elevation                          «Возвышение»
    flat_base_dmg                      «Дополнительный базовый урон»

ТЕГИ СОСТОЯНИЙ (gi_damage.data.tags)
    on_field / off_field               где персонаж
    instructor                         окно «Инструктор + A4 Сахарозы»
    ...любые свои строки

ЦЕЛЬ (Enemy)
    res        БАЗОВОЕ сопротивление по стихиям в долях; снижения из
               "res_reduction" вычитаются автоматически (рекомендуется)
    res_mult   готовые множители сопротивления; снижения к ним НЕ применяются
    def_mult   готовый множитель защиты
    Приоритет: res_override источника -> Enemy.res -> Enemy.res_mult
    Формулы:
        from gi_damage.core.formulas import (resistance_multiplier,
                                             inverse_resistance_multiplier,
                                             defense_multiplier)

ОКНО УСИЛЕНИЯ НА ВЕСЬ КУСОК РОТАЦИИ
    from gi_damage.core.entities import add_state_tags
    build = add_state_tags(build, "dreamdrifter")   # тег ко всем ударам сборки

РЕЖИМЫ КРИТА
    expected     1 + min(шанс,1)*крит.урон   (математическое ожидание)
    always       1 + крит.урон
    none         1
    balance      1 + CV²/8, если CV меньше 4, иначе CV - 1
"""
