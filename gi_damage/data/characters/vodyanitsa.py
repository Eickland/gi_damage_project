from __future__ import annotations
from dataclasses import replace  # noqa: F401 — для patches= в файлах отрядов

from ...core.buffs import OTHERS, SELF, TEAM, Buff, temp
from ...core.entities import Character, Constellation, with_rotation
from ...core.stats import S
from ..tags import DREAM, INST, OFF, ON, MIZUKI_C1, VODYA_CHORUS,VODYA_LEAD
from ...core.sources import elemental, occ, stellar_swirl

def vodyanitsa_stack_bonus(max_hp: float) -> float:
    """+260 доп. базового урона за каждую 1000 Max HP Водяницы свыше 40000,
    максимум 6500 (A4 «Dirge of the Fandyr»)."""
    return min(260.0 * max(0.0, max_hp - 40000.0) / 1000.0, 6500.0)

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
         target="Весна", requires=(VODYA_LEAD,),
         source="Водяница: Lead Vocal (SSW навыка)"),
            Buff(S.FLAT_BASE_DMG, lambda ctx: vodyanitsa_stack_bonus(
             ctx.stat("Водяница", "hp", frozenset({OFF}))),
         target="Крио ГГ", requires=(VODYA_CHORUS,),
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


VODYA_COMBO_DICT = {
    "off_field" : with_rotation(VODYANITSA_KIT,    
            sources=(elemental("Использование навыка", "hp", 0.589, "hydro", "skill",
                  [occ(1, ON,)]),
        elemental("Навык, Horn of Spring", "hp", 0.589, "hydro", "skill",
                  [occ(5, OFF,),]),),)
}