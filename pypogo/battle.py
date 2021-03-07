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

    def run_step(self):
        """
        from pypogo.battle import *  # NOQA

        while True:
            self = BattleZone.random()
            # print('self = {}'.format(ub.repr2(self, nl=1)))
            self.run_step()
        """
        player1, player2  = self.players

        mon1 = player1.pokemon[0]
        mon2 = player2.pokemon[0]

        env = self
        action1 = player1.choose_action(env)
        action2 = player1.choose_action(env)

        move1 = action1['move']
        move2 = action2['move']

        # action = 'fast_move'
        # if action == 'fast_move':

        move1 = mon1.fast_move
        move2 = mon2.fast_move

        effects = []
        effect = {
            'desc': f'{mon1.name} used {move1["name"]} against {mon2.name}',
            'damage': compute_damage(mon1, mon2, move1),
            'target': mon2,
        }
        effects.append(effect)
        effect = {
            'desc': f'{mon2.name} used {move2["name"]} against {mon1.name}',
            'damage': compute_damage(mon2, mon1, move2),
            'target': mon1,
        }
        effects.append(effect)

        for effect in effects:
            print('resolve effect = {}'.format(ub.repr2(effect, nl=1)))


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
            mon.feinted = False
            mon.energy = False
            mon.active = False

        self.active_mon = self.pokemon[0]
        self.active_mon.active = True

    def choose_action(self, env):
        """
        env = BattleZone.random()
        self = env.players[0]
        self.initialize()
        """
        mon = self.active_mon
        mon.fast_move
        avail_charge_moves = [c for c in mon.charged_moves if (c['energy_delta'] + mon.energy) > 0]
        move_cand = [mon.fast_move] + avail_charge_moves
        # todo: swap?
        move = self.rng.choices(move_cand)

        action = {
            'move': move,
        }
        return action


def compute_damage(mon1, mon2, move):
    attack_type = move['type']
    defender_types = mon2.typing
    lut = mon1.api.data['type_effectiveness']
    effectiveness = 1
    for def_type in defender_types:
        effectiveness *= lut[attack_type][def_type]

    # Todo calculate correctly
    attack_buf_factor = 1.0
    defense_debuf_factor = 1.0

    attack_power = mon1.adjusted['attack'] * attack_buf_factor
    defense_power = max(mon2.adjusted['defense'], 0.0001) / defense_debuf_factor

    damage = move['power'] * attack_power / defense_power

    damage = damage * effectiveness

    if mon1.shadow:
        damage = damage * 1.2

    if mon2.shadow:
        damage = damage * 1.2

    return damage
