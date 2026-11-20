#!/usr/bin/env python3
"""Проверка сгенерированных отрядов «Сандроне (ДД) — SC».

    python -m scripts.verify_sandrone_dd_sc

Проверяется:
  * все отряды импортируются и считаются;
  * основной ДД — Сандроне, в отряде три саппорта;
  * набор персонажей не повторяет существующие отряды;
  * Сердце горна обязательно, саппорт-сеты не повторяются;
  * Водяница не в 2+2;
  * правило 10: временные баффы саппортов попадают в теги комбо Сандроне.
"""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from gi_damage.teams._sandrone_dd_sc_factory import UNIQUE_SUPPORT_SETS
from scripts.generate_sandrone_dd_sc import TEAMS, existing_support_sets, slug


def _character_tags(build) -> set[str]:
    tags: set[str] = set()
    for src in build.all_sources():
        for occ in src.occurrences:
            tags.update(occ.state)
    return tags


def _four_piece(build) -> set[str]:
    return {a.name for a in build.artifacts if a.pieces >= 4}


def main() -> int:
    existing = existing_support_sets()
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
        expected = ["Сандроне", *supports]
        if names != expected:
            errors.append(f"{folder}: состав {names}, ожидался {expected}")
        if team.dd_name() != "Сандроне":
            errors.append(f"{folder}: ДД = {team.dd_name()!r}")

        support_set = frozenset(names[1:])
        if support_set in existing:
            errors.append(f"{folder}: такой набор саппортов уже есть в репозитории")

        support_builds = [b for b in team.builds if b.name != "Сандроне"]
        electro = [b for b in support_builds if b.name in {"Алеша", "Митя", "Даника"}]
        for b in support_builds:
            if b.name == "Даника" and len(electro) == 1 and b.weapon.name != "Двуручный меч фавония":
                errors.append(f"{folder}: Даника — единственный электро, но оружие {b.weapon.name}")
            if b.name == "Водяница" and b.weapon.name == "Ода водоворота":
                errors.append(f"{folder}: у Водяницы Ода водоворота, её убрали")
        support_sets = [name for b in support_builds for name in _four_piece(b)]
        dup = {name for name in support_sets if name in UNIQUE_SUPPORT_SETS
               and support_sets.count(name) > 1}
        if dup:
            errors.append(f"{folder}: повторяются саппорт-сеты {sorted(dup)}")
        if "Сердце горна" not in support_sets:
            errors.append(f"{folder}: в отряде нет Сердца горна")
        for b in support_builds:
            if b.name == "Водяница" and any(a.pieces != 4 for a in b.artifacts):
                errors.append(f"{folder}: Водяница в 2+2")

        dd_tags = _character_tags(team.build("Сандроне"))
        for b in support_builds:
            for _owner, buff in b.all_buffs():
                if not buff.temporary:
                    continue
                if b.name == "Водяница" and "vodya_lead_elem" in buff.requires:
                    continue
                vv_tags = {t for t in buff.requires if t.startswith("vv_")}
                if vv_tags and "vv_cryo" not in vv_tags:
                    continue
                missing = set(buff.requires) - dd_tags
                if missing:
                    errors.append(
                        f"{folder}: {b.name}, временный бафф {buff.stat!r} "
                        f"требует {sorted(missing)}, которых нет в комбо Сандроне"
                    )

        rows.append((folder, team.compute().dps))

    print(f"Проверено отрядов: {len(rows)} / {len(TEAMS)}")
    for folder, dps in sorted(rows, key=lambda x: -x[1]):
        print(f"  {folder:<48} DPS {dps:>12,.0f}")
    if errors:
        print(f"\nОШИБОК: {len(errors)}")
        for e in errors:
            print(" -", e)
        return 1
    print("\nОшибок нет: составы новые, сеты не повторяются, правило 10 выполняется.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
