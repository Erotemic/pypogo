"""
The PVPoke implementation of battle logic can be found in [1]_.

References:
    .. [1] https://github.com/pvpoke/pvpoke/blob/master/src/js/battle/Battle.js
    .. [2] https://gamepress.gg/pokemongo/damage-mechanics
    .. [3] https://gamepress.gg/pokemongo/evaluating-stat-boosts-and-rng
    .. [3] https://pokemongohub.net/post/pvp/comprehensive-pvp-mechanics-guide-in-pokemon-go/


    .. [4] https://en.wikipedia.org/wiki/Reinforcement_learning
    .. [4] https://en.wikipedia.org/wiki/Deep_reinforcement_learning


Basic components of Reinforcement Learning:
    * An environment: E, with a state and space-time grid
    * A set set of actors: {A_i}, each with a state
    * Each actor A has a policy A.P.
    * At each timestep each actor makes a decision based on its policy
    * Actions modify the state of the environment and other actors
    * Changes in state may generate a reward R
    * Rewards R may be used to compute gradient wrt actor decision functions

"""
from pypogo.pokemon import Pokemon
from pypogo.utils import PriorityQueue  # NOQA
from pypogo.utils import PriorityData  # NOQA
import ubelt as ub
import random
import sortedcontainers


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


class PriorityList(ub.NiceRepr):
    """
    Holds actions with a turn duration until they are finished

    CommandLine:
        xdoctest -m pypogo.battle PriorityList

    Example:
        >>> from pypogo.battle import *  # NOQA
        >>> q = self = PriorityList()
        >>> q.add({'meta': 3}, priority=3)
        >>> q.add({'meta': 5}, priority=5)
        >>> print('q = {!r}'.format(q))
        >>> for i in range(8):
        >>>     print('-----')
        >>>     print('q = {!r}'.format(q))
        >>>     ready = q.pop_ready()
        >>>     print('pop ready = {!r}'.format(ready))
        >>>     print('q = {!r}'.format(q))
        >>>     q.step()
    """
    def __init__(self):
        import itertools as it
        self._items = sortedcontainers.SortedListWithKey(key=lambda x: x[0])
        # self._items = PriorityQueue()
        self._nextid = it.count(0)

    def __nice__(self):
        return ub.repr2(list(self._items), nl=1)

    def add(self, action, priority=0):
        self._items.add([priority, action])

    def peek(self):
        priority0, item0 = self._items[0]
        return item0

    def pop_ready(self):
        """
        Return all actions where the turn duration is at zero.
        """
        if not len(self._items):
            return None
        priority0, item0 = self._items[0]
        if priority0 <= 0:
            return self.pop_next()

    def pop_next(self):
        """
        Return all actions where the turn duration is at zero.
        """
        if not len(self._items):
            return None

        priority0, item0 = self._items[0]
        idx = -1
        top_level = []
        for idx, (priority, item) in enumerate(self._items):
            if priority0 != priority:
                top_level.append(item)
                break
        idx += 1
        if idx == 0:
            return []

        # pop
        cls = self._items.__class__
        key = self._items.key
        removed = self._items[0:idx]
        remain = cls(self._items[idx:], key=key)
        top_level = [item for _, item in removed]
        self._items = remain
        return top_level

    def step(self):
        # Hack, but it works
        for item in self._items:
            item[0] -= 1


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
        self.action_queue = PriorityList()
        self.effect_queue = PriorityList()
        self.timeline = []
        self.clock = 0
        self.tic_delta = 500 / 500
        self.time_limit = 240000 / 500
        self.verbose = 1
        self.blocked = set()

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
        CommandLine:
            xdoctest -m pypogo.battle BattleZone.run

        Example:
            >>> # xdoctest: +SKIP
            >>> from pypogo.battle import *  # NOQA
            >>> self = BattleZone.random()
            >>> mon1 = self.players[0].pokemon[0] = Pokemon.random('articuno', moves=['Ice Shard', 'Icy Wind', 'Hurricane']).maximize(2500)
            >>> mon2 = self.players[1].pokemon[0] = Pokemon.random('snorlax', moves=['lick', 'super_power']).maximize(2500)
            >>> self.initialize()
            >>> self.verbose = 1
            >>> self.time_limit = 20000 / 500
            >>> self.run(verbose=1)
            >>> print('self.timeline = {}'.format(ub.repr2(self.timeline, nl=1)))
        """
        self.verbose = verbose
        events = self.initialize()
        for event in events:
            self.log_event(event)

        ongoing = True
        while ongoing:
            events = self.step()
            # for event in events:
            #     self.log_event(event)
            if self.clock >= self.time_limit:
                self.log_event({'desc': 'times up', 'clock': self.clock})
                ongoing = False

    def log_event(self, event):
        if self.verbose:
            # try:
            #     print(event['desc'])
            # except Exception:
            print('{}'.format(ub.repr2(event, nl=0)))
        self.timeline.append(event)

    def step(self):
        """
        CommandLine:
            xdoctest -m pypogo.battle BattleZone.step

        Example:
            >>> from pypogo.battle import *  # NOQA
            >>> self = BattleZone.random()
            >>> mon1 = self.players[0].pokemon[0] = Pokemon.random('articuno', moves=['Ice Shard', 'Icy Wind', 'Hurricane']).maximize(2500)
            >>> mon2 = self.players[1].pokemon[0] = Pokemon.random('snorlax', moves=['lick', 'super_power']).maximize(2500)
            >>> self.initialize()
            >>> print('self.action_queue = {!r}'.format(self.action_queue))
            >>> print('---step---')
            >>> print(self.step())
            >>> print('self.action_queue = {!r}'.format(self.action_queue))
            >>> print('---step---')
            >>> print(self.step())
            >>> print('self.action_queue = {!r}'.format(self.action_queue))
            >>> print('---step---')
            >>> print(self.step())
            >>> print('---step---')
            >>> print(self.step())
            >>> print('---step---')
            >>> print(self.step())
            >>> print(self.players[0].pokemon[0].hp)
            >>> print(self.players[1].pokemon[0].hp)
        """

        if self.clock >= self.time_limit:
            return []
            pass

        # At each step, any unblocked player should be able to add an action to
        # the priority queue.

        # Actions in the queue are then resolved in priority order, and then
        # induce a cooldown time that blocks the actor.

        player1, player2  = self.players
        # mon1 = player1.pokemon[0]
        # mon2 = player2.pokemon[0]

        env = self
        action1 = None
        action2 = None
        if player1 not in self.blocked:
            action1 = player1.choose_action(env)
            self.log_event({'desc': 'enqueue action1', 'clock': self.clock})
            self.action_queue.add(action1, priority=action1['countdown'])
            self.blocked.add(player1)

        if player2 not in self.blocked:
            action2 = player2.choose_action(env)
            self.log_event({'desc': 'enqueue action2', 'clock': self.clock})
            self.action_queue.add(action2, priority=action2['countdown'])
            self.blocked.add(player2)

        # Enquing an action for a fast move starts the attack animation

        # self.action_queue.step()
        # self.action_queue.step()
        # self.action_queue.step()

        ready_actions = self.action_queue.pop_ready()

        if ready_actions:
            action_types = {action['type'] for action in ready_actions}

            if 'charge' in action_types:
                pass

            for action in ready_actions:
                attacker = action['user']
                defender = action['opponent'].pokemon[0]
                move = action['move']
                effect = compute_move_effect(attacker, defender, move)
                effect['player'] = action['player']
                effect_priority = 3
                if move['type'] == 'fast':
                    effect_priority = 2
                elif move['type'] == 'charged':
                    effect_priority = 1
                self.effect_queue.add(effect, priority=effect_priority)

        # move1 = action1['move']
        # move2 = action2['move']
        # if move1['move_type'] == 'fast' and move2['move_type'] == 'fast':
        #     pass

        resolved = []
        while self.effect_queue:
            effects = self.effect_queue.pop_next()
            if effects is None:
                break
            # Check for effects fizzled in previou priority step
            for effect in effects:
                if effect['player'] in self.blocked:
                    self.blocked.remove(effect['player'])
                    # self.log_event({'desc': 'remove block', 'clock': self.clock, 'time_limit': self.time_limit})

                if effect['attacker'].hp <= 0:
                    effect['fizzled'] = True

            for effect in effects:
                if not effect.get('fizzled', False):
                    effect['target'].hp -= effect['damage']
                    effect['attacker'].energy += effect['energy_delta']
                    for mod in effect['modifiers']:
                        stat = mod['stat']
                        max_stat_delta = 4
                        v = mod['target'].modifiers[stat] + mod['delta']
                        v = max(-max_stat_delta, min(max_stat_delta, v))
                        mod['target'].modifiers[stat] = v
                    resolved.append(effect)
                    self.log_event({'desc': 'resolved effect: {}'.format(effect['desc']), 'clock': self.clock})
                    self.log_event({'desc': 'new hp: {}'.format(effect['target'].hp)})
                    if effect['target'].hp <= 0:
                        self.log_event({'desc': 'FEINT!'})
                        # TODO: add feint to the priority queue and handle it

                        raise NotImplementedError
                    # self.log_event(effect)

        # Need to figure out the right quing system
        # action = 'fast_move'
        # if action == 'fast_move':

        self.action_queue.step()
        self.clock += self.tic_delta
        return resolved


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
        return f'shields={self.shields}'

    @classmethod
    def random(cls):
        pokemon = []
        while len(pokemon) < 3:
            try:
                mon = Pokemon.random(level=1).maximize(1500)
            except Exception:
                # Some mon will break beause they arent allowed in pvp
                # Just roll until we get a good one
                continue
            # Cant use the same one twice
            if mon.name in [p.name for p in pokemon]:
                continue
            pokemon.append(mon)
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
        self.active_mon.modifiers['attack'] = 0
        self.active_mon.modifiers['defense'] = 0
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
            opponent = None
            for other in  env.players:
                if other is not self:
                    opponent = other

            mon = self.active_mon
            mon.pvp_fast_move
            avail_charge_moves = [c for c in mon.pvp_charge_moves if (c['energy_delta'] + mon.energy) > 0]
            move_cand = [mon.pvp_fast_move] + avail_charge_moves
            # todo: swap?
            move = self.rng.choice(move_cand)

            action = {
                'player': self,
                'opponent': opponent,
                'move': move,
                'type': move['move_type'],
                'user': self.pokemon[0],
                'countdown': move['turn_duration'],
            }
        else:
            action = {}

        return action


def compute_move_effect(mon1, mon2, move, charge=1.0, rng=None):
    """
    Compute damage and other effects caused by a move

    Args:
        mon1: (Pokemon): attacker
        mon2: (Pokemon): defender
        move: (dict): move dictionary
        charge: (float): between 0 and 1, if this move is a charge move,
            this is the percent of bubbles popped.
        rng (RandomState):

    Example:
        >>> from pypogo.battle import *  # NOQA
        >>> mon1 = Pokemon.random('machamp', moves=['counter', 'cross chop', 'rock slide'], shadow=True).maximize(1500)
        >>> mon1 = Pokemon.random('articuno', moves=['Ice Shard', 'Icy Wind', 'Hurricane'], shadow=True).maximize(1500)
        >>> mon2 = Pokemon.random('snorlax', moves=['lick', 'super_power'], shadow=True).maximize(1500)
        >>> mon2 = Pokemon.random('magikarp', shadow=True).maximize(1500)
        >>> move = mon1.pvp_charge_moves[0]
        >>> effect = compute_move_effect(mon1, mon2, move)
        >>> print('effect = {}'.format(ub.repr2(effect, nl=2)))
        >>> move = mon2.pvp_charge_moves[0]
        >>> effect = compute_move_effect(mon2, mon1, move)
        >>> print('effect = {}'.format(ub.repr2(effect, nl=2)))
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

    def modifier_factor(delta):
        if delta > 0:
            return 1 + (delta / 4)
        else:
            return 1 / (1 + (-delta / 4))

    attack_modifier_factor = modifier_factor(mon1.modifiers['attack'])
    defense_modifier_factor = modifier_factor(mon2.modifiers['defense'])

    attack_shadow_factor = 1.2 if mon1.shadow else 1.0
    defense_shadow_factor = (1 / 1.2) if mon2.shadow else 1.0

    pvp_bonus_multiplier = 1.3  # Hard coded in game, See [3].
    attack_power = (
        pvp_bonus_multiplier *
        charge *
        stab *
        adjusted_attack *
        attack_modifier_factor *
        attack_shadow_factor *
        effectiveness
    )

    defense_power = (
        adjusted_defense *
        defense_modifier_factor *
        defense_shadow_factor
    )

    half = 0.5  # not sure why a half is in the formula

    damage = math.floor(half * move_power * attack_power / defense_power) + 1

    if rng is None:
        rng = random.Random()

    # Determine if any buffs / debuffs occur
    buffs = move.get('buffs', None)
    modifiers = []
    if buffs is not None:
        chance = move['buffs']['activation_chance']
        if chance == 1 or chance > rng.random():
            attacker_att_delta = buffs.get('attacker_attack_stat_stage_change', 0)
            attacker_def_delta = buffs.get('attacker_defense_stat_stage_change', 0)
            target_att_delta = buffs.get('target_attack_stat_stage_change', 0)
            target_def_delta = buffs.get('target_defense_stat_stage_change', 0)
            if attacker_att_delta != 0:
                modifiers.append({
                    'target': mon1,
                    'stat': 'attack',
                    'delta': attacker_att_delta,
                })
            if attacker_def_delta != 0:
                modifiers.append({
                    'target': mon1,
                    'stat': 'defense',
                    'delta': attacker_def_delta,
                })
            if target_att_delta != 0:
                modifiers.append({
                    'target': mon2,
                    'stat': 'attack',
                    'delta': target_att_delta,
                })
            if target_def_delta != 0:
                modifiers.append({
                    'target': mon2,
                    'stat': 'defense',
                    'delta': target_def_delta,
                })

    # Buff factors can be [1, 1.25, 1.5, 1.75, 2.0]
    # DeBuff factors can be [1, 0.8, 0.66, 0.57, 0.5]
    # This formula might make more sense, but its not what it is.
    # 2 ** np.linspace(-1, 1, 9)
    # np.logspace(-1, 1, 9, base=2)
    # Is there a natural way to express?
    # I don't think so, the right half is linear and the left half is
    # non-linear.
    if 0:
        import kwplot
        import numpy as np
        plt = kwplot.autoplt()
        from scipy.optimize import curve_fit
        x = np.array([-4, -3, -2, -1, 0, 1, 2, 3, 4])
        y = np.array([0.5,  0.57, 0.66, 0.8, 1, 1.25, 1.5, 1.75, 2.0])
        def func(x, c0, c1, c2, c3, c4):
            return (
                c4 * x ** 4 +
                c3 * x ** 3 +
                c2 * x ** 2 +
                c1 * x ** 1 +
                c0 * x ** 0 +
                # b1 ** (x * e1)
                0
            )

        left_y = 1 / (1 + (-x / 4))
        right_y = 1 + (x / 4)

        popt, pcov = curve_fit(func, x, y)

        y_nat = 2. ** (np.array(x) / 4)

        plt.clf()
        plt.plot(x, y, 'b-o', label='real')
        plt.plot(x, y_nat, 'r-o', label='natural')
        plt.plot(x, np.abs(y - y_nat), 'r-o', label='nat_abs_delta')
        plt.plot(x, left_y, '--', label='left-y')
        plt.plot(x, right_y, '--', label='right-y')

        x_hat = np.linspace(x[0], x[-1], 100)
        y_hat = func(x_hat, *popt)

        plt.plot(x_hat, y_hat, 'g--', label='fit')
        plt.legend()

    effect = {
        'desc': f'{mon1.name!r}  (hp={mon1.hp}, energy={mon1.energy}) used {move["name"]!r} against {mon2.name!r} (hp={mon2.hp}, energy={mon2.energy})',
        'attacker': mon1,
        'target': mon2,
        'damage': damage,
        'stab': stab,
        'pvp_bonus_multiplier': pvp_bonus_multiplier,
        'adjusted_attack': adjusted_attack,
        'attack_shadow_factor': attack_shadow_factor,
        'effectiveness': effectiveness,
        'adjusted_defense': adjusted_defense,
        'defense_modifier_factor': defense_modifier_factor,
        'attack_modifier_factor': attack_modifier_factor,
        'defense_shadow_factor': defense_shadow_factor,
        'attack_power': attack_power,
        'defense_power': defense_power,
        'energy_delta': move['energy_delta'],
        'turn_duration': move['turn_duration'],
        'modifiers': modifiers,
    }
    return effect
