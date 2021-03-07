from pypogo.pokemon import Pokemon
import ubelt as ub


class Environment(ub.NiceRepr):
    """
    Has a space-time grid.
    """
    def __init__(self):
        self.actors = []
        self.properties = {}
        self.clock = None
        self.current_timestep = None


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
        self = BattleZone.random()
        """
        player1, player2  = self.players

        mon1 = player1.pokemon[0]
        mon2 = player2.pokemon[0]

        # action1 = player1.choose_action
        # action2 = player1.choose_action

        action = 'fast_move'
        if action == 'fast_move':
            move1 = mon1.fast_move

        def compute_damage(mon1, mon2, move):
            damage = (move['power'] * mon1.adjusted['attack']) / mon2.adjusted['defense']
            return damage

        # move = mon1.fast_move
        damage = compute_damage(mon1, mon2, move1)

        effect = {
            'damage': damage,
        }

        print('effect = {}'.format(ub.repr2(effect, nl=1)))


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
