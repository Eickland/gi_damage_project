from __future__ import annotations
from dataclasses import replace  # noqa: F401 — для patches= в файлах отрядов

from ...core.buffs import OTHERS, SELF, TEAM, Buff, temp
from ...core.entities import Character, Constellation, with_rotation
from ...core.stats import S
from ..tags import DREAM, INST, OFF, ON, MIZUKI_C1, VODYA_CHORUS,VODYA_LEAD, VODYA_LEAD_ELEM
from ...core.sources import elemental, occ, stellar_swirl

def vodyanitsa_stack_bonus(max_hp: float) -> float:
    """+260 доп. базового урона за каждую 1000 Max HP Водяницы свыше 40000,
    максимум 6500 (A4 «Dirge of the Fandyr»)."""
    return min(260.0 * max(0.0, max_hp - 40000.0) / 1000.0, 6500.0)

def vodyanitsa_elem_bonus(max_hp: float) -> float:
    """+140 к гидро/крио урону за каждую 1000 Max HP Водяницы свыше 40000,
    максимум 3500 (та же пассивка, режим без Wandering Vortex)."""
    return min(140.0 * max(0.0, max_hp - 40000.0) / 1000.0, 3500.0)


def _vodya_hp(ctx) -> float:
    return ctx.stat("Водяница", "hp", frozenset({OFF}))


def vodyanitsa_c1_bonus(max_hp: float) -> float:
    return 0.008*max_hp

VODYANITSA_KIT = Character(
    name="Водяница",
    element="hydro",
    weapon_type="catalyst",
    default_field=OFF,
    crit_mode="balance",
    stats={
        S.BASE_HP: 14818.0,
        S.CRIT_VALUE: 0.6,
        S.HP_PCT: 0.288
    },
    buffs=(Buff(S.FLAT_BASE_DMG, lambda ctx: vodyanitsa_stack_bonus(
             ctx.stat("Водяница", "hp", frozenset({OFF}))),
         target=TEAM, requires=(VODYA_LEAD,),
         source="Водяница: Lead Vocal (SSW навыка)"),
            Buff(S.FLAT_BASE_DMG, lambda ctx: vodyanitsa_stack_bonus(
             ctx.stat("Водяница", "hp", frozenset({OFF}))),
         target=TEAM, requires=(VODYA_CHORUS,),
         source="Водяница: Chorus (SSW навыка)"),
        Buff("res_reduction.anemo", 0.35, target=TEAM,
                    source="-35% анемо сопротивления"),
        Buff("res_reduction.cryo", 0.3, target=TEAM,
                    source="-30% крио сопротивления"),
        Buff("res_reduction.hydro", 0.3, target=TEAM,
                    source="-30% гидро сопротивления"),
        Buff("res_reduction.anemo", -1000, target=SELF,
                    source="Нет вклада в звездные реакции"),
        Buff("res_reduction.cryo", -1000, target=SELF,
                    source="Нет вклада в звездные реакции")),
    

    constellations={
        1: Constellation(
            number=1,
            name="C1",
            buffs=(
                Buff(S.FLAT_ATK, lambda ctx: vodyanitsa_c1_bonus(
             ctx.stat("Водяница", "hp", frozenset({OFF}))),
                     target=OTHERS,
                     source="C1"),
            ),
        ),
        2: Constellation(
            number=2,
            name="C2",
            buffs=(
                Buff("crit_value.stellar_swirl",
                     0.6,
                     target=OTHERS, requires=(ON,),
                     source="C2: +60% К криту урону звездного рассеивания"),
            ),
        ),
        3: Constellation(
            number=3,
            name="C3",
            buffs=(Buff("res_reduction.cryo", 0.054, target=TEAM,
                    source="C3: Бонус к срезу крио сопротивления"),
            Buff("res_reduction.hydro", 0.054, target=TEAM,
                    source="C3: Бонус к срезу сопротивления")
            ),
        ),
        4: Constellation(
            number=4,
            name="C4",
            buffs=(Buff(S.HP_PCT, 0.6, target=SELF,
                    source="C4: Бонус к хп"),
            ),
        ),
        5: Constellation(
            number=5,
            name="C5",
        ),         
        6: Constellation(
            number=6,
            name="C6",
            buffs=(
                Buff("elevation.stellar_swirl", 0.25, target=TEAM,
                    source="C6: +25% возвышения урона SSW всем"),
                Buff("crit_value.stellar_swirl",0.6,
                     target=OTHERS, requires=(OFF,),
                     source="C6: +60% К криту урону звездного рассеивания"),
            ),
        ),
    },
    note="",
)


# --------------------------------------------------------------------------- #
#  Режим БЕЗ Wandering Vortex (любые отряды без звёздного рассеивания)          #
# --------------------------------------------------------------------------- #
#  Без вихря на поле те же эффекты работают на ГИДРО и КРИО урон, а не на
#  урон звёздного рассеивания. Эти баффы добавляются только в комбо
#  "sc_off_field", поэтому отряды звёздного рассеивания ("off_field") не меняются.
#  В отрядах звёздного проводника Водяница — опциональный слот: элементального
#  урона там мало, основная польза — от C2/C6.
#
#  Lead Vocal: удар активного персонажа, помеченный VODYA_LEAD_ELEM, получает
#      +140 за каждую 1000 HP Водяницы свыше 40000 (макс. 3500) — плоская
#      прибавка к базе ТОЛЬКО ЭЛЕМЕНТАЛЬНОГО урона ("flat_dmg"). На урон
#      звёздного проводника не действует.
#  C2 «Two Voices in Black and White»: +50% КУ гидро и крио урона активного
#      персонажа — ко ВСЕМУ гидро/крио урону, включая звёздный проводник
#      (теги удара: стихия + тип + модель, ключ "crit_value.cryo" ловит все).
#  C6: «Two Voices» — всему отряду (и вне поля), +60% гидро и крио урона.

SC_MODE_BUFFS = tuple(
    Buff(key, lambda ctx: vodyanitsa_elem_bonus(_vodya_hp(ctx)),
         target=TEAM, requires=(ON, VODYA_LEAD_ELEM),
         source=f"Водяница: Lead Vocal (+140 за 1000 HP сверх 40000, макс. 3500) — {label}")
    for key, label in (
        ("flat_dmg.hydro", "гидро урон"),
        ("flat_dmg.cryo", "крио урон"),
    )
)

SC_MODE_CONSTELLATION_BUFFS = {
    2: tuple(
        Buff(f"crit_value.{el}", 0.50, target=TEAM, requires=(ON,),
             source=f"C2: Two Voices in Black and White, +50% КУ {name} урона активному")
        for el, name in (("hydro", "гидро"), ("cryo", "крио"))
    ),
    6: tuple(
        Buff(f"crit_value.{el}", 0.50, target=TEAM, requires=(OFF,),
             source=f"C6: Two Voices in Black and White всему отряду, +50% КУ {name} урона")
        for el, name in (("hydro", "гидро"), ("cryo", "крио"))
    ) + tuple(
        Buff(f"dmg_bonus.{el}", 0.60, target=TEAM,
             source=f"C6: Song of Ages Past, +60% {name} урона")
        for el, name in (("hydro", "гидро"), ("cryo", "крио"))
    ),
}

_VODYA_SOURCES = (
    elemental("Использование навыка", "hp", 0.589, "hydro", "skill", [occ(1, ON,)]),
    elemental("Навык, Horn of Spring", "hp", 0.589, "hydro", "skill", [occ(5, OFF,),]),
)

VODYA_COMBO_DICT = {
    "off_field" : with_rotation(VODYANITSA_KIT,    
            sources=(elemental("Использование навыка", "hp", 0.589, "hydro", "skill",
                  [occ(1, ON,)]),
        elemental("Навык, Horn of Spring", "hp", 0.589, "hydro", "skill",
                  [occ(5, OFF,),]),),),
    # Отряды без вихря (в т.ч. звёздного проводника): те же удары + баффы режима без вихря
    "sc_off_field": with_rotation(
        VODYANITSA_KIT,
        sources=_VODYA_SOURCES,
        extra_buffs=SC_MODE_BUFFS,
        constellation_extra_buffs=SC_MODE_CONSTELLATION_BUFFS,
    ),
}
