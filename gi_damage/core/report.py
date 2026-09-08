"""Вывод результатов: текстовые таблицы и разбивка по источникам."""

from __future__ import annotations

from typing import Dict, Iterable, List, Sequence

from .engine import TeamResult


def fmt(x: float, digits: int = 0) -> str:
    return f"{x:,.{digits}f}".replace(",", " ")


def table(rows: Sequence[Sequence[object]], headers: Sequence[str],
          align: str = "") -> str:
    """Простая ASCII-таблица без внешних зависимостей."""
    data = [[str(c) for c in row] for row in rows]
    cols = len(headers)
    widths = [len(h) for h in headers]
    for row in data:
        for i in range(cols):
            widths[i] = max(widths[i], len(row[i]))
    align = (align + "l" * cols)[:cols]

    def line(cells: Sequence[str]) -> str:
        out = []
        for i, c in enumerate(cells):
            out.append(c.ljust(widths[i]) if align[i] == "l" else c.rjust(widths[i]))
        return "  ".join(out).rstrip()

    sep = "  ".join("-" * w for w in widths)
    return "\n".join([line(headers), sep] + [line(r) for r in data])


def team_summary(result: TeamResult) -> str:
    """Итоги по отряду: урон каждого персонажа, DPR, DPS."""
    rows = []
    for name, ch in result.characters.items():
        rows.append([name, fmt(ch.direct), fmt(ch.reaction), fmt(ch.total)])
    rows.append(["ИТОГО",
                 fmt(sum(c.direct for c in result.characters.values())),
                 fmt(sum(c.reaction for c in result.characters.values())),
                 fmt(result.dpr)])
    body = table(rows, ["Персонаж", "Прямой урон", "Урон реакций", "Всего"], align="lrrr")
    return (f"=== {result.team_name} ===\n{body}\n"
            f"\nВремя ротации: {result.rotation_time:g} с"
            f"\nDPR: {fmt(result.dpr)}"
            f"\nDPS: {fmt(result.dps)}\n")


def source_breakdown(result: TeamResult, digits: int = 0) -> str:
    """Подробная разбивка по источникам урона."""
    rows = []
    for name, ch in result.characters.items():
        for src, value in ch.by_source().items():
            rows.append([name, src, fmt(value, digits)])
        for src, value in ch.reaction_breakdown.items():
            rows.append([name, f"[реакция] {src}", fmt(value, digits)])
    return table(rows, ["Персонаж", "Источник", "Урон"], align="llr")


def hit_details(result: TeamResult) -> str:
    """Совсем подробно: каждое вхождение источника со своим состоянием."""
    rows = []
    for name, ch in result.characters.items():
        for h in ch.hits:
            tags = ", ".join(sorted(h.state)) or "-"
            rows.append([name, h.source, tags, f"{h.count:g}",
                         fmt(h.per_hit), fmt(h.total)])
    return table(rows, ["Персонаж", "Источник", "Состояние", "Кол-во",
                        "За удар", "Всего"], align="lllrrr")


def _setup_fields(result: TeamResult) -> Dict[str, str]:
    """Раскладка отряда в виде плоского словаря «поле -> значение»."""
    fields: Dict[str, str] = {
        "Ротация": result.rotation or "—",
        "Время ротации": f"{result.rotation_time:g} с",
    }
    for name, s in result.setup.items():
        fields[f"{name}\0созвездие"] = f"C{s.constellation}"
        fields[f"{name}\0оружие"] = s.weapon or "—"
        fields[f"{name}\0артефакты"] = s.artifacts or "—"
        fields[f"{name}\0время"] = f"{s.time:g} с"
    return fields


def roster_report(results: Sequence[TeamResult], key: str = "dps",
                  title: str = "", ascending: bool = False) -> str:
    """Отчёт по перебору: что осталось постоянным и что дало какой результат.

    Постоянные и переменные части определяются автоматически — сравнением
    раскладок всех вариантов между собой.

    key       — по какому полю сортировать ("dps" или "dpr")
    ascending — True: от худшего к лучшему (по умолчанию наоборот)

    Колонка «% от предыдущего» — отношение к строке НАД текущей, то есть
    размер шага между соседними вариантами. «% от лучшего» — к максимуму.
    """
    if not results:
        return "(нет вариантов)"

    tables = [_setup_fields(r) for r in results]
    keys = list(dict.fromkeys(k for t in tables for k in t))
    constant = [k for k in keys if len({t.get(k, "—") for t in tables}) == 1]
    varying = [k for k in keys if k not in constant]

    out: List[str] = []
    if title:
        out += [f"=== {title} ===", ""]

    # ---- что постоянно ----------------------------------------------------- #
    out.append("Постоянно:")
    for k in constant:
        if "\0" not in k:
            out.append(f"    {k:<22s} {tables[0][k]}")
    # персонажей собираем по одной строке, показывая только неизменные части
    for name in results[0].setup:
        parts = [tables[0][k].removeprefix("") for k in constant
                 if k.startswith(f"{name}\0") and not k.endswith("\0время")]
        if parts:
            out.append(f"    {name:<22s} {' · '.join(parts)}")
    out.append("")

    # ---- что меняется ------------------------------------------------------ #
    if not varying:
        out.append("Меняется: ничего — все варианты одинаковы.")
    else:
        owners = {k.split("\0")[0] for k in varying if "\0" in k}
        one_owner = len(owners) == 1 and all("\0" in k for k in varying)
        subject = (f"Меняется у «{owners.pop()}»:" if one_owner else "Меняется:")
        out.append(subject)

        def header(k: str) -> str:
            if "\0" not in k:
                return k
            owner, field = k.split("\0")
            return field if one_owner else f"{owner}: {field}"

        order = sorted(range(len(results)),
                       key=lambda i: getattr(results[i], key),
                       reverse=not ascending)
        best = max(getattr(r, key) for r in results)
        worst = min(getattr(r, key) for r in results)
        rows = []
        previous = None
        for rank, i in enumerate(order, start=1):
            r, t = results[i], tables[i]
            value = getattr(r, key)
            step = f"{value / previous * 100:.1f}%" if previous else "—"
            previous = value
            rows.append([str(rank)] + [t.get(k, "—") for k in varying]
                        + [fmt(r.dpr), fmt(r.dps),
                           f"{value / best * 100:.1f}%" if best else "—",
                           f"{value / worst * 100:.1f}%" if worst else "—",
                           step])
        headers = ["#"] + [header(k) for k in varying] + [
            "DPR", "DPS", "% от лучшего", "% от худшего", "% от предыдущего"]
        align = "r" + "l" * len(varying) + "rrrrr"
        out.append(table(rows, headers, align=align))

    return "\n".join(out)


def compare(results: Sequence[TeamResult], key: str = "dps",
            ascending: bool | None = None) -> str:
    """Сравнение нескольких отрядов/сборок.

    ascending=None — порядок как передали; True/False — отсортировать
    по возрастанию/убыванию `key`.
    """
    ordered = list(results)
    if ascending is not None:
        ordered.sort(key=lambda r: getattr(r, key), reverse=not ascending)

    values = [getattr(r, key) for r in ordered]
    best = max(values) if values else 0.0
    worst = min(values) if values else 0.0
    rows = []
    previous = None
    for r, value in zip(ordered, values):
        rows.append([r.team_name, fmt(r.dpr), fmt(r.dps),
                     f"{value / best * 100:.1f}%" if best else "—",
                     f"{value / worst * 100:.1f}%" if worst else "—",
                     f"{value / previous * 100:.1f}%" if previous else "—"])
        previous = value
    return table(rows, ["Вариант", "DPR", "DPS", "% от лучшего",
                        "% от худшего", "% от предыдущего"], align="lrrrrr")