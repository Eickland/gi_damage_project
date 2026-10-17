from __future__ import annotations
from dataclasses import dataclass, field, replace
from typing import Callable, Mapping, Optional, Sequence

from .entities import Build
from .reactions import ReactionEvent

BuildPatch = Callable[[Build], Build]


@dataclass(frozen=True)
class Phase:
    """Одна ротация внутри цикла."""
    name: str
    count: float = 1.0                       # сколько таких ротаций в цикле
    builds: Mapping[str, BuildPatch] = field(default_factory=dict)  # слот -> правка сборки
    reactions: Optional[Sequence[ReactionEvent]] = None             # None = как у Team
    rotation: str = ""                       # описание для отчёта