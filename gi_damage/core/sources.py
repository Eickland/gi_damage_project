"""
Источники урона персонажа.

Источник урона = «что-то, что бьёт», описанное как процент от базового
параметра (атака / здоровье / защита / мастерство стихий).

Пример (Мидзуки, урон навыка):

    DamageSource(
        name="Навык",
        scaling="atk",
        mv=1.0394 + 0.8084 * 20,        # множитель таланта, 1.0 = 100%
        element="anemo",
        kind="skill",
        occurrences=[Occurrence(state("on_field"), 1)],
    )

`occurrences` — это и есть реализация принципа «по каждому временному
усилению добавить те источники урона, которые в нём происходят»:
один и тот же источник может срабатывать N раз в базовом окне и M раз
в окне усиления.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, List, Optional, Sequence, Tuple, Union

from .buffs import State, state

# Модель урона:
#   "elemental"     — обычный элементальный/физический урон (учитывает ЗЩ цели)
#   "stellar_swirl" — прямой урон звёздного рассеивания (ЗЩ цели НЕ учитывается,
#                     зато применяется множитель МС/бонуса SSW)
ELEMENTAL = "elemental"
STELLAR_SWIRL = "stellar_swirl"
STELLAR_CONDUCT = "stellar_conduct"
#: Прямой урон лунных реакций (Direct Lunar-…)
LUNAR_CRYSTALLIZE = "lunar_crystallize"
LUNAR_CHARGED = "lunar_charged"
LUNAR_BLOOM = "lunar_bloom"
LUNAR_MODELS = (LUNAR_CRYSTALLIZE, LUNAR_CHARGED, LUNAR_BLOOM)
#: Общий тег всех лунных реакций (для "elevation.lunar", "lunar_bonus" и т.п.)
LUNAR = "lunar"

MotionValue = Union[float, Callable[["object"], float]]


@dataclass(frozen=True)
class Occurrence:
    """Сколько раз источник срабатывает в данном состоянии."""

    state: State
    count: float = 1.0


def occ(count: float, *tags: str) -> Occurrence:
    """Короткая запись: occ(3, "off_field", "instructor")."""
    return Occurrence(state(*tags), count)


@dataclass
class DamageSource:
    """Один источник урона."""

    name: str
    scaling: str                       # "atk" | "hp" | "def" | "em"
    mv: MotionValue                    # множитель таланта в долях (1.0 = 100%)
    element: str = "physical"          # "anemo", "cryo", ...
    kind: str = "skill"                # "normal", "charged", "plunge", "skill", "burst", ...
    model: str = ELEMENTAL             # ELEMENTAL | STELLAR_SWIRL
    occurrences: Sequence[Occurrence] = field(default_factory=lambda: [Occurrence(state())])
    applies_def: bool = True           # учитывать ли множитель защиты цели
    flat_base: float = 0.0             # «Дополнительный базовый урон» (плоское слагаемое)
    multipliers: Tuple[str, ...] = ()  # имена доп. множителей персонажа (см. Character.multipliers)
    res_override: Optional[float] = None   # заменить множитель сопротивления цели
    crit_mode: Optional[str] = None    # переопределить режим крита для этого источника
    polar_stacks: int = 1 
    #: Доп. слагаемые базы от других статов: (("em", 1.5),) = «+150% МС».
    #: База удара = Стат × Множитель + Σ Стат_i × k_i (до бонусов урона /
    #: множителя звёздной реакции). Пример: пассивка Сайно A4.
    extra_scaling: Tuple[Tuple[str, float], ...] = ()
    note: str = ""

    # Дополнительные теги для поиска бонусов урона: element + kind + пользовательские
    extra_tags: Tuple[str, ...] = ()

    def tags(self) -> Tuple[str, ...]:
        return (self.element, self.kind, self.model) + tuple(self.extra_tags)

    def motion_value(self, ctx=None) -> float:
        return self.mv(ctx) if callable(self.mv) else float(self.mv)

    def base_term(self, stats, ctx=None) -> float:
        """Стат × Множитель + доп. слагаемые от других статов (extra_scaling)."""
        out = stats.stat(self.scaling) * self.motion_value(ctx)
        for stat_name, k in self.extra_scaling:
            out += stats.stat(stat_name) * k
        return out


def elemental(name: str, scaling: str, mv: MotionValue, element: str, kind: str,
              occurrences: Sequence[Occurrence], **kwargs) -> DamageSource:
    """Обычный элементальный источник урона."""
    return DamageSource(name=name, scaling=scaling, mv=mv, element=element,
                        kind=kind, model=ELEMENTAL, occurrences=list(occurrences), **kwargs)


def stellar_swirl(name: str, scaling: str, mv: MotionValue, element: str,
                  occurrences: Sequence[Occurrence], kind: str = "skill",
                  **kwargs) -> DamageSource:
    """Прямой урон звёздного рассеивания (из талантов персонажей).

    Формула (см. картинку в проекте):
        База = Стат × Множитель × (1 + Бонус базового урона)
               × (1 + 6·МС/(МС+2000) + Бонус урона звёздной реакции)
        Итог = (База + Доп. базовый урон) × Сопр. × Крит × Возвышение

    Защита цели в этой формуле НЕ участвует.
    """
    kwargs.setdefault("applies_def", False)
    return DamageSource(name=name, scaling=scaling, mv=mv, element=element,
                        kind=kind, model=STELLAR_SWIRL,
                        occurrences=list(occurrences), **kwargs)
    
def stellar_conduct(name: str, scaling: str, mv: MotionValue, element: str,
                  occurrences: Sequence[Occurrence], kind: str = "skill",
                  **kwargs) -> DamageSource:
    """Прямой урон звёздного проводника (из талантов персонажей).
    """
    kwargs.setdefault("applies_def", False)
    return DamageSource(name=name, scaling=scaling, mv=mv, element=element,
                        kind=kind, model=STELLAR_CONDUCT,
                        occurrences=list(occurrences), **kwargs)


def lunar_direct_source(name: str, reaction: str, scaling: str, mv: MotionValue,
                        occurrences: Sequence[Occurrence], element: str,
                        kind: str = "skill", **kwargs) -> DamageSource:
    """Прямой урон лунной реакции (Direct Lunar-…).

        База = K × Стат × Множитель × (1 + Base Increase)
               × (1 + 6·МС/(МС+2000) + лунный бонус урона)
        Итог = (База + Доп. базовый урон) × Сопр. × Крит × Возвышение

    K — formulas.LUNAR_DIRECT_FACTOR: кристаллизация 1.6, заряд 3, бутоны 1.
    Защита цели не учитывается. Теги удара: стихия, тип, модель реакции
    ("lunar_crystallize" / "lunar_charged" / "lunar_bloom") и общий "lunar" —
    поэтому работают ключи "lunar_bonus", "lunar_bonus.lunar_charged",
    "elevation.lunar", "flat_base_dmg.lunar_bloom" и т.д.
    """
    if reaction not in LUNAR_MODELS:
        raise ValueError(f"Неизвестная лунная реакция: {reaction!r}")
    kwargs.setdefault("applies_def", False)
    extra = tuple(kwargs.pop("extra_tags", ()))
    return DamageSource(name=name, scaling=scaling, mv=mv, element=element,
                        kind=kind, model=reaction,
                        occurrences=list(occurrences),
                        extra_tags=(LUNAR,) + extra, **kwargs)


def lunar_crystallize(name: str, scaling: str, mv: MotionValue,
                      occurrences: Sequence[Occurrence], kind: str = "skill",
                      element: str = "geo", **kwargs) -> DamageSource:
    """Прямой урон лунной кристаллизации (гео, ×1.6)."""
    return lunar_direct_source(name, LUNAR_CRYSTALLIZE, scaling, mv, occurrences,
                               element, kind, **kwargs)


def lunar_charged(name: str, scaling: str, mv: MotionValue,
                  occurrences: Sequence[Occurrence], kind: str = "skill",
                  element: str = "electro", **kwargs) -> DamageSource:
    """Прямой урон лунного заряда (электро, ×3)."""
    return lunar_direct_source(name, LUNAR_CHARGED, scaling, mv, occurrences,
                               element, kind, **kwargs)


def lunar_bloom(name: str, scaling: str, mv: MotionValue,
                occurrences: Sequence[Occurrence], kind: str = "skill",
                element: str = "dendro", **kwargs) -> DamageSource:
    """Прямой урон лунных бутонов (дендро, ×1). Урона реакции у бутонов нет."""
    return lunar_direct_source(name, LUNAR_BLOOM, scaling, mv, occurrences,
                               element, kind, **kwargs)
