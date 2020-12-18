"""
Temporary place for my personal PVP pokemon inventory
"""
import ubelt as ub
from pypogo.pokemon import Pokemon


def pvp_inventory():
    """
    The idea is you put info about your candidates here and we find good mons
    to power up.
    """
    inventory = [
        Pokemon('Magnezone', (14, 14, 14), cp=1815, form='Normal'),
        Pokemon('Magnemite', (7, 14, 9), cp=792),
        Pokemon('Magnemite', (10, 14, 13), cp=747),
        Pokemon('Magnemite', (13, 9, 15), cp=602),
        Pokemon('Magneton', (13, 14, 13), cp=550, form='Shadow'),
        Pokemon('Magnemite', (15, 13, 7), cp=293, form='Shadow'),
        Pokemon('Magnemite', (2, 14, 15), cp=283, form='Shadow'),
    ]

    inventory = [
        Pokemon('sirfetch’d', (4, 11, 12), cp=1924, form='Galarian'),
        Pokemon('farfetch’d', (12, 15, 15), cp=1495, form='Galarian'),
        Pokemon('farfetch’d', (14, 14, 15), cp=948, form='Galarian'),
    ]

    inventory = [
        Pokemon('bulbasaur', (7, 13, 12), cp=382, form='Shadow'),
        Pokemon('bulbasaur', (4, 8, 13), cp=366, form='Shadow'),
        Pokemon('bulbasaur', (7, 12, 8), cp=227, form='Shadow'),
    ]

    inventory = [
        Pokemon('Clefable', (12, 13, 12), cp=1828),
        Pokemon('Clefairy', (4, 2, 7), cp=389),
    ]

    inventory = [
        Pokemon('Jigglypuff', (10, 14, 15), cp=631),
        Pokemon('Jigglypuff', (10, 12, 15), cp=286),
    ]

    inventory = [
        Pokemon('poliwag', (10, 13, 14), cp=335),
        Pokemon('poliwag', (10, 14, 13), cp=335),
    ]

    inventory = [
        Pokemon('drifloon', (15, 15, 1), cp=695),
        Pokemon('drifloon', (0, 9, 14), cp=527),
        Pokemon('drifloon', (15, 15, 12), cp=509),
        Pokemon('drifloon', (14, 15, 14), cp=508),
        Pokemon('drifloon', (14, 11, 14), cp=497),
        Pokemon('drifloon', (11, 13, 12), cp=489, shiny=True),
        Pokemon('drifloon', (0, 4, 8), cp=336),
        Pokemon('drifloon', (12, 10, 12), cp=118),
    ]

    inventory = [
        Pokemon('shelmet', (10, 15, 8), cp=351),
        Pokemon('shelmet', (0, 13, 0), cp=166),
        Pokemon('shelmet', (15, 10, 12), cp=158),
    ]

    inventory = [
        Pokemon('Karrablast', (10, 4, 12), cp=824),
        Pokemon('Karrablast', (13, 13, 13), cp=655),
        Pokemon('Karrablast', (13, 14, 15), cp=16),
    ]

    inventory = [
        Pokemon('Ralts', (14, 14, 13)),
        Pokemon('Ralts', (14, 11, 12)),
        Pokemon('Ralts', (0, 11, 0), shadow=True),
        Pokemon('Ralts', (1, 14, 2), shadow=True),
        Pokemon('Ralts', (12, 12, 6), shadow=True),
        Pokemon('Ralts', (5, 14, 14)),
        Pokemon('Ralts', (7, 11, 11)),
    ]

    inventory = [
        Pokemon('Toxicroak', (11, 13, 14)),
        Pokemon('Croagunk', (9, 11, 13), cp=794),
        Pokemon('Croagunk', (8, 6, 8), cp=429),
    ]

    inventory = [
        Pokemon('Snorlax', (7, 6, 13), shadow=True),
        Pokemon('Snorlax', (0, 0, 13), shadow=0),
        Pokemon('Snorlax', (8, 15, 14), shadow=0, cp=1155),
        Pokemon('Snorlax', (8, 12, 11), shadow=0, cp=2106),
        Pokemon('Snorlax', (9, 15, 10), shadow=0, cp=2487),
        Pokemon('Snorlax', (1, 15, 14), shadow=0, cp=1372),
        Pokemon('Snorlax', (7, 11, 15), shadow=0, cp=3044),
        Pokemon('Snorlax', (2, 15, 1), shadow=1),
        Pokemon('Munchlax', (14, 11, 14), shadow=0, cp=1056),
    ]

    inventory = [
        Pokemon('Obstagoon', (11, 15, 13), cp=1478, form='Galarian'),
        Pokemon('zigzagoon', (10, 14, 14), cp=268, form='Galarian'),
        Pokemon('zigzagoon', (11, 12, 13), cp=268, form='Galarian'),
        Pokemon('zigzagoon', (11, 12, 15), cp=270, form='Galarian'),
        Pokemon('zigzagoon', (12, 11, 15), cp=272, form='Galarian'),
    ]

    inventory = [
        Pokemon('Meditite', (5, 12, 4), cp=25),
        Pokemon('Medicham', (14, 12, 12), cp=1116),
        Pokemon('Medicham', (15, 15, 10), cp=966),
    ]

    inventory = [
        Pokemon('Electabuzz', (12, 14, 15), cp=2000),
        Pokemon('Electabuzz', (10, 15, 14), cp=1558),
        Pokemon('Electabuzz', (14, 13, 14), cp=1711),
        Pokemon('Electabuzz', (12, 14, 14), cp=1307),
        Pokemon('Electabuzz', (4, 14, 14), cp=754),
        Pokemon('Electabuzz', (1, 15, 15), cp=30),
        Pokemon('Electabuzz', (1, 4, 7), cp=464, shadow=True),
        Pokemon('Electivire', (0, 11, 11), cp=2436),
        Pokemon('Electivire', (5, 9, 12), cp=2312),
        Pokemon('Electivire', (4, 13, 14), cp=659),
    ]

    inventory = [Pokemon('Gyarados', ivs=ivs) for ivs in [
        (0, 10, 15),
        (1, 14, 11),
        (2, 13, 12),
        (2, 15, 14),
        (7, 13, 15),
        (11, 14, 13),
        (12, 12, 13),
        (14, 13, 13),
        (15, 13, 15),
        (2, 13, 15),
    ]]
    inventory += [
        Pokemon('Gyarados', ivs=(4, 12, 15), shadow=True),
        Pokemon('Magikarp', ivs=(3, 5, 2), shiny=True, cp=55),
    ]
    rank_inventory(inventory)

    inventory = [
        Pokemon('Mudkip', (11, 13, 12), shadow=True, cp=242),
        Pokemon('Mudkip', (4, 13, 9), shadow=True, cp=227),
        Pokemon('Mudkip', (4, 2, 13), cp=747),
        Pokemon('Mudkip', (13, 14, 13), cp=628),
        Pokemon('Mudkip', (12, 13, 15), cp=625),
        Pokemon('Mudkip', (13, 14, 11), cp=624),
        Pokemon('Mudkip', (10, 13, 12), cp=609),
        Pokemon('Mudkip', (11, 11, 12), cp=608),
        Pokemon('Mudkip', (15, 12, 13), cp=48),
        Pokemon('Marshtomp', (14, 14, 10), cp=1141),
        Pokemon('Swampert', (0, 2, 14), cp=1526),
        Pokemon('Swampert', (13, 14, 13), cp=2467),
    ]

    inventory = [
        Pokemon('Tangrowth', (4, 15, 15), cp=2592),
        Pokemon('Tangrowth', (14, 15, 13), cp=1716),
        Pokemon('Tangela', (9, 14, 13), cp=1998),
        Pokemon('Tangela', (7, 10, 7), cp=1715),
        Pokemon('Tangela', (12, 15, 15), cp=1259),
        Pokemon('Tangela', (15, 11, 15), cp=1264),
        Pokemon('Tangela', (15, 11, 15), cp=1264),
    ]

    inventory = [
        Pokemon('Snover', (15, 14, 14), cp=1019),
        Pokemon('Snover', (5, 14, 12), cp=920),
        Pokemon('Snover', (10, 10, 15), cp=623),
        Pokemon('Snover', (0, 10, 0), cp=438),
        Pokemon('Snover', (7, 12, 10), cp=423),
        Pokemon('Snover', (9, 13, 13), cp=405, shadow=True),
        Pokemon('Snover', (5, 9, 5), cp=228, shadow=True),
    ]

    inventory = [
        Pokemon('Cottonee', (8, 15, 15), cp=597),
        Pokemon('Cottonee', (1, 13, 13), cp=396),
        Pokemon('Cottonee', (4, 10, 9), cp=468),
        Pokemon('Cottonee', (11, 11, 10), cp=276),
        Pokemon('Cottonee', (9, 9, 4), cp=209),
    ]

    inventory = [
        Pokemon('Ferroseed', (13, 13, 11), cp=516),
        Pokemon('Ferroseed', (10, 13, 13), cp=377),
        Pokemon('Ferroseed', (14, 14, 13), cp=526),
    ]

    inventory = [
        Pokemon('Makuhita', (9, 15, 14), cp=127),
        Pokemon('Makuhita', (4, 13, 10), cp=389),
        Pokemon('Makuhita', (12, 13, 14), cp=357),
        Pokemon('Makuhita', (9, 15, 14), cp=127),
        Pokemon('Hariyama', (7, 7, 13), cp=1956),
    ]
    # for self in inventory:
    #     list(self.family())

    inventory = [
        Pokemon('Sableye', (11, 13, 15), cp=278),
        Pokemon('Sableye', (3, 11, 7), cp=294, shadow=True),
        Pokemon('Sableye', (15, 10, 14), cp=20),
        Pokemon('Sableye', (13, 13, 15), cp=620),
        Pokemon('Sableye', (13, 10, 14), cp=816),
    ]

    inventory = [
        Pokemon('machop', (15, 15, 14), cp=910),
        Pokemon('machop', (15, 15, 14), cp=437),
        Pokemon('machop', (15, 14, 11), cp=359),
        Pokemon('machop', (8, 12, 12), cp=442, shadow=True),
        Pokemon('machoke', (1, 11, 0), cp=1480),
        Pokemon('machamp', (13, 15, 15), cp=3032),
        Pokemon('machamp', (14, 14, 12), cp=1722),
        Pokemon('machamp', (13, 12, 14), cp=1713),
        Pokemon('machamp', (11, 14, 15), cp=1713),
        Pokemon('machamp', (5, 11, 10), cp=1474, shadow=True),
    ]
    rank_inventory(inventory)


def rank_inventory(inventory):
    candidates = list(ub.flatten(list(pkmn.family(ancestors=False, node=True))
                                 for pkmn in inventory))

    groups = ub.group_items(candidates, key=lambda p: p.name)

    leages = {
        'master': {'max_cp': float('inf')},
        'ultra': {'max_cp': 2500},
        'great': {'max_cp': 1500},
        'little': {'max_cp': 500},
    }

    max_level = 45  # for XL candy
    # max_level = 40  # normal

    all_dfs = []

    for name, group in groups.items():
        print('\n\n------------\n\n')
        print('name = {!r}'.format(name))
        for leage_name, leage_filters in leages.items():
            max_cp = leage_filters['max_cp']
            print('')
            print(' ========== ')
            print(' --- {} in {} --- '.format(name, leage_name))
            not_eligible = [p for p in group if p.cp is not None and p.cp > max_cp]
            eligible = [p for p in group if p.cp is None or p.cp <= max_cp]
            print('not_eligible = {!r}'.format(not_eligible))
            if len(eligible) > 0:
                first = ub.peek(eligible)
                have_ivs = eligible
                df = first.leage_rankings_for(have_ivs, max_cp=max_cp,
                                              max_level=max_level)
                all_dfs.append(df)
            else:
                print('none eligable')

    # Print out the best ranks for each set of IVS over all possible forms
    # (lets you know which ones can be transfered safely)

    iv_to_rank = ub.ddict(list)
    for df in all_dfs:
        if df is not None:
            df = df.set_index(['iva', 'ivd', 'ivs'])
            for iv, rank in zip(df.index, df['rank']):
                iv_to_rank[iv].append(rank)

    iv_to_best_rank = ub.map_vals(sorted, iv_to_rank)
    iv_to_best_rank = ub.sorted_vals(iv_to_best_rank)
    print('iv_to_best_rank = {}'.format(ub.repr2(iv_to_best_rank, nl=1, align=':')))
