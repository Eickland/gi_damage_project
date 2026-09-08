"""
Движок расчёта: отряд, разрешение статов по состояниям, урон.

Порядок работы
--------------
1. `StatResolver` считает статы каждого персонажа для каждого нужного
   СОСТОЯНИЯ (набора тегов). Постоянные баффы применяются всегда,
   временные — только если их теги входят в состояние.
2. Динамические баффы (зависящие от статов других персонажей) разрешаются
   итеративно: значения берутся с предыдущей итерации. По умолчанию 4 прохода —
   этого хватает для цепочек вида «МС Сахарозы → МС Мидзуки → бонус отряду».
3. Каждый источник урона считается отдельно для каждого своего «вхождения»
   (состояние + количество ударов).
4. Реакции считаются для всех персонажей и распределяются по долям.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

from .buffs import Buff, BuffContext, State, state
from .entities import Build, Enemy
from .formulas import (elemental_damage, stellar_swirl_direct,
                       stellar_swirl_reaction)
from .reactions import ReactionEvent, distribute, pick_primary
from .sources import ELEMENTAL, STELLAR_SWIRL, DamageSource
from .stats import S, Stats, crit_multiplier


# --------------------------------------------------------------------------- #
#  Конфигурация расчёта                                                        #
# --------------------------------------------------------------------------- #
@dataclass
class Config:
    """Настройки движка.

    excel_compat — воспроизводить поведение исходной таблицы Excel:
                   множитель (1 + «Base stellar swirl DMG%») применяется дважды
                   в уроне РЕАКЦИИ звёздного рассеивания.
                   False = строго по формуле (один раз).
    resolve_passes — сколько итераций разрешения динамических баффов.
    """

    excel_compat: bool = False
    resolve_passes: int = 4


# --------------------------------------------------------------------------- #
#  Разрешение статов                                                           #
# --------------------------------------------------------------------------- #
class StatResolver:
    """Считает статы персонажа в заданном состоянии."""

    #: условный «владелец» для баффов, заданных на уровне отряда
    TEAM_OWNER = "__team__"

    def __init__(self, builds: Sequence[Build], passes: int = 4,
                 team_buffs: Sequence[Buff] = ()):
        self.builds: Dict[str, Build] = {b.name: b for b in builds}
        self.passes = max(1, passes)
        self._base: Dict[str, Stats] = {n: b.base_stats() for n, b in self.builds.items()}
        # (владелец, бафф) для всего отряда
        self._buffs: List[Tuple[str, Buff]] = []
        for b in builds:
            self._buffs.extend(b.all_buffs())
        # Отрядные баффы (резонанс, еда, статуи и т.п.) — учитываются ОДИН раз,
        # независимо от количества сборок. Владелец у них условный, поэтому
        # адресуйте их через TEAM или через явные имена персонажей;
        # SELF/OTHERS здесь смысла не имеют.
        for b in team_buffs:
            self._buffs.append((self.TEAM_OWNER, b))
        self._cache: Dict[Tuple[str, State, int], Stats] = {}
        self._depth = self.passes - 1  # текущий «уровень» для внешних запросов

    # -- публичный API ------------------------------------------------------- #
    def base(self, character: str) -> Stats:
        """Статы без единого баффа отряда (строки вида «EM no % buff»)."""
        return self._base[character]

    def stats(self, character: str, st: State | Iterable[str]) -> Stats:
        return self._compute(character, frozenset(st), self._depth)

    def previous(self, character: str, st: State) -> Stats:
        """Значение с предыдущей итерации (для динамических баффов)."""
        return self._compute(character, frozenset(st), max(0, self._current_depth - 1))

    # -- внутреннее ---------------------------------------------------------- #
    _current_depth = 0

    def _compute(self, character: str, st: State, depth: int) -> Stats:
        key = (character, st, depth)
        cached = self._cache.get(key)
        if cached is not None:
            return cached
        result = self._base[character].copy()
        prev_depth = self._current_depth
        self._current_depth = depth
        try:
            for owner, bf in self._buffs:
                if not bf.applies_to(owner, character):
                    continue
                if not bf.active_in(st):
                    continue
                if callable(bf.value):
                    if depth == 0:
                        continue  # на нулевой итерации динамические баффы не применяем
                    ctx = BuffContext(self, owner, character, st)
                    value = bf.value(ctx)
                else:
                    value = float(bf.value)
                result.add(bf.stat, value)
        finally:
            self._current_depth = prev_depth
        self._cache[key] = result
        return result


# --------------------------------------------------------------------------- #
#  Результаты                                                                  #
# --------------------------------------------------------------------------- #
@dataclass
class HitResult:
    source: str
    state: State
    count: float
    per_hit: float

    @property
    def total(self) -> float:
        return self.per_hit * self.count


@dataclass
class CharacterResult:
    name: str
    hits: List[HitResult] = field(default_factory=list)
    reaction: float = 0.0
    reaction_breakdown: Dict[str, float] = field(default_factory=dict)

    @property
    def direct(self) -> float:
        return sum(h.total for h in self.hits)

    @property
    def total(self) -> float:
        return self.direct + self.reaction

    def by_source(self) -> Dict[str, float]:
        out: Dict[str, float] = {}
        for h in self.hits:
            out[h.source] = out.get(h.source, 0.0) + h.total
        return out


@dataclass(frozen=True)
class BuildSetup:
    """Снимок того, из чего собран персонаж, — для отчётов и сравнений."""

    character: str
    constellation: int
    weapon: str
    artifacts: str
    time: float

    def describe(self) -> str:
        parts = [f"C{self.constellation}"]
        if self.weapon:
            parts.append(self.weapon)
        if self.artifacts:
            parts.append(self.artifacts)
        return " · ".join(parts)


@dataclass
class TeamResult:
    team_name: str
    characters: Dict[str, CharacterResult]
    rotation_time: float
    #: раскладка отряда: имя -> BuildSetup. Нужна, чтобы отчёт мог показать,
    #: что в переборе осталось постоянным, а что заменяется.
    setup: Dict[str, "BuildSetup"] = field(default_factory=dict)
    rotation: str = ""

    @property
    def dpr(self) -> float:
        """Damage per rotation — суммарный урон за ротацию."""
        return sum(c.total for c in self.characters.values())

    @property
    def dps(self) -> float:
        return self.dpr / self.rotation_time if self.rotation_time else float("nan")

    def totals(self) -> Dict[str, float]:
        return {n: c.total for n, c in self.characters.items()}


# --------------------------------------------------------------------------- #
#  Контекст отряда (для множителей таланта, зависящих от ротации)              #
# --------------------------------------------------------------------------- #
@dataclass
class TeamContext:
    rotation_time: float
    times: Dict[str, float]
    resolver: StatResolver


# --------------------------------------------------------------------------- #
#  Отряд                                                                       #
# --------------------------------------------------------------------------- #
@dataclass
class Team:
    name: str
    builds: Sequence[Build]
    enemy: Enemy = field(default_factory=Enemy)
    reactions: Sequence[ReactionEvent] = field(default_factory=tuple)
    #: баффы уровня ОТРЯДА (резонанс стихий, еда, бафферы вне сборок).
    #: Применяются ровно один раз — в отличие от Build.extra_buffs, которые
    #: с target=TEAM продублируются, если положить их в несколько сборок.
    buffs: Sequence[Buff] = field(default_factory=tuple)
    rotation: str = ""
    config: Config = field(default_factory=Config)
    #: если задано — используется вместо суммы времён персонажей
    rotation_time_override: Optional[float] = None

    # ---- вспомогательное --------------------------------------------------- #
    @property
    def rotation_time(self) -> float:
        if self.rotation_time_override is not None:
            return self.rotation_time_override
        return sum(b.time for b in self.builds)

    def build(self, name: str) -> Build:
        for b in self.builds:
            if b.name == name:
                return b
        raise KeyError(name)

    def elements(self) -> Dict[str, str]:
        return {b.name: b.element for b in self.builds}

    # ---- расчёт ------------------------------------------------------------ #
    def compute(self) -> TeamResult:
        resolver = StatResolver(self.builds, self.config.resolve_passes, self.buffs)
        ctx = TeamContext(self.rotation_time,
                          {b.name: b.time for b in self.builds},
                          resolver)

        results = {b.name: CharacterResult(b.name) for b in self.builds}

        # --- прямой урон ---------------------------------------------------- #
        for b in self.builds:
            multipliers = b.extra_multipliers()
            crit_mode = b.effective_crit_mode()
            for src in b.all_sources():
                for occurrence in src.occurrences:
                    if not occurrence.count:
                        continue
                    st = occurrence.state
                    stats = resolver.stats(b.name, st)
                    value = self._source_damage(src, stats, b, multipliers,
                                                crit_mode, ctx)
                    results[b.name].hits.append(
                        HitResult(src.name, st, occurrence.count, value))

        # --- урон реакций --------------------------------------------------- #
        elements = self.elements()
        for event in self.reactions:
            per_char: Dict[str, float] = {}
            for b in self.builds:
                st = frozenset({b.effective_field()} | set(event.tags))
                stats = resolver.stats(b.name, st)
                per_char[b.name] = self._reaction_damage(event, stats, b)
            primary = pick_primary(per_char, event, elements)
            shares = distribute(per_char, primary, event.weights)
            for name, value in shares.items():
                gained = value * event.count
                results[name].reaction += gained
                results[name].reaction_breakdown[event.name] = (
                    results[name].reaction_breakdown.get(event.name, 0.0) + gained)

        setup = {
            b.name: BuildSetup(
                character=b.character.name,
                constellation=b.constellation,
                weapon=(f"{b.weapon.name} R{b.weapon.refinement}"
                        if b.weapon is not None else ""),
                artifacts="/".join(a.name for a in b.artifacts),
                time=b.time,
            )
            for b in self.builds
        }
        return TeamResult(self.name, results, self.rotation_time,
                          setup=setup, rotation=self.rotation)

    # ---- отдельные формулы ------------------------------------------------- #
    def _source_damage(self, src: DamageSource, stats: Stats, b: Build,
                       multipliers, crit_mode: str, ctx: TeamContext) -> float:
        tags = src.tags()
        mv = src.motion_value(ctx)
        stat_value = stats.stat(src.scaling)
        crit = crit_multiplier(stats, src.crit_mode or crit_mode, *tags)
        res = self._res(src.element, stats, src.res_override)
        elevation = self.enemy.elevation + stats.elevation(*tags)

        if src.model == STELLAR_SWIRL:
            value = stellar_swirl_direct(
                stat_value, mv, stats, tags, res, crit, elevation,
                flat_base=src.flat_base + stats.flat_base_dmg(*tags))
        else:
            def_mult = self.enemy.def_mult if src.applies_def else 1.0
            value = elemental_damage(
                stat_value * mv, stats, tags, def_mult, res, crit, elevation,
                flat_base=src.flat_base)

        for m in src.multipliers:
            value *= multipliers[m](stats)
        return value

    def _res(self, element: str, stats: Stats, override: Optional[float]) -> float:
        """Множитель сопротивления цели для конкретного удара.

        Приоритет: res_override источника -> базовое сопротивление Enemy.res
        минус накопленные снижения -> готовый множитель Enemy.res_mult.

        Снижение сопротивления берётся из статов АТАКУЮЩЕГО в его текущем
        состоянии, поэтому оно может быть временным (работать только внутри
        окна) — ровно как любой другой бафф.
        """
        if override is not None:
            return override
        return self.enemy.res_multiplier(element, stats.res_reduction(element))

    def _reaction_damage(self, event: ReactionEvent, stats: Stats, b: Build) -> float:
        tags = (event.element, "stellar_swirl", "reaction")
        crit = crit_multiplier(stats, b.effective_crit_mode(), *tags)
        res = self._res(event.element, stats, event.res_override)
        elevation = self.enemy.elevation + stats.elevation(*tags)
        return stellar_swirl_reaction(
            event.multiplier, stats, tags, res, crit, elevation,
            base_dmg=event.base_dmg, flat_base=stats.flat_base_dmg(*tags),
            excel_compat=self.config.excel_compat)