from ..core.stats import S

"Стандартный набор подстатов из артефактов"
STANDART_SUBSTAT_PRESET = {
            S.ATK_PCT: 0.049*4,
            S.HP_PCT: 0.049*4,
            S.DEF_PCT: 0.062*4,
            S.FLAT_ATK: 16.5*4+311,
            S.FLAT_DEF: 19.6*4,
            S.FLAT_HP: 250*4+4780,
            S.BASE_EM: 20*4,
            S.CRIT_VALUE: 0.066 * 20,    
}

STANDART_SUBSTAT_FULL_ATK_PRESET = {
            S.ATK_PCT: 0.049*8,
            S.HP_PCT: 0.049*4,
            S.DEF_PCT: 0.062*4,
            S.FLAT_ATK: 16.5*4+311,
            S.FLAT_DEF: 19.6*4,
            S.FLAT_HP: 250*4+4780,
            S.BASE_EM: 20*4,
            S.CRIT_VALUE: 0.066 * 4,    
}

STANDART_SUBSTAT_PRESET_EM_SCALE = {
            S.ATK_PCT: 0.049*2,
            S.HP_PCT: 0.049*2,
            S.DEF_PCT: 0.062*4,
            S.FLAT_ATK: 16.5*4+311,
            S.FLAT_DEF: 19.6*4,
            S.FLAT_HP: 250*4+4780,
            S.BASE_EM: 20*6,
            S.CRIT_VALUE: 0.066 * 20,    
}

HIGH_SUBSTAT_PRESET = {
            S.ATK_PCT: 0.049*4,
            S.HP_PCT: 0.049*4,
            S.DEF_PCT: 0.062*4,
            S.FLAT_ATK: 16.5*4+311,
            S.FLAT_DEF: 19.6*4,
            S.FLAT_HP: 250*4+4780,
            S.BASE_EM: 20*6,
            S.CRIT_VALUE: 0.066 * 24,    
}

EM_ER_SUBSTAT_PRESET = {
            S.ATK_PCT: 0.049*2,
            S.HP_PCT: 0.049*2,
            S.DEF_PCT: 0.062*4,
            S.FLAT_ATK: 16.5*4+311,
            S.FLAT_DEF: 19.6*4,
            S.FLAT_HP: 250*4+4780,
            S.BASE_EM: 20*8,
            S.CRIT_VALUE: 0.066 * 4,    
}