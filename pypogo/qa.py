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


def hows_my_medicham_doing():
    base = Pokemon('medicham', ivs=[7, 15, 14], level=46)
    rankings = base.league_ranking_table()
    classic_rankings = base.league_ranking_table(max_level=41)

    import pandas as pd

    level = base.level
    while level < 49.5:
        print('level = {!r}'.format(level))
        base = base.copy(level=level)

        print('base.stat_product_k = {!r}'.format(base.stat_product_k))
        xl_row = rankings[rankings.stat_product_k < base.stat_product_k].iloc[0:1]
        classic_row = classic_rankings[classic_rankings.stat_product_k < base.stat_product_k].iloc[0:1]
        print(pd.concat([xl_row, classic_row]))
        level += 0.5


def plot_stats_comparison():
    from pypogo.pokemon import Pokemon
    base = Pokemon('eevee')

    league_cps = {
        'Great': 1500,
        'Ultra': 2500,
    }

    league_families = {
        key: [mon.maximize(val, ivs='maximize', max_level=51)
                 for mon in ub.ProgIter(base.family(), desc='maximizing')]
        for key, val in league_cps.items()
    }

    for key, leauge_family in league_families.items():

        rows = []
        for mon in leauge_family:
            mon.base_stats
            row = {
                'name': mon.display_name() + '\n' + str(mon.cp) + ' ' + str(mon.ivs),
                'stat_product': mon.stat_product,
            }
            row.update(mon.adjusted)
            rows.append(row)

        expanded = []
        for row in rows:
            orig = row.copy()
            row = ub.dict_union(orig, {'stat': row['attack'], 'stat_type': 'attack'})
            expanded.append(row)
            row = ub.dict_union(orig, {'stat': row['defense'], 'stat_type': 'defense'})
            expanded.append(row)
            row = ub.dict_union(orig, {'stat': row['stamina'], 'stat_type': 'stamina'})
            expanded.append(row)
            row = ub.dict_union(orig, {'stat': row['stat_product'] ** (1 / 3), 'stat_type': 'stat_prod^(1/3)'})
            expanded.append(row)

        import pandas as pd
        df = pd.DataFrame(expanded)

        import seaborn as sns
        import kwplot
        kwplot.autompl()
        sns.set()

        kwplot.figure(fnum=league_cps[key])
        ax = sns.barplot(data=df, y='stat', x='name', hue='stat_type')
        ax.set_title('Best Adjusted Stats for {}'.format(key))
