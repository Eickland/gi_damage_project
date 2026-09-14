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

MY_MIZUKI_VV_BUILD = {
            S.ATK_PCT: 0.122,
            S.BASE_EM: 23,
            S.CRIT_VALUE: 2.426-0.622,
            S.FLAT_ATK: 311,    
}

MY_CMC_SSW_BUILD = {
            S.ATK_PCT: 0.041,
            S.BASE_EM: 75,
            S.CRIT_VALUE: 2.154-0.078-0.622,
            S.FLAT_ATK: 33+311,    
}

MY_ODETTE_SSW_BUILD = {
            S.ATK_PCT: 0.245,
            S.BASE_EM: 63,
            S.CRIT_VALUE: 2.13-0.622,
            S.FLAT_ATK: 47+311,    
}
