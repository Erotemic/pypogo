"""
Temporary place for my personal PVP pokemon inventory
"""
import ubelt as ub
from pypogo import Pokemon


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

    for self in inventory:
        list(self.family())

    candidates = list(ub.flatten(list(pkmn.family(ancestors=False)) for pkmn in inventory)) + inventory

    groups = ub.group_items(candidates, key=lambda p: p.name)

    leages = {
        'master': {'max_cp': float('inf')},
        'ultra': {'max_cp': 2500},
        'great': {'max_cp': 1500},
        'little': {'max_cp': 500},
    }

    max_level = 45  # for XL candy
    max_level = 40  # normal

    for name, group in groups.items():
        print('\n\n------------\n\n')
        print('name = {!r}'.format(name))
        for leage_name, leage_filters in leages.items():
            max_cp = leage_filters['max_cp']
            print('')
            print(' ========== ')
            print(' --- {} in {} --- '.format(name, leage_name))
            not_eligible = [p for p in group if p.cp is not None and p.cp > max_cp]
            print('not_eligible = {!r}'.format(not_eligible))
            have_ivs = [p.ivs for p in group if p.cp is None or p.cp <= max_cp]
            if len(have_ivs) > 0:
                first = ub.peek(group)
                first.leage_rankings_for(have_ivs, max_cp=max_cp,
                                         max_level=max_level)
            else:
                print('none eligable')
