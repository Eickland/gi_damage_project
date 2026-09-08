"""
Баффы и состояния (окна усилений).

Ключевая идея проекта
---------------------
Каждый источник урона «происходит» в некотором СОСТОЯНИИ — наборе строковых
тегов, описывающих, какие временные усиления сейчас активны и на поле ли
персонаж. Например:

    {"on_field"}                        — персонаж на поле, временных окон нет
    {"off_field", "instructor"}         — персонаж вне поля, работает 4ч. Инструктора
    {"on_field", "instructor", "vv"}    — на поле, Инструктор + шред Изумрудной тени

Бафф объявляет, при каких тегах он работает (`requires`) и при каких выключается
(`excludes`). Постоянные и «псевдопостоянные» баффы просто не имеют requires —
они работают всегда.

Тогда расчёт отряда сводится к принципу из ТЗ:
  «для каждого источника урона взять все постоянные усиления, а затем
   по каждому временному усилению добавить те источники урона, которые
   происходят в этом окне».

Технически это значит: у источника урона есть список «вхождений»
(Occurrence: состояние + количество ударов), и статы считаются отдельно
для каждой пары (персонаж, состояние).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, FrozenSet, Iterable, Sequence, Tuple, Union

State = FrozenSet[str]


def state(*tags: str) -> State:
    """Удобный конструктор состояния: state("on_field", "instructor")."""
    return frozenset(tags)


# --------------------------------------------------------------------------- #
#  Кому достаётся бафф                                                         #
# --------------------------------------------------------------------------- #
SELF = "self"        # только владельцу
TEAM = "team"        # всему отряду, включая владельца
OTHERS = "others"    # всем, кроме владельца

Target = Union[str, Sequence[str]]  # SELF/TEAM/OTHERS либо список имён персонажей


# --------------------------------------------------------------------------- #
#  Контекст для динамических баффов                                            #
# --------------------------------------------------------------------------- #
class BuffContext:
    """Даёт доступ к статам отряда при вычислении «динамического» баффа.

    Значения берутся с предыдущей итерации разрешения статов (см. resolver),
    поэтому взаимные зависимости (МС Сахарозы -> МС отряда -> ...) не зацикливаются.
    """

    def __init__(self, resolver, owner: str, recipient: str, recipient_state: State):
        self._resolver = resolver
        self.owner = owner              # чей это бафф
        self.recipient = recipient      # на кого он сейчас применяется
        self.state = recipient_state    # в каком состоянии считается получатель

    # -- запросы статов ----------------------------------------------------- #
    def stat(self, character: str, name: str, st: State | Iterable[str] | None = None) -> float:
        """Стат персонажа `character` в состоянии `st` (по умолчанию — текущее)."""
        st = self.state if st is None else frozenset(st)
        return self._resolver.previous(character, st).stat(name)

    def own(self, name: str, st: State | Iterable[str] | None = None) -> float:
        """Стат владельца баффа."""
        return self.stat(self.owner, name, st)

    def base(self, character: str, name: str) -> float:
        """«Голый» стат персонажа — до применения любых баффов отряда.

        Соответствует строкам вида «EM no % buff» в Excel.
        """
        return self._resolver.base(character).stat(name)
    

    # -- работа с состояниями ------------------------------------------------ #
    def mirror(self, *base_tags: str, keep: Iterable[str] = ()) -> State:
        """Состояние из `base_tags` + те теги получателя, что перечислены в `keep`.

        Пример: бафф Мидзуки читает её МС «в том же окне Инструктора»,
        в котором сейчас считается получатель:

            ctx.stat("Мидзуки", "em", ctx.mirror("on_field", keep=["instructor"]))
        """
        kept = {t for t in keep if t in self.state}
        return frozenset(set(base_tags) | kept)

    def has(self, tag: str) -> bool:
        return tag in self.state


BuffValue = Union[float, Callable[[BuffContext], float]]


# --------------------------------------------------------------------------- #
#  Бафф                                                                        #
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class Buff:
    """Одно изменение стата.

    stat      — ключ стата (см. gi_damage.core.stats.S), можно точечный
    value     — число либо функция от BuffContext (для баффов, зависящих
                от статов других персонажей)
    target    — SELF / TEAM / OTHERS / список имён
    requires  — теги состояния, при которых бафф работает (все должны быть)
    excludes  — теги, при которых бафф выключается (ни одного не должно быть)
    source    — человекочитаемое описание источника (для отчётов)
    temporary — пометка «временный» (влияет только на отчёты, не на расчёт)
    """

    stat: str
    value: BuffValue
    target: Target = TEAM
    requires: Tuple[str, ...] = ()
    excludes: Tuple[str, ...] = ()
    source: str = ""
    temporary: bool = False

    def __post_init__(self):
        for field_name in ("requires", "excludes"):
            value = getattr(self, field_name)
            if isinstance(value, str):
                object.__setattr__(self, field_name, (value,))
            elif not isinstance(value, tuple):
                object.__setattr__(self, field_name, tuple(value))

    # ---- применимость ------------------------------------------------------ #
    def applies_to(self, owner: str, recipient: str) -> bool:
        if isinstance(self.target, str):
            if self.target == SELF:
                return recipient == owner
            if self.target == TEAM:
                return True
            if self.target == OTHERS:
                return recipient != owner
            return recipient == self.target  # трактуем как имя персонажа
        return recipient in tuple(self.target)

    def active_in(self, st: State) -> bool:
        if any(tag not in st for tag in self.requires):
            return False
        if any(tag in st for tag in self.excludes):
            return False
        return True

    def resolve(self, ctx: BuffContext) -> float:
        return self.value(ctx) if callable(self.value) else float(self.value)


def buff(stat: str, value: BuffValue, **kwargs) -> Buff:
    """Короткий конструктор баффа."""
    return Buff(stat=stat, value=value, **kwargs)


def temp(stat: str, value: BuffValue, requires: Tuple[str, ...] | str, **kwargs) -> Buff:
    """Короткий конструктор ВРЕМЕННОГО баффа (работает только в своём окне)."""
    if isinstance(requires, str):
        requires = (requires,)
    kwargs.setdefault("temporary", True)
    return Buff(stat=stat, value=value, requires=tuple(requires), **kwargs)


@dataclass
class BuffSource:
    """Набор баффов с общим названием (оружие, набор артефактов, созвездие…)."""

    name: str
    buffs: Tuple[Buff, ...] = field(default_factory=tuple)

    def tagged(self) -> Tuple[Buff, ...]:
        return tuple(
            b if b.source else Buff(**{**b.__dict__, "source": self.name})
            for b in self.buffs
        )