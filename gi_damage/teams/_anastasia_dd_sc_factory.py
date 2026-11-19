"""Фабрика отрядов «Анастасия (ДД) — звёздный проводник».

Отряды Анастасии-ДД, у которых:
  * основной ДД — Анастасия (``dd="Анастасия"``);
  * реакция — звёздный проводник (SC);
  * в отряде есть второй крио персонаж;
  * в отряде есть электро персонаж;
  * Сердце горна обязательно, саппорт-сеты не повторяются; Одетта может
    взять Звёздный сет, Митя — сет на урон, Водяница — Миллелит.

Фабрика принимает тройку саппортов и возвращает готовый набор атрибутов
модуля ``builds.py``: ``make_team``, ``all_teams``, ``team_name``,
``anastasia_build``, ``<support>_build``, ``VARIANTS`` и т. п. Тонкие
модули в ``gi_damage/teams/<slug>/builds.py`` создаются генератором
``scripts/generate_anastasia_dd_sc.py``.

Почему фабрика, а не 30 копий: у всех отрядов одна и та же ротация
Анастасии и одни и те же правила для саппортов. Отличаются только состав,
сеты и оружие саппортов. Комбо Анастасии — ``dd_sc``: в нём есть все окна
саппортов, которые используются в этих отрядах (``seven_sacred``,
``cats_tail``, ``noble``, ``ttds_*``, ``instructor`` + ``sucrose_passive``),
поэтому правило 10 выполняется для любого из 30 составов.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import Callable, Dict, Iterable, Mapping, Sequence, Tuple

from ..core.buffs import TEAM, Buff
from ..core.engine import Config, Team
from ..core.entities import Build, Enemy
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
from ..data.characters.alyosha import ALYOSHA_COMBO_DICT
from ..data.characters.anastasia import ANASTASIA_COMBO_DICT, DD_TIME
from ..data.characters.danika import (
    C2_ACTIVE_STACKS,
    C2_OTHER_STACKS,
    DANIKA_C2,
    DANIKA_COMBO_DICT,
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
from ..data.characters.sucrose import SUCROSE_COMBO_DICT
from ..data.characters.vodyanitsa import VODYA_COMBO_DICT
from ..data.weapons import (
    ARTEMISIA,
    ATONEMENT,
    FAV_BOW,
    FAV_LANCE,
    FAV_SWORD,
    MAELSTROM,
    SACFRAG,
    SILVER_LIGHT,
    TTDS_FULL_CATALYSATOR,
    TTDS_HALF_CATALYSATOR,
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
    "Алеша": 1.9,
    "Митя": 1.5,
    "Даника": 3.25,
    "Водяница": 1.6,
    "Сахароза": 1.6,
}

SUPPORT_ACTION = {
    "Одетта": "Одетта EE",
    "Ци Ци": "Ци Ци E",
    "Диона": "Диона EQ",
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
    "Алеша": "electro",
    "Митя": "electro",
    "Даника": "electro",
    "Водяница": "hydro",
    "Сахароза": "anemo",
}

#: 4-шт. наборы с баффом отряду — в одном отряде не повторяются.
UNIQUE_SUPPORT_SETS = {
    HEART_OF_FORGE.name,
    INSTRUCTOR.name,
    MILLELITH.name,
    NOBLESSE.name,
    VIRIDESCENT.name,
}


# --------------------------------------------------------------------------- #
#  Сборки саппортов                                                            #
# --------------------------------------------------------------------------- #
def _tag_c2(build: Build, hits: float) -> Build:
    """Пометить SC-удары для C2 Даники.

    Тег ставится всегда, даже если Даника C0: при C0 баффа C2 просто нет,
    а при подъёме созвездия в ростере тег уже на месте — пересобирать
    отряд под C2 не нужно.
    """
    return tag_stellar_conduct_hits(build, DANIKA_C2, hits)


def _anastasia_build(
    constellation: int = 0,
    weapon=ARTEMISIA.at(1),
    artifacts: Sequence = (DISENCHANTMENT,),
    main_stats: Mapping[str, float] = MAIN_ATK,
    extra_buffs: Sequence[Buff] = (),
) -> Build:
    return _tag_c2(
        Build(
            character=ANASTASIA_COMBO_DICT["dd_sc"],
            constellation=constellation,
            weapon=weapon,
            artifacts=tuple(artifacts),
            extra_stats=merge_dicts(main_stats, STANDART_SUBSTAT_PRESET),
            extra_buffs=tuple(extra_buffs),
            time=DD_TIME,
        ),
        C2_ACTIVE_STACKS,
    )


def _odette_build(
    constellation: int = 0,
    weapon=SILVER_LIGHT,
    artifacts: Sequence = (DISENCHANTMENT,),
    extra_buffs: Sequence[Buff] = (),
) -> Build:
    use_burst = constellation >= 4
    return _tag_c2(
        Build(
            character=ODETTE_COMBO_DICT["odette_ssc_combo"],
            constellation=constellation,
            weapon=weapon,
            artifacts=tuple(artifacts),
            extra_stats=merge_dicts(MAIN_ATK, STANDART_SUBSTAT_PRESET),
            extra_sources=ODETTE_BURST_SOURCES if use_burst else (),
            extra_buffs=tuple(extra_buffs)
            + (odette_burst_buffs(constellation) if use_burst else ()),
            time=SUPPORT_TIME["Одетта"] + (ODETTE_BURST_TIME if use_burst else 0.0),
        ),
        C2_OTHER_STACKS,
    )


def _qiqi_build(
    constellation: int = 0,
    weapon=FAV_SWORD,
    artifacts: Sequence = (MILLELITH,),
    extra_buffs: Sequence[Buff] = (),
) -> Build:
    return _tag_c2(
        Build(
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
        ),
        C2_OTHER_STACKS,
    )


def _diona_build(
    constellation: int = 6,
    weapon=FAV_BOW.at(5),
    artifacts: Sequence = (MILLELITH,),
    extra_buffs: Sequence[Buff] = (),
) -> Build:
    return _tag_c2(
        Build(
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
        ),
        C2_OTHER_STACKS,
    )


def _sucrose_build(
    constellation: int = 6,
    weapon=TTDS_FULL_CATALYSATOR,
    artifacts: Sequence = (VIRIDESCENT,),
    extra_buffs: Sequence[Buff] = (),
) -> Build:
    return _tag_c2(
        Build(
            character=SUCROSE_COMBO_DICT["cryo_burst_combo"],
            constellation=constellation,
            weapon=weapon,
            artifacts=tuple(artifacts),
            extra_stats=merge_dicts({S.BASE_EM: 187.0 * 3}, STANDART_SUBSTAT_PRESET),
            extra_buffs=tuple(extra_buffs),
            time=SUPPORT_TIME["Сахароза"],
        ),
        C2_OTHER_STACKS,
    )


def _alyosha_build(
    constellation: int = 6,
    weapon=FAV_LANCE,
    artifacts: Sequence = (HEART_OF_FORGE,),
    extra_buffs: Sequence[Buff] = (),
) -> Build:
    return _tag_c2(
        Build(
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
        ),
        C2_OTHER_STACKS,
    )


def _mitya_build(
    constellation: int = 0,
    weapon=TTDS_FULL_CATALYSATOR,
    artifacts: Sequence = (MILLELITH,),
    extra_buffs: Sequence[Buff] = (),
) -> Build:
    return _tag_c2(
        Build(
            character=MITYA_COMBO_DICT["support_steady"],
            constellation=constellation,
            weapon=weapon,
            artifacts=tuple(artifacts),
            extra_stats=merge_dicts(MAIN_EM, STANDART_SUBSTAT_PRESET),
            extra_buffs=tuple(extra_buffs),
            time=SUPPORT_TIME["Митя"],
        ),
        C2_OTHER_STACKS,
    )


def _danika_build(
    constellation: int = 0,
    weapon=ATONEMENT,
    artifacts: Sequence = (HEART_OF_FORGE,),
    extra_buffs: Sequence[Buff] = (),
) -> Build:
    return _tag_c2(
        Build(
            character=DANIKA_COMBO_DICT["support_eq"],
            constellation=constellation,
            weapon=weapon,
            artifacts=tuple(artifacts),
            extra_stats=merge_dicts(FULL_ATK, STANDART_SUBSTAT_FULL_ATK_PRESET),
            extra_buffs=tuple(extra_buffs),
            time=SUPPORT_TIME["Даника"],
        ),
        C2_OTHER_STACKS,
    )


def _vodya_build(
    constellation: int = 0,
    weapon=TTDS_HALF_CATALYSATOR,
    artifacts: Sequence = (MILLELITH,),
    extra_buffs: Sequence[Buff] = (),
) -> Build:
    return _tag_c2(
        Build(
            character=VODYA_COMBO_DICT["sc_off_field"],
            constellation=constellation,
            weapon=weapon,
            artifacts=tuple(artifacts),
            extra_stats=merge_dicts(MAIN_HP, STANDART_SUBSTAT_PRESET),
            extra_buffs=tuple(extra_buffs),
            time=SUPPORT_TIME["Водяница"],
        ),
        C2_OTHER_STACKS,
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
    """Кортеж наборов; ``MILLELITH.at(2)`` и т.п. уже готовые ArtifactSet."""
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
    "Сахароза": SupportSpec(
        "Сахароза", "sucrose", 6, TTDS_FULL_CATALYSATOR,
        (_art(VIRIDESCENT), _art(INSTRUCTOR)),
        _sucrose_build,
    ),
    "Алеша": SupportSpec(
        "Алеша", "alyosha", 6, FAV_LANCE,
        (_art(HEART_OF_FORGE), _art(NOBLESSE)),
        _alyosha_build,
    ),
    "Митя": SupportSpec(
        "Митя", "mitya", 0, TTDS_FULL_CATALYSATOR,
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
}

SUPPORT_ORDER = (
    "Одетта", "Ци Ци", "Диона", "Алеша", "Митя", "Даника", "Водяница", "Сахароза",
)


# --------------------------------------------------------------------------- #
#  Подбор саппорт-сетов                                                        #
# --------------------------------------------------------------------------- #
def _four_piece_names(arts: Iterable) -> Tuple[str, ...]:
    return tuple(a.name for a in arts if a.pieces >= 4)


def _assign_artifacts(supports: Sequence[str]) -> Dict[str, Tuple]:
    """Раздать саппортам наборы по приоритетам.

    Жёсткие условия:
      * Сердце горна в отряде обязательно;
      * 4-шт. саппорт-сеты не повторяются.

    Приоритеты (по убыванию важности):
      1. Одетта — Звёздный сет: она наносит много урона; ради этого можно
         остаться с двумя саппорт-сетами вместо трёх.
      2. Водяница в SC не должна носить 2+2 — только Миллелит.
      3. Больше разных саппорт-сетов (Сердце горна, Миллелит, Знать,
         Изумрудная тень, Инструктор).
      4. Сердце горна — носители по приоритету: Даника, Митя, Одетта,
         затем остальные.
      5. Митя-саппорт — саппорт-сет, а не сет на урон (2+2 МС/Разочарование),
         но сет на урон допустим как низкий приоритет.
      6. Даника — Сердце горна, если это не мешает собрать нужный
         саппорт-сет (Знать она носит, только если Знать больше некому).
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
def module_for(supports: Sequence[str]) -> dict:
    """Сгенерировать атрибуты ``builds.py`` для тройки саппортов."""
    supports = tuple(supports)
    if len(supports) != 3 or len(set(supports)) != 3:
        raise ValueError(f"Нужны три разных саппорта, а не {supports!r}")
    unknown = [s for s in supports if s not in SUPPORT_SPECS]
    if unknown:
        raise ValueError(f"Неизвестные саппорты: {unknown!r}")
    if "Анастасия" in supports:
        raise ValueError("Анастасия — ДД, а не саппорт")

    specs = [SUPPORT_SPECS[s] for s in supports]
    artifacts = _assign_artifacts(supports)

    weapons = {s.name: s.default_weapon for s in specs}
    if "Водяница" in supports:
        # Два Эпоса в одном отряде не нужны: если Митя уже с Эпосом,
        # Водяница берёт сигну/саппорт-оружие без второго окна Эпоса.
        weapons["Водяница"] = (
            MAELSTROM.at(1) if "Митя" in supports else TTDS_HALF_CATALYSATOR
        )
    if "Сахароза" in supports:
        # Как и с Водяницей: второй Эпос в отряде не нужен.
        weapons["Сахароза"] = (
            SACFRAG.at(5) if "Митя" in supports else TTDS_FULL_CATALYSATOR
        )

    electro_count = sum(1 for s in specs if SUPPORT_ELEMENT[s.name] == "electro")
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

    def team_name() -> str:
        parts = ["C0R1 Анастасия (ДД, полное)"]
        for spec in specs:
            w = weapons[spec.name]
            parts.append(f"C{spec.default_constellation}R{w.refinement} {spec.name}")
        return ", ".join(parts)

    base_name = team_name()
    rotation_text = rotation_for(supports)

    def make_team(name: str = "") -> Team:
        team_label = name or base_name
        builds = [
            _anastasia_build(),
            *(
                SUPPORT_SPECS[spec.name].builder(
                    SUPPORT_SPECS[spec.name].default_constellation,
                    weapons[spec.name],
                    artifacts[spec.name],
                )
                for spec in specs
            ),
        ]
        return Team(
            name=team_label,
            builds=builds,
            enemy=enemy(),
            buffs=team_buffs,
            rotation=rotation_text,
            config=Config(),
            dd="Анастасия",
        )

    def all_teams() -> Dict[str, Team]:
        return {base_name: make_team(base_name)}

    # Явные build-функции с именами <key>_build — их ищет standard_rosters.
    generated = {
        "SUPPORTS": supports,
        "SLUG": "_".join(SUPPORT_SLUG[s] for s in supports),
        "TIMES": {"Анастасия": DD_TIME, **{s: SUPPORT_TIME[s] for s in supports}},
        "ROTATION": rotation_text,
        "TEAM_BUFFS": team_buffs,
        "VARIANTS": ({},),
        "BASE_NAME": base_name,
        "team_name": team_name,
        "make_team": make_team,
        "all_teams": all_teams,
        "enemy": enemy,
        "anastasia_build": _anastasia_build,
    }
    for spec in specs:
        def _build(
            constellation: int = spec.default_constellation,
            weapon=weapons[spec.name],
            artifacts=artifacts[spec.name],
            extra_buffs: Sequence[Buff] = (),
            _spec=spec,
        ) -> Build:
            return _spec.builder(constellation, weapon, artifacts, extra_buffs)

        _build.__name__ = f"{spec.key}_build"
        _build.__qualname__ = _build.__name__
        generated[_build.__name__] = _build

    return generated


def rotation_for(supports: Sequence[str]) -> str:
    return " / ".join(
        [SUPPORT_ACTION[s] for s in supports] + ["Анастасия hEQ (N5 sE)×3"]
    )


def enemy() -> Enemy:
    return Enemy(
        res={"anemo": 0.10, "cryo": 0.10, "electro": 0.10},
        def_mult=0.4875,
        elevation=0.0,
    )


def make_module(supports: Sequence[str]) -> dict:
    """Публичное имя фабрики (используется сгенерированными модулями)."""
    return module_for(supports)
