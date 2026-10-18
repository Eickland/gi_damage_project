"""
Теги состояний, используемые в данных.

Состояние источника урона — это набор таких тегов. Постоянные и
псевдопостоянные баффы не требуют тегов вообще; временные — требуют.

Добавляйте свои теги свободно: движок ничего о них не знает,
он только сравнивает множества строк.
"""

# --- где находится персонаж ------------------------------------------------ #
ON = "on_field"      # персонаж на поле
OFF = "off_field"    # персонаж вне поля

# --- окна временных усилений ----------------------------------------------- #
#: окно «Инструктор + A4 Сахарозы» (в таблице — «instructor + Sucrose»)
INST = "instructor"



#: 15с усиление звзедного урона от Крио ГГ
FROSTGLOW = "frostglow"

# 12с увеличение урона звзедных реакций от лука
BREEZEBORNE = "breezeborne"

# --- Весна: состояние «Armed for Action» ------------------------------------ #
ARMED = "armed_for_action"

DA1 = "da1"
DA2 = "da2"
DA3 = "da3"
DA4 = "da4"
DA5 = "da5"
DA6 = "da6"

# --- Водяница ------------------------------------ #
VODYA_LEAD  = "vodya_lead"     # 1-й потраченный стак Lead Vocal
VODYA_CHORUS = "vodya_chorus"  # 1-й потраченный стак Chorus

# --- Мидзуки ------------------------------------ #
MIZUKI_C1 = "mizuki_c1" # увеличение урона звездного рассеивания от с1

#: окно состояния «Дрейф грёз» (Dreamdrifter) Мидзуки — пока она на поле.
#: В нём работают эффекты её C2: бонус урона отряду и снижение сопротивлений цели.
DREAM = "dreamdrifter"

# --- Сандроне ------------------------------------ #
DECODING = "decoding"
SANDRONE_CA_STACKS_1 = "sandrone_ca_1"
SANDRONE_CA_STACKS_2 = "sandrone_ca_2"
SANDRONE_CA_STACKS_3 = "sandrone_ca_3"

#Эпос, 10с увеличение атаки
TTDS_HALF = "ttds_half"
TTDS_FULL = "ttds_full"

#Анемо сет
VV_CRYO = "vv_cryo"
VV_PYRO = "vv_pyro"
VV_HYDRO = "vv_hydro"
VV_ELECTRO = "vv_electro"

#С6 диона
CATS_TAIL = "cats_tail"

#Ци ци
SEVEN_SACRED = "seven_sacred"

#Церемония знати
NOBLE = "noble"

# --- Сайно ------------------------------------ #
#: Сайно в состоянии «Pactsworn Pathclearer» (после взрыва стихии)
PACTSWORN = "pactsworn_pathclearer"
#: «Together We Rise» (C1 Radiance) на персонаже, на которого Сайно переключился
TOGETHER_WE_RISE = "together_we_rise"
#: Тег источников «Duststalker Bolt - Starsame» (доп. базовый урон от МС, A4)
STARSAME = "starsame"

# --- Яэ Мико ------------------------------------ #
#: Тег источников «Сесшо Сакура» (бонус от МС, C6 игнор защиты)
SESSHOU_SAKURA = "sesshou_sakura"

# --- Валера ------------------------------------ #
#: Окно «Offensive Directive»: удар активного персонажа, тратящий стак
#: (электро урон звёздного проводника получает доп. базовый урон от АТК Валеры)
OFFENSIVE_DIRECTIVE = "offensive_directive"

# --- Ризли ------------------------------------ #
#: C1 Ризли: +50% урона SC 5-го удара после Luster: Vaulting Fist и
#: +50% урона Luster: Vaulting Fist после 5-го удара
WRIO_C1 = "wriothesley_c1"

# --- Николь ------------------------------------ #
#: Guidance of Theosis (Methexis): активный персонаж провёл на поле 3 с → +300 АТК
THEOSIS = "guidance_of_theosis"

#Элегия
ELEGY = "ELEGY"

__all__ = ["ON", "OFF", "INST", "DREAM", "FROSTGLOW", "BREEZEBORNE",
           "ARMED", "DA1", "DA2", "DA3", "DA4", "DA5", "DA6","VODYA_LEAD","VODYA_CHORUS","TTDS_HALF","VV_CRYO","VV_PYRO"
           ,"VV_HYDRO","VV_ELECTRO","CATS_TAIL","SEVEN_SACRED","MIZUKI_C1","DECODING","TTDS_FULL","SANDRONE_CA_STACKS_1","SANDRONE_CA_STACKS_2","SANDRONE_CA_STACKS_3",
           "NOBLE","PACTSWORN","TOGETHER_WE_RISE","SESSHOU_SAKURA","STARSAME","ELEGY","OFFENSIVE_DIRECTIVE","WRIO_C1","THEOSIS"]
