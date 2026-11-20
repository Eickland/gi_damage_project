"""Фабрика отрядов «Сандроне — звёздный проводник».

Отряды Сандроне-ДД (SC):
  * основной ДД — Сандроне (``dd="Сандроне"``);
  * реакция — звёздный проводник;
  * в отряде есть второй крио персонаж;
  * в отряде есть электро персонаж;
  * Сердце горна обязательно, саппорт-сеты не повторяются;
  * Одетта может взять Звёздный сет, Митя — сет на урон,
    Водяница — Миллелит (2+2 — только крайний случай).

Комбо Сандроне:
  * без Сахарозы — ``sandrone_sc_combo``;
  * с Сахарозой — ``sandrone_sc_sucrose_combo``;
  * если в отряде есть Знать — берётся ``sandrone_sc_combo`` (в нём
    размечено окно ``NOBLE``), иначе окно Знати не с чем совместить.

Фабрика возвращает готовые атрибуты ``builds.py``; тонкие модули
создаёт ``scripts/generate_sandrone_dd_sc.py``.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from itertools import product
from typing import Callable, Dict, Iterable, Mapping, Sequence, Tuple

from ..core.buffs import TEAM, Buff
from ..core.engine import Config, Team
from ..core.entities import Build, Enemy
from ..core.sources import occ
from ..core.stats import S
from ..core.utilits import merge_dicts
from ..data.artifacts import (
    AUBADE,
    DISENCHANTMENT,
    GILDED,
    HEART_OF_FORGE,
    INSTRUCTOR,
    MILLELITH,
    NOBLESSE,
    STELLAR_SET,
    VIRIDESCENT,
    VOURUKASHA,
)
from ..data.artifacts_presets import (
    STANDART_SUBSTAT_FULL_ATK_PRESET,
    STANDART_SUBSTAT_PRESET,
)
from ..data.tags import NOBLE, OFF, SUCROSE_PASSIVE
from ..data.characters.alyosha import ALYOSHA_COMBO_DICT
from ..data.characters.anastasia import CROWN_HITS, anastasia_support
from ..data.characters.danika import (
    C2_ACTIVE_STACKS,
    C2_OTHER_STACKS,
    DANIKA_C2,
    DANIKA_COMBO_DICT,
    add_tags,
    tag_stellar_conduct_hits,
)
from ..data.characters.diona import DIONA_COMBO_DICT
from ..data.characters.mitya import MITYA_COMBO_DICT
from ..data.characters.odette import (
    ODETTE_BURST_SOURCES,
    ODETTE_BURST_TIME,
    ODETTE_COMBO_DICT,
    odette_burst_buffs,
)
from ..data.characters.qiqi import QIQI_COMBO_DICT
from ..data.characters.sandrone import SANDRONE_COMBO_DICT
from ..data.characters.sucrose import SUCROSE_COMBO_DICT
from ..data.characters.vodyanitsa import VODYA_COMBO_DICT
from ..data.weapons import (
    ATONEMENT,
    BREEZEBORNE_BOW,
    FAV_BOW,
    FAV_GREATSWORD,
    FAV_LANCE,
    FAV_SWORD,
    SACFRAG,
    SILVER_LIGHT,
    TTDS_FULL_CATALYSATOR,
    TTDS_HALF_CATALYSATOR,
    WANDERING_STAR,
)

# --------------------------------------------------------------------------- #
#  Общие статы и времена                                                       #
# --------------------------------------------------------------------------- #
MAIN_ATK = {S.ATK_PCT: 0.466 * 2, S.CRIT_VALUE: 0.622}
MAIN_EM = {S.BASE_EM: 187.0 * 2, S.CRIT_VALUE: 0.622}
FULL_ATK = {S.ATK_PCT: 0.466 * 3}
MAIN_HP = {S.HP_PCT: 0.466 * 3}

SUPPORT_TIME = {
    "Одетта": 2.4,
    "Ци Ци": 1.5,
    "Диона": 2.3,
    "Анастасия": 3.5,
    "Алеша": 1.9,
    "Митя": 1.5,
    "Даника": 3.25,
    "Водяница": 1.6,
    "Сахароза": 2.95,
}

SUPPORT_ACTION = {
    "Одетта": "Одетта EE",
    "Ци Ци": "Ци Ци E",
    "Диона": "Диона EQ",
    "Анастасия": "Анастасия EQ",
    "Алеша": "Алеша EQ",
    "Митя": "Митя E",
    "Даника": "Даника EQ",
    "Водяница": "Водяница E",
    "Сахароза": "Сахароза EQ",
}

SUPPORT_SLUG = {
    "Одетта": "odette",
    "Ци Ци": "qiqi",
    "Диона": "diona",
    "Анастасия": "anastasia",
    "Алеша": "alyosha",
    "Митя": "mitya",
    "Даника": "danika",
    "Водяница": "vodya",
    "Сахароза": "sucrose",
}

SUPPORT_ELEMENT = {
    "Одетта": "cryo",
    "Ци Ци": "cryo",
    "Диона": "cryo",
    "Анастасия": "cryo",
    "Алеша": "electro",
    "Митя": "electro",
    "Даника": "electro",
    "Водяница": "hydro",
    "Сахароза": "anemo",
}

SUPPORT_ORDER = (
    "Одетта", "Ци Ци", "Диона", "Анастасия", "Алеша", "Митя", "Даника",
    "Водяница", "Сахароза",
)

UNIQUE_SUPPORT_SETS = {
    HEART_OF_FORGE.name,
    INSTRUCTOR.name,
    MILLELITH.name,
    NOBLESSE.name,
    VIRIDESCENT.name,
}

SANDRONE_TIME = 14.0


# --------------------------------------------------------------------------- #
#  Сборки                                                                      #
# --------------------------------------------------------------------------- #
def _tag_c2(build: Build, hits: float) -> Build:
    return tag_stellar_conduct_hits(build, DANIKA_C2, hits)


def _sandrone_build(
    constellation: int = 0,
    weapon=ATONEMENT,
    artifacts: Sequence = (DISENCHANTMENT,),
    extra_buffs: Sequence[Buff] = (),
) -> Build:
    return Build(
        character=SANDRONE_COMBO_DICT["sandrone_sc_combo"],
        constellation=constellation,
        weapon=weapon,
        artifacts=tuple(artifacts),
        extra_stats=merge_dicts(MAIN_ATK, STANDART_SUBSTAT_PRESET),
        extra_buffs=tuple(extra_buffs),
        time=SANDRONE_TIME,
    )


def _odette_build(
    constellation: int = 0,
    weapon=SILVER_LIGHT,
    artifacts: Sequence = (STELLAR_SET,),
    extra_buffs: Sequence[Buff] = (),
) -> Build:
    use_burst = constellation >= 4
    return Build(
        character=ODETTE_COMBO_DICT["odette_ssc_combo"],
        constellation=constellation,
        weapon=weapon,
        artifacts=tuple(artifacts),
        extra_stats=merge_dicts(MAIN_ATK, STANDART_SUBSTAT_PRESET),
        extra_sources=ODETTE_BURST_SOURCES if use_burst else (),
        extra_buffs=tuple(extra_buffs)
        + (odette_burst_buffs(constellation) if use_burst else ()),
        time=SUPPORT_TIME["Одетта"] + (ODETTE_BURST_TIME if use_burst else 0.0),
    )


def _qiqi_build(
    constellation: int = 0,
    weapon=FAV_SWORD,
    artifacts: Sequence = (MILLELITH,),
    extra_buffs: Sequence[Buff] = (),
) -> Build:
    return Build(
        character=QIQI_COMBO_DICT["off_field"],
        constellation=constellation,
        weapon=weapon,
        artifacts=tuple(artifacts),
        extra_stats=merge_dicts(
            {S.ATK_PCT: 0.466 * 1, S.CRIT_VALUE: 0.622},
            STANDART_SUBSTAT_PRESET,
        ),
        extra_buffs=tuple(extra_buffs),
        time=SUPPORT_TIME["Ци Ци"],
    )


def _diona_build(
    constellation: int = 6,
    weapon=FAV_BOW.at(5),
    artifacts: Sequence = (MILLELITH,),
    extra_buffs: Sequence[Buff] = (),
) -> Build:
    return Build(
        character=DIONA_COMBO_DICT["off_field"],
        constellation=constellation,
        weapon=weapon,
        artifacts=tuple(artifacts),
        extra_stats=merge_dicts(
            {S.ATK_PCT: 0.466 * 1, S.CRIT_VALUE: 0.622},
            STANDART_SUBSTAT_PRESET,
        ),
        extra_buffs=tuple(extra_buffs),
        time=SUPPORT_TIME["Диона"],
    )


def _anastasia_build(
    constellation: int = 0,
    weapon=BREEZEBORNE_BOW.at(1),
    artifacts: Sequence = (MILLELITH,),
    extra_buffs: Sequence[Buff] = (),
) -> Build:
    return Build(
        character=anastasia_support("sc", [occ(CROWN_HITS, OFF)]),
        constellation=constellation,
        weapon=weapon,
        artifacts=tuple(artifacts),
        extra_stats=merge_dicts(MAIN_ATK, STANDART_SUBSTAT_PRESET),
        extra_buffs=tuple(extra_buffs),
        time=SUPPORT_TIME["Анастасия"],
    )


def _alyosha_build(
    constellation: int = 6,
    weapon=FAV_LANCE,
    artifacts: Sequence = (HEART_OF_FORGE,),
    extra_buffs: Sequence[Buff] = (),
) -> Build:
    return Build(
        character=ALYOSHA_COMBO_DICT["sc_combo"],
        constellation=constellation,
        weapon=weapon,
        artifacts=tuple(artifacts),
        extra_stats=merge_dicts(
            {S.ATK_PCT: 0.466 * 1, S.CRIT_VALUE: 0.622},
            STANDART_SUBSTAT_PRESET,
        ),
        extra_buffs=tuple(extra_buffs),
        time=SUPPORT_TIME["Алеша"],
    )


def _mitya_build(
    constellation: int = 0,
    weapon=TTDS_HALF_CATALYSATOR,
    artifacts: Sequence = (MILLELITH,),
    extra_buffs: Sequence[Buff] = (),
) -> Build:
    return Build(
        character=MITYA_COMBO_DICT["support_steady"],
        constellation=constellation,
        weapon=weapon,
        artifacts=tuple(artifacts),
        extra_stats=merge_dicts(MAIN_EM, STANDART_SUBSTAT_PRESET),
        extra_buffs=tuple(extra_buffs),
        time=SUPPORT_TIME["Митя"],
    )


def _danika_build(
    constellation: int = 0,
    weapon=ATONEMENT,
    artifacts: Sequence = (HEART_OF_FORGE,),
    extra_buffs: Sequence[Buff] = (),
) -> Build:
    return Build(
        character=DANIKA_COMBO_DICT["support_eq"],
        constellation=constellation,
        weapon=weapon,
        artifacts=tuple(artifacts),
        extra_stats=merge_dicts(FULL_ATK, STANDART_SUBSTAT_FULL_ATK_PRESET),
        extra_buffs=tuple(extra_buffs),
        time=SUPPORT_TIME["Даника"],
    )


def _vodya_build(
    constellation: int = 0,
    weapon=TTDS_HALF_CATALYSATOR,
    artifacts: Sequence = (MILLELITH,),
    extra_buffs: Sequence[Buff] = (),
) -> Build:
    return Build(
        character=VODYA_COMBO_DICT["sc_off_field"],
        constellation=constellation,
        weapon=weapon,
        artifacts=tuple(artifacts),
        extra_stats=merge_dicts(MAIN_HP, STANDART_SUBSTAT_PRESET),
        extra_buffs=tuple(extra_buffs),
        time=SUPPORT_TIME["Водяница"],
    )


def _sucrose_build(
    constellation: int = 6,
    weapon=TTDS_FULL_CATALYSATOR,
    artifacts: Sequence = (VIRIDESCENT,),
    extra_buffs: Sequence[Buff] = (),
) -> Build:
    return Build(
        character=SUCROSE_COMBO_DICT["cryo_burst_combo"],
        constellation=constellation,
        weapon=weapon,
        artifacts=tuple(artifacts),
        extra_stats=merge_dicts({S.BASE_EM: 187.0 * 3}, STANDART_SUBSTAT_PRESET),
        extra_buffs=tuple(extra_buffs),
        time=SUPPORT_TIME["Сахароза"],
    )


# --------------------------------------------------------------------------- #
#  Спецификации саппортов                                                      #
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class SupportSpec:
    name: str
    key: str
    default_constellation: int
    default_weapon: object
    artifact_options: Tuple[Tuple, ...]
    builder: Callable[..., Build]


def _art(*sets) -> Tuple:
    return tuple(sets)


SUPPORT_SPECS: Dict[str, SupportSpec] = {
    "Одетта": SupportSpec(
        "Одетта", "odette", 0, SILVER_LIGHT,
        (_art(HEART_OF_FORGE), _art(MILLELITH), _art(STELLAR_SET)),
        _odette_build,
    ),
    "Ци Ци": SupportSpec(
        "Ци Ци", "qiqi", 0, FAV_SWORD,
        (_art(HEART_OF_FORGE), _art(MILLELITH)),
        _qiqi_build,
    ),
    "Диона": SupportSpec(
        "Диона", "diona", 6, FAV_BOW.at(5),
        (_art(HEART_OF_FORGE), _art(MILLELITH), _art(NOBLESSE)),
        _diona_build,
    ),
    "Анастасия": SupportSpec(
        "Анастасия", "anastasia", 0, BREEZEBORNE_BOW.at(1),
        (_art(HEART_OF_FORGE), _art(MILLELITH)),
        _anastasia_build,
    ),
    "Алеша": SupportSpec(
        "Алеша", "alyosha", 6, FAV_LANCE,
        (_art(HEART_OF_FORGE), _art(NOBLESSE)),
        _alyosha_build,
    ),
    "Митя": SupportSpec(
        "Митя", "mitya", 0, TTDS_HALF_CATALYSATOR,
        (
            _art(HEART_OF_FORGE),
            _art(MILLELITH),
            _art(AUBADE.at(2), GILDED.at(2)),   # сет на урон, низкий приоритет
            _art(DISENCHANTMENT),               # сет на урон, низкий приоритет
        ),
        _mitya_build,
    ),
    "Даника": SupportSpec(
        "Даника", "danika", 0, ATONEMENT,
        (_art(HEART_OF_FORGE), _art(MILLELITH), _art(NOBLESSE)),
        _danika_build,
    ),
    "Водяница": SupportSpec(
        "Водяница", "vodya", 0, TTDS_HALF_CATALYSATOR,
        (
            _art(MILLELITH),
            _art(MILLELITH.at(2), VOURUKASHA.at(2)),
        ),
        _vodya_build,
    ),
    "Сахароза": SupportSpec(
        "Сахароза", "sucrose", 6, TTDS_FULL_CATALYSATOR,
        (_art(VIRIDESCENT), _art(INSTRUCTOR)),
        _sucrose_build,
    ),
}


# --------------------------------------------------------------------------- #
#  Подбор саппорт-сетов                                                        #
# --------------------------------------------------------------------------- #
def _four_piece_names(arts: Iterable) -> Tuple[str, ...]:
    return tuple(a.name for a in arts if a.pieces >= 4)


def _assign_artifacts(supports: Sequence[str]) -> Dict[str, Tuple]:
    """Раздать саппортам наборы по приоритетам (как у Анастасии).

    Жёсткие условия:
      * Сердце горна в отряде обязательно;
      * 4-шт. саппорт-сеты не повторяются.

    Приоритеты:
      1. Одетта — Звёздный сет;
      2. Водяница — не 2+2, а Миллелит;
      3. больше разных саппорт-сетов;
      4. Сердце горна: Даника, Митя, Одетта, затем остальные;
      5. Митя — саппорт-сет, но сет на урон допустим;
      6. Даника — Сердце горна, если это не мешает собрать Знать.
    """
    specs = [SUPPORT_SPECS[s] for s in supports]
    index = {s.name: i for i, s in enumerate(specs)}
    best: tuple | None = None
    for combo in product(*(s.artifact_options for s in specs)):
        names = [name for arts in combo for name in _four_piece_names(arts)]
        if len(names) != len(set(names)):
            continue
        if HEART_OF_FORGE.name not in names:
            continue

        support_count = sum(1 for name in names if name in UNIQUE_SUPPORT_SETS)

        heart_idx = next(
            i for i, arts in enumerate(combo)
            if HEART_OF_FORGE.name in _four_piece_names(arts)
        )
        heart_holder = specs[heart_idx].name
        heart_priority = {"Даника": 4, "Митя": 3, "Одетта": 2}.get(heart_holder, 1)

        odette_idx = index.get("Одетта")
        odette_stellar = (
            1 if odette_idx is None
            else int(STELLAR_SET.name in _four_piece_names(combo[odette_idx]))
        )

        vodya_idx = index.get("Водяница")
        vodya_ok = (
            1 if vodya_idx is None
            else int(bool(_four_piece_names(combo[vodya_idx])))
        )

        mitya_idx = index.get("Митя")
        mitya_support = (
            1 if mitya_idx is None
            else int(any(name in UNIQUE_SUPPORT_SETS
                         for name in _four_piece_names(combo[mitya_idx])))
        )

        danika_idx = index.get("Даника")
        danika_heart = (
            1 if danika_idx is None
            else int(HEART_OF_FORGE.name in _four_piece_names(combo[danika_idx]))
        )

        score = (
            odette_stellar,
            vodya_ok,
            support_count,
            heart_priority,
            mitya_support,
            danika_heart,
        )
        if best is None or score > best[0]:
            best = (score, combo)
    if best is None:
        raise ValueError(f"Не удалось раздать сеты саппортам: {supports}")
    return {spec.name: arts for spec, arts in zip(specs, best[1])}


# --------------------------------------------------------------------------- #
#  Модуль отряда                                                               #
# --------------------------------------------------------------------------- #
def rotation_for(supports: Sequence[str]) -> str:
    return " / ".join(
        [SUPPORT_ACTION[s] for s in supports]
        + ["Сандроне E CA EQ CA E CA E"]
    )


def enemy() -> Enemy:
    return Enemy(
        res={"anemo": 0.10, "cryo": 0.10, "electro": 0.10},
        def_mult=0.4875,
        elevation=0.0,
    )


def module_for(supports: Sequence[str]) -> dict:
    """Сгенерировать атрибуты ``builds.py`` для тройки саппортов."""
    supports = tuple(supports)
    if len(supports) != 3 or len(set(supports)) != 3:
        raise ValueError(f"Нужны три разных саппорта, а не {supports!r}")
    unknown = [s for s in supports if s not in SUPPORT_SPECS]
    if unknown:
        raise ValueError(f"Неизвестные саппорты: {unknown!r}")
    if "Сандроне" in supports:
        raise ValueError("Сандроне — ДД, а не саппорт")

    specs = [SUPPORT_SPECS[s] for s in supports]
    artifacts = _assign_artifacts(supports)
    has_noble = any(
        NOBLESSE.name in _four_piece_names(arts) for arts in artifacts.values()
    )
    has_sucrose = "Сахароза" in supports

    sandrone_combo = (
        "sandrone_sc_sucrose_combo"
        if has_sucrose and not has_noble
        else "sandrone_sc_combo"
    )
    odette_combo = (
        "odette_ssc_combo_sucrose_sandrone"
        if has_sucrose and not has_noble
        else "odette_ssc_combo"
    )

    weapons = {s.name: s.default_weapon for s in specs}
    if "Митя" in supports:
        # Как в фабрике Анастасии: второй катализатор в отряде не должен
        # дублировать Эпос.
        weapons["Митя"] = (
            WANDERING_STAR.at(1) if "Водяница" in supports
            else TTDS_HALF_CATALYSATOR
        )
    if "Сахароза" in supports:
        weapons["Сахароза"] = (
            SACFRAG.at(5) if "Митя" in supports
            else TTDS_FULL_CATALYSATOR
        )

    electro_count = sum(1 for s in specs if SUPPORT_ELEMENT[s.name] == "electro")
    if "Даника" in supports and electro_count == 1:
        # Единственный электро — Даника играет от энергии:
        # базово двуручный меч фавония.
        weapons["Даника"] = FAV_GREATSWORD
    resonance = 0.15 if electro_count >= 2 else 0.30
    resonance_note = (
        " (ослаблен ×0.5: 2+ электро в отряде)" if electro_count >= 2 else ""
    )
    team_buffs = (
        Buff(
            S.CRIT_VALUE, resonance, target=TEAM,
            source=f"Крио резонанс{resonance_note}: +{resonance * 50:.1f}% крит. шанса "
                   f"({resonance:.2f} крит-вэлью)",
        ),
    )

    def _post(build: Build, *, noble: bool, sucrose: bool) -> Build:
        if noble:
            build = add_tags(build, NOBLE)
        if sucrose:
            build = add_tags(build, SUCROSE_PASSIVE)
        return build

    def sandrone_build(
        constellation: int = 0,
        weapon=ATONEMENT,
        artifacts: Sequence = (DISENCHANTMENT,),
        extra_buffs: Sequence[Buff] = (),
    ) -> Build:
        build = _sandrone_build(constellation, weapon, artifacts, extra_buffs)
        build = replace(build, character=SANDRONE_COMBO_DICT[sandrone_combo])
        # В combo уже размечено окно NOBLE; добавляем только пассивку Сахарозы.
        if has_sucrose:
            build = add_tags(build, SUCROSE_PASSIVE)
        return _tag_c2(build, C2_ACTIVE_STACKS)

    def make_support_build(spec: SupportSpec):
        def build(
            constellation: int = spec.default_constellation,
            weapon=weapons[spec.name],
            artifacts: Sequence = artifacts[spec.name],
            extra_buffs: Sequence[Buff] = (),
            _spec=spec,
        ) -> Build:
            out = _spec.builder(constellation, weapon, artifacts, extra_buffs)
            if spec.name == "Одетта":
                out = replace(out, character=ODETTE_COMBO_DICT[odette_combo])
            elif spec.name == "Даника" and has_noble:
                out = replace(out, character=DANIKA_COMBO_DICT["support_eq_noble"])
            out = _post(out, noble=has_noble, sucrose=has_sucrose)
            return _tag_c2(out, C2_OTHER_STACKS)

        build.__name__ = f"{spec.key}_build"
        build.__qualname__ = build.__name__
        return build

    def team_name() -> str:
        parts = ["C0R1 Сандроне"]
        for spec in specs:
            w = weapons[spec.name]
            parts.append(f"C{spec.default_constellation}R{w.refinement} {spec.name}")
        return ", ".join(parts)

    base_name = team_name()
    rotation_text = rotation_for(supports)

    def make_team(name: str = "") -> Team:
        team_label = name or base_name
        builds = [sandrone_build()]
        for spec in specs:
            builds.append(make_support_build(spec)())
        return Team(
            name=team_label,
            builds=builds,
            enemy=enemy(),
            buffs=team_buffs,
            rotation=rotation_text,
            config=Config(),
            dd="Сандроне",
        )

    def all_teams() -> Dict[str, Team]:
        return {base_name: make_team(base_name)}

    generated = {
        "SUPPORTS": supports,
        "SLUG": "_".join(SUPPORT_SLUG[s] for s in supports),
        "TIMES": {"Сандроне": SANDRONE_TIME,
                  **{s: SUPPORT_TIME[s] for s in supports}},
        "ROTATION": rotation_text,
        "TEAM_BUFFS": team_buffs,
        "VARIANTS": ({},),
        "BASE_NAME": base_name,
        "team_name": team_name,
        "make_team": make_team,
        "all_teams": all_teams,
        "enemy": enemy,
        "sandrone_build": sandrone_build,
    }
    for spec in specs:
        generated[f"{spec.key}_build"] = make_support_build(spec)
    return generated


def make_module(supports: Sequence[str]) -> dict:
    return module_for(supports)
