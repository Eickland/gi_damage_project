"""
Формулы урона.

1. Обычный элементальный урон (KQM):
   https://library.keqingmains.com/combat-mechanics/damage/damage-formula

       Урон = Базовый урон × (1 + Бонус урона) × Защита × Сопротивление
              × Крит × Возвышение

2. Прямой урон звёздного рассеивания (Stellar Swirl Direct DMG):

       База = Стат × Множитель таланта × (1 + Бонус базового урона)
              × (1 + 6·МС/(МС+2000) + Бонус урона звёздной реакции)
       Итог = (База + Доп. базовый урон) × Сопротивление × Крит × Возвышение

3. Урон реакции звёздного рассеивания:

       Урон = 1446.85 × Базовый множитель × (1 + Бонус базового урона)
              × (1 + 6·МС/(МС+2000) + Бонус урона звёздной реакции)
              × Сопротивление × Крит × Возвышение

   Базовый множитель: 0.75 для анемо-рассеивания,
   2 при 1–2 стаках вихря и 3 при 3–6 стаках для крио-детонации.
"""

from __future__ import annotations

from .stats import S, Stats

#: Базовый урон реакции звёздного рассеивания на 90 ур.
STELLAR_SWIRL_BASE_DMG = 1446.85

#: Базовый множитель анемо-рассеивания
SSW_ANEMO_MULTIPLIER = 0.75

#: Базовые множители детонации вихря по количеству стаков
SSW_VORTEX_MULTIPLIER = {1: 2.0, 2: 2.0, 3: 3.0, 4: 3.0, 5: 3.0, 6: 3.0}


def em_swirl_term(em: float) -> float:
    """6·МС / (МС + 2000) — вклад мастерства стихий в звёздное рассеивание."""
    return 6.0 * em / (em + 2000.0)


def ssw_multiplier(stats: Stats, *tags: str) -> float:
    """(1 + 6·МС/(МС+2000) + Бонус урона звёздной реакции)."""
    return 1.0 + em_swirl_term(stats.em) + stats.ssw_bonus(*tags)


def base_increase(stats: Stats, *tags: str) -> float:
    """(1 + Бонус базового урона) — «Base DMG Increase%»."""
    return 1.0 + stats.ssw_base_inc(*tags)


def elemental_damage(base: float, stats: Stats, tags, def_mult: float,
                     res_mult: float, crit: float, elevation: float,
                     flat_base: float = 0.0) -> float:
    """Обычный элементальный урон."""
    return ((base + flat_base)
            * (1.0 + stats.dmg_bonus(*tags))
            * def_mult
            * res_mult
            * crit
            * (1.0 + elevation))


def stellar_swirl_direct(stat_value: float, mv: float, stats: Stats, tags,
                         res_mult: float, crit: float, elevation: float,
                         flat_base: float = 0.0) -> float:
    """Прямой урон звёздного рассеивания (из талантов)."""
    base = (stat_value * mv
            * base_increase(stats, *tags)
            * ssw_multiplier(stats, *tags))
    return (base + flat_base) * res_mult * crit * (1.0 + elevation)


def stellar_swirl_reaction(multiplier: float, stats: Stats, tags,
                           res_mult: float, crit: float, elevation: float,
                           base_dmg: float = STELLAR_SWIRL_BASE_DMG,
                           flat_base: float = 0.0,
                           excel_compat: bool = False) -> float:
    """Урон самой реакции звёздного рассеивания.

    excel_compat=True воспроизводит поведение исходной таблицы, где множитель
    (1 + Бонус базового урона) применён ДВАЖДЫ: один раз внутри строки «EMM»
    и второй раз в строке урона реакции. По формуле он должен применяться один раз.

    flat_base — плоская добавка к урону ЭТОЙ конкретной реакции (например,
    Lead Vocal/Chorus «Водяницы»); прибавляется до сопротивления/крита/возвышения,
    как и в остальных двух формулах.
    """
    inc = base_increase(stats, *tags)
    base = base_dmg * multiplier * inc * ssw_multiplier(stats, *tags)
    if excel_compat:
        base *= inc
    return (base + flat_base) * res_mult * crit * (1.0 + elevation)


def defense_multiplier(attacker_level: int, enemy_level: int,
                       def_reduction: float = 0.0, def_ignore: float = 0.0) -> float:
    """Классический множитель защиты цели (если нужно считать его, а не задавать)."""
    enemy_def = (enemy_level + 100) * max(0.0, 1.0 - def_reduction) * max(0.0, 1.0 - def_ignore)
    return (attacker_level + 100) / (attacker_level + 100 + enemy_def)


def resistance_multiplier(res: float) -> float:
    """Множитель сопротивления цели по её итоговому сопротивлению `res` (в долях).

        res < 0      ->  1 - res/2      (сопротивление в минусе работает вполсилы)
        0 <= res<0.75->  1 - res
        res >= 0.75  ->  1 / (4·res + 1)
    """
    if res < 0:
        return 1.0 - res / 2.0
    if res < 0.75:
        return 1.0 - res
    return 1.0 / (4.0 * res + 1.0)


def inverse_resistance_multiplier(mult: float) -> float:
    """Обратная функция: по готовому множителю вернуть сопротивление цели.

    Нужна, когда цель задана готовыми множителями (как в исходной таблице),
    а сверху надо доложить ещё одно снижение сопротивления.

        1.05 -> -0.10      1.15 -> -0.30      0.90 -> +0.10
    """
    if mult > 1.0:
        return 2.0 * (1.0 - mult)
    if mult >= 0.25:
        return 1.0 - mult
    return (1.0 / mult - 1.0) / 4.0


__all__ = [
    "STELLAR_SWIRL_BASE_DMG", "SSW_ANEMO_MULTIPLIER", "SSW_VORTEX_MULTIPLIER",
    "em_swirl_term", "ssw_multiplier", "base_increase",
    "elemental_damage", "stellar_swirl_direct", "stellar_swirl_reaction",
    "defense_multiplier", "resistance_multiplier",
    "inverse_resistance_multiplier", "S", "Stats",
]