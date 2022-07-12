"""
Defines the class that represents a pokemon as well as operations that can be
applied on that pokemon. More functionality will be added over time.

TODO:
    - [ ] Implement ranges for unknown properties
"""
import re
import ubelt as ub
import itertools as it
import numpy as np
import pandas as pd
import networkx as nx
from pypogo.pogo_api import global_api


class Pokemon(ub.NiceRepr):
    """
    An object to represent a Pokemon and all of its attributes.

    xdoctest ~/code/pypogo/pypogo/pokemon.py

    Example:
        >>> import pypogo
        >>> import ubelt as ub
        >>> mon = pypogo.Pokemon.random('mew', moves=['wild charge'], rng=43903).maximize(max_cp=1500)
        >>> print('mon = {!r}'.format(mon))
        >>> _ = mon.league_ranking(verbose=1)
        >>> # xdoctest: +IGNORE_WANT
        >>> print('mon.fast_move = {}'.format(ub.repr2(mon.fast_move['pvp'], nl=2)))
        >>> print('mon.charge_moves = {}'.format(ub.repr2(mon.charge_moves['pvp'], nl=3)))
        Leage 1500 Rankings
        self = <Pokemon(mew, 1476, 16.5, [15, 4, 7], ['wild charge', 'Rock Smash']) at ...
           iva  ivd  ivs    rank  level      cp  stat_product_k      attack     defense  stamina    percent name
        0   15    4    7  3815.0   16.5  1476.0      1772.24242  122.093046  116.124053    125.0  22.481043  mew
        mon.fast_move = {
            'energy_delta': 7,
            'move_env': 'pvp',
            'move_id': 241,
            'move_type': 'fast',
            'name': 'Rock Smash',
            'power': 9,
            'turn_duration': 3,
            'type': 'Fighting',
        }
        mon.charge_moves = [
            {
                'buffs': {
                    'activation_chance': 1.0,
                    'attacker_defense_stat_stage_change': -2,
                },
                'energy_delta': -45,
                'move_env': 'pvp',
                'move_id': 251,
                'move_type': 'charge',
                'name': 'Wild Charge',
                'power': 100,
                'turn_duration': 1,
                'type': 'Electric',
            },
        ]


    Example:
        >>> from pypogo.pokemon import *  # NOQA
        >>> self = Pokemon('weedle', level=20, ivs=(0, 1, 10))
        >>> print('self = {}'.format(self))
        self = <Pokemon(weedle, 183, 20, (0, 1, 10), None)>
        >>> family = sorted(self.family(), key=lambda p: p.name)
        >>> print('family = {}'.format(ub.repr2(family, nl=1, si=1, sort=False)))
        family = [
            <Pokemon(beedrill, 907, 20, (0, 1, 10), None)>,
            <Pokemon(kakuna, 168, 20, (0, 1, 10), None)>,
        ]

        >>> Pokemon('castform_snowy', ivs=[0, 0, 0], level=30).populate_stats()
    """
    def __init__(self, name, ivs=None, level=None, moves=None, shadow=False,
                 form=None, cp=None, autobuild=True, shiny=False,
                 adjusted=None, purified=False, hints=''):

        self.api = global_api()
        self.hints = hints

        name, form = self.api.normalize_name_and_form(name, form, hints=hints)

        self.name = name.lower()
        self.level = level
        self.ivs = ivs
        self.moves = moves
        self.shadow = shadow
        self.purified = purified  # or form.lower() == 'purified'
        self.shiny = shiny

        # if shadow:
        #     # form = 'Shadow'
        #     pass

        self.form = form
        self.cp = cp
        self.adjusted = adjusted

        # PVP attributes
        self.hp = None
        self.energy = None
        self.modifiers = {
            'attack': 0,
            'defense': 0,
        }

        self.populate_stats()

        if cp is None:
            if level is not None and self.ivs is not None:
                if autobuild:
                    self.populate_cp()
        else:
            # If CP is specified, get the one that is closest
            # TODO: handle unknown ivs
            if level is None and self.ivs is not None:
                self.populate_level()

    def slug(self):
        """
        Get slug text suitable for hashing

        Example:
            import pypogo
            self = pypogo.Pokemon.random()
            print(self.slug())

        """
        parts = ub.sorted_keys(ub.dict_diff(self.__json__(), ['adjusted']))
        slug = ub.repr2(parts, compact=1).lower().replace(' ', '')
        return slug

    def init_pvp_state(self):
        self.hp = int(self.adjusted['stamina'])
        self.energy = 0
        self.reset_modifiers()
        return self

    def reset_modifiers(self):
        self.modifiers['defense'] = 0
        self.modifiers['attack'] = 0

    def __json__(self):
        return {
            'name': self.name,
            'ivs': self.ivs,
            'level': self.level,
            'form': self.form,
            'shadow': self.shadow,
            'shiny': self.shiny,
            'moves': self.moves,
            # Depends on other properties
            'cp': self.cp,
            'adjusted': self.adjusted,
        }

    def copy(self, **overwrite):
        """
        Create a copy of this pokemon with possibly different attributes
        """
        kw = self.__json__()
        # Invalidate depenencies
        if 'ivs' in overwrite:
            if overwrite['ivs'] != kw['ivs']:
                kw.pop('cp', None)
                kw.pop('adjusted', None)

        if 'level' in overwrite:
            if overwrite['level'] != kw['level']:
                kw.pop('cp', None)
                kw.pop('adjusted', None)

        if 'cp' in overwrite:
            if overwrite['cp'] != kw['cp']:
                kw.pop('level', None)

        kw.update(overwrite)
        new = Pokemon(**kw)
        return new

    @property
    def typing(self):
        return tuple(sorted(self.info['type'] ))

    def display_name(self):

        use_emoji = True
        if use_emoji:
            glpyhs = {
                'shadow': '😈',
                'purified': '👼',
                'shiny': '✨',
            }
        else:
            glpyhs = {
                'shadow': 'shadow',
                'purified': 'purified',
                'shiny': 'shiny',
            }

        aux_parts = []
        if self.shadow:
            shadow_glyph = glpyhs['shadow']
            aux_parts.append(shadow_glyph)

        elif self.form not in {'Normal', 'Shadow', 'Purified'}:
            aux_parts.append('{}'.format(self.form))

        if self.purified:
            purified_glyph = glpyhs['purified']
            aux_parts.append(purified_glyph)

        if self.shiny:
            shiny_glpyh = glpyhs['shiny']
            aux_parts.append(shiny_glpyh)
        if aux_parts:
            disp_name = self.name + '(' + ','.join(aux_parts) + ')'
        else:
            disp_name = self.name
        return disp_name

    def __nice__(self):
        disp_name = self.display_name()
        if self.hp is not None:
            # display for PVP
            info = '{}, {}, {}, {}, {}, {}, {}'.format(disp_name, self.hp,
                                                       self.energy, self.cp,
                                                       self.level, self.ivs,
                                                       self.moves)
        else:
            info = '{}, {}, {}, {}, {}'.format(disp_name, self.cp, self.level,
                                               self.ivs, self.moves)
        return info
        # return str([self.name] + self.moves + [self.level] + self.ivs)

    def lookup_moves(self):
        possible_moves = self.api.name_to_moves[self.name]
        return possible_moves

    def populate_all(self):
        if self.ivs is None or self.level is None:
            raise Exception('must have level and ivs to populate all')
        self.populate_cp()
        self.populate_stats()
        self.populate_move_stats()

    def populate_level(self, max_level=51):
        """ Try and find the level given the info """
        # hacky, could be more elegant
        target_cp = self.cp
        iva, ivd, ivs = self.ivs
        attack = self.info['base_attack'] + iva
        defense = self.info['base_defense'] + ivd
        stamina = self.info['base_stamina'] + ivs

        found_level = None

        for cand_level in np.arange(1, max_level + 0.5, 0.5):
            # TODO: could binary search
            cp, adjusted = calc_cp(attack, defense, stamina, cand_level)
            if cp == target_cp:
                found_level = cand_level
            elif cp > target_cp:
                break

        if found_level is None:
            raise Exception('cp does not match ivs')
        else:
            self.level = found_level
        return self

    def populate_stats(self):
        """
        Example:
            >>> # TODO: handle castform cases.
            >>> from pypogo.pokemon import *  # NOQA
            >>> Pokemon('castform', form='snowy', ivs=[0, 0, 0], level=30).populate_stats()
            >>> Pokemon('castform_snowy', ivs=[0, 0, 0], level=30).populate_stats()
        """
        info = self.api.get_pokemon_info(name=self.name, form=self.form)
        self.learnable = self.api.learnable[self.name]
        self.info = info
        # self.items = items
        return self

    def populate_cp(self):
        level = self.level
        iva, ivd, ivs = self.ivs
        attack = self.info['base_attack'] + iva
        defense = self.info['base_defense'] + ivd
        stamina = self.info['base_stamina'] + ivs
        cp, adjusted = calc_cp(attack, defense, stamina, level)
        self.cp = cp
        self.adjusted = adjusted
        return self

    def evolved(self):
        """
        Ignore:
            self = Pokemon('gastly', ivs=[6, 13, 15], cp=400)
            self.evolved()

            self = Pokemon('eevee', ivs=[6, 13, 15], cp=400)
            self.evolved()

            self = Pokemon('mew', ivs=[6, 13, 15], cp=400)
            self.evolved()
        """
        possibilities = []
        for other in self.family(onlyadj=True):
            # other.populate_cp()
            possibilities.append(other)
        return possibilities

    def purify(self):
        """
        Example:
            >>> # xdoctest: +IGNORE_WANT
            >>> from pypogo.pokemon import *  # NOQA
            >>> self = Pokemon('ralts', ivs=[6, 13, 15], level=20,
            >>>                 shadow=True, shiny=True)
            >>> new = self.purify()
            >>> print('self = {}'.format(self))
            >>> print('new  = {}'.format(new))
            >>> evos = new.evolved()[0].evolved()
            >>> print(evos[0])
            >>> print(evos[1])
            self = <Pokemon(ralts(😈,✨), 274, 20, [6, 13, 15], None)>
            new  = <Pokemon(ralts(👼,✨), 285, 20, (8, 15, 15), None)>
            <Pokemon(gallade(👼,✨), 1718, 20, (8, 15, 15), None)>
            <Pokemon(gardevoir(👼,✨), 1718, 20, (8, 15, 15), None)>

        """
        if not self.shadow:
            raise Exception('Only can purify shadow pokemon')

        overwrite = {}
        if self.ivs is not None:
            new_ivs = tuple([min(15, s + 2) for s in self.ivs])
            overwrite['ivs'] = new_ivs
        # overwrite['form'] = 'Purified'
        overwrite['purified'] = True
        overwrite['shadow'] = False
        # TODO: replace frustration with return
        new = self.copy(**overwrite)
        return new

    def alternate_forms(self):
        """
        Example:
            >>> self = Pokemon('darmanitan')
            >>> print(list(self.alternate_forms()))

            >>> self = Pokemon('giratina')
            >>> print(list(self.alternate_forms()))

            >>> self = Pokemon('castform')
            >>> print(list(self.alternate_forms()))
        """
        forms = []
        for info in self.api.name_to_stats[self.name]:
            forms.append(info['form'])

        for form in forms:
            other = Pokemon(self.name, form=form)
            yield other

    @property
    def can_evolve(self):
        # TODO: check form restriction
        # Our form has to match one of the valid forms to evolve.
        flag = len(self.api.evo_graph.succ[self.name]) > 0
        if flag:
            matches_form = False
            for info in self.api.name_to_evolutions[self.name]:
                if info['form'] == self.form:
                    matches_form = True
            return matches_form
        return False

    @property
    def is_evolved(self):
        # Are pokemon like AWak AChu evolved?
        return len(self.api.evo_graph.pred[self.name]) > 0

    def evolution_stage(self):
        # TODO: check form restriction
        # Our form has to match one of the valid forms to evolve.
        name = self.name
        stage = 0
        prev = self.api.evo_graph.pred[name]
        while prev:
            name = prev[0]
            stage += 1
            prev = self.api.evo_graph.pred[name]
        return stage

    def family(self, ancestors=True, node=False, onlyadj=False):
        """
        Get other members of this pokemon family

        Yields:
            Pokemon: other members of this family

        Ignore:
            >>> self = Pokemon('gengar', ivs=[6, 13, 15])
            >>> list(self.family())

            >>> self = Pokemon('eevee', ivs=[6, 13, 15])
            >>> list(self.family(onlyadj=True))

            >>> self = Pokemon('ralts', ivs=[6, 13, 15], shadow=True)
            >>> list(self.family())
        """
        blocklist = set()
        if not node:
            blocklist.add(self.name)

        if not ancestors:
            toadd = set(nx.ancestors(self.api.evo_graph, self.name))
            blocklist.update(toadd)

        cc = self.api.name_to_family[self.name]
        if onlyadj:
            keeplist = set(self.api.evo_graph.adj[self.name])
            blocklist = set(cc) - keeplist

        kw = {
            'level': self.level,
            'form': self.form,
            'ivs': self.ivs,
            'shadow': self.shadow,
            'purified': self.purified,
            'shiny': self.shiny,
        }
        for name in sorted(cc):
            if name not in blocklist:
                if name == self.name:
                    other = Pokemon(name, cp=self.cp, **kw)
                else:
                    other = Pokemon(name, **kw)
                yield other

                if other.shadow:
                    yield other.purify()

    def check_evolution_cps(self, max_cp=1500, max_level=51):
        """
        self = Pokemon('gastly', ivs=[6, 13, 15])
        self.check_evolution_cps()

        self = Pokemon('gyarados', ivs=[6, 13, 15])
        self.check_evolution_cps()

        self = Pokemon('magikarp', ivs=[6, 13, 15])
        self.check_evolution_cps()
        """
        evos = list(self.family(ancestors=False))

        if len(evos) == 0:
            print('no evolutions available')

        for evo in evos:
            other = evo

            best_level = None
            for level in list(np.arange(1, max_level + 0.5, 0.5)):
                # TODO: could binary search
                other.level = level
                other.populate_cp()
                if other.cp <= max_cp:
                    best_level = level
                else:
                    break
            other.level = best_level
            other.populate_cp()

            print('To achieve other = {!r}'.format(other))
            self.level = best_level
            self.populate_cp()
            print('self = {!r}'.format(self))
            print('Pokemon CP must be less than this to be used in league')

    @property
    def stat_product(self):
        product = (self.adjusted['attack'] * self.adjusted['stamina'] * self.adjusted['defense'])
        return product

    @property
    def stat_product_k(self):
        """
        In other websites stat product is usually divided by 1000
        """
        product = self.stat_product / 1000
        return product

    @property
    def base_stats(self):
        base_stats = {
            'attack': self.info['base_attack'],
            'defense': self.info['base_defense'],
            'stamina': self.info['base_stamina'],
        }
        return base_stats

    def league_ranking(self, max_cp=1500, max_level=51, min_iv=0, have_ivs=None, verbose=0, force=False):
        """
        Given a set of IVs for this pokemon compute the league rankings

        Example:

            # When does a potential good XL medicham become better than non XL?

            z = Pokemon('machamp', [1, 15, 6]).maximize(1500)
            z.populate_cp()
            z.stat_product_k
            print('z = {!r}'.format(z))
            print('z.stat_product_k = {!r}'.format(z.stat_product_k))

            self = Pokemon('medicham', ivs=[7, 15, 14], cp=1368)
            self.populate_cp()
            print('self = {!r}'.format(self))
            self.adjusted
            print('self.adjusted = {!r}'.format(self.adjusted))
            stat_product_k = self.stat_product_k
            print('stat_product_k = {!r}'.format(stat_product_k))

            m3 = Pokemon('medicham', ivs=[7, 15, 14], cp=1377)
            m3.populate_cp()
            print('m3 = {!r}'.format(m3))
            m3.adjusted
            print('m3.adjusted = {!r}'.format(m3.adjusted))
            stat_product_k = m3.stat_product_k
            print('stat_product_k = {!r}'.format(stat_product_k))

            n = self.copy()
            n.level += 0.5 * 4
            n.cp = None
            n.populate_cp()
            print('n = {!r}'.format(n))
            print('n.adjusted = {!r}'.format(n.adjusted))
            stat_product1 = n.stat_product_k
            print('stat_product1 = {!r}'.format(stat_product1))

            y = self.copy().maximize(max_cp=1400, max_level=51)
            print('y = {!r}'.format(y))
            y.level += 0.5
            y.cp = None
            y.populate_cp()
            print('y.adjusted = {!r}'.format(y.adjusted))
            stat_product1 = y.stat_product_k
            print('stat_product1 = {!r}'.format(stat_product1))

            x = Pokemon('medicham', ivs=[13, 13, 13]).maximize(max_cp=1500, max_level=40)
            n.populate_cp()
            print('x = {!r}'.format(x))
            stat_product2 = x.stat_product_k
            print('x.adjusted = {!r}'.format(x.adjusted))
            print('stat_product2 = {!r}'.format(stat_product2))


        """
        if have_ivs is None:
            have_ivs = [self.ivs]

        league_df = self.league_ranking_table(max_cp=max_cp,
                                              max_level=max_level,
                                              min_iv=min_iv)
        league_df = league_df.set_index(['iva', 'ivd', 'ivs'])

        if abs(min(league_df['cp'].max() - min(3000, max_cp), 0)) > 200:
            if verbose:
                print('Out of this league {}'.format(max_cp))

        rows = []
        for haves in have_ivs:

            if isinstance(haves, Pokemon) or type(haves).__name__ == 'Pokemon':
                pkmn = haves
                ivs = pkmn.ivs
                name = pkmn.display_name()
            else:
                ivs = haves
                name = self.name

            ivs = tuple(ivs)
            # ultra_row = ultra_df.loc[haves]
            league_row = league_df.loc[ivs]
            rows.append({
                'iva': ivs[0],
                'ivd': ivs[1],
                'ivs': ivs[2],
                'rank': league_row['rank'],
                'level': league_row['level'],
                'cp': league_row['cp'],
                'stat_product_k': league_row['stat_product_k'],
                'attack': league_row['attack'],
                'defense': league_row['defense'],
                'stamina': league_row['stamina'],
                'percent': league_row['percent'],
                'name': name,
            })
        rankings = pd.DataFrame.from_dict(rows)
        #
        if verbose:
            print('')
            print('Leage {} Rankings'.format(max_cp))
            print('self = {!r}'.format(self))
            print(rankings.sort_values('rank'))
        return rankings

    def level_up(self, num_times=1):
        """
        Num times is the number of times you press the level up button. So its
        really the number of "half levels".
        """
        new_level = self.level + num_times * 0.5
        if new_level > self.api.LEVEL_CAP:
            raise ValueError('Cannot level past cap')
        self.level = new_level
        self.populate_cp()
        return self

    def maximize(self, max_cp=1500, max_level=50, ivs='auto'):
        """
        Choose level that maximizes CP subject to constraints.

        Args:
            max_cp (int): Maximum CP for target league
            max_level (int): Usually 40, 41, 50, or 51.
            ivs (str):
                if "keep", keep existing ivs.
                if "maximize", find the best ivs.
                if "auto", keep existing ivs, otherwise find the best.

        Example:
            self = Pokemon('dewgong', (15, 8, 15), moves=['ICE_SHARD', 'ICY_WIND', 'WATER_PULSE'])
            self.maximize(max_cp=1500)
        """
        if ivs == 'auto':
            ivs = 'maximize' if self.ivs is None else 'keep'

        max_cp = _coerce_max_cp(max_cp)

        if isinstance(ivs, list):
            self.ivs = ivs
        elif ivs == 'maximize':
            # TODO: could be more efficient
            table = self.league_ranking_table(
                max_cp=max_cp, max_level=max_level)
            row = table.iloc[0]
            self.ivs = [int(row['iva']), int(row['ivd']), int(row['ivs'])]
        elif ivs == 'keep':
            if self.ivs is None:
                raise ValueError('Cannot keep ivs when they are unknown')
        else:
            raise KeyError(ivs)

        assert self.ivs is not None
        iva, ivd, ivs = self.ivs

        attack = self.info['base_attack'] + iva
        defense = self.info['base_defense'] + ivd
        stamina = self.info['base_stamina'] + ivs

        best_level = None
        best_cp = None
        best_adjusted = None
        for level in list(np.arange(1, max_level + 0.5, 0.5)):
            cand_cp, adjusted = calc_cp(attack, defense, stamina, level)
            if cand_cp <= max_cp:
                best_cp = cand_cp
                best_level = level
                best_adjusted = adjusted
            else:
                break

        if best_level is not None:
            self.adjusted = best_adjusted
            self.level = best_level
            self.cp = best_cp

        return self

    def league_ranking_table(self, max_cp=1500, max_level=51, min_iv=0):
        """
        Calculate this Pokemon species' league rankings for all IV
        combinations, based on the adjusted stat product heuristic.

        Ignore:
            >>> self = Pokemon('beedrill')
            >>> beedrill_df = self.league_ranking_table(max_cp=1500)
            >>> print(beedrill_df)
                  iva  ivd  ivs    cp  level      attack     defense  stamina  stat_product_k  rank     percent
            rank
            1       0   13   14  1499   32.5  126.206025  106.789714      132     1779.030702     1  100.000000
            2       0   14   13  1500   32.5  126.206025  107.536495      131     1777.899723     2   99.316671
            3       0   14   15  1496   32.0  125.700414  107.105679      132     1777.146120     3   98.861349
            4       0   15   14  1497   32.0  125.700414  107.849468      131     1775.930690     4   98.126996
            5       1   13   15  1500   32.0  126.444204  106.361889      132     1775.247460     5   97.714193
            ...   ...  ...  ...   ...    ...         ...         ...      ...             ...   ...         ...
            4092   14    2    1  1489   32.0  136.113467   98.180205      121     1617.001419  4092    2.103120
            4093   15    0    2  1490   32.0  136.857256   96.692626      122     1614.436679  4093    0.553523
            4094   15    0    0  1493   32.5  137.407744   97.081558      121     1614.110696  4094    0.356567
            4095   15    1    3  1488   31.5  136.304546   97.042911      122     1613.741564  4095    0.133540
            4096   15    1    1  1492   32.0  136.857256   97.436416      121     1613.520542  4096    0.000000
            ...
            [4096 rows x 11 columns]

        Ignore:
            >>> self = Pokemon('beedrill')
            >>> beedrill_df = self.league_ranking_table(max_cp=1500)

            >>> # Find the best IVs that we have for PVP
            >>> self = Pokemon('empoleon')
            >>> have_ivs = [
            >>>     (0, 10, 14),
            >>>     (1, 11, 5),
            >>>     (1, 5, 7),
            >>>     (1, 9, 13),
            >>>     (2, 15, 13),
            >>>     (2, 2, 10),
            >>>     (2, 6, 9),
            >>>     (3, 13, 11),
            >>>     (3, 3, 2),
            >>>     (4, 13, 13),
            >>>     (5, 13, 14),
            >>>     (4, 14, 14),
            >>>     (7, 13, 3),
            >>>     (13, 14, 14),
            >>>     (15, 14, 14),
            >>> ]

            >>> self = Pokemon('beedrill')
            >>> have_ivs = [
            >>>     (0, 8, 14),
            >>>     (0, 12, 14),
            >>>     (1,  3, 10),
            >>>     (1, 13, 6),
            >>>     (4, 11, 13),
            >>>     (4, 14, 13),
            >>>     (1, 13, 7),
            >>>     (1, 10, 8),
            >>>     (4, 13, 13),
            >>>     (4, 14, 14),
            >>>     (4, 15, 12),
            >>>     (5, 14, 11),
            >>>     (11, 15, 14),
            >>>     (15, 15, 15),
            >>>     (12, 15, 15),
            >>> ]
            >>> self.league_ranking(have_ivs=have_ivs)

            >>> have_ivs = [
            >>>     (4, 13, 10),
            >>>     (5, 11, 14),
            >>>     (4, 13, 11),
            >>>     (6, 13, 15),
            >>>     (7, 12, 13),
            >>>     (7, 14, 14),
            >>>     (7, 15, 15),
            >>>     (7, 2, 9),
            >>>     (10, 15, 11),
            >>>     (15, 15, 15),
            >>>     (7, 15, 15),
            >>> ]
            >>> self = Pokemon('gengar')
            >>> print('self.info = {}'.format(ub.repr2(self.info, nl=2)))
            >>> self.league_ranking(have_ivs=have_ivs)

            >>> self = Pokemon('haunter')
            >>> print('self.info = {}'.format(ub.repr2(self.info, nl=2)))
            >>> self.league_ranking(have_ivs=have_ivs)

            >>> have_ivs = [
            >>>     (12, 11, 14),
            >>>     (12, 15, 15),
            >>>     (15, 15, 15),
            >>> ]
            >>> Pokemon('blaziken').league_ranking(have_ivs=have_ivs, max_cp=1500)
            >>> Pokemon('blaziken').league_ranking(have_ivs=have_ivs, max_cp=2500)
            >>> Pokemon('blaziken').league_ranking(have_ivs=have_ivs, max_cp=np.inf)

            >>> have_ivs = [
            >>>     (0, 2, 14),
            >>>     (4, 2, 13),
            >>>     (11, 13, 12),
            >>>     (4, 13, 9),
            >>>     (15, 12, 13),
            >>>     (13, 14, 13),
            >>>     (13, 14, 13),
            >>>     (14, 14, 10),
            >>>     (6, 15, 11),  # purified
            >>>     (13, 15, 14),  # purified
            >>> ]
            >>> Pokemon('swampert').league_ranking(have_ivs=have_ivs, max_cp=1500)
            >>> Pokemon('swampert').league_ranking(have_ivs=have_ivs, max_cp=2500)
            >>> Pokemon('swampert').league_ranking(have_ivs=have_ivs, max_cp=np.inf)

            >>> have_ivs = [
            >>>     (1, 2, 15),
            >>>     (12, 15, 14),
            >>>     (14, 15, 14),
            >>>     (14, 14, 14),
            >>>     (14, 13, 15),
            >>>     (15, 15, 10),
            >>> ]
            >>> Pokemon('sceptile').league_ranking(have_ivs=have_ivs, max_cp=1500)
            >>> Pokemon('sceptile').league_ranking(have_ivs=have_ivs, max_cp=2500)

            >>> have_ivs = [
            >>>     (14, 14, 15),
            >>>     (10, 14, 15),
            >>>     (15, 15, 15),
            >>>     (15, 15, 15),
            >>> ]
            >>> Pokemon('rhyperior').league_ranking(have_ivs=have_ivs, max_cp=np.inf)

            >>> have_ivs = [
            >>>     (14, 14, 14),
            >>>     (12, 13, 14),
            >>>     (13, 14, 14),
            >>>     (15, 13, 14),
            >>>     (8, 6, 8),
            >>> ]
            >>> Pokemon('vigoroth').league_ranking(have_ivs=have_ivs, max_cp=1500)


            >>> have_ivs = [
            >>>     (6, 15, 13),
            >>>     (3, 4, 14),
            >>>     (2, 9, 15),
            >>>     (6, 14, 15),
            >>>     (7, 15, 15),
            >>>     (10, 15, 15),
            >>> ]
            >>> Pokemon('shiftry').league_ranking(have_ivs=have_ivs, max_cp=1500)
            >>> Pokemon('shiftry').league_ranking(have_ivs=have_ivs, max_cp=2500)

            >>> have_ivs = [
            >>>     (15, 15, 14),
            >>>     (0, 7, 8),
            >>>     (3, 12, 14),
            >>>     (5, 5, 15),
            >>>     (4, 7, 12),
            >>>     (15, 14, 14),
            >>>     (10, 14, 15),
            >>> ]
            >>> Pokemon('alakazam').league_ranking(have_ivs=have_ivs, max_cp=1500)
            >>> Pokemon('alakazam').league_ranking(have_ivs=have_ivs, max_cp=2500)

            >>> have_ivs = [
            >>>     (0, 15, 6),
            >>>     (11, 10, 10),
            >>>     (12, 12, 11),
            >>>     (15, 10, 12),
            >>> ]
            >>> Pokemon('salamence').league_ranking(have_ivs=have_ivs, max_cp=1500)
            >>> Pokemon('salamence').league_ranking(have_ivs=have_ivs, max_cp=2500)
            >>> Pokemon('salamence').league_ranking(have_ivs=have_ivs, max_cp=np.inf)

            >>> have_ivs = [
            >>>     (6, 10, 10),
            >>>     (11, 9, 14),
            >>>     (13, 12, 14),
            >>>     (15, 15, 15),
            >>>     (15, 15, 5),
            >>> ]
            >>> Pokemon('flygon').league_ranking(have_ivs=have_ivs, max_cp=1500)
            >>> Pokemon('flygon').league_ranking(have_ivs=have_ivs, max_cp=2500)
            >>> Pokemon('flygon').league_ranking(have_ivs=have_ivs, max_cp=np.inf)

            >>> have_ivs = [
            >>>     (6, 11, 11),
            >>>     (10, 11, 10),
            >>>     (10, 11, 12),
            >>>     (6, 14, 4),
            >>>     (15, 12, 15),
            >>>     (15, 7, 15),
            >>> ]
            >>> Pokemon('mamoswine').league_ranking(have_ivs=have_ivs, max_cp=1500)
            >>> Pokemon('mamoswine').league_ranking(have_ivs=have_ivs, max_cp=2500)
            >>> Pokemon('mamoswine').league_ranking(have_ivs=have_ivs, max_cp=np.inf)

            >>> pd.options.display.max_rows = 100
            >>> pd.options.display.min_rows = 40
            >>> Pokemon('registeel').league_ranking_table(max_cp=1500, min_iv=10, max_level=40)
            >>> Pokemon('registeel').league_ranking_table(max_cp=2500, min_iv=10, max_level=40)
            >>> have_ivs = [
            >>>     (10, 14, 15),
            >>>     (14, 14, 12),
            >>>     (13, 11, 15),
            >>>     (12, 15, 15),
            >>>     (13, 10, 15),
            >>>     (14, 10, 12),
            >>>     (14, 13, 10),
            >>>     (12, 11, 15),
            >>>     (11, 13, 15),
            >>>     (12, 15, 10),
            >>>     (11, 10, 14),
            >>>     (11, 13, 11),
            >>>     (13, 15, 10),
            >>>     (15, 15, 11),
            >>> ]
            >>> _ = Pokemon('registeel').league_ranking(have_ivs=have_ivs, max_cp=1500, min_iv=10, max_level=51)
            >>> _ = Pokemon('registeel').league_ranking(have_ivs=have_ivs, max_cp=2500, min_iv=10, max_level=51)

        """
        base_attack = self.info['base_attack']
        base_defense = self.info['base_defense']
        base_stamina = self.info['base_stamina']
        max_cp = _coerce_max_cp(max_cp)

        df = _memo_rank_table(base_attack, base_defense, base_stamina, max_level, max_cp, min_iv)
        return df

    @classmethod
    def random(Pokemon, name=None, level=None, ivs=None, moves=None, form=None, shadow=None, rng=None):
        """
        Example:
            >>> from pypogo.pokemon import *  # NOQA
            >>> self = Pokemon.random()
            >>> print('self = {!r}'.format(self))
            >>> self.league_ranking()
            >>> print('self.pve_fast_move = {}'.format(ub.repr2(self.pve_fast_move, nl=1)))
            >>> print('self.pvp_charge_moves = {}'.format(ub.repr2(self.pvp_charge_moves, nl=2)))

        Ignore:
            while True:
                self = Pokemon.random()

            self.random(name='shellos')
            self.random(name='cherrim')
            self.random(name='sawsbuck')
            self.random(name='smeargle')

            self = Pokemon(name='smeargle')
            self = Pokemon.random(name='honedge')

            name='smeargle'

            sawsbuck
        """
        import random
        # rng = None
        # rng = ub.ensure_rng(None)
        if rng is None:
            rng = random.Random()
        elif isinstance(rng, int):
            rng = random.Random(rng)

        blocklist = {
            'smeargle',
            'honedge',
            'aegislash',
            'doublade',
            'zygarde',
            'gourgeist',
            'pumpkaboo',
        }

        while name is None or name in blocklist:
            # if name is None:
            api = global_api()
            valid_names = list(api.name_to_base)
            name = rng.choice(valid_names)

        self = Pokemon(name, form=form, shadow=shadow)

        max_level = 51
        if level is None:
            self.level = rng.randint(1, max_level)
        else:
            self.level = level
        assert 1 <= self.level <= max_level

        if ivs is None:
            self.ivs = [rng.randint(0, 15), rng.randint(0, 15), rng.randint(0, 15)]
        else:
            self.ivs = ivs

        self.moves = moves
        self.populate_moves()

        # if moves is None:
        #     cands = self.candidate_moveset()
        #     fast_name = rng.choice(cands['fast'])
        #     charged_names = rng.sample(cands['charged'], k=min(len(cands['charged']), 2))
        #     self.moves = [fast_name] + charged_names
        # else:
        #     moves = list(moves)
        #     cands = self.candidate_moveset()
        #     cand_fast = set(map(self.api.normalize, cands['fast']))
        #     cand_charged = set(map(self.api.normalize, cands['charged']))
        #     move_have = set(map(self.api.normalize, moves))
        #     if len(move_have & cand_fast) == 0:
        #         fast_name = rng.choice(cands['fast'])
        #         moves = moves + [fast_name]
        #     if len(move_have & cand_charged) == 0:
        #         charge_name = rng.choice(cands['charged'])
        #         moves = moves + [charge_name]
        #     self.moves = moves

        self.populate_all()
        return self

    def populate_moves(self, rng=None):
        if rng is None:
            import random
            rng = random.Random()

        if self.moves is None:
            moves = []
        else:
            moves = list(self.moves)

        if moves is None or len(moves) == 0:
            cands = self.candidate_moveset()
            fast_name = rng.choice(cands['fast'])
            charged_names = rng.sample(cands['charged'], k=min(len(cands['charged']), 2))
            self.moves = [fast_name] + charged_names
        else:
            moves = list(moves)
            cands = self.candidate_moveset()
            cand_fast = set(map(self.api.normalize, cands['fast']))
            cand_charged = set(map(self.api.normalize, cands['charged']))
            move_have = set(map(self.api.normalize, moves))
            if len(move_have & cand_fast) == 0:
                fast_name = rng.choice(cands['fast'])
                moves = moves + [fast_name]
            if len(move_have & cand_charged) == 0:
                charge_name = rng.choice(cands['charged'])
                moves = moves + [charge_name]
            self.moves = moves
        return self

    def populate_move_stats(self):
        """
        Example:
            >>> import pypogo
            >>> self = pypogo.Pokemon('medicham', moves=['counter', 'power_up_punch'])
            >>> self.populate_move_stats()
            >>> self.pvp_fast_move
            >>> print('self.pvp_fast_move = {!r}'.format(self.pvp_fast_move))
            >>> self.pve_fast_move
            >>> print('self.pve_fast_move = {!r}'.format(self.pve_fast_move))
        """
        if self.moves is None:
            raise Exception('no moves specified on this mon')
        pve_fast_cand = []
        pve_charge_cand = []
        pvp_fast_cand = []
        pvp_charge_cand = []

        for move in self.moves:
            move_info = self.api.get_move_info(move)
            if move_info['move_type'] == 'fast':
                pve_fast_cand.extend(move_info['pve'])
                pvp_fast_cand.extend(move_info['pvp'])
            elif move_info['move_type'] == 'charged':
                pve_charge_cand.extend(move_info['pve'])
                pvp_charge_cand.extend(move_info['pvp'])
            else:
                raise KeyError

        # Hack for plus moves, which seem to have their name normalized away?
        pve_charge_cand = list(ub.unique(pve_charge_cand, key=lambda x: x['name']))

        if len(pve_fast_cand) != 1:
            raise Exception('MUST HAVE 1 FAST MOVE')

        if not (0 < len(pve_charge_cand) < 3):
            raise Exception('MUST HAVE 1-2 CHARGE MOVES')

        if len(pvp_fast_cand) != 1:
            raise Exception('MUST HAVE 1 FAST MOVE')

        if not (0 < len(pvp_charge_cand) < 3):
            raise Exception('MUST HAVE 1-2 CHARGE MOVES')

        for move in pve_fast_cand:
            move['move_type'] = 'fast'
            move['move_env'] = 'pve'
        for move in pve_charge_cand:
            move['move_type'] = 'charge'
            move['move_env'] = 'pve'

        for move in pvp_fast_cand:
            move['move_type'] = 'fast'
            move['move_env'] = 'pvp'
        for move in pvp_charge_cand:
            move['move_type'] = 'charge'
            move['move_env'] = 'pvp'

        self.pve_fast_move = pve_fast_cand[0]
        self.pve_charge_moves = pve_charge_cand[0:2]
        self.pvp_fast_move = pvp_fast_cand[0]
        self.pvp_charge_moves = pvp_charge_cand[0:2]

    @property
    def charge_moves(self):
        """

        """
        return {
            'pve': self.pve_charge_moves,
            'pvp': self.pvp_charge_moves,
        }

    @property
    def fast_move(self):
        return {
            'pve': self.pve_fast_move,
            'pvp': self.pvp_fast_move,
        }

    @classmethod
    def from_pvpoke_row(Pokemon, row):
        """
        Atempt to build a pokemon object from the format used by pvpoke.com

        References:
            https://pvpoke.com/team-builder/

        Example:
            >>> from pypogo.pokemon import *  # NOQA
            >>> row_line = 'victreebel_shadow-shadow,RAZOR_LEAF,LEAF_BLADE,FRUSTRATION,22.5,4,14,14'
            >>> row = row_line.split(',')
            >>> self = Pokemon.from_pvpoke_row(row)
            >>> print(f'self={self}')
        """
        name = row[0]
        shadow = False
        if name.endswith('-shadow'):
            name = name.split('-shadow')[0]
            # weird case for victreebel
            if name.endswith('_shadow'):
                name = name.split('_shadow')[0]
            shadow = True
        level = None
        ivs = [None, None, None]

        moves = []
        idx = 0
        for idx in range(1, 4):
            if idx >= len(row):
                break
            if not re.match('[a-z]+', row[idx].lower()):
                break
            moves.append(row[idx])
        idx += 1
        if idx < len(row):
            level = float(row[idx])
        idx += 1
        if idx < len(row):
            ivs = list(map(int, row[idx:]))

        if ivs == [None, None, None]:
            ivs = None

        self = Pokemon(name, level=level, ivs=ivs, moves=moves, shadow=shadow)
        return self

    def to_pvpoke_import_line(self):
        """
        Text suitable for import into pvpoke

        Example
            >>> self = Pokemon('darmanitan')
            >>> for mon in self.alternate_forms():
            >>>     print('mon = {!r}'.format(mon))
            >>>     print(mon.to_pvpoke_import_line())

            >>> self = Pokemon('giratina')
            >>> list(self.alternate_forms())

        Ignore:
            from pypogo.pokemon import *  # NOQA
            api = global_api()

            api.data['pokemon_forms']

        """
        name = self.name.replace('’', '')

        # have to take care of a lot of special cases
        if name == 'ho-oh':
            name = 'ho_oh'

        pvpoke_id = name

        only_galar = {
            'perrserker',
            'farfetchd',
            'sirfetchd',
            'obstagoon',
            'mr. rime',
        }
        form_ = self.form.lower()

        recognized_pvp_forms = {
            'shadow',

            'alola',

            'galarian',
            'galarian_standard',
            'galarian_zen',
            'standard',
            'zen'

            'sunny',
            'overcast',

            'west_sea',
            'east_sea',

            'altered',
            'origin',

            'incarnate',
            'therian',

            'rainy',
            'snowy',

            'speed',
            'defense',
            'attack',
        }

        unrecognized_pvp_forms = {
            '2020',
            '2021',
            'copy_2019',
            'costume_2020',
            'adventure_hat_2020',
            'autumn',
            'summer',
            'spring',
            'winter',
            'vs_2019',
            'fall_2019',
            'winter_2020',
        }

        undetermined_form = {
            'purified',

            'black',
            'white',

            'blue_striped',
            'red_striped',

            'burn',
            'chill',
            'frost',
            'heat',

            'douse',

            'bug',
            'dark',
            'dragon',
            'electric',
            'fairy',
            'fighting',
            'fire',
            'flying',
            'ghost',
            'grass',
            'ground',
            'ice',
            'poison',
            'psychic',
            'rock',
            'steel',
            'water',

            'fan',

            'female',

            'land',

            'mow',
            'normal',
            'ordinary',

            'a',
            'aria',
            'pirouette',
            'plant',
            'resolute',
            'sandy',
            'shock',
            'sky',
            'trash',
            'wash',
        }

        form_map = {
            'alola': 'alolan',
            # 'east_sea': 'east',
            # 'west_sea': 'west',
            'normal': '',
            'shadow': '',
        }
        pvpoke_form = form_map.get(form_, form_)

        if pvpoke_form == 'purified':
            pvpoke_form = ''

        if pvpoke_form == 'female' and name == 'frillish':
            pvpoke_form = ''

        if pvpoke_form == 'galarian' and name in only_galar:
            pvpoke_form = ''

        if pvpoke_form in unrecognized_pvp_forms:
            pvpoke_form = ''

        if pvpoke_form:
            pvpoke_id = '{}_{}'.format(pvpoke_id, pvpoke_form)

        if self.level is not None and self.level > 41:
            pvpoke_id += '_xl'

        if self.shadow:
            pvpoke_id = name + '-shadow'

        fixup = {
            'FUTURE_SIGHT': 'FUTURESIGHT',
        }
        parts = []
        if self.moves is not None:
            for move in self.moves:
                part = move.upper().replace(' ', '_').replace(')', '').replace('(', '')
                part = fixup.get(part, part)
                parts.append(part)

        if self.level is not None:
            if self.ivs and all(v is not None for v in self.ivs):
                parts.extend(list(map(str, [self.level, *self.ivs])))

        line = ','.join([pvpoke_id] + parts)
        return line

    def to_pvpoke_url(self):
        parts = []

        name = self.name.replace('’', '')

        if self.form == 'Alola':
            parts.append(name + '_alolan')
        else:
            parts.append(name)

        if self.level is not None:
            parts.append(str(self.level))

        needs_441 = False

        if self.ivs and all(v is not None for v in self.ivs):
            parts.extend(list(map(str, self.ivs)))
            needs_441 = True
        if self.shadow:
            parts.append('shadow')
            needs_441 = True

        if needs_441:
            parts.append('4-4-1')  # no idea what this is

        if self.moves:
            parts.append('m')
            moves = self.moves + ([None] * max(0, 3 - len(self.moves)))
            fm, cm1, cm2 = moves

            fixup = {
                'FUTURE_SIGHT': 'FUTURESIGHT',
            }
            cm1 = fixup.get(cm1, cm1)
            cm2 = fixup.get(cm2, cm2)

            # Check if a shadow variant exists to ensure the move index is right on pvpoke
            _api = self.api
            if not self.shadow:
                if self.form not in {'Alola', 'Galarian'}:
                    has_shadow = any(item['form'] == 'Shadow' for item in _api.name_to_stats[self.name])
                    if has_shadow:
                        if 'RETURN' not in _api.learnable[self.name]['charge']:
                            _api.learnable[self.name]['charge'].append('RETURN')
                            _api.learnable[self.name]['charge'] = sorted(_api.learnable[self.name]['charge'])

            fm_idx = _api.learnable[self.name]['fast'].index(fm)
            cm1_idx = _api.learnable[self.name]['charge'].index(cm1) + 1
            parts.append(str(fm_idx))
            parts.append(str(cm1_idx))
            if cm2 is not None:
                if cm2.lower() == 'frustration':
                    # hack for frustration
                    cm2_idx = 0
                else:
                    cm2_idx = _api.learnable[self.name]['charge'].index(cm2) + 1
                parts.append(str(cm2_idx))
        else:
            parts.append('m-1-1-2')

        # parts.append(self.moves[0])
        # parts.append(self.moves[1])
        # parts.append('0')
        # parts.append(self.moves[2])
        # parts.append('1')
        # need a lut
        # for move in self.moves:
        #     pass
        code = '-'.join(parts)
        return code

    def candidate_moveset(self, tmable=False):
        """
        Args:
            tmable (bool): if you need an ETM or not

        self = Pokemon.random('mew')
        print('self = {!r}'.format(self))
        possible_moves = self.api.name_to_moves[self.name]
        print('possible_moves = {!r}'.format(possible_moves))
        """
        variant_groups = self.api.name_to_moves[self.name]
        candidates = {
            'fast': set(),
            'charged': set(),
        }
        for variant in variant_groups:
            if False:
                variant['form']
                variant['pokemon_name']
                variant['pokemon_id']
                variant['charged_moves']
                variant['elite_charged_moves']
                variant['fast_moves']
                variant['elite_fast_moves']

            if True or variant['form'] == self.form:
                # TODO: ensure this works

                if not tmable:
                    candidates['fast'].update(variant['elite_fast_moves'])
                    candidates['charged'].update(variant['elite_charged_moves'])

                candidates['fast'].update(variant['fast_moves'])
                candidates['charged'].update(variant['charged_moves'])

        candidates = ub.map_vals(sorted, candidates)
        return candidates

# cpm_step_lut = {
#     0: 0.009426125469,
#     10: 0.008919025675,
#     20: 0.008924905903,
#     30: 0.00445946079,
# }
CPM_LUT = {
    1: 0.09399999678134918, 1.5: 0.1351374313235283, 2.0: 0.16639786958694458,
    2.5: 0.1926509141921997, 3.0: 0.21573247015476227, 3.5: 0.23657265305519104,
    4.0: 0.2557200491428375, 4.5: 0.27353037893772125, 5.0: 0.29024988412857056,
    5.5: 0.3060573786497116, 6.0: 0.3210875988006592, 6.5: 0.33544503152370453,
    7.0: 0.3492126762866974, 7.5: 0.362457737326622, 8.0: 0.37523558735847473,
    8.5: 0.38759241108516856, 9.0: 0.39956727623939514, 9.5: 0.4111935495172506,
    10.0: 0.4225000143051148, 10.5: 0.4329264134104144, 11.0: 0.443107545375824,
    11.5: 0.4530599538719858, 12.0: 0.46279838681221, 12.5: 0.4723360780626535,
    13.0: 0.4816849529743195, 13.5: 0.4908558102324605, 14.0: 0.4998584389686584,
    14.5: 0.5087017565965652, 15.0: 0.517393946647644, 15.5: 0.5259425118565559,
    16.0: 0.5343543291091919, 16.5: 0.5426357612013817, 17.0: 0.5507926940917969,
    17.5: 0.5588305993005633, 18.0: 0.5667545199394226, 18.5: 0.574569147080183,
    19.0: 0.5822789072990417, 19.5: 0.5898879119195044, 20.0: 0.5974000096321106,
    20.5: 0.6048236563801765, 21.0: 0.6121572852134705, 21.5: 0.6194041110575199,
    22.0: 0.6265671253204346, 22.5: 0.633649181574583, 23.0: 0.6406529545783997,
    23.5: 0.6475809663534164, 24.0: 0.654435634613037, 24.5: 0.6612192690372467,
    25.0: 0.667934000492096, 25.5: 0.6745819002389908, 26.0: 0.6811649203300476,
    26.5: 0.6876849085092545, 27.0: 0.6941436529159546, 27.5: 0.7005428969860077,
    28.0: 0.7068842053413391, 28.5: 0.7131690979003906, 29.0: 0.719399094581604,
    29.5: 0.7255756109952927, 30.0: 0.7317000031471252, 30.5: 0.7347410172224045,
    31.0: 0.7377694845199585, 31.5: 0.740785576403141, 32.0: 0.7437894344329834,
    32.5: 0.7467812150716782, 33.0: 0.7497610449790955, 33.5: 0.7527291029691696,
    34.0: 0.7556855082511902, 34.5: 0.7586303651332855, 35.0: 0.7615638375282288,
    35.5: 0.7644860669970512, 36.0: 0.7673971652984619, 36.5: 0.7702972739934921,
    37.0: 0.7731865048408508, 37.5: 0.7760649472475052, 38.0: 0.7789327502250671,
    38.5: 0.78179006, 39.0: 0.78463697, 39.5: 0.78747358,
    40.0: 0.79030001, 40.5: 0.79280001, 41.0: 0.79530001,
    41.5: 0.79780001, 42.0: 0.8003, 42.5: 0.8028,
    43.0: 0.8053, 43.5: 0.8078, 44.0: 0.81029999,
    44.5: 0.81279999, 45.0: 0.81529999,
}

# POGO API doesn't have these, taken from gamepress.gg Not sure if they are
# right
CPM_LUT.update({
    45.5:    0.81779999,
    46:      0.82029999,
    46.5:    0.82279999,
    47:      0.82529999,
    47.5:    0.82779999,
    48:      0.83029999,
    48.5:    0.83279999,
    49:      0.83529999,
    49.5:    0.83779999,
    50:      0.84029999,
    50.5:    0.84279999,
    51:      0.84529999,
})


def calc_cp(attack, defense, stamina, level):
    """
    References:
        https://www.dragonflycave.com/pokemon-go/stats
    """

    # cpm_step = cpm_step_lut[(level // 10) * 10]
    # cpm_step
    cp_multiplier = CPM_LUT[level]

    # https://gamepress.gg/pokemongo/cp-multiplier
    # https://gamepress.gg/pokemongo/pokemon-stats-advanced#:~:text=Calculating%20CP,*%20CP_Multiplier%5E2)%20%2F%2010
    a, d, s = attack, defense, stamina

    adjusted = {
        'attack': a * cp_multiplier,
        'defense': d * cp_multiplier,
        'stamina': int(s * cp_multiplier),
        '_flt_stamina': s * cp_multiplier,
        '_cp_multiplier': cp_multiplier,
    }
    cp = int(a * (d ** 0.5) * (s ** 0.5) * (cp_multiplier ** 2) / 10)
    return cp, adjusted


# class Moves():
#     def __init__(moves):
#         pass
#     pass


@ub.memoize
def _memo_rank_table(base_attack, base_defense, base_stamina, max_level, max_cp, min_iv):
    rows = []
    iva_range = list(range(min_iv, 16))
    ivd_range = list(range(min_iv, 16))
    ivs_range = list(range(min_iv, 16))

    for iva, ivd, ivs in it.product(iva_range, ivd_range, ivs_range):
        attack = base_attack + iva
        defense = base_defense + ivd
        stamina = base_stamina + ivs

        best_level = None
        best_cp = None
        best_adjusted = None
        for level in list(np.arange(1, max_level + 0.5, 0.5)):
            cand_cp, adjusted = calc_cp(attack, defense, stamina, level)
            if cand_cp <= max_cp:
                best_cp = cand_cp
                best_level = level
                best_adjusted = adjusted
            else:
                break

        row = {
            'iva': iva,
            'ivd': ivd,
            'ivs': ivs,
            'cp': best_cp,
            'level': best_level,
            'attack': best_adjusted['attack'],
            'defense': best_adjusted['defense'],
            'stamina': best_adjusted['stamina'],
        }
        rows.append(row)

    df = pd.DataFrame.from_dict(rows)
    df['stat_product_k'] = (df['attack'] * df['defense'] * df['stamina']) / 1000
    df = df.sort_values('stat_product_k', ascending=False)
    df['rank'] = np.arange(1, len(df) + 1)
    df = df.set_index('rank', drop=False)
    min_ = df['stat_product_k'].min()
    max_ = df['stat_product_k'].max()
    df['percent'] = ((df['stat_product_k'] - min_) / (max_ - min_)) * 100
    return df


def _coerce_max_cp(max_cp):
    if isinstance(max_cp, str):
        if 'great' in max_cp:
            max_cp = 1500
        elif 'ultra' in max_cp:
            max_cp = 2500
        elif 'master' in max_cp:
            max_cp = np.inf
        else:
            raise KeyError(max_cp)
    return max_cp
