"""
Массовые расчёты: ростеры и переборы.

Позволяет одной строкой посчитать «а что если»:
  * заменить оружие одного персонажа на любое из списка;
  * заменить самого персонажа на другого;
  * перебрать созвездия;
  * перебрать наборы артефактов;
  * любую комбинацию перечисленного.
"""

from __future__ import annotations

import itertools
from dataclasses import dataclass, field, replace
from typing import Callable, Dict, Iterable, List, Optional, Sequence, Tuple

from .engine import Team, TeamResult
from .entities import ArtifactSet, Build, Weapon

#: Преобразование сборки: получает текущее состояние слота, возвращает новое.
BuildTransform = Callable[[Build], Build]


# --------------------------------------------------------------------------- #
def _swap_build(team: Team, slot: str, new_build: Build) -> Team:
    builds = [new_build if b.name == slot else b for b in team.builds]
    return replace(team, builds=builds)


def _rename_reactions(team: Team, old: str, new: str) -> Team:
    """Если заменяемый персонаж был триггером реакции — переставить триггер."""
    if old == new:
        return team
    events = []
    for e in team.reactions:
        events.append(replace(e, trigger=new) if e.trigger == old else e)
    return replace(team, reactions=events)


# --------------------------------------------------------------------------- #
@dataclass
class Variation:
    """Одна ось перебора: что меняем в конкретном слоте отряда."""

    slot: str                                    # имя персонажа в отряде
    weapons: Sequence[Weapon] = ()               # варианты оружия
    constellations: Sequence[int] = ()           # варианты созвездий
    builds: Sequence[Build] = ()                 # варианты целиком другой сборки/персонажа

    #: Варианты НАБОРОВ артефактов. Список списков, потому что персонаж носит
    #: не один набор, а комплект: 4ч — это (SET,), а 2+2 — это (SET_A, SET_B).
    #: Поэтому один вариант перебора сам по себе является последовательностью:
    #:
    #:     artifact_sets=[
    #:         (VIRIDESCENT,),                    # 4ч Изумрудная тень
    #:         (INSTRUCTOR,),                     # 4ч Инструктор
    #:         (VIRIDESCENT_2PC, GLADIATOR_2PC),  # 2+2
    #:     ]
    #:
    #: Одиночный набор без обёртки тоже принимается — он завернётся сам.
    #: (С оружием такого нет: оружие ровно одно, поэтому там список плоский.)
    artifact_sets: Sequence[Sequence[ArtifactSet]] = ()

    def options(self, base: Build) -> List[Tuple[str, "BuildTransform"]]:
        """Список (подпись, преобразование сборки).

        Возвращаются именно ПРЕОБРАЗОВАНИЯ, а не готовые сборки: тогда
        несколько осей на один и тот же слот складываются, а не затирают
        друг друга (например созвездия × оружие одного персонажа).
        """
        out: List[Tuple[str, BuildTransform]] = []
        if self.builds:
            for b in self.builds:
                out.append((b.describe(), lambda cur, b=b: b))
        if self.weapons:
            for w in self.weapons:
                out.append((f"{base.name}: {w.name} R{w.refinement}",
                            lambda cur, w=w: cur.with_weapon(w)))
        if self.constellations:
            for c in self.constellations:
                out.append((f"{base.name}: C{c}",
                            lambda cur, c=c: cur.with_constellation(c)))
        if self.artifact_sets:
            for sets in self.artifact_sets:
                # Одиночный набор, записанный без обёртки, трактуем как комплект
                # из одного набора — чтобы плоский список тоже работал.
                if isinstance(sets, ArtifactSet):
                    sets = (sets,)
                label = "/".join(a.name for a in sets)
                out.append((f"{base.name}: {label}",
                            lambda cur, sets=tuple(sets): cur.with_artifacts(*sets)))
        if not out:
            out.append((base.describe(), lambda cur: cur))
        return out


# --------------------------------------------------------------------------- #
@dataclass
class Roster:
    """Перебор вариантов на базе одного отряда."""

    base_team: Team
    variations: Sequence[Variation] = field(default_factory=tuple)
    #: дополнительная правка отряда перед расчётом (например смена цели)
    tweak: Optional[Callable[[Team], Team]] = None

    def _slot_index(self, slot: str) -> int:
        for i, b in enumerate(self.base_team.builds):
            if b.name == slot:
                return i
        raise KeyError(f"В отряде нет персонажа {slot!r}")

    def _apply(self, chosen: Sequence[Tuple[str, "BuildTransform"]]) -> Tuple[str, Team]:
        # Работаем по индексу слота, а не по имени: имя может смениться после
        # замены персонажа, а следующая ось на том же слоте должна применяться
        # поверх уже изменённой сборки.
        builds = list(self.base_team.builds)
        renames: List[Tuple[str, str]] = []
        labels = []
        for variation, (label, transform) in zip(self.variations, chosen):
            i = self._slot_index(variation.slot)
            old_name = builds[i].name
            builds[i] = transform(builds[i])
            if builds[i].name != old_name:
                renames.append((old_name, builds[i].name))
            labels.append(label)

        team = replace(self.base_team, builds=builds)
        for old, new in renames:
            team = _rename_reactions(team, old, new)
        if self.tweak:
            team = self.tweak(team)
        name = " + ".join(labels) if labels else team.name
        return name, replace(team, name=name)

    def run(self) -> List[TeamResult]:
        """Полный декартов перебор всех вариаций."""
        per_axis = []
        for variation in self.variations:
            base = self.base_team.build(variation.slot)
            per_axis.append(variation.options(base))
        results: List[TeamResult] = []
        for chosen in itertools.product(*per_axis) if per_axis else [()]:
            name, team = self._apply(chosen)
            results.append(team.compute())
        return results

    def ranked(self, key: str = "dps") -> List[TeamResult]:
        return sorted(self.run(), key=lambda r: getattr(r, key), reverse=True)


# --------------------------------------------------------------------------- #
def compare_teams(teams: Iterable[Team]) -> List[TeamResult]:
    """Просто посчитать несколько готовых отрядов."""
    return [t.compute() for t in teams]


def weapon_scan(team: Team, slot: str, weapons: Sequence[Weapon]) -> List[TeamResult]:
    """Перебор оружия у одного персонажа."""
    return Roster(team, [Variation(slot=slot, weapons=list(weapons))]).run()


def character_scan(team: Team, slot: str, builds: Sequence[Build]) -> List[TeamResult]:
    """Замена персонажа в слоте на любую из сборок."""
    return Roster(team, [Variation(slot=slot, builds=list(builds))]).run()


def constellation_scan(team: Team, slot: str, levels: Sequence[int]) -> List[TeamResult]:
    """Перебор созвездий одного персонажа."""
    return Roster(team, [Variation(slot=slot, constellations=list(levels))]).run()