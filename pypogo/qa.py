import ubelt as ub
from pypogo.pokemon import Pokemon
from pypogo.pogo_api import api

def stats_distro():
    candidates = [
        # Pokemon('Gengar', (7, 14, 14), cp=2500, moves=['SHADOW_CLAW', 'SHADOW_PUNCH', 'SHADOW_BALL']),
        # Pokemon('Togekiss', (15, 15, 14), cp=2469, moves=['CHARM', 'FLAMETHROWER', 'AERIAL_ACE']),
        # Pokemon('Venusaur', (15, 13, 13), cp=2482, moves=['VINE_WHIP', 'FRENZY_PLANT', 'SLUDGE_BOMB']),
        # Pokemon('Muk', (9, 7, 4), cp=2486, form='Alola', moves=['SNARL', 'DARK_PULSE', 'SLUDGE_WAVE']),
        # Pokemon('Swampert', (0, 2, 14), cp=2500, moves=['WATER_GUN', 'HYDRO_CANNON', 'SLUDGE_WAVE']),
        # Pokemon('Empoleon', (0, 10, 14), cp=2495, moves=['WATERFALL', 'HYDRO_CANNON', 'DRILL_PECK']),
        # Pokemon('sirfetch’d', (4, 11, 12), cp=2485, form='Galarian', moves=['COUNTER', 'CLOSE_COMBAT', 'LEAF_BLADE']),

        # Pokemon('dewgong', (15, 8, 15), moves=['ICE_SHARD', 'ICY_WIND', 'WATER_PULSE']).maximize(max_cp=1500),
        # Pokemon('azumarill', (12, 13, 15), moves=['BUBBLE', 'ICE_BEAM', 'HYDRO_PUMP']).maximize(max_cp=1500),
        # registeel,LOCK_ON,FLASH_CANNON,FOCUS_BLAST,22,10,14,15
        # stunfisk_galarian,MUD_SHOT,ROCK_SLIDE,EARTHQUAKE,25,11,14,14
        # # altaria,DRAGON_BREATH,SKY_ATTACK,DRAGON_PULSE,26.5,14,12,13
        # skarmory,AIR_SLASH,SKY_ATTACK,FLASH_CANNON,26,11,13,10
    ]

    candidate_csv_text = ub.codeblock(
        '''
        registeel,LOCK_ON,FLASH_CANNON,FOCUS_BLAST,22,10,14,15
        stunfisk_galarian,MUD_SHOT,ROCK_SLIDE,EARTHQUAKE,25,11,14,14
        altaria,DRAGON_BREATH,SKY_ATTACK,DRAGON_PULSE,26.5,14,12,13

        skarmory,AIR_SLASH,SKY_ATTACK,FLASH_CANNON,26,11,13,10

        azumarill,BUBBLE,ICE_BEAM,HYDRO_PUMP,38,12,15,13
        dewgong,ICE_SHARD,ICY_WIND,WATER_PULSE,26.5,15,08,15

        umbreon,SNARL,FOUL_PLAY,LAST_RESORT,24.5,15,10,15

        hypno,CONFUSION,SHADOW_BALL,THUNDER_PUNCH,25.5,13,15,14

        # machamp-shadow,COUNTER,ROCK_SLIDE,CROSS_CHOP,18,5,11,10
        victreebel_shadow-shadow,RAZOR_LEAF,LEAF_BLADE,FRUSTRATION,22.5,4,14,14
        ''')

    candidates = []
    for line in candidate_csv_text.split('\n'):
        line = line.strip()
        if line.startswith('#'):
            continue
        if line:
            row = line.split(',')
            cand = Pokemon.from_pvpoke_row(row)
            candidates.append(cand)

    candidates += [
        # Pokemon('rattata', (7, 14, 14)).maximize(1500),
        Pokemon('pidgeot', (7, 14, 14)).maximize(1500),
        Pokemon('electrode', (7, 14, 14)).maximize(1500),
        # Pokemon('dragonair', (7, 14, 14)).maximize(1500),
        Pokemon('tauros', (7, 14, 14)).maximize(1500),
        Pokemon('wailord', (7, 14, 14)).maximize(1500),
        Pokemon('venomoth', (7, 14, 14)).maximize(1500),
        Pokemon('kingler', (7, 14, 14)).maximize(1500),
        Pokemon('haunter', (7, 14, 14)).maximize(1500),
        # Pokemon('gengar', (0, 14, 15)).maximize(1500),
        Pokemon('gengar', (15, 15, 15)).maximize(1500),
    ]

    #

    stats_data = {}
    for cand in candidates:
        cand.maximize(max_cp=1500)
        print('cand = {!r}'.format(cand))
        print('cand.adjusted = {}'.format(ub.repr2(cand.adjusted, nl=1, precision=2)))
        key = cand.name
        x = 2
        while key in stats_data:
            key = cand.name + str(int(x))
            x += 1
        stats_data[key] = cand.adjusted
    import pandas as pd

    stats_df = pd.DataFrame(stats_data)
    stats_df_T = stats_df.T
    import numpy as np
    stats_df_T['bulk'] = np.sqrt(stats_df_T.defense * stats_df_T.stamina)
    print(stats_df_T.sort_values('bulk'))

    import kwplot
    plt = kwplot.autoplt()
    from mpl_toolkits.mplot3d import Axes3D  # NOQA
    # import seaborn as sbn
    # sbn.set()

    fig = plt.gcf()
    fig.clf()
    # ax = plt.gca(projection='3d')

    pnums = kwplot.PlotNums(nCols=2, nRows=1)
    for pnum in pnums:
        ax = fig.add_subplot(*pnum, projection='3d')

        ax.cla()

        ax.set_xlabel('att')
        ax.set_ylabel('def')
        ax.set_zlabel('sta')

        ax.set_xlim(0, stats_df.values.max() * 1.05)
        ax.set_ylim(0, stats_df.values.max() * 1.05)
        ax.set_zlim(0, stats_df.values.max() * 1.05)

        origin = [10, 10, 10]

        for name, stat in stats_df.T.iterrows():
            print('stat = {!r}'.format(stat))
            x, y, z = stat.to_list()
            ox, oy, oz = origin
            ax.plot([ox, x], [oy, y], [oz, z], '-o', label=name)
            ax.text(x, y, z, s=name)

        kwplot.legend(ax=ax)


def whats_the_cp_for_evo():
    name = 'meganium'
    max_cp = 1500
    max_level = 44
    constraint = dict(max_cp=max_cp, max_level=max_level)
    base = Pokemon(name)
    ranking = base.league_ranking_table(**constraint)
    print(ranking)

    ivs000 = list(map(int, ranking.iloc[0][['iva', 'ivd', 'ivs']].tolist()))
    ivs100 = list(map(int, ranking.iloc[100][['iva', 'ivd', 'ivs']].tolist()))

    variants = {
        'iv_high': base.copy(ivs=[15, 15, 15]).maximize(**constraint),
        'iv_low': base.copy(ivs=[0, 0, 0]).maximize(**constraint),
        'ivs000': base.copy(ivs=ivs000).maximize(**constraint),
        'ivs100': base.copy(ivs=ivs100).maximize(**constraint),
    }

    for key, variant in variants.items():
        print('key = {!r}'.format(key))
        print('variant = {!r}'.format(variant))
        for mon in list(variant.family()):
            print(mon)
