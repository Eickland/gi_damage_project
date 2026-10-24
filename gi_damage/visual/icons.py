"""Поиск иконок персонажей, оружия и артефактов.

Иконки кладутся в папки (ICON_DIR = <корень проекта>/assets/icons):

    assets/icons/characters/<имя>.png
    assets/icons/weapons/<имя>.png
    assets/icons/artifacts/<имя>.png

Имя файла — это либо значение из ALIASES, либо само название из проекта
(«Мидзуки.png»), либо его «слаг» (строчные буквы, пробелы -> «_»).
Расширения: png, webp, jpg, jpeg, svg. Если файла нет — рисуется заглушка
с инициалами, так что карточки собираются и без единой картинки.
"""

from __future__ import annotations

import base64
import hashlib
import html
import mimetypes
import re
from pathlib import Path
from typing import Dict, Mapping, Optional

ICON_DIR = Path(__file__).resolve().parents[2] / "assets" / "icons"
EXTENSIONS = (".png", ".webp", ".jpg", ".jpeg", ".svg")

#: название в проекте -> имя файла без расширения. Правьте под свои файлы.
ALIASES: Dict[str, Dict[str, str]] = {
    "characters": {
        "Мидзуки": "mizuki",
        "Крио ГГ": "cryo_traveler",
        "Одетта": "odette",
        "Сахароза": "sucrose",
        "Фарузан": "faruzan",
        "Весна": "vesna",
        "Водяница": "vodyanitsa",
        "Диона":"diona",
        "Ци Ци" : "qiqi",
        "Сандроне" : "sandrone",
        "Алеша" : "alyosha",
        "Сайно" : "cyno",
        "Яэ Мико" : "yae",
        "Митя" : "mitya",
        "Валера" : "valera",
        "Ризли" : "wrio",
        "Линея" : "linnea",
        "Николь" : "nicole",
        "Колумбина" : "columbina",
        "Цзы Бай" : "zibai",
        "Иллуги" : "illuga",
    },
    "weapons": {
        "Песнь странника": "wanderers_song",
        "Сон солнечным утром": "sunny_morning_sleep_in",
        "Пробуждение": "exaiphanes",
        "Серебряный свет": "silver_light",
        "Церемон": "sacrificial_fragments",
        "Лук фавония": "favonius_warbow",
        "Напевы ветра": "breezeborne_bow",
        "Морозное перо белого озера": "frostfeather",
        "Застывшее сердце зимы": "winter",
        "За пределами кокона": "beyond_the_chrysalis",
        "Источник пламени": "emberwell",
        "Эпос": "ttds",
        "Ода водоворота": "maelstrom",
        "Финал глубин": "finale_of_the_deep",
        "Предвестник": "harbinger",
        "Новая ветвь": "new_bough",
        "Лазурное сияние": "azurelight",
        "Меч фавония":"fav_sword",
        "Копье фавония":"fav_lance",
        "Reliquary of Truth":"reliquary",
        "Starsealed Edict":"starsealed",
        "Starcaller's Watch":"starcaller",
        "Sacrificial Jade":"jade",
        "Тень волны":"tidal_shadow",
        "Меч драконьей кости":"serpent_spine",
        "Цветок в латах":"flower",
        "Чайная ложка":"teaspoon",
        "Тысяча солнц":"thousand_suns",
        "Симфонист ароматов":"symphonist",
        "Смертельный бой":"dmatch",
        "Отголоски сердца":"echoes",
        "Истина кагура":"kagura",
        "Посох алых песков":"staff",
        "Элегия":"elegy",
        "Флейта":"flute",
        "Завет мороза":"covenant",
        "Погибель драконов":"dragons_bane",
        "Янтарь":"amber",
        "Клинок искупления":"atonement",
        "Золотая клятва":"golden_oath",
        "Ноктюрн":"nocturne",
        "Осколок луны":"moonshard",
    },
    "artifacts": {
        "Инструктор": "instructor",
        "Изумрудная тень": "viridescent_venerer",
        "Милеллит": "millelith",
        "Сердце горна": "heart_of_forge",
        "Багряное доказательство": "scarlet_proof",
        "Сияние Вурукаши": "vourukasha",
        "Рассветная песнь": "aubade",
        "Ночь неба": "night_sky",
        "Позолоченные сны":"gilded",
        "Разочарование":"disenchantment",
        "Знать":"noble",
        "Серенада":"serenade",
    },
}


def slug(name: str) -> str:
    return re.sub(r"[^\w]+", "_", name.strip().lower()).strip("_")


def initials(name: str) -> str:
    words = [w for w in re.split(r"[\s+]+", name) if w]
    if not words:
        return "?"
    if len(words) == 1:
        return words[0][:2].capitalize()
    return (words[0][0] + words[1][0]).upper()


class IconStore:
    """Достаёт иконки с диска и встраивает их в HTML как data-URI."""

    def __init__(self, root: Path | str = ICON_DIR,
                 aliases: Optional[Mapping[str, Mapping[str, str]]] = None):
        self.root = Path(root)
        merged = {k: dict(v) for k, v in ALIASES.items()}
        for kind, table in (aliases or {}).items():
            merged.setdefault(kind, {}).update(table)
        self.aliases = merged
        self._cache: Dict[tuple, Optional[str]] = {}

    def find(self, kind: str, name: str) -> Optional[Path]:
        stems = [self.aliases.get(kind, {}).get(name), name, slug(name)]
        for stem in filter(None, stems):
            for ext in EXTENSIONS:
                path = self.root / kind / f"{stem}{ext}"
                if path.is_file():
                    return path
        return None

    def data_uri(self, kind: str, name: str) -> Optional[str]:
        key = (kind, name)
        if key not in self._cache:
            path = self.find(kind, name)
            if path is None:
                self._cache[key] = None
            else:
                mime = mimetypes.guess_type(path.name)[0] or "image/png"
                raw = base64.b64encode(path.read_bytes()).decode("ascii")
                self._cache[key] = f"data:{mime};base64,{raw}"
        return self._cache[key]

    def missing(self, kind: str, names) -> list:
        return sorted({n for n in names if self.find(kind, n) is None})

    def img(self, kind: str, name: str, css_class: str = "") -> str:
        """<img> с иконкой либо SVG-заглушка с инициалами."""
        uri = self.data_uri(kind, name)
        title = html.escape(name, quote=True)
        if uri:
            return f'<img class="{css_class}" src="{uri}" alt="{title}" title="{title}">'
        hue = int(hashlib.md5(name.encode("utf-8")).hexdigest()[:4], 16) % 360
        text = html.escape(initials(name))
        svg = (
            f'<svg class="{css_class} ph" viewBox="0 0 64 64" role="img" '
            f'aria-label="{title}"><title>{title}</title>'
            f'<rect width="64" height="64" fill="hsl({hue},38%,30%)"/>'
            f'<text x="32" y="40" text-anchor="middle" font-size="24" '
            f'font-weight="700" fill="hsl({hue},60%,88%)">{text}</text></svg>'
        )
        return svg