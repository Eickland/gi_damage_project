"""
Реакции, наносящие урон сами по себе.

Пока реализовано звёздное рассеивание (Stellar Swirl, SSW), но модель общая:
реакция = базовый урон × базовый множитель × множители получателя,
посчитанные ДЛЯ КАЖДОГО персонажа отряда, а затем распределённые по долям.

Распределение (из официальной таблицы):
    Итоговый урон = 3/5 · «главный» + 3/10 · второй + 1/20 · третий + 1/20 · четвёртый

    * для анемо-рассеивания «главный» — персонаж, вызвавший реакцию (анемо);
    * для детонации вихря «главный» — сильнейший из крио-персонажей;
    * остальные сортируются по убыванию их собственного урона реакции.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple, Mapping

from .buffs import State, state
from .formulas import (SSW_ANEMO_MULTIPLIER, SSW_VORTEX_MULTIPLIER,
                       STELLAR_SWIRL_BASE_DMG, LUNAR_REACTION_MULTIPLIER)

#: Доли распределения урона реакции по персонажам отряда
DEFAULT_WEIGHTS: Tuple[float, ...] = (3 / 5, 3 / 10, 1 / 20, 1 / 20)

#: Модели реакций
REACTION_SSW = "stellar_swirl"
REACTION_LUNAR_CRYSTALLIZE = "lunar_crystallize"


@dataclass
class ReactionEvent:
    """Одно «срабатывание» реакции (или пачка одинаковых срабатываний).

    name        — название для отчёта
    element     — стихия урона реакции ("anemo" / "cryo"): влияет на сопротивление
    multiplier  — базовый множитель реакции (0.75 для анемо-SSW, 2 или 3 для вихря)
    trigger     — имя персонажа, вызвавшего реакцию (получает долю 3/5)
    primary_from— если trigger не задан: выбрать «главного» как сильнейшего
                  из перечисленных персонажей (или из всех персонажей стихии,
                  если передать строку-стихию, например "cryo")
    tags        — дополнительные теги состояния (например "instructor"),
                  которые добавляются к «полевому» состоянию каждого персонажа
    count       — сколько раз это происходит за ротацию
    base_dmg    — базовый урон реакции (по умолчанию 1446.85 для 90 ур.)
    res_override— заменить множитель сопротивления цели (например при C2 Мидзуки)
    weights     — доли распределения
    """

    name: str
    element: str
    multiplier: float
    trigger: Optional[str] = None
    primary_from: Optional[object] = None       # Sequence[str] | str (стихия)
    tags: Tuple[str, ...] = ()
    trigger_tags: Tuple[str, ...] = ()
    char_tags: Mapping[str, Tuple[str, ...]] = field(default_factory=dict)
    count: float = 1.0
    base_dmg: float = STELLAR_SWIRL_BASE_DMG
    res_override: Optional[float] = None
    weights: Tuple[float, ...] = DEFAULT_WEIGHTS
    #: формула: "stellar_swirl" (по умолчанию) или "lunar_crystallize"
    model: str = REACTION_SSW
    #: на поле/вне поля для отдельных персонажей в момент реакции:
    #: {"Цзы Бай": "off_field"} — реакция происходит, пока она вне поля
    field_override: Mapping[str, str] = field(default_factory=dict)
    note: str = ""


# --------------------------------------------------------------------------- #
#  Удобные конструкторы для звёздного рассеивания                              #
# --------------------------------------------------------------------------- #
def ssw_anemo(trigger: str, count: float, *tags: str, **kwargs) -> ReactionEvent:
    """Анемо-рассеивание: срабатывает при каждом триггере реакции."""
    return ReactionEvent(
        name=kwargs.pop("name", f"SSW анемо ({trigger})"),
        element="anemo",
        multiplier=SSW_ANEMO_MULTIPLIER,
        trigger=trigger,
        tags=tuple(tags),
        count=count,
        **kwargs,
    )


def ssw_vortex(stacks: int, count: float, *tags: str,
               primary_from: object = "cryo", **kwargs) -> ReactionEvent:
    """Детонация вихря (крио).

    Базовый множитель: 2 при 1–2 стаках, 3 при 3–6 стаках.
    """
    return ReactionEvent(
        name=kwargs.pop("name", f"SSW вихрь ×{stacks} стаков"),
        element="cryo",
        multiplier=SSW_VORTEX_MULTIPLIER[stacks],
        primary_from=primary_from,
        tags=tuple(tags),
        count=count,
        **kwargs,
    )


# --------------------------------------------------------------------------- #
#  Лунная кристаллизация                                                       #
# --------------------------------------------------------------------------- #
def lunar_crystallize_reaction(count: float, *tags: str, **kwargs) -> ReactionEvent:
    """Урон реакции лунной кристаллизации (Moondrift Harmony — удары Лунных клеток).

    Каждая реакция создаёт 3 клетки; за каждые 3 реакции каждая из 3 клеток
    бьёт один раз — то есть ударов клеток столько же, сколько реакций.
    count — число ударов клеток за ротацию.

    Урон считается для каждого персонажа и распределяется 60/30/5/5 по
    убыванию (главный — сильнейший, а не триггер).
    """
    return ReactionEvent(
        name=kwargs.pop("name", "Лунная кристаллизация (клетки)"),
        element=kwargs.pop("element", "geo"),
        multiplier=LUNAR_REACTION_MULTIPLIER["lunar_crystallize"],
        tags=tuple(tags),
        count=count,
        weights=kwargs.pop("weights", (0.60, 0.30, 0.05, 0.05)),
        model=REACTION_LUNAR_CRYSTALLIZE,
        **kwargs,
    )


# --------------------------------------------------------------------------- #
def distribute(per_character: Dict[str, float], primary: str,
               weights: Sequence[float] = DEFAULT_WEIGHTS) -> Dict[str, float]:
    """Распределить урон реакции по долям.

    primary получает weights[0], остальные — по убыванию их значения.
    """
    others = sorted(((v, k) for k, v in per_character.items() if k != primary),
                    key=lambda t: (-t[0], t[1]))
    result = {primary: per_character.get(primary, 0.0) * weights[0]}
    for i, (value, name) in enumerate(others, start=1):
        w = weights[i] if i < len(weights) else 0.0
        result[name] = value * w
    return result


def pick_primary(per_character: Dict[str, float], event: ReactionEvent,
                 elements: Dict[str, str]) -> str:
    """Кто получает долю 3/5."""
    if event.trigger:
        return event.trigger
    candidates: List[str]
    pf = event.primary_from
    if pf is None:
        candidates = list(per_character)
    elif isinstance(pf, str):
        candidates = [n for n, el in elements.items() if el == pf] or list(per_character)
    else:
        candidates = [n for n in pf if n in per_character] or list(per_character) # type: ignore
    return max(candidates, key=lambda n: (per_character.get(n, 0.0), n))
