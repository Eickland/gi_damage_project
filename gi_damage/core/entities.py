"""
Сущности: персонаж, созвездия, оружие, набор артефактов, сборка, цель.

Разделение по ТЗ:
  * Character      — база персонажа + таланты (источники урона) + пассивки
  * Constellation  — то, что добавляет созвездие (статы, баффы, источники урона)
  * Weapon         — база оружия + баффы (в т.ч. по рангу пробуждения R1..R5)
  * ArtifactSet    — статы и баффы набора
  * Build          — персонаж + созвездие + оружие + артефакты + «ручные» статы
  * Enemy          — параметры цели (сопротивления, защита, возвышение)
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Callable, Dict, List, Mapping, Optional, Sequence, Tuple

from .buffs import Buff, State
from .sources import DamageSource
from .stats import Stats

#: Доп. множитель источника урона: функция от (Stats персонажа) -> число.
#: Нужен, например, для пассивки Одетты: MIN(АТК-1000, 3000)*0.015/100 + 1
ExtraMultiplier = Callable[[Stats], float]


# --------------------------------------------------------------------------- #
@dataclass
class Constellation:
    """Одно созвездие персонажа."""

    number: int
    name: str = ""
    stats: Mapping[str, float] = field(default_factory=dict)
    buffs: Sequence[Buff] = field(default_factory=tuple)
    sources: Sequence[DamageSource] = field(default_factory=tuple)
    #: Изменения уже существующих источников урона: {имя источника: функция(src)->src}
    patches: Mapping[str, Callable[[DamageSource], DamageSource]] = field(default_factory=dict)
    multipliers: Mapping[str, ExtraMultiplier] = field(default_factory=dict)


# --------------------------------------------------------------------------- #
@dataclass
class Weapon:
    """Оружие. Ранг пробуждения (R1..R5) выбирается при сборке."""

    name: str
    base_atk: float = 0.0
    stats: Mapping[str, float] = field(default_factory=dict)
    #: баффы по рангу: {1: [...], 5: [...]} либо общий список в buffs
    buffs: Sequence[Buff] = field(default_factory=tuple)
    buffs_by_refinement: Mapping[int, Sequence[Buff]] = field(default_factory=dict)
    stats_by_refinement: Mapping[int, Mapping[str, float]] = field(default_factory=dict)
    refinement: int = 1
    note: str = ""

    def at(self, refinement: int) -> "Weapon":
        return replace(self, refinement=refinement)

    def resolved_stats(self) -> Dict[str, float]:
        out = dict(self.stats)
        for k, v in self.stats_by_refinement.get(self.refinement, {}).items():
            out[k] = out.get(k, 0.0) + v
        out["base_atk"] = out.get("base_atk", 0.0) + self.base_atk
        return out

    def resolved_buffs(self) -> List[Buff]:
        return list(self.buffs) + list(self.buffs_by_refinement.get(self.refinement, ()))


# --------------------------------------------------------------------------- #
@dataclass
class ArtifactSet:
    """Набор артефактов (обычно 4 предмета, но можно и 2+2)."""

    name: str
    pieces: int = 4
    stats: Mapping[str, float] = field(default_factory=dict)
    buffs: Sequence[Buff] = field(default_factory=tuple)
    #: статы/баффы, зависящие от количества предметов: {2: {...}, 4: {...}}
    stats_by_pieces: Mapping[int, Mapping[str, float]] = field(default_factory=dict)
    buffs_by_pieces: Mapping[int, Sequence[Buff]] = field(default_factory=dict)
    note: str = ""

    def resolved_stats(self) -> Dict[str, float]:
        out = dict(self.stats)
        for n, extra in self.stats_by_pieces.items():
            if self.pieces >= n:
                for k, v in extra.items():
                    out[k] = out.get(k, 0.0) + v
        return out

    def resolved_buffs(self) -> List[Buff]:
        out = list(self.buffs)
        for n, extra in self.buffs_by_pieces.items():
            if self.pieces >= n:
                out.extend(extra)
        return out


# --------------------------------------------------------------------------- #
@dataclass
class Character:
    """Персонаж: база, таланты, пассивки, созвездия."""

    name: str
    element: str
    weapon_type: str = ""
    level: int = 90
    stats: Mapping[str, float] = field(default_factory=dict)
    buffs: Sequence[Buff] = field(default_factory=tuple)
    sources: Sequence[DamageSource] = field(default_factory=tuple)
    constellations: Mapping[int, Constellation] = field(default_factory=dict)
    multipliers: Mapping[str, ExtraMultiplier] = field(default_factory=dict)
    crit_mode: str = "expected"
    default_field: str = "off_field"
    note: str = ""


def with_rotation(
    character: Character,
    sources: Optional[Sequence[DamageSource]] = None,
    constellation_sources: Optional[Mapping[int, Sequence[DamageSource]]] = None,
    constellation_patches: Optional[Mapping[int, Mapping[str, Callable[[DamageSource], DamageSource]]]] = None,
    extra_buffs: Optional[Sequence[Buff]] = None,
    constellation_extra_buffs: Optional[Mapping[int, Sequence[Buff]]] = None,
) -> Character:
    """Клонирует персонажа с ДРУГИМ набором источников урона — своих и по
    созвездиям, — оставляя статы/баффы/патчи/мультипликаторы (весь «кит»,
    определяемый самой игрой) без изменений.

    Нужно, когда один и тот же персонаж встречается в нескольких отрядах
    с разной ротацией: пишете статы/баффы/патчи ОДИН раз в «ките»
    (см. data/kits/), а под каждый отряд отдельно подставляете только
    occurrences/mv через этот хелпер.

        # data/kits/mizuki.py — один раз
        MIZUKI_KIT = Character(name="Мидзуки", ..., sources=(),
                                constellations={1: Constellation(1, "C1"),
                                                ...})

        # data/teams/some_team.py — под конкретную ротацию
        MIZUKI = with_rotation(MIZUKI_KIT,
            sources=(elemental(...), ...),
            constellation_sources={1: (stellar_swirl(...), elemental(...))},
        )

    `Constellation.patches` в ките сопоставляются по ИМЕНИ источника
    (см. Build.all_sources) — значит, имена в sources= у разных отрядов
    должны совпадать с именами, которые ждут патчи в ките, иначе патч
    молча не применится (сматчить будет не с чем).

    Если для константы (номера созвездия) не передан свой список
    источников — созвездие берётся из кита без изменений (обычно это
    верно для тех, где sources пустые, а есть только buffs/patches).

    constellation_patches — для случая, когда СОЗВЕЗДИЕ патчит occurrences/mv
    именованного источника (а не добавляет новый), и эти occurrences/mv сами
    зависят от ротации — то есть в разных отрядах патч должен быть разным
    (typичный пример: C4 просто меняет количество ударов у уже существующей
    атаки). В ките для такого созвездия patches обычно не задают вообще —
    задают per-team здесь. Патчи из кита и отсюда объединяются (per-team
    добавляются, не заменяют — если оба патчат одно и то же имя, кит
    применяется первым, per-team вторым).

    extra_buffs / constellation_extra_buffs — на случай, если для КОНКРЕТНОГО
    отряда персонажу нужен разовый бафф, которого нет в общем ките (например,
    какая-то реакция или окно есть только в этой ротации). Баффы кита при этом
    никуда не деваются — extra_buffs ДОБАВЛЯЮТСЯ к ним, а не заменяют их.
    Обычно это не нужно: если баффы кита правильно завязаны на теги состояния
    (ON/OFF/INST/...), они сами включаются и выключаются под любую ротацию,
    ничего в них менять не приходится — различаются как раз только
    occurrences/mv, для этого и есть sources=/constellation_sources=.
    """
    new_character = character
    if sources is not None:
        new_character = replace(new_character, sources=tuple(sources))
    if constellation_sources:
        new_constellations = dict(new_character.constellations)
        for number, srcs in constellation_sources.items():
            base_c = new_constellations.get(number) or Constellation(number=number)
            new_constellations[number] = replace(base_c, sources=tuple(srcs))
        new_character = replace(new_character, constellations=new_constellations)
    if constellation_patches:
        new_constellations = dict(new_character.constellations)
        for number, patches in constellation_patches.items():
            base_c = new_constellations.get(number) or Constellation(number=number)
            new_constellations[number] = replace(
                base_c, patches={**base_c.patches, **patches})
        new_character = replace(new_character, constellations=new_constellations)
    if extra_buffs:
        new_character = replace(
            new_character, buffs=tuple(new_character.buffs) + tuple(extra_buffs))
    if constellation_extra_buffs:
        new_constellations = dict(new_character.constellations)
        for number, buffs in constellation_extra_buffs.items():
            base_c = new_constellations.get(number) or Constellation(number=number)
            new_constellations[number] = replace(
                base_c, buffs=tuple(base_c.buffs) + tuple(buffs))
        new_character = replace(new_character, constellations=new_constellations)
    return new_character


# --------------------------------------------------------------------------- #
@dataclass
class Build:
    """Готовая сборка персонажа: кто, с чем, с каким созвездием."""

    character: Character
    constellation: int = 0
    weapon: Optional[Weapon] = None
    artifacts: Sequence[ArtifactSet] = field(default_factory=tuple)
    #: «ручные» статы: сабстаты, главстаты, всё, что не разложено по источникам
    extra_stats: Mapping[str, float] = field(default_factory=dict)
    extra_buffs: Sequence[Buff] = field(default_factory=tuple)
    extra_sources: Sequence[DamageSource] = field(default_factory=tuple)
    #: доля времени ротации, приходящаяся на персонажа (секунды)
    time: float = 0.0
    crit_mode: Optional[str] = None
    default_field: Optional[str] = None
    label: str = ""     # если нужно отличать двух одинаковых персонажей

    # ---- производные ------------------------------------------------------- #
    @property
    def name(self) -> str:
        return self.label or self.character.name

    @property
    def element(self) -> str:
        return self.character.element

    def active_constellations(self) -> List[Constellation]:
        return [c for n, c in sorted(self.character.constellations.items())
                if n <= self.constellation]

    def base_stats(self) -> Stats:
        """Статы БЕЗ баффов отряда — «сырая» база (аналог строки 'EM no % buff')."""
        s = Stats()
        s.add_many(self.character.stats)
        for c in self.active_constellations():
            s.add_many(c.stats)
        if self.weapon is not None:
            s.add_many(self.weapon.resolved_stats())
        for art in self.artifacts:
            s.add_many(art.resolved_stats())
        s.add_many(self.extra_stats)
        return s

    def all_buffs(self) -> List[Tuple[str, Buff]]:
        """Все баффы, которые ЭТА сборка даёт (владелец, бафф)."""
        out: List[Tuple[str, Buff]] = []
        for b in self.character.buffs:
            out.append((self.name, b))
        for c in self.active_constellations():
            for b in c.buffs:
                out.append((self.name, b))
        if self.weapon is not None:
            for b in self.weapon.resolved_buffs():
                out.append((self.name, b))
        for art in self.artifacts:
            for b in art.resolved_buffs():
                out.append((self.name, b))
        for b in self.extra_buffs:
            out.append((self.name, b))
        return out

    def all_sources(self) -> List[DamageSource]:
        """Источники урона с учётом созвездий (добавления и патчи)."""
        sources = {s.name: s for s in self.character.sources}
        order = [s.name for s in self.character.sources]
        for c in self.active_constellations():
            for name, patch in c.patches.items():
                if name in sources:
                    sources[name] = patch(sources[name])
            for s in c.sources:
                if s.name not in sources:
                    order.append(s.name)
                sources[s.name] = s
        for s in self.extra_sources:
            if s.name not in sources:
                order.append(s.name)
            sources[s.name] = s
        return [sources[n] for n in order]

    def extra_multipliers(self) -> Dict[str, ExtraMultiplier]:
        out = dict(self.character.multipliers)
        for c in self.active_constellations():
            out.update(c.multipliers)
        return out

    def effective_crit_mode(self) -> str:
        return self.crit_mode or self.character.crit_mode

    def effective_field(self) -> str:
        return self.default_field or self.character.default_field

    # ---- замены (для ростеров) --------------------------------------------- #
    def with_weapon(self, weapon: Weapon) -> "Build":
        return replace(self, weapon=weapon)

    def with_constellation(self, n: int) -> "Build":
        return replace(self, constellation=n)

    def with_artifacts(self, *sets: ArtifactSet) -> "Build":
        return replace(self, artifacts=tuple(sets))

    def describe(self) -> str:
        parts = [f"{self.name} C{self.constellation}"]
        if self.weapon is not None:
            parts.append(f"{self.weapon.name} R{self.weapon.refinement}")
        if self.artifacts:
            parts.append("/".join(a.name for a in self.artifacts))
        return " | ".join(parts)


# --------------------------------------------------------------------------- #
@dataclass
class Enemy:
    """Цель.

    Сопротивление можно задать двумя способами.

    1) `res` — БАЗОВОЕ сопротивление цели по стихиям, в долях
       (0.10 = 10%). Тогда снижения сопротивления, накопленные в статах
       атакующего (ключ "res_reduction" / "res_reduction.<стихия>"),
       вычитаются автоматически, а множитель считается по формуле
       formulas.resistance_multiplier(). Это рекомендуемый способ: снижение
       сопротивления становится обычным баффом и может зависеть от состояния
       (например работать только внутри окна навыка).

    2) `res_mult` — ГОТОВЫЙ множитель (как в исходной таблице: 0.9, 1.15, …).
       Такие значения берутся как есть, снижения к ним НЕ применяются —
       предполагается, что они уже всё учитывают.

    Если стихия есть в `res`, используется способ 1; иначе способ 2.

    def_mult — готовый множитель защиты (в таблице 0.4875).
    """

    name: str = "Цель"
    level: int = 100
    res: Mapping[str, float] = field(default_factory=dict)
    res_mult: Mapping[str, float] = field(default_factory=dict)
    default_res_mult: float = 0.9
    def_mult: float = 0.4875
    elevation: float = 0.0

    def res_for(self, element: str) -> float:
        """Готовый множитель без учёта снижений (способ 2)."""
        return self.res_mult.get(element, self.default_res_mult)

    def res_multiplier(self, element: str, reduction: float = 0.0) -> float:
        """Итоговый множитель сопротивления с учётом снижения `reduction`."""
        from .formulas import resistance_multiplier
        
        if element in self.res:            
            return resistance_multiplier(self.res[element] - reduction)
        
        return self.res_for(element)


# --------------------------------------------------------------------------- #
def add_state_tags(build: Build, *tags: str) -> Build:
    """Добавить теги ко ВСЕМ вхождениям источников урона сборки.

    Удобно, когда весь кусок ротации попадает в одно окно усиления:

        build = add_state_tags(build, "dreamdrifter")

    Если в окно попадает только часть ударов — правьте `occurrences`
    у нужных источников вручную (или через Constellation.patches).
    """
    from .sources import Occurrence
    patched = []
    for src in build.all_sources():
        patched.append(replace(src, occurrences=[
            Occurrence(frozenset(o.state | set(tags)), o.count)
            for o in src.occurrences
        ]))
    return replace(build, extra_sources=tuple(patched))