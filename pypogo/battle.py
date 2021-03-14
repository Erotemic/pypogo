"""
The PVPoke implementation of battle logic can be found in [1]_.

References:
    .. [1] https://github.com/pvpoke/pvpoke/blob/master/src/js/battle/Battle.js
    .. [2] https://gamepress.gg/pokemongo/damage-mechanics
    .. [3] https://gamepress.gg/pokemongo/evaluating-stat-boosts-and-rng
    .. [3] https://pokemongohub.net/post/pvp/comprehensive-pvp-mechanics-guide-in-pokemon-go/
"""
from pypogo.pokemon import Pokemon
import ubelt as ub
import random


class Environment(ub.NiceRepr):
    """
    Has a space-time grid.
    """
    def __init__(self):
        self.actors = []
        self.properties = {}
        self.clock = None
        self.current_timestep = None
        self.rng = random.Random()


class Actor(ub.NiceRepr):
    """
    Interacts with other actors in a space-time grid.
    """


class BattleZone(Environment):
    """
    Example:
        from pypogo.battle import *  # NOQA
        self = BattleZone.random()

    """

    def __init__(self):
        super().__init__()
        self.players = []
        self.state = 'FAST_STATE'  #
        self.valid_states = [
            'START_STATE',
            'FAST_STATE',
            'CHARGE_STATE',
            'END_STATE',
        ]
        self.action_queue = []
        self.timeline = []
        self.clock = 0
        self.delta = 500
        self.time_limit = 240000
        self.verbose = 1

    def __nice__(self):
        return ub.repr2({
            'players': self.players,
        })

    @classmethod
    def random(cls):
        player1 = Trainer.random()
        player2 = Trainer.random()
        players = [player1, player2]
        self = cls()
        self.players = players
        return self

    def initialize(self):
        self.timeline = []
        self.clock = 0
        events = []
        for player in self.players:
            player.initialize()
            events.append({
                'desc': 'initialize {}'.format(player),

            })
        return events

    def run(self, verbose=0):
        """
        Example:
            self = BattleZone.random()
            self.initialize()
            self.time_limit = 1000
            self.run(verbose=1)
        """
        self.verbose = verbose
        events = self.initialize()
        for event in events:
            self.log_event(event)

        ongoing = True
        while ongoing:
            events = self.step()
            for event in events:
                self.log_event(event)

            if self.clock >= self.time_limit:
                self.log_event({'desc': 'times up'})
                ongoing = False

    def log_event(self, event):
        if self.verbose:
            print('{}'.format(ub.repr2(event, nl=1)))
        self.timeline.append(event)

    def step(self):
        """
        from pypogo.battle import *  # NOQA

        self = BattleZone.random()
        self.initialize()
        self.step()
        """

        if self.clock >= self.time_limit:
            return []
            pass

        # At each step, any unblocked player should be able to add an action to
        # the priority queue.

        # Actions in the queue are then resolved in priority order, and then
        # induce a cooldown time that blocks the actor.

        player1, player2  = self.players

        mon1 = player1.pokemon[0]
        mon2 = player2.pokemon[0]

        env = self
        action1 = player1.choose_action(env)
        action2 = player2.choose_action(env)

        move1 = action1['move']
        move2 = action2['move']

        if move1['move_type'] == 'fast' and move2['move_type'] == 'fast':
            pass

        # action = 'fast_move'
        # if action == 'fast_move':

        effects = []
        effect = {
            'desc': f'{mon1.name!r} used {move1["name"]!r} against {mon2.name!r}',
            'damage': compute_damage(mon1, mon2, move1),
            'target': mon2,
        }
        effects.append(effect)
        effect = {
            'desc': f'{mon2.name!r} used {move2["name"]!r} against {mon1.name!r}',
            'damage': compute_damage(mon2, mon1, move2),
            'target': mon1,
        }
        effects.append(effect)

        for effect in effects:
            effect['target'].hp -= effect['damage']

        self.clock += self.delta
        return effects


class Trainer(Actor):
    """

    from pypogo.battle import *  # NOQA
    player1 = Trainer.random()
    player2 = Trainer.random()

    print('player1 = {!r}'.format(player1))
    print('player2 = {!r}'.format(player2))
    """

    def __init__(self, pokemon=[]):
        self.pokemon = pokemon
        self.sheilds = 2
        self.rng = random.Random()
        self.initialize()

    def __nice__(self):
        return ub.repr2(self.pokemon)

    @classmethod
    def random(cls):
        pokemon = [
            Pokemon.random(level=1).maximize(1500)
            for _ in range(3)
        ]
        self = cls(pokemon)
        return self

    def initialize(self):
        self.shields = 2
        for mon in self.pokemon:
            mon.hp = int(mon.adjusted['stamina'])
            mon.energy = 0
            mon.feinted = False
            mon.active = False

        self.active_mon = self.pokemon[0]
        self.active_mon.active = True
        self.active_mon.buffs = 0
        self.active_mon.debuffs = 0
        self.switch_clock = 0
        self.blocked = False

    def choose_action(self, env):
        """
        env = BattleZone.random()
        self = env.players[0]
        self.initialize()

        Cases:

           (

                (

                    * Your opponent is executing a fast option (attack or switch)

                    XOR

                    * Your opponent is giving no inputs

                )

                AND OR

                (

                    * You are executing a fast option (attack or switch)

                    XOR

                    * You are giving no inputs

                )

           )

           XOR

           * You are using a charge attack (bubble minigame)

           XOR

           * Your opponent using a charge attack (option to shield)

           XOR

           * Your pokemon has been KO-ed and you need to choose a new mon

           XOR

           * Your opponents pokemon has been KO-ed and you need to choose a new mon

           XOR

           * START STATE

           XOR

           * END STATE

        """
        if env.state == 'FAST_STATE':
            mon = self.active_mon
            mon.fast_move
            avail_charge_moves = [c for c in mon.charge_moves if (c['energy_delta'] + mon.energy) > 0]
            move_cand = [mon.fast_move] + avail_charge_moves
            # todo: swap?
            move = self.rng.choice(move_cand)

            action = {
                'move': move,
            }
        else:
            action = {}

        return action


def compute_damage(mon1, mon2, move, charge=1.0):
    """
    Compute damage dealt by a move

    Args:
        mon1: (Pokemon): attacker
        mon2: (Pokemon): defender
        move: (dict): move dictionary
        charge: (float): between 0 and 1, if this move is a charge move,
            this is the percent of bubbles popped.

    Example:
        >>> from pypogo.battle import *  # NOQA
        >>> mon1 = Pokemon.random('machamp', moves=['counter', 'cross chop', 'rock slide'], shadow=True).maximize(1500)
        >>> mon2 = Pokemon.random('snorlax', shadow=True).maximize(1500)
        >>> move = mon1.charge_moves[0]
        >>> compute_damage(mon1, mon2, move)
    """
    import math
    move_type = move['type']
    move_power = move['power']

    effectiveness_lut = mon1.api.data['type_effectiveness']
    effectiveness = 1
    for def_type in mon2.typing:
        effectiveness *= effectiveness_lut[move_type][def_type]

    # Attack and defense after taking IVs and level into account
    adjusted_attack = mon1.adjusted['attack']
    adjusted_defense = max(mon2.adjusted['defense'], 1e-5)

    stab = 1.2 if (move_type in mon1.typing) else 1.0

    num_buffs = 0
    num_debuffs = 0

    bonus_multiplier = 1.3  # Hard coded in game, See [3].

    # Buff factors can be [1, 1.25, 1.5, 1.75, 2.0]
    # Buff factors can be [1, 0.8, 0.66, 0.57, 0.5]
    buf_factor = 1 + (num_buffs / 4)
    debuf_factor = 1 / (1 + (num_debuffs / 4))

    attack_shadow_factor = 1.2 if mon1.shadow else 1.0
    defendse_shadow_factor = (1 / 1.2) if mon2.shadow else 1.0

    attack_power = (
        bonus_multiplier *
        charge *
        stab *
        adjusted_attack *
        buf_factor *
        attack_shadow_factor *
        effectiveness
    )

    defense_power = (
        adjusted_defense *
        debuf_factor *
        defendse_shadow_factor
    )

    half = 0.5  # not sure why a half is in the formula

    damage = math.floor(half * move_power * attack_power / defense_power) + 1

    return damage
