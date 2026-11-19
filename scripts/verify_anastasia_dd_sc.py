#!/usr/bin/env python3
"""Проверка 30 сгенерированных отрядов «Анастасия (ДД) — SC».

    python -m scripts.verify_anastasia_dd_sc

Что проверяется:
  * все 30 модулей импортируются и считаются;
  * в каждом отряде ровно один ДД — Анастасия, и три заданных саппорта;
  * ни один состав не повторяет уже существующий отряд (сравнение по
    набору персонажей + основному ДД);
  * у саппортов не повторяются 4-шт. саппорт-сеты;
  * временные баффы саппортов (правило 10) попадают в теги комбо
    Анастасии ``dd_sc``.
"""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from gi_damage.data.characters.anastasia import ANASTASIA_COMBO_DICT
from gi_damage.teams._anastasia_dd_sc_factory import UNIQUE_SUPPORT_SETS
from scripts.generate_anastasia_dd_sc import TEAMS, existing_teams, slug


def _combo_tags() -> set[str]:
    tags: set[str] = set()
    char = ANASTASIA_COMBO_DICT["dd_sc"]
    sources = list(char.sources)
    for c in char.constellations.values():
        sources.extend(c.sources)
    for src in sources:
        for occ in src.occurrences:
            tags.update(occ.state)
    return tags


def _four_piece(build) -> set[str]:
    return {a.name for a in build.artifacts if a.pieces >= 4}


def main() -> int:
    generated = {slug(s) for s in TEAMS}
    existing = existing_teams(generated)
    existing_sets = {chars for _, chars in existing}
    combo_tags = _combo_tags()
    errors: list[str] = []
    rows: list[tuple[str, float]] = []

    for supports in TEAMS:
        folder = slug(supports)
        try:
            mod = importlib.import_module(f"gi_damage.teams.{folder}.builds")
            teams = mod.all_teams()
            if len(teams) != 1:
                errors.append(f"{folder}: all_teams() вернул {len(teams)} команд")
                continue
            team = next(iter(teams.values()))
            team.compute()
        except Exception as exc:
            errors.append(f"{folder}: {type(exc).__name__}: {exc}")
            continue

        names = [b.name for b in team.builds]
        expected = ["Анастасия", *supports]
        if names != expected:
            errors.append(f"{folder}: состав {names}, ожидался {expected}")
        if team.dd_name() != "Анастасия":
            errors.append(f"{folder}: ДД = {team.dd_name()!r}, ожидалась Анастасия")

        if frozenset(names) in existing_sets:
            errors.append(f"{folder}: такой набор персонажей уже есть в репозитории")

        support_builds = [b for b in team.builds if b.name != "Анастасия"]
        for b in support_builds:
            # Водянице разрешён 2+2 на HP, Мите — 2+2 на МС/Разочарование
            # как сет на урон с низким приоритетом. Остальные — 4-шт. набор.
            if b.name not in {"Водяница", "Митя"} and any(
                a.pieces != 4 for a in b.artifacts
            ):
                errors.append(
                    f"{folder}: {b.name} — не 4-шт. набор: "
                    f"{[a.name + ':' + str(a.pieces) for a in b.artifacts]}"
                )
        support_sets = [name for b in support_builds for name in _four_piece(b)]
        dup = {name for name in support_sets if name in UNIQUE_SUPPORT_SETS
               and support_sets.count(name) > 1}
        if dup:
            errors.append(f"{folder}: повторяются саппорт-сеты {sorted(dup)}")
        if "Сердце горна" not in support_sets:
            errors.append(f"{folder}: в отряде нет Сердца горна")
        for b in support_builds:
            if b.name == "Водяница" and any(a.pieces != 4 for a in b.artifacts):
                errors.append(f"{folder}: Водяница в 2+2, а должна быть в Миллелите")

        for b in support_builds:
            for _owner, buff in b.all_buffs():
                if not buff.temporary:
                    continue
                # Водяница в SC намеренно не даёт базовых баффов (п.8).
                if b.name == "Водяница" and "vodya_lead_elem" in buff.requires:
                    continue
                # У Изумрудной тени по одному окну на стихию; в крио-отряде
                # относится только vv_cryo, остальные варианты не должны
                # считаться «потерянным окном».
                vv_tags = {t for t in buff.requires if t.startswith("vv_")}
                if vv_tags and "vv_cryo" not in vv_tags:
                    continue
                missing = set(buff.requires) - combo_tags
                if missing:
                    errors.append(
                        f"{folder}: {b.name}, временный бафф {buff.stat!r} "
                        f"требует {sorted(missing)}, которых нет в dd_sc"
                    )

        rows.append((folder, team.compute().dps))

    print(f"Проверено отрядов: {len(rows)} / {len(TEAMS)}")
    for folder, dps in sorted(rows, key=lambda x: -x[1]):
        print(f"  {folder:<42} DPS {dps:>12,.0f}")
    if errors:
        print(f"\nОШИБОК: {len(errors)}")
        for e in errors:
            print(" -", e)
        return 1
    print("\nОшибок нет: составы новые, саппорт-сеты не повторяются, правило 10 выполняется.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
