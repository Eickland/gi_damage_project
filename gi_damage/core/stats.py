"""
Контейнер статов и производные значения.

Идея: все статы хранятся в плоском словаре со строковыми ключами.
Ключи можно делать «точечными» (dotted), чтобы задавать бонусы
для конкретной стихии или типа атаки:

    "dmg_bonus"            — общий бонус урона (ко всему)
    "dmg_bonus.anemo"      — бонус анемо урона
    "dmg_bonus.skill"      — бонус урона от элементального навыка
    "dmg_bonus.anemo.skill" — комбинация (стихия + тип)

Собираются они аддитивно: bonus(kind, element) = сумма всех подходящих ключей.

Такой подход позволяет добавлять новые категории (например "dmg_bonus.stellar_swirl")
не меняя движок.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, Mapping


# --------------------------------------------------------------------------- #
#  Имена статов                                                                #
# --------------------------------------------------------------------------- #
class S:
    """Канонические имена статов (чтобы не опечатываться в строках)."""

    # Атака
    BASE_ATK = "base_atk"      # база персонажа + база оружия
    ATK_PCT = "atk_pct"        # прибавка в долях (0.466 = 46.6%)
    FLAT_ATK = "flat_atk"      # плоская атака (после умножения на %)

    # Здоровье
    BASE_HP = "base_hp"
    HP_PCT = "hp_pct"
    FLAT_HP = "flat_hp"

    # Защита
    BASE_DEF = "base_def"
    DEF_PCT = "def_pct"
    FLAT_DEF = "flat_def"

    # Мастерство стихий
    BASE_EM = "base_em"        # МС, к которому применяется em_pct
    EM_PCT = "em_pct"          # процентная прибавка МС (0.1 = +10%)
    FLAT_EM = "flat_em"        # плоский МС ПОСЛЕ применения em_pct
                               # (например A4 Сахарозы: +20% от её МС)

    # Крит
    CRIT_RATE = "crit_rate"
    CRIT_DMG = "crit_dmg"
    CRIT_VALUE = "crit_value"  # «крит-вэлью» = шанс*2 + урон (как в таблице)

    # Бонусы урона (можно с точечными суффиксами)
    DMG_BONUS = "dmg_bonus"

    # Звёздное рассеивание (Stellar Swirl)
    SSW_BONUS = "ssw_bonus"        # «Stellar Swirl DMG Bonus%» — внутрь скобки с МС
    SSW_BASE_INC = "ssw_base_inc"  # «Base DMG Increase%» — множитель (1 + x)

    # Прочее
    ELEVATION = "elevation"    # «Возвышение», итоговый множитель = 1 + elevation
    FLAT_BASE_DMG = "flat_base_dmg"  # «Дополнительный базовый урон»

    # Пробитие/снижение сопротивления цели (учитывается в Enemy)
    RES_REDUCTION = "res_reduction"  # можно "res_reduction.cryo"


# Ключи, которые складываются напрямую (все — по умолчанию).
SCALING_KEYS = {
    "atk": (S.BASE_ATK, S.ATK_PCT, S.FLAT_ATK),
    "hp": (S.BASE_HP, S.HP_PCT, S.FLAT_HP),
    "def": (S.BASE_DEF, S.DEF_PCT, S.FLAT_DEF),
    "em": (S.BASE_EM, S.EM_PCT, S.FLAT_EM),
}


# --------------------------------------------------------------------------- #
#  Контейнер                                                                   #
# --------------------------------------------------------------------------- #
@dataclass
class Stats:
    """Аддитивный набор статов."""

    data: Dict[str, float] = field(default_factory=dict)

    # ---- базовые операции ------------------------------------------------- #
    def add(self, key: str, value: float) -> "Stats":
        if value:
            self.data[key] = self.data.get(key, 0.0) + value
        return self

    def add_many(self, mapping: Mapping[str, float]) -> "Stats":
        for k, v in mapping.items():
            self.add(k, v)
        return self

    def get(self, key: str, default: float = 0.0) -> float:
        return self.data.get(key, default)

    def copy(self) -> "Stats":
        return Stats(dict(self.data))

    def merged(self, other: "Stats" | Mapping[str, float]) -> "Stats":
        out = self.copy()
        src = other.data if isinstance(other, Stats) else other
        out.add_many(src)
        return out

    def __add__(self, other):
        return self.merged(other)

    def __repr__(self) -> str:  # pragma: no cover - удобство отладки
        body = ", ".join(f"{k}={v:g}" for k, v in sorted(self.data.items()))
        return f"Stats({body})"

    # ---- производные значения --------------------------------------------- #
    def scaled(self, what: str) -> float:
        """Итоговое значение стата: база * (1 + %) + плоская прибавка.

        what: "atk" | "hp" | "def" | "em"
        """
        base_key, pct_key, flat_key = SCALING_KEYS[what]
        return self.get(base_key) * (1.0 + self.get(pct_key)) + self.get(flat_key)

    @property
    def atk(self) -> float:
        return self.scaled("atk")

    @property
    def hp(self) -> float:
        return self.scaled("hp")

    @property
    def defense(self) -> float:
        return self.scaled("def")

    @property
    def em(self) -> float:
        return self.scaled("em")

    def stat(self, name: str) -> float:
        """Универсальный доступ: производный стат либо «сырой» ключ."""
        if name in SCALING_KEYS:
            return self.scaled(name)
        return self.get(name)

    # ---- бонусы урона ------------------------------------------------------ #
    def dmg_bonus(self, *tags: str) -> float:
        """Сумма всех бонусов урона, подходящих под набор тегов.

        Учитывается ключ "dmg_bonus" и любой "dmg_bonus.<tag>",
        где <tag> — одна из переданных меток (стихия, тип атаки и т.п.).
        Также поддерживаются составные "dmg_bonus.a.b", если ВСЕ части входят в tags.
        """
        return self._tagged_sum(S.DMG_BONUS, tags)

    def ssw_bonus(self, *tags: str) -> float:
        return self._tagged_sum(S.SSW_BONUS, tags)

    def ssw_base_inc(self, *tags: str) -> float:
        return self._tagged_sum(S.SSW_BASE_INC, tags)

    def flat_base_dmg(self, *tags: str) -> float:
        """«Дополнительный базовый урон» с учётом точечных ключей вида
        \"flat_base_dmg.<тег>\" — так же, как dmg_bonus/ssw_bonus.

        Нужно, например, для баффов вроде «Водяницы»: плоская добавка
        должна попадать ровно в один конкретный удар (свой уникальный
        тег), а не во все источники персонажа сразу.
        """
        return self._tagged_sum(S.FLAT_BASE_DMG, tags)

    def crit_rate(self, *tags: str) -> float:
        """Шанс крита с учётом точечных ключей вида "crit_rate.anemo"."""
        return self._tagged_sum(S.CRIT_RATE, tags)

    def crit_dmg(self, *tags: str) -> float:
        """Крит. урон с учётом точечных ключей вида "crit_dmg.anemo"."""
        return self._tagged_sum(S.CRIT_DMG, tags)

    def crit_value(self, *tags: str) -> float:
        """Крит-вэлью с учётом точечных ключей вида "crit_value.anemo"."""
        return self._tagged_sum(S.CRIT_VALUE, tags)

    def elevation(self, *tags: str) -> float:
        """«Возвышение» с учётом точечных ключей вида "elevation.stellar_swirl".

        Итоговый множитель урона — (1 + возвышение).
        """
        return self._tagged_sum(S.ELEVATION, tags)

    def res_reduction(self, *tags: str) -> float:
        """Суммарное снижение сопротивления цели для данной стихии.

        Учитывается ключ "res_reduction" (снижение ко всем стихиям)
        и "res_reduction.<стихия>". Значения — в долях: 0.20 = -20% RES.
        """
        return self._tagged_sum(S.RES_REDUCTION, tags)

    def _tagged_sum(self, prefix: str, tags: Iterable[str]) -> float:
        tagset = set(tags)
        total = 0.0
        for key, value in self.data.items():
            if key == prefix:
                total += value
            elif key.startswith(prefix + "."):
                parts = key[len(prefix) + 1:].split(".")
                if all(p in tagset for p in parts):
                    total += value
        return total


# --------------------------------------------------------------------------- #
#  Крит                                                                        #
# --------------------------------------------------------------------------- #
def crit_multiplier(stats: Stats, mode: str = "expected", *tags: str) -> float:
    """Множитель крита для удара с данными тегами.

    Крит-статы, как и бонусы урона, поддерживают точечные ключи:

        "crit_dmg"          — ко всему урону
        "crit_dmg.anemo"    — только к анемо урону
        "crit_rate.burst"   — только к урону взрыва
        "crit_value.anemo"  — то же для режимов, считающих по крит-вэлью

    Теги удара — стихия, тип атаки и модель урона (см. DamageSource.tags()),
    поэтому «+40% анемо крит. урона» сам собой не попадёт на крио-удары.

    Режимы:
      "expected"   — 1 + min(шанс,1) * крит.урон  (математическое ожидание)
      "always"     — 1 + крит.урон  (всегда крит)
      "none"       — 1
      "cv_sq_8"    — 1 + CV²/8  (приближение из таблицы Excel)
      "cv_minus_1" — CV - 1     (вариант, встречающийся в таблице у Крио ГГ)
    """
    if mode == "expected":
        return 1.0 + min(stats.crit_rate(*tags), 1.0) * stats.crit_dmg(*tags)
    if mode == "always":
        return 1.0 + stats.crit_dmg(*tags)
    if mode == "none":
        return 1.0
    cv = stats.crit_value(*tags)
    if mode in ("cv_sq_8", "balance"):   # ЗАГЛУШКА: считаю "balance" == 1 + CV**2/8
        return 1.0 + cv * cv / 8.0
    if mode == "cv_minus_1":
        return cv - 1.0
    raise ValueError(f"Неизвестный режим крита: {mode!r}")