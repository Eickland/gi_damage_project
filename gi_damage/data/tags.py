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

__all__ = ["ON", "OFF", "INST", "DREAM", "FROSTGLOW", "BREEZEBORNE",
           "ARMED", "DA1", "DA2", "DA3", "DA4", "DA5", "DA6","VODYA_LEAD","VODYA_CHORUS","TTDS_HALF","VV_CRYO","VV_PYRO"
           ,"VV_HYDRO","VV_ELECTRO","CATS_TAIL","SEVEN_SACRED","MIZUKI_C1","DECODING","TTDS_FULL","SANDRONE_CA_STACKS_1","SANDRONE_CA_STACKS_2","SANDRONE_CA_STACKS_3",
           "NOBLE"]
