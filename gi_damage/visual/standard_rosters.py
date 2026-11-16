"""Стандартные ростеры отряда: созвездия, оружие и артефакты КАЖДОГО персонажа.

    from gi_damage.visual.standard_rosters import run_standard
    from gi_damage.teams.<отряд> import builds
    run_standard(builds, sys.argv[1:])          # → <папка отряда>/rosters.html

База — первая команда из builds.all_teams(). Для каждого персонажа и каждой
оси (созвездия / оружие / артефакты) вариант собирается так, чтобы учесть
логику отряда:

  1. make_team(**база, <ключ>_c / _weapon / _artifacts = вариант) — если
     у make_team есть такой параметр и с параметрами базы он воспроизводит
     базовую команду (тогда пересобирается весь отряд: стаки C2 Даники,
     взрыв Одетты с C4 и т.п.);
  2. иначе <ключ>_build(constellation=…, weapon=…, artifacts=…) из файла
     отряда — тоже с проверкой, что воспроизводит базу;
  3. иначе просто замена поля сборки.

Правила, общие для всех отрядов (раньше были tweak-функциями в ростерах):
  * один 4-шт. набор с баффом отряду (Изумрудная тень, Миллелит, Знать,
    Сердце горна, Инструктор) не носят двое. Если персонаж надевает такой
    набор, а его уже носит сокомандник, у которого в ARTIFACTS есть замена,
    сокомандник переодевается (сначала в прежний набор персонажа — обмен),
    и набор из отряда не пропадает; иначе вариант пропускается;
  * Изумрудная тень остаётся в отряде: если её снял ДД, её надевает
    Фарузан / Сахароза; если ДД её надел, они переходят на Инструктора;
  * Мидзуки C6 — корона на МС вместо крита;
  * Сайно — главные статы следуют за оружием (сигна: МС/МС/крит).

Кандидаты оружия и артефактов — словари WEAPONS / ARTIFACTS ниже (собраны
из того, что персонажи носят в проекте). Правьте их здесь — изменения
подхватят все отряды. Ось, где вариант один, не выводится.
"""

from __future__ import annotations

import inspect
from dataclasses import replace
from pathlib import Path
from typing import Callable, Dict, List, Optional, Sequence, Tuple

from ..core.engine import Team
from ..core.report import hit_details, source_breakdown, team_summary
from ..core.stats import S
from ..data import artifacts as A
from ..data import weapons as W
from .rosters import RosterBook

CONSTELLATIONS = (0, 1, 2, 3, 4, 5, 6)

#: персонаж -> префиксы параметров make_team / имени <префикс>_build
KEYS: Dict[str, Tuple[str, ...]] = {
    "Крио ГГ": ("cmc", "cryo_mc"), "Анастасия": ("anastasia",), "Одетта": ("odette",),
    "Даника": ("danika",), "Митя": ("mitya",), "Яэ Мико": ("yae",), "Алеша": ("alyosha",),
    "Сандроне": ("sandrone",), "Сайно": ("cyno",), "Ризли": ("wrio", "wriothesley"),
    "Весна": ("vesna",), "Мидзуки": ("mizuki",), "Фарузан": ("faruzan",),
    "Водяница": ("vodya", "vodyanitsa"), "Валера": ("valera",), "Сахароза": ("sucrose",),
    "Диона": ("diona",), "Ци Ци": ("qiqi",), "Николь": ("nicole",), "Шилонен": ("xilonen",),
    "Цзы Бай": ("zibai",), "Линея": ("linnea",), "Колумбина": ("columbina",),
    "Иллуги": ("illuga",),
}

#: Кандидаты оружия. Оружие базы добавляется само (в т.ч. «Эпос» нужного вида).
WEAPONS: Dict[str, Sequence] = {
    "Цзы Бай": (W.HARBINGER.at(5), W.FLUTE_OF_EZPITZAL.at(5), W.MOONSHARD.at(1), W.MOONSHARD.at(5)),
    "Линея": (W.SLINGSHOT.at(5), W.COVENANT_FROST_SNOW.at(5), W.GOLDEN_OATH.at(1), W.GOLDEN_OATH.at(5), W.ARTEMISIA.at(1),W.ARTEMISIA.at(3),W.ARTEMISIA.at(5)),
    "Колумбина": (W.PROTOTYPE_AMBER.at(5), W.NOCTURNE.at(1), W.NOCTURNE.at(5), W.SAC_JADE.at(1),W.SAC_JADE.at(5)),
    "Алеша": (W.FAV_LANCE, W.SYMPHONIST.at(1), W.SYMPHONIST.at(5)),
    "Анастасия": (W.CHAIN_BREAKER.at(5), W.BREEZEBORNE_BOW.at(1),W.BREEZEBORNE_BOW.at(3), W.BREEZEBORNE_BOW.at(5), W.ARTEMISIA.at(1),W.ARTEMISIA.at(3),W.ARTEMISIA.at(5),
                  W.SILVER_RADIANCE.at(1),W.SILVER_RADIANCE.at(5),),
    "Валера": (W.FINALE.at(5), W.FAV_SWORD),
    "Весна": (W.EMBERWELL.at(5), W.CHRYSALIS.at(1), W.CHRYSALIS.at(5), W.FROSTFEATHER.at(1),
              W.FROSTFEATHER.at(5), W.BOUGH.at(1), W.BOUGH.at(5)),
    "Водяница": (W.MAELSTROM.at(1), W.MAELSTROM.at(5)),
    "Даника": (W.FAV_GREATSWORD, W.ATONEMENT.at(5), W.SPRING_TIDE.at(1), W.SPRING_TIDE.at(5)),
    "Диона": (W.FAV_BOW, W.BREEZEBORNE_BOW.at(1),W.BREEZEBORNE_BOW.at(3), W.BREEZEBORNE_BOW.at(5)),
    "Крио ГГ": (W.EXAIPHANES.at(5), W.FAV_SWORD),
    "Мидзуки": (W.WANDERER_SONG.at(5), W.SUNNY_MORNING_SLEEP_IN.at(1), W.RELIQUARY_OF_TRUTH,
                W.SAC_JADE.at(5), W.STARCALLERS_WATCH, W.SACFRAG.at(5), W.STARSEALED.at(1)),
    "Митя": (W.SPINDLELUTE.at(5), W.STARSEALED.at(1), W.STARSEALED.at(5), W.RELIQUARY_OF_TRUTH,W.WANDERING_STAR.at(1),W.WANDERING_STAR.at(5)),
    "Одетта": (W.SILVER_LIGHT.at(5), W.FROSTFEATHER.at(1), W.FROSTFEATHER.at(5), W.AZURELIGHT.at(1),
               W.FINALE.at(5), W.HARBINGER.at(5), W.BOUGH.at(5), W.EMBERWELL.at(5), W.BOUGH.at(1)),
    "Ризли": (W.TREASURY_OVERSIGHT.at(1), W.WANDERER_SONG_CRYO.at(5), W.SACFRAG.at(5), W.STARSEALED.at(1), W.KAGURA.at(1),
              W.ECHOES.at(5)),
    "Сайно": (W.DEATHMATCH.at(1), W.SCARLET_SANDS.at(1),W.DEATHMATCH.at(5),W.SCARLET_SANDS.at(5)),
    "Сандроне": (W.MAGIC_SUPERSWORD,W.ATONEMENT.at(5), W.TIDAL_SHADOW.at(5), W.FLOWER,
                 W.THOUSAND_SUNS.at(1), W.TEASPOON, W.TEASPOON.at(5)),
    "Сахароза": (W.SACFRAG.at(5), W.CODEX_FAVONIUS,W.WANDERING_STAR.at(1),W.WANDERING_STAR.at(5)),
    "Фарузан": (W.FAV_BOW, W.BREEZEBORNE_BOW.at(1),W.BREEZEBORNE_BOW.at(3), W.BREEZEBORNE_BOW.at(5)),
    "Яэ Мико": (W.ECHOES.at(5), W.KAGURA.at(1), W.WANDERER_SONG_ELECTRO.at(5), W.WINTER.at(1), W.WINTER.at(5),W.WANDERING_STAR.at(1),W.WANDERING_STAR.at(5)),
}

#: Кандидаты наборов артефактов (комплект — кортеж наборов). База добавляется сама.
ARTIFACTS: Dict[str, Sequence[Tuple]] = {
    "Алеша": ((A.HEART_OF_FORGE,), (A.NOBLESSE,)),
    "Анастасия": ((A.STELLAR_SET,), (A.DISENCHANTMENT,), (A.HEART_OF_FORGE,), (A.MILLELITH,)),
    "Валера": ((A.NOBLESSE,), (A.HEART_OF_FORGE,),(A.HEART_OF_FORGE.at(2), A.SCARLET_PROOF.at(2))),
    "Весна": ((A.SCARLET_PROOF,), (A.NIGHT_SKY.at(2), A.AUBADE.at(2)),(A.HEART_OF_FORGE.at(2), A.SCARLET_PROOF.at(2),(A.VIRIDESCENT,))),
    "Водяница": ((A.MILLELITH,), (A.MILLELITH.at(2), A.VOURUKASHA.at(2)),),
    "Даника": ((A.HEART_OF_FORGE,), (A.MILLELITH,), (A.NOBLESSE,)),
    "Диона": ((A.MILLELITH,), (A.NOBLESSE,), (A.HEART_OF_FORGE,)),
    "Крио ГГ": ((A.DISENCHANTMENT,), (A.MILLELITH,), (A.NOBLESSE,),
                (A.HEART_OF_FORGE,), (A.HEART_OF_FORGE.at(2), A.SCARLET_PROOF.at(2)), ((A.NIGHT_SKY.at(2), A.AUBADE.at(2)))),
    "Мидзуки": ((A.VIRIDESCENT,), (A.NIGHT_SKY.at(2), A.AUBADE.at(2)), (A.GILDED,),
                (A.SCARLET_PROOF,)),
    "Митя": ((A.MILLELITH,), (A.DISENCHANTMENT,), (A.HEART_OF_FORGE,),
             (A.AUBADE.at(2), A.GILDED.at(2))),
    "Одетта": ((A.STELLAR_SET,), (A.DISENCHANTMENT,), (A.HEART_OF_FORGE,), (A.MILLELITH,)),
    "Ризли": ((A.DISENCHANTMENT,), (A.HEART_OF_FORGE.at(2), A.SCARLET_PROOF.at(2)),(A.STELLAR_SET,)),
    "Сайно": ((A.DISENCHANTMENT,), (A.HEART_OF_FORGE.at(2), A.SCARLET_PROOF.at(2))),
    "Сандроне": ((A.DISENCHANTMENT,), (A.NIGHT_SKY.at(2), A.AUBADE.at(2)), (A.HEART_OF_FORGE.at(2), A.SCARLET_PROOF.at(2))),
    "Сахароза": ((A.VIRIDESCENT,), (A.INSTRUCTOR,)),
    "Фарузан": ((A.VIRIDESCENT,), (A.NOBLESSE,), (A.MILLELITH,), (A.INSTRUCTOR,)),
    "Яэ Мико": ((A.DISENCHANTMENT,), (A.MILLELITH,), (A.HEART_OF_FORGE,)),
    "Ци Ци": ((A.MILLELITH,), (A.HEART_OF_FORGE,)),
    "Шилонен": ((A.INSTRUCTOR,)),
    "Николь": ((A.HEART_OF_FORGE.at(2), A.SCARLET_PROOF.at(2))),
}

#: 4-шт. наборы с баффом отряду — двое их не носят
UNIQUE_SETS = {A.VIRIDESCENT.name, A.MILLELITH.name, A.NOBLESSE.name,
               A.HEART_OF_FORGE.name, A.INSTRUCTOR.name}
#: кто надевает Изумрудную тень, если её снял другой
VV_FALLBACK = ("Фарузан", "Сахароза")

AXES = (("c", "Созвездия"), ("weapon", "Оружие"), ("artifacts", "Артефакты"))


# --------------------------------------------------------------------------- #
#  Сборка вариантов                                                            #
# --------------------------------------------------------------------------- #
def _dps(team: Team) -> float:
    return team.compute().dps


def _same(a: float, b: float) -> bool:
    return abs(a - b) <= 1e-9 * max(1.0, abs(a))


def _wkey(w) -> Tuple:
    return (w.name, w.refinement) if w is not None else None


def _flat(arts) -> Tuple:
    """Комплект наборов без вложенности: ((SET,),) и SET -> (SET,)."""
    if not isinstance(arts, (tuple, list)):
        return (arts,)
    out = []
    for a in arts:
        out.extend(_flat(a) if isinstance(a, (tuple, list)) else (a,))
    return tuple(out)


def _akey(arts) -> Tuple:
    return tuple((a.name, a.pieces) for a in _flat(arts))


def _base_kwargs(mod) -> Optional[dict]:
    variants = getattr(mod, "VARIANTS", None)
    if not variants:
        return {}
    first = variants[0]
    if isinstance(first, dict):
        return dict(first)
    if isinstance(first, tuple) and len(first) == 2 and isinstance(first[1], dict):
        return dict(first[1])
    return None


def _team_param(mod, char: str, axis: str) -> Optional[str]:
    make = getattr(mod, "make_team", None)
    if make is None:
        return None
    params = inspect.signature(make).parameters
    sfx = {"c": ("_c",), "weapon": ("_weapon",),
           "artifacts": ("_artifacts", "_arts", "_art")}[axis]
    for p in KEYS.get(char, ()):
        for s in sfx:
            if p + s in params:
                return p + s
    return None


def _build_fn(mod, char: str) -> Optional[Callable]:
    for p in KEYS.get(char, ()):
        fn = getattr(mod, f"{p}_build", None)
        if fn is not None:
            return fn
    return None


def _swap(team: Team, char: str, build) -> Team:
    return replace(team, builds=[build if b.name == char else b for b in team.builds])


def _cyno_main(build, weapon):
    from ..data.characters.cyno import cyno_main_stats
    old_m, new_m = cyno_main_stats(build.weapon), cyno_main_stats(weapon)
    st = dict(build.extra_stats)
    for k, v in old_m.items():
        st[k] = st.get(k, 0.0) - v
    for k, v in new_m.items():
        st[k] = st.get(k, 0.0) + v
    return {k: v for k, v in st.items() if abs(v) > 1e-12}


class _Maker:
    """Способ пересобрать отряд с изменённым параметром персонажа."""

    def __init__(self, mod, base: Team, char: str, axis: str):
        self.mod, self.base, self.char, self.axis = mod, base, char, axis
        self.b = base.build(char)
        self.base_dps = _dps(base)
        self.mode = "field"
        kw = _base_kwargs(mod)
        param = _team_param(mod, char, axis)
        if param is not None and kw is not None:
            try:
                if _same(_dps(mod.make_team("база", **kw)), self.base_dps):
                    self.mode, self.param, self.kw = "team", param, kw
                    return
            except Exception:
                pass
        fn = _build_fn(mod, char)
        if fn is not None:
            try:
                if _same(_dps(_swap(base, char, self._call_fn(fn, {}))), self.base_dps):
                    self.mode, self.fn = "build", fn
            except Exception:
                pass

    def _call_fn(self, fn, change: dict):
        b = self.b
        args = {"constellation": b.constellation, "weapon": b.weapon,
                "artifacts": _flat(b.artifacts)}
        args.update(change)
        params = inspect.signature(fn).parameters
        args = {k: v for k, v in args.items() if k in params}
        try:
            return fn(**args)
        except Exception:
            if "artifacts" in args and len(args["artifacts"]) == 1:
                args["artifacts"] = args["artifacts"][0]
                return fn(**args)
            raise

    def team(self, value) -> Team:
        field = {"c": "constellation", "weapon": "weapon", "artifacts": "artifacts"}[self.axis]
        if self.mode == "team":
            tries = [value]
            if self.axis == "artifacts" and len(value) == 1:
                tries.append(value[0])      # make_team ждёт один набор, а не кортеж
            last = None
            for v in tries:
                try:
                    team = self.mod.make_team(self.char, **{**self.kw, self.param: v})
                    team.compute()          # проверка, что вариант собирается
                    return team
                except Exception as exc:
                    last = exc
            raise last
        if self.mode == "build":
            return _swap(self.base, self.char, self._call_fn(self.fn, {field: value}))
        nb = replace(self.b, **{field: value})
        if self.axis == "weapon" and self.char == "Сайно":
            nb = replace(nb, extra_stats=_cyno_main(self.b, value))
        return _swap(self.base, self.char, nb)


def _holders(team: Team, set_name: str) -> List[str]:
    return [b.name for b in team.builds
            if any(a.name == set_name and a.pieces >= 4 for a in _flat(b.artifacts))]


def _apply_rules(team: Team, base: Team, char: str, axis: str, value) -> Tuple[Optional[Team], str]:
    """(команда, пометка) или (None, причина пропуска)."""
    note = ""
    if axis == "c" and char == "Мидзуки" and value >= 6 and base.build(char).constellation < 6:
        m = team.build(char)
        st = dict(m.extra_stats)
        if st.get(S.CRIT_VALUE, 0) >= 0.622 - 1e-9:
            st[S.CRIT_VALUE] = st[S.CRIT_VALUE] - 0.622
            st[S.BASE_EM] = st.get(S.BASE_EM, 0) + 187
            team = _swap(team, char, replace(m, extra_stats=st))
            note = "корона на МС"
    if axis == "artifacts":
        vv = A.VIRIDESCENT.name
        if _holders(base, vv) and not _holders(team, vv):
            for who in VV_FALLBACK:
                if who != char and who in [b.name for b in team.builds]:
                    team = _swap(team, who, replace(team.build(who), artifacts=(A.VIRIDESCENT,)))
                    note = f"Изумрудная тень — у {who}"
                    break
        others = [w for w in _holders(team, vv) if w != char]
        if char in _holders(team, vv) and others and others[0] in VV_FALLBACK:
            who = others[0]
            team = _swap(team, who, replace(team.build(who), artifacts=(A.INSTRUCTOR,)))
            note = f"{who} — Инструктор вместо Изумрудной тени"
        team, swap_note = _swap_support_sets(team, base, char)
        if swap_note:
            note = "; ".join(x for x in (note, swap_note) if x)
        for s in UNIQUE_SETS:
            h = _holders(team, s)
            if len(h) > 1:
                return None, f"{s} уже у {', '.join(x for x in h if x != char)}"
    return team, note


def _set_names(arts) -> set:
    return {a.name for a in _flat(arts) if a.pieces >= 4}


def _swap_support_sets(team: Team, base: Team, char: str) -> Tuple[Team, str]:
    """Персонаж надел 4-шт. набор с баффом отряду, который уже носит другой.
    Если этот набор есть в словаре ARTIFACTS персонажа, а у второго в словаре
    есть замена — второй переодевается, набор остаётся в отряде:
      1) в прежний набор персонажа (обмен сетами), если может его носить;
      2) иначе — в первый набор из своего словаря без конфликтов."""
    mine = _set_names(team.build(char).artifacts)
    allowed = {n for arts in ARTIFACTS.get(char, ()) for n in _set_names(arts)}
    old = _flat(base.build(char).artifacts)
    notes = []
    for s in sorted(mine & UNIQUE_SETS & allowed):
        for who in [x for x in _holders(team, s) if x != char]:
            if who == "Фарузан" or who == "Сахароза":
                if s == A.VIRIDESCENT.name:
                    continue                    # Изумрудная тень — отдельное правило
            cands = [old] + [_flat(a) for a in ARTIFACTS.get(who, ())]
            own = {_akey(_flat(a)) for a in ARTIFACTS.get(who, ())}
            for arts in cands:
                if arts is not old and _akey(arts) not in own:
                    continue
                if arts is old and _akey(old) not in own:
                    continue
                trial = _swap(team, who, replace(team.build(who), artifacts=arts))
                if all(len(_holders(trial, u)) <= 1 for u in UNIQUE_SETS) and s not in _set_names(arts):
                    team = trial
                    label = "/".join(a.name if a.pieces >= 4 else f"{a.name}({a.pieces})" for a in arts)
                    notes.append(f"{who} — {label} вместо {s}")
                    break
    return team, "; ".join(notes)


def _options(char: str, axis: str, b) -> List:
    if axis == "c":
        return list(CONSTELLATIONS)
    if axis == "weapon":
        out, seen = [], set()
        for w in (b.weapon,) + tuple(WEAPONS.get(char, ())):
            if w is not None and _wkey(w) not in seen:
                seen.add(_wkey(w)); out.append(w)
        return out
    out, seen = [], set()
    for arts in (_flat(b.artifacts),) + tuple(ARTIFACTS.get(char, ())):
        if _akey(arts) not in seen:
            seen.add(_akey(arts)); out.append(_flat(arts))
    return out


def _label(axis: str, value) -> str:
    if axis == "c":
        return f"C{value}"
    if axis == "weapon":
        return f"{value.name} R{value.refinement}"
    return "/".join(a.name if a.pieces >= 4 else f"{a.name}({a.pieces})" for a in _flat(value))


def add_standard_sections(book: RosterBook, mod, base: Optional[Team] = None,
                          chars: Optional[Sequence[str]] = None,
                          skip: Sequence[Tuple[str, str]] = ()) -> None:
    """Добавить в book ростеры созвездий / оружия / артефактов персонажей отряда.

    skip — какие ростеры не строить: пары (персонаж, ось), ось — "c",
    "weapon" или "artifacts". Например {("Мидзуки", "weapon")}."""
    skip = set(skip)
    base = base or next(iter(mod.all_teams().values()))
    for b in base.builds:
        char = b.name
        if chars is not None and char not in chars:
            continue
        for axis, title in AXES:
            if (char, axis) in skip:
                continue
            opts = _options(char, axis, b)
            if len(opts) < 2:
                continue
            maker = _Maker(mod, base, char, axis)
            results, notes, base_idx = [], [], 0
            base_val = _options(char, axis, b)[0] if axis != "c" else b.constellation
            for v in opts:
                try:
                    team, note = _apply_rules(maker.team(v), base, char, axis, v)
                    if team is not None:
                        team.compute()
                except Exception as exc:          # вариант не собирается
                    notes.append(f"{_label(axis, v)}: ошибка {type(exc).__name__}: {exc}")
                    continue
                if team is None:
                    notes.append(f"{_label(axis, v)} пропущен: {note}")
                    continue
                if note:
                    notes.append(f"{_label(axis, v)}: {note}")
                if v is base_val or (axis == "c" and v == base_val):
                    base_idx = len(results)
                results.append(replace(team, name=_label(axis, v)).compute())
            if len(results) >= 2:
                if maker.mode == "field":
                    notes.append("вариант собран заменой поля сборки (без пересборки отряда)")
                book.add(results, f"{title} — {char}", ascending=True, notes=notes,
                         base=base_idx)


def run_standard(mod, argv: Sequence[str] = (),
                 extra: Optional[Callable[[RosterBook, Team], None]] = None,
                 out: Optional[str | Path] = None,
                 skip: Sequence[Tuple[str, str]] = ()) -> int:
    """Сводка команд отряда + стандартные ростеры + extra(book, base) → HTML.

    По умолчанию HTML пишется в папку отряда: <папка>/rosters.html.
    """
    argv = list(argv)
    details = "--details" in argv
    if "--out" in argv:
        out = argv[argv.index("--out") + 1]
    teams = mod.all_teams()
    for team in teams.values():
        result = team.compute()
        print(team_summary(result))
        if details:
            print(source_breakdown(result))
            print()
            print(hit_details(result))
            print()
    base = next(iter(teams.values()))
    book = RosterBook()
    add_standard_sections(book, mod, base, skip=skip)
    if extra is not None:
        extra(book, base)
    path = Path(out) if out else Path(mod.__file__).with_name("rosters.html")
    book.save(path, title=f"Ростеры: {base.name}")
    print(f"HTML: {path.resolve()}")
    return 0


def print_main_stats(mod, who: str, key: str, options: Sequence[Tuple[str, dict]]) -> None:
    """Главные статы в карточках ростера не различимы — сравниваем текстом.

    key — параметр make_team (например "cyno_main_stats")."""
    print(f"=== Главные статы: {who} ===")
    for label, main in options:
        r = mod.make_team(label, **{key: main}).compute()
        print(f"{label:<18} DPR {r.dpr:>12,.0f}  DPS {r.dps:>10,.0f}")
    print()
