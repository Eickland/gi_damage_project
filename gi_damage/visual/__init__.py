"""Второй уровень вывода: HTML-карточки отрядов и ростеров с иконками.

Текстовые отчёты (core/report.py) остаются как были — этот пакет только читает
готовые TeamResult и ничего не считает сам.

    from gi_damage.visual import save_cards, RosterBook
    save_cards(results, "cards.html", columns=2)      # отряды
    book = RosterBook(); book.add(roster, "оружие"); book.save("rosters.html")
"""

from .cards import render_card, render_page, save_cards, save_png
from .icons import ALIASES, ICON_DIR, IconStore
from .rosters import RosterBook, render_roster, save_rosters
from .search import SearchBook, render_alternatives, render_plan

__all__ = ["render_card", "render_page", "save_cards", "save_png",
           "RosterBook", "render_roster", "save_rosters",
           "SearchBook", "render_alternatives", "render_plan",
           "IconStore", "ICON_DIR", "ALIASES"]