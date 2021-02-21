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
from pypogo.pogo_api import api


class Pokemon(ub.NiceRepr):
    """
    xdoctest ~/code/pypogo/pypogo/pokemon.py

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
    """
    def __init__(self, name, ivs=None, level=None, moves=None, shadow=False,
                 form='Normal', cp=None, autobuild=True, shiny=False,
                 adjusted=None):
        self.name = name.lower()
        self.level = level
        self.ivs = ivs
        self.moves = moves
        self.shadow = shadow
        self.shiny = shiny
        if shadow:
            form = 'Shadow'
        self.form = form
        self.api = api
        self.cp = cp
        self.adjusted = adjusted

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
            aux_parts.append('({})'.format(self.form))

        if self.form == 'Purified':
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
        info = '{}, {}, {}, {}, {}'.format(disp_name, self.cp, self.level, self.ivs, self.moves)
        return info
        # return str([self.name] + self.moves + [self.level] + self.ivs)

    def lookup_moves(self):
        possible_moves = api.name_to_moves[self.name]
        return possible_moves

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
        info = api.get_info(name=self.name, form=self.form)
        self.learnable = api.learnable[self.name]
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
            >>> self = Pokemon('ralts', ivs=[6, 13, 15], level=20,
            >>>                 shadow=True, shiny=True)
            >>> new = self.purify()
            >>> print('self = {}'.format(self))
            >>> print('new  = {}'.format(new))
            self = <Pokemon(ralts(😈,✨), 274, 20, [6, 13, 15], None)>
            new  = <Pokemon(ralts(👼,✨), 285, 20, (8, 15, 15), None)>
        """
        if not self.shadow:
            raise Exception('Only can purify shadow pokemon')

        overwrite = {}
        if self.ivs is not None:
            new_ivs = tuple([min(15, s + 2) for s in self.ivs])
            overwrite['ivs'] = new_ivs
        overwrite['form'] = 'Purified'
        overwrite['shadow'] = False
        # TODO: replace frustration with return
        new = self.copy(**overwrite)
        return new

    def family(self, ancestors=True, node=False, onlyadj=False):
        """
        Get other members of this pokemon family

        Yields:
            Pokemon: other members of this family

        Ignore:
            self = Pokemon('gastly', ivs=[6, 13, 15])
            self = Pokemon('haunter', ivs=[6, 13, 15])
            self = Pokemon('gengar', ivs=[6, 13, 15])
            list(self.family())

            self = Pokemon('magikarp', ivs=[6, 13, 15])
            list(self.family())

            self = Pokemon('eevee', ivs=[6, 13, 15])
            list(self.family(onlyadj=True))

            self = Pokemon('ralts', ivs=[6, 13, 15], shadow=True)
            list(self.family(onlyadj=True))
            list(self.family())
        """
        blocklist = set()
        if not node:
            blocklist.add(self.name)

        if not ancestors:
            toadd = set(nx.ancestors(api.evo_graph, self.name))
            blocklist.update(toadd)

        cc = api.name_to_family[self.name]
        if onlyadj:
            keeplist = set(api.evo_graph.adj[self.name])
            blocklist = set(cc) - keeplist

        kw = {
            'level': self.level,
            'form': self.form,
            'ivs': self.ivs,
            'shadow': self.shadow,
            'shiny': self.shiny,
        }
        for name in cc:
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
        product = (self.adjusted['attack'] * self.adjusted['stamina'] * self.adjusted['defense']) / 1000
        return product

    @property
    def base_stats(self):
        base_stats = {
            'attack': self.info['base_attack'],
            'defense': self.info['base_defense'],
            'stamina': self.info['base_stamina'],
        }
        return base_stats

    def league_ranking(self, have_ivs=None, max_cp=1500, max_level=51, min_iv=0):
        """
        Given a set of IVs for this pokemon compute the league rankings

        Example:

            # When does a potential good XL medicham become better than non XL?

            z = Pokemon('machamp', [1, 15, 6]).maximize(1500)
            z.populate_cp()
            z.stat_product
            print('z = {!r}'.format(z))
            print('z.stat_product = {!r}'.format(z.stat_product))

            self = Pokemon('medicham', ivs=[7, 15, 14], cp=1368)
            self.populate_cp()
            print('self = {!r}'.format(self))
            self.adjusted
            print('self.adjusted = {!r}'.format(self.adjusted))
            stat_product = self.stat_product
            print('stat_product = {!r}'.format(stat_product))

            m3 = Pokemon('medicham', ivs=[7, 15, 14], cp=1377)
            m3.populate_cp()
            print('m3 = {!r}'.format(m3))
            m3.adjusted
            print('m3.adjusted = {!r}'.format(m3.adjusted))
            stat_product = m3.stat_product
            print('stat_product = {!r}'.format(stat_product))

            n = self.copy()
            n.level += 0.5 * 4
            n.cp = None
            n.populate_cp()
            print('n = {!r}'.format(n))
            print('n.adjusted = {!r}'.format(n.adjusted))
            stat_product1 = n.stat_product
            print('stat_product1 = {!r}'.format(stat_product1))

            y = self.copy().maximize(max_cp=1400, max_level=51)
            print('y = {!r}'.format(y))
            y.level += 0.5
            y.cp = None
            y.populate_cp()
            print('y.adjusted = {!r}'.format(y.adjusted))
            stat_product1 = y.stat_product
            print('stat_product1 = {!r}'.format(stat_product1))

            x = Pokemon('medicham', ivs=[13, 13, 13]).maximize(max_cp=1500, max_level=40)
            n.populate_cp()
            print('x = {!r}'.format(x))
            stat_product2 = x.stat_product
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
            print('Out of this league {}'.format(max_cp))
        else:
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
                    'stat_product': league_row['stat_product'],
                    'attack': league_row['attack'],
                    'defense': league_row['defense'],
                    'stamina': league_row['stamina'],
                    'percent': league_row['percent'],
                    'name': name,
                })
            rankings = pd.DataFrame.from_dict(rows)
            #
            print('')
            print('Leage {} Rankings'.format(max_cp))
            print('self = {!r}'.format(self))
            print(rankings.sort_values('rank'))
            return rankings

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
            ivs = 'maximize' if ivs is None else 'keep'

        if ivs == 'maximize':
            # TODO: could be more efficient
            table = self.league_ranking_table(
                max_cp=max_cp, max_level=max_level)
            row = table.iloc[0]
            self.ivs = [row['iva'], row['ivd'], row['ivs']]
        elif ivs == 'keep':
            if self.ivs is not None:
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
            >>> self.league_ranking(have_ivs)

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
            >>> self.league_ranking(have_ivs)

            >>> self = Pokemon('haunter')
            >>> print('self.info = {}'.format(ub.repr2(self.info, nl=2)))
            >>> self.league_ranking(have_ivs)

            >>> have_ivs = [
            >>>     (12, 11, 14),
            >>>     (12, 15, 15),
            >>>     (15, 15, 15),
            >>> ]
            >>> Pokemon('blaziken').league_ranking(have_ivs, max_cp=1500)
            >>> Pokemon('blaziken').league_ranking(have_ivs, max_cp=2500)
            >>> Pokemon('blaziken').league_ranking(have_ivs, max_cp=np.inf)

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
            >>> Pokemon('swampert').league_ranking(have_ivs, max_cp=1500)
            >>> Pokemon('swampert').league_ranking(have_ivs, max_cp=2500)
            >>> Pokemon('swampert').league_ranking(have_ivs, max_cp=np.inf)

            >>> have_ivs = [
            >>>     (1, 2, 15),
            >>>     (12, 15, 14),
            >>>     (14, 15, 14),
            >>>     (14, 14, 14),
            >>>     (14, 13, 15),
            >>>     (15, 15, 10),
            >>> ]
            >>> Pokemon('sceptile').league_ranking(have_ivs, max_cp=1500)
            >>> Pokemon('sceptile').league_ranking(have_ivs, max_cp=2500)

            >>> have_ivs = [
            >>>     (14, 14, 15),
            >>>     (10, 14, 15),
            >>>     (15, 15, 15),
            >>>     (15, 15, 15),
            >>> ]
            >>> Pokemon('rhyperior').league_ranking(have_ivs, max_cp=np.inf)

            >>> have_ivs = [
            >>>     (14, 14, 14),
            >>>     (12, 13, 14),
            >>>     (13, 14, 14),
            >>>     (15, 13, 14),
            >>>     (8, 6, 8),
            >>> ]
            >>> Pokemon('vigoroth').league_ranking(have_ivs, max_cp=1500)


            >>> have_ivs = [
            >>>     (6, 15, 13),
            >>>     (3, 4, 14),
            >>>     (2, 9, 15),
            >>>     (6, 14, 15),
            >>>     (7, 15, 15),
            >>>     (10, 15, 15),
            >>> ]
            >>> Pokemon('shiftry').league_ranking(have_ivs, max_cp=1500)
            >>> Pokemon('shiftry').league_ranking(have_ivs, max_cp=2500)

            >>> have_ivs = [
            >>>     (15, 15, 14),
            >>>     (0, 7, 8),
            >>>     (3, 12, 14),
            >>>     (5, 5, 15),
            >>>     (4, 7, 12),
            >>>     (15, 14, 14),
            >>>     (10, 14, 15),
            >>> ]
            >>> Pokemon('alakazam').league_ranking(have_ivs, max_cp=1500)
            >>> Pokemon('alakazam').league_ranking(have_ivs, max_cp=2500)

            >>> have_ivs = [
            >>>     (0, 15, 6),
            >>>     (11, 10, 10),
            >>>     (12, 12, 11),
            >>>     (15, 10, 12),
            >>> ]
            >>> Pokemon('salamence').league_ranking(have_ivs, max_cp=1500)
            >>> Pokemon('salamence').league_ranking(have_ivs, max_cp=2500)
            >>> Pokemon('salamence').league_ranking(have_ivs, max_cp=np.inf)

            >>> have_ivs = [
            >>>     (6, 10, 10),
            >>>     (11, 9, 14),
            >>>     (13, 12, 14),
            >>>     (15, 15, 15),
            >>>     (15, 15, 5),
            >>> ]
            >>> Pokemon('flygon').league_ranking(have_ivs, max_cp=1500)
            >>> Pokemon('flygon').league_ranking(have_ivs, max_cp=2500)
            >>> Pokemon('flygon').league_ranking(have_ivs, max_cp=np.inf)

            >>> have_ivs = [
            >>>     (6, 11, 11),
            >>>     (10, 11, 10),
            >>>     (10, 11, 12),
            >>>     (6, 14, 4),
            >>>     (15, 12, 15),
            >>>     (15, 7, 15),
            >>> ]
            >>> Pokemon('mamoswine').league_ranking(have_ivs, max_cp=1500)
            >>> Pokemon('mamoswine').league_ranking(have_ivs, max_cp=2500)
            >>> Pokemon('mamoswine').league_ranking(have_ivs, max_cp=np.inf)

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
            >>> _ = Pokemon('registeel').league_ranking(have_ivs, max_cp=1500, min_iv=10, max_level=51)
            >>> _ = Pokemon('registeel').league_ranking(have_ivs, max_cp=2500, min_iv=10, max_level=51)

        """
        rows = []
        iva_range = list(range(min_iv, 16))
        ivd_range = list(range(min_iv, 16))
        ivs_range = list(range(min_iv, 16))

        for iva, ivd, ivs in it.product(iva_range, ivd_range, ivs_range):
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
        df['stat_product'] = (df['attack'] * df['defense'] * df['stamina']) / 1000
        df = df.sort_values('stat_product', ascending=False)
        df['rank'] = np.arange(1, len(df) + 1)
        df = df.set_index('rank', drop=False)
        min_ = df['stat_product'].min()
        max_ = df['stat_product'].max()
        df['percent'] = ((df['stat_product'] - min_) / (max_ - min_)) * 100
        return df

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
            if not self.shadow:
                if self.form not in {'Alola', 'Galarian'}:
                    has_shadow = any(item['form'] == 'Shadow' for item in api.name_to_stats[self.name])
                    if has_shadow:
                        if 'RETURN' not in api.learnable[self.name]['charge']:
                            api.learnable[self.name]['charge'].append('RETURN')
                            api.learnable[self.name]['charge'] = sorted(api.learnable[self.name]['charge'])

            fm_idx = api.learnable[self.name]['fast'].index(fm)
            cm1_idx = api.learnable[self.name]['charge'].index(cm1) + 1
            parts.append(str(fm_idx))
            parts.append(str(cm1_idx))
            if cm2 is not None:
                if cm2.lower() == 'frustration':
                    # hack for frustration
                    cm2_idx = 0
                else:
                    cm2_idx = api.learnable[self.name]['charge'].index(cm2) + 1
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


def calc_cp(attack, defense, stamina, level):
    """
    References:
        https://www.dragonflycave.com/pokemon-go/stats
    """
    # cpm_step_lut = {
    #     0: 0.009426125469,
    #     10: 0.008919025675,
    #     20: 0.008924905903,
    #     30: 0.00445946079,
    # }
    cmp_lut = {
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
    cmp_lut.update({
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

    # cpm_step = cpm_step_lut[(level // 10) * 10]
    # cpm_step
    cp_multiplier = cmp_lut[level]

    # https://gamepress.gg/pokemongo/cp-multiplier
    # https://gamepress.gg/pokemongo/pokemon-stats-advanced#:~:text=Calculating%20CP,*%20CP_Multiplier%5E2)%20%2F%2010
    a, d, s = attack, defense, stamina

    adjusted = {
        'attack': a * cp_multiplier,
        'defense': d * cp_multiplier,
        'stamina': int(s * cp_multiplier),
    }
    cp = int(a * (d ** 0.5) * (s ** 0.5) * (cp_multiplier ** 2) / 10)
    return cp, adjusted


# class Moves():
#     def __init__(moves):
#         pass
#     pass
