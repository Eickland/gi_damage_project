"""Ядро расчёта урона."""

from .buffs import (OTHERS, SELF, TEAM, Buff, BuffContext, BuffSource, State,
                    buff, state, temp)
from .engine import (CharacterResult, Config, HitResult, StatResolver, Team,
                     TeamContext, TeamResult)
from .entities import (ArtifactSet, Build, Character, Constellation, Enemy,
                       Weapon, add_state_tags)
from .formulas import (SSW_ANEMO_MULTIPLIER, SSW_VORTEX_MULTIPLIER,
                       STELLAR_SWIRL_BASE_DMG, elemental_damage,
                       em_swirl_term, inverse_resistance_multiplier,
                       resistance_multiplier, stellar_swirl_direct,
                       stellar_swirl_reaction)
from .reactions import (DEFAULT_WEIGHTS, ReactionEvent, distribute, ssw_anemo,
                        ssw_vortex)
from .roster import (Roster, Variation, character_scan, compare_teams,
                     constellation_scan, weapon_scan)
from .sources import (ELEMENTAL, STELLAR_SWIRL, DamageSource, Occurrence,
                      elemental, occ, stellar_swirl)
from .stats import S, Stats, crit_multiplier

__all__ = [n for n in dir() if not n.startswith("_")]
