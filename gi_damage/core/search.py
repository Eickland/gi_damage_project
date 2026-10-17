"""
Поиск по отрядам: замены персонажей и порядок инвестиций.

Ничего нового в расчёт не добавляется: каждый вариант считается обычным
`Roster(...).run()` / `Team.compute()`. Здесь только перебор и отбор.

1. Альтернативы (`find_alternatives`)
   В базовом отряде заменяется ОДИН слот. Кандидат — это персонаж плюс наборы
   созвездий, оружия и артефактов; перебирается их декартово произведение.

       report = find_alternatives(base_team, "Крио ГГ", [
           Candidate("Крио ГГ", lambda c: cryo_mc_build(c, MILLELITH),
                     constellations=(0, 4, 6)),
           Candidate("Ци Ци", lambda c: qiqi_build(c, MILLELITH)),
       ])
       print(alternatives_report(report))

2. Порядок инвестиций (`plan_investments`)
   Есть БАЗОВАЯ линия — отряд из доступных персонажей и оружия. Поверх неё
   можно «покупать» (каждая покупка = 1 кост):
     * персонажа (C0) и каждое его созвездие   — `Investable`;
     * легендарное оружие и каждое пробуждение — `SignatureWeapon`.
   Для каждого косте 0..budget ищется лучшее распределение покупок
   (поиск по уровням с лучом: `beam=None` — полный перебор).

       plan = plan_investments(base_team, investables, weapons, budget=12)
       print(plan_report(plan))
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import (Callable, Dict, List, NamedTuple, Optional, Sequence,
                    Tuple, Union)

from .engine import Team, TeamResult
from .entities import ArtifactSet, Build, Weapon
from .report import fmt, table
from .roster import Roster, Variation

#: правка отряда после замен (как `Roster(tweak=...)`)
TeamTweak = Callable[[Team], Team]


def _compose(*tweaks: Optional[TeamTweak]) -> Optional[TeamTweak]:
    funcs = [t for t in tweaks if t]
    if not funcs:
        return None

    def run(team: Team) -> Team:
        for f in funcs:
            team = f(team)
        return team
    return run


def _compute(base: Team, variations: Sequence[Variation],
             tweak: Optional[TeamTweak]) -> TeamResult:
    """Один вариант: все `variations` имеют по одной опции — значит, результат один."""
    if not variations:
        return (tweak(base) if tweak else base).compute()
    return Roster(base, list(variations), tweak=tweak).run()[0]


# =========================================================================== #
#  1. Альтернативы                                                            #
# =========================================================================== #
@dataclass
class Candidate:
    """Кандидат на замену слота.

    name           — подпись в отчёте («Ци Ци»)
    make           — готовая сборка C0 ЛИБО функция `созвездие -> Build`
                     (нужна, если сборка зависит от созвездия, как odette_build)
    constellations — какие созвездия перебирать
    weapons        — какие оружия перебирать (пусто = оружие из сборки)
    artifact_sets  — какие комплекты артефактов (пусто = из сборки);
                     комплект — это кортеж: (SET,) или (SET_A.at(2), SET_B.at(2))
    tweak          — правка отряда именно для этого кандидата
    """

    name: str
    make: Union[Build, Callable[[int], Build]]
    constellations: Sequence[int] = (0,)
    weapons: Sequence[Weapon] = ()
    artifact_sets: Sequence[Union[ArtifactSet, Sequence[ArtifactSet]]] = ()
    tweak: Optional[TeamTweak] = None

    def builds(self) -> List[Build]:
        out: List[Build] = []
        for c in self.constellations:
            b0 = self.make(c) if callable(self.make) else self.make.with_constellation(c)
            for w in (self.weapons or (None,)):
                b1 = b0 if w is None else b0.with_weapon(w)
                for arts in (self.artifact_sets or (None,)):
                    if arts is None:
                        out.append(b1)
                        continue
                    if isinstance(arts, ArtifactSet):
                        arts = (arts,)
                    out.append(b1.with_artifacts(*arts))
        return out


@dataclass
class AlternativeRow:
    candidate: str
    build: Build
    result: TeamResult
    is_baseline: bool = False

    def value(self, key: str) -> float:
        return getattr(self.result, key)


@dataclass
class AlternativesReport:
    slot: str
    base_build: Build
    baseline: TeamResult
    rows: List[AlternativeRow]
    key: str = "dps"

    def ranked(self, ascending: bool = False) -> List[AlternativeRow]:
        return sorted(self.rows, key=lambda r: r.value(self.key), reverse=not ascending)

    @property
    def baseline_value(self) -> float:
        return getattr(self.baseline, self.key)


def find_alternatives(base_team: Team, slot: str, candidates: Sequence[Candidate],
                      tweak: Optional[TeamTweak] = None, key: str = "dps",
                      include_baseline: bool = True) -> AlternativesReport:
    """Заменить слот `slot` каждым вариантом каждого кандидата."""
    base_build = base_team.build(slot)
    baseline = _compute(base_team, [], tweak)
    rows: List[AlternativeRow] = []
    if include_baseline:
        rows.append(AlternativeRow("база", base_build, baseline, is_baseline=True))
    for cand in candidates:
        t = _compose(tweak, cand.tweak)
        for b in cand.builds():
            result = _compute(base_team, [Variation(slot=slot, builds=[b])], t)
            rows.append(AlternativeRow(cand.name, b,
                                       replace(result, team_name=b.describe())))
    return AlternativesReport(slot, base_build, baseline, rows, key)


def alternatives_report(report: AlternativesReport, ascending: bool = False) -> str:
    """Текстовая таблица замен (аналог roster_report)."""
    base = report.baseline_value
    ranked = report.ranked(ascending)
    best = max(r.value(report.key) for r in ranked) or 1.0
    rows = []
    for rank, r in enumerate(ranked, start=1):
        v = r.value(report.key)
        mark = "  (база)" if r.is_baseline else ""
        rows.append([rank, r.build.describe() + mark, fmt(r.result.dpr),
                     fmt(r.result.dps), f"{v / best * 100:.1f}%",
                     f"{(v / base - 1) * 100:+.1f}%" if base else "—"])
    head = f"=== Замены слота «{report.slot}» ===\n"
    return head + table(rows, ["#", "Вариант", "DPR", "DPS", "% от лучшего", "к базе"],
                        align="rlrrrr")


# =========================================================================== #
#  2. Порядок инвестиций                                                      #
# =========================================================================== #
@dataclass
class Investable:
    """Персонаж, у которого платные C0 и/или созвездия.

    label             — как называть в отчётах и в `SignatureWeapon.character`
    slot              — имя слота в БАЗОВОМ отряде, который он занимает
                        (если он заменяет другого персонажа — имя того)
    make              — функция `созвездие -> Build`
    max_constellation — до какого созвездия разрешено докупать
    owned             — True: C0 уже есть (бесплатен), платные только C1..Cn;
                        False: C0 тоже стоит 1 кост, пока не куплен — слот
                        занимает базовый персонаж
    """

    label: str
    slot: str
    make: Callable[[int], Build]
    max_constellation: int = 6
    owned: bool = True
    _name: Optional[str] = field(default=None, init=False, repr=False, compare=False)

    @property
    def max_steps(self) -> int:
        return self.max_constellation + (0 if self.owned else 1)

    def constellation_at(self, steps: int) -> Optional[int]:
        """Созвездие после `steps` покупок; None — персонажа нет."""
        if self.owned:
            return steps
        return None if steps == 0 else steps - 1

    @property
    def character(self) -> str:
        if self._name is None:
            self._name = self.make(0).name
        return self._name


@dataclass
class SignatureWeapon:
    """Легендарное оружие: R1 стоит 1 кост, каждое следующее пробуждение — ещё 1.

    slot      — слот БАЗОВОГО отряда, на который оно надевается. Если оружие
                принадлежит покупаемому персонажу, можно указать его `label`
                (или `character=`) — слот подставится сам: тот, который этот
                персонаж занимает в базовом отряде.
    character — `label` Investable, чьё оружие это; пока его нет, оружие
                недоступно. None — без ограничения.
    """

    slot: str
    weapon: Weapon
    max_refinement: int = 5
    character: Optional[str] = None

    @property
    def max_steps(self) -> int:
        return self.max_refinement


class Holding(NamedTuple):
    kind: str      # "character" | "weapon"
    name: str      # имя персонажа / оружия — для иконки
    level: int     # созвездие / пробуждение
    label: str


class Change(NamedTuple):
    kind: str
    name: str
    old: Optional[int]
    new: Optional[int]

    @property
    def text(self) -> str:
        p = "C" if self.kind == "character" else "R"
        f = lambda x: "—" if x is None else f"{p}{x}"
        return f"{self.name}: {f(self.old)} → {f(self.new)}"


@dataclass
class Allocation:
    state: Tuple[int, ...]
    value: float
    result: TeamResult

    @property
    def cost(self) -> int:
        return sum(self.state)


@dataclass
class LevelResult:
    cost: int
    best: Allocation
    runners_up: List[Allocation]
    changes: List[Change]
    delta: float
    delta_pct: float


@dataclass
class InvestmentPlan:
    investables: List[Investable]
    weapons: List[SignatureWeapon]
    key: str = "dps"
    levels: List[LevelResult] = field(default_factory=list)

    # ---- описание состояния ------------------------------------------------ #
    def holdings(self, state: Sequence[int]) -> List[Holding]:
        out: List[Holding] = []
        for i, it in enumerate(self.investables):
            c = it.constellation_at(state[i])
            if c is not None:
                out.append(Holding("character", it.character, c, f"{it.label} C{c}"))
        for j, w in enumerate(self.weapons):
            r = state[len(self.investables) + j]
            if r > 0:
                out.append(Holding("weapon", w.weapon.name, r, f"{w.weapon.name} R{r}"))
        return out

    def changes(self, old: Sequence[int], new: Sequence[int]) -> List[Change]:
        out: List[Change] = []
        n = len(self.investables)
        for i in range(len(new)):
            if old[i] == new[i]:
                continue
            if i < n:
                it = self.investables[i]
                out.append(Change("character", it.character,
                                  it.constellation_at(old[i]), it.constellation_at(new[i])))
            else:
                w = self.weapons[i - n]
                out.append(Change("weapon", w.weapon.name, old[i] or None, new[i] or None))
        return out

    def owns(self, label: str, state: Sequence[int]) -> bool:
        for i, it in enumerate(self.investables):
            if it.label == label:
                return it.constellation_at(state[i]) is not None
        return False

    def weapon_available(self, j: int, state: Sequence[int]) -> bool:
        w = self.weapons[j]
        return w.character is None or self.owns(w.character, state)

    @property
    def best_value(self) -> float:
        return max(l.best.value for l in self.levels) if self.levels else 0.0


def plan_investments(baseline: Team, investables: Sequence[Investable],
                     weapons: Sequence[SignatureWeapon] = (), budget: int = 10,
                     key: str = "dps", beam: Union[int, str, None] = "auto",
                     keep: int = 3, max_evals: int = 3000,
                     tweak: Optional[TeamTweak] = None) -> InvestmentPlan:
    """Лучшее распределение покупок на каждом косте 0..budget.

    Идёт по уровням: на косте k берутся состояния лучших `beam` вариантов кост k-1
    и к каждому докупается один шаг (+1 созвездие / +1 пробуждение / новый
    персонаж или оружие).

    beam="auto" — полный перебор, если всех состояний не больше `max_evals`,
                  иначе луч шириной 40; число — своя ширина луча; None — всегда
                  полный перебор. Луч — эвристика: он может пропустить
                  комбинацию, которая окупается только вместе (например C2+C2
                  с синергией), поэтому при сомнениях увеличьте ширину.
    keep        — сколько запасных вариантов хранить на каждом косте.
    """
    inv = list(investables)
    if len({i.slot for i in inv}) != len(inv):
        raise ValueError("У двух Investable один и тот же слот; сравните их через find_alternatives")
    by_label = {i.label: i for i in inv}
    slots = [b.name for b in baseline.builds]

    def need_slot(slot: str, who: str) -> None:
        if slot not in slots:
            raise KeyError(
                f"{who}: в базовом отряде нет слота {slot!r}. Слоты: {slots}. "
                f"Для покупаемого персонажа указывайте слот, который он заменяет "
                f"(пока он не куплен, там стоит другой персонаж).")

    for i in inv:
        need_slot(i.slot, f"Investable {i.label!r}")

    wps: List[SignatureWeapon] = []
    for w in weapons:
        slot, character = w.slot, w.character
        if character is None and slot not in slots and slot in by_label:
            character = slot                       # SignatureWeapon("Одетта", ...)
        if character is not None:
            if character not in by_label:
                raise ValueError(f"SignatureWeapon {w.weapon.name!r}: нет Investable "
                                 f"с label={character!r}")
            slot = by_label[character].slot        # слот, который он занимает в базе
        need_slot(slot, f"SignatureWeapon {w.weapon.name!r}")
        wps.append(replace(w, slot=slot, character=character))

    plan = InvestmentPlan(inv, wps, key)
    n_inv = len(inv)
    maxes = [i.max_steps for i in inv] + [w.max_steps for w in wps]
    cache: Dict[Tuple[int, ...], Allocation] = {}

    def variations(state: Tuple[int, ...]) -> List[Variation]:
        out = []
        for i, it in enumerate(inv):                 # сначала замены персонажей…
            c = it.constellation_at(state[i])
            if c is not None:
                out.append(Variation(slot=it.slot, builds=[it.make(c)]))
        for j, w in enumerate(wps):                  # …потом оружие поверх них
            r = state[n_inv + j]
            if r > 0:
                out.append(Variation(slot=w.slot, weapons=[w.weapon.at(r)]))
        return out

    def evaluate(state: Tuple[int, ...]) -> Allocation:
        a = cache.get(state)
        if a is None:
            result = _compute(baseline, variations(state), tweak)
            a = Allocation(state, getattr(result, key), result)
            cache[state] = a
        return a

    if beam == "auto":
        ways = [1] + [0] * budget                 # число состояний с суммой шагов ≤ budget
        for m in maxes:
            ways = [sum(ways[s - k] for k in range(min(m, s) + 1)) for s in range(budget + 1)]
        beam = None if sum(ways) <= max_evals else 40

    zero = (0,) * len(maxes)
    start = evaluate(zero)
    plan.levels.append(LevelResult(0, start, [], [], 0.0, 0.0))
    frontier = [zero]

    for cost in range(1, budget + 1):
        nxt = set()
        for s in frontier:
            for i, m in enumerate(maxes):
                if s[i] >= m:
                    continue
                if i >= n_inv and not plan.weapon_available(i - n_inv, s):
                    continue
                nxt.add(s[:i] + (s[i] + 1,) + s[i + 1:])
        if not nxt:
            break
        allocs = sorted((evaluate(s) for s in nxt), key=lambda a: (-a.value, a.state))
        prev = plan.levels[-1].best
        best = allocs[0]
        delta = best.value - prev.value
        plan.levels.append(LevelResult(
            cost, best, allocs[1:keep], plan.changes(prev.state, best.state),
            delta, delta / prev.value * 100 if prev.value else 0.0))
        frontier = [a.state for a in (allocs if beam is None else allocs[:beam])] # type: ignore
    return plan


def plan_report(plan: InvestmentPlan) -> str:
    """Текстовая таблица: что докупать на каждом косте."""
    top = plan.best_value or 1.0
    rows = []
    for lv in plan.levels:
        step = "; ".join(c.text for c in lv.changes) or "база"
        hold = ", ".join(h.label for h in plan.holdings(lv.best.state)) or "—"
        rows.append([lv.cost, step, hold, fmt(lv.best.result.dpr), fmt(lv.best.result.dps),
                     f"{lv.delta_pct:+.1f}%" if lv.cost else "—",
                     f"{lv.best.value / top * 100:.1f}%"])
    return ("=== Порядок инвестиций ===\n"
            + table(rows, ["Кост", "Шаг", "Инвестиции", "DPR", "DPS", "к пред.", "% от макс."],
                    align="rllrrrr"))