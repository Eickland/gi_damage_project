"""
gi_damage — расчёт урона отрядов Genshin Impact.

Быстрый старт:

    from gi_damage.presets.mizuki_sucrose_odette_cmc import all_teams
    from gi_damage.core.report import team_summary

    for name, team in all_teams().items():
        print(team_summary(team.compute()))
"""

from .core import *  # noqa: F401,F403

__version__ = "0.1.0"
