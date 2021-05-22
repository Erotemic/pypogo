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
        key: [mon.maximize(max_cp, ivs='maximize', max_level=51)
                 for mon in ub.ProgIter(base.family(), desc='maximizing')]
        for key, max_cp in league_cps.items()
    }

    others = [
        'meganium',
        'ampharos',
        'typhlosion',
        'politoed',
        'darkrai',
        'hypno',
        'ninetales',
        'Raichu',
        # 'regice',
        # 'castform_snowy',
    ]

    for key, candidates in league_families.items():
        max_cp = league_cps[key]
        for name in ub.ProgIter(others, 'maximize others'):
            mon = Pokemon(name).maximize(max_cp, ivs='maximize', max_level=51)
            candidates.append(mon)

    for key, candidates in league_families.items():

        max_cp = league_cps[key]

        import seaborn as sns
        import kwplot
        kwplot.autompl()
        sns.set()

        type_to_cand = ub.group_items(candidates, lambda c: c.typing)
        pnum_ = kwplot.PlotNums(nSubplots=len(type_to_cand), nCols=1)
        for typing, cands in type_to_cand.items():
            rows = []
            for mon in cands:
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

            kwplot.figure(fnum=max_cp, pnum=pnum_())
            ax = sns.barplot(data=df, x='stat', y='name', hue='stat_type', orient='h')

            if max_cp == 2500:
                ax.set_xlim(0, 250)
            else:
                ax.set_xlim(0, 200)

        kwplot.set_figtitle('Best Adjusted Stats for {}'.format(key))


def floor_iv_ranks():
    from pypogo.pokemon import Pokemon
    base = Pokemon('mew')
    df = base.league_ranking_table(max_cp=1500, min_iv=10)
    print(df.to_string())

    from pypogo.pokemon import Pokemon
    base = Pokemon('Giratina', hints='origin', ivs=[13, 14, 15])
    df = base.league_ranking_table(max_cp=2500, min_iv=10)
    print(df.to_string())
    print(base.league_ranking(max_cp=2500, min_iv=10))

    base = Pokemon('mew', ivs=[10, 14, 15]).maximize(max_cp=1500)
    print(base.league_ranking(min_iv=10))

    base = Pokemon('mew', ivs=[15, 12, 11]).maximize(max_cp=1500)
    print(base.league_ranking(min_iv=10))


def cress_damage():
    from pypogo.battle import compute_move_effect
    from pypogo.pokemon import Pokemon
    base = Pokemon.random('cresselia', moves=['psycho cut', 'moonblast', 'futuresight']).maximize(2500)

    mon1 = base
    mon2 = Pokemon.random('snorlax').maximize(2500)

    move = base.pvp_charge_moves[0]
    print('move = {!r}'.format(move))
    effect = compute_move_effect(mon1, mon2, move, charge=1.0)
    damage = effect['damage']
    print('damage = {!r}'.format(damage))
    dpe = damage / (-move['energy_delta'])
    print('dpe = {!r}'.format(dpe))

    move = base.pvp_charge_moves[1]
    print('move = {!r}'.format(move))
    effect = compute_move_effect(mon1, mon2, move, charge=1.0)
    damage = effect['damage']
    print('damage = {!r}'.format(damage))
    dpe = damage / (-move['energy_delta'])
    print('dpe = {!r}'.format(dpe))

    # Shadow Mewtwo vs Umbreon
    # https://www.youtube.com/watch?v=BP50jy_2lco
    from pypogo.battle import compute_move_effect
    from pypogo.pokemon import Pokemon
    umbr1 = Pokemon.random('umbreon').maximize(2500, ivs='maximize').init_pvp_state()
    umbr2 = Pokemon.random('umbreon').maximize(2500, ivs=[0, 0, 0]).init_pvp_state()
    print('umbr1.hp = {!r}'.format(umbr1.hp))
    print('umbr2.hp = {!r}'.format(umbr2.hp))

    attacker1 = Pokemon.random('mewtwo', moves=['psycho cut', 'psystrike', 'focus blast'], shadow=True).maximize(2500, ivs='maximize').init_pvp_state()
    print('attacker1.adjusted = {!r}'.format(attacker1.adjusted))
    attacker2 = Pokemon.random('mewtwo', moves=['psycho cut', 'psystrike', 'focus blast'], shadow=True).maximize(2500, ivs=[15, 0, 0]).init_pvp_state()
    effect1 = compute_move_effect(attacker1, umbr1, attacker1.pvp_charge_moves[1])
    effect2 = compute_move_effect(attacker2, umbr2, attacker2.pvp_charge_moves[1])
    print('effect1 = {}'.format(ub.repr2(effect1, nl=1)))
    print('effect2 = {}'.format(ub.repr2(effect2, nl=1)))

    attacker1 = Pokemon.random('blaziken', moves=['focus blast']).maximize(2500, ivs='maximize').init_pvp_state()
    attacker2 = Pokemon.random('blaziken', moves=['focus blast']).maximize(2500, ivs=[15, 0, 0]).init_pvp_state()
    effect1 = compute_move_effect(attacker1, umbr1, attacker1.pvp_charge_moves[0])
    effect2 = compute_move_effect(attacker2, umbr2, attacker2.pvp_charge_moves[0])
    print('effect1 = {}'.format(ub.repr2(effect1, nl=1)))
    print('effect2 = {}'.format(ub.repr2(effect2, nl=1)))

    attacker1 = Pokemon.random('togekiss', moves=['charm', 'ancient power', 'Dazzling gleam']).maximize(2500, ivs='maximize').init_pvp_state()
    attacker2 = Pokemon.random('togekiss', moves=['charm', 'ancient power', 'Dazzling gleam']).maximize(2500, ivs=[15, 0, 0]).init_pvp_state()
    attacker1.modifiers['attack'] = 2
    attacker2.modifiers['attack'] = 2
    effect1 = compute_move_effect(attacker1, umbr1, attacker1.pvp_charge_moves[1])
    effect2 = compute_move_effect(attacker2, umbr2, attacker2.pvp_charge_moves[1])
    print('effect1 = {}'.format(ub.repr2(effect1, nl=1)))
    print('effect2 = {}'.format(ub.repr2(effect2, nl=1)))

    attacker1.modifiers['attack'] = 4
    attacker2.modifiers['attack'] = 4
    effect1 = compute_move_effect(attacker1, umbr1, attacker1.pvp_charge_moves[1])
    effect2 = compute_move_effect(attacker2, umbr2, attacker2.pvp_charge_moves[1])
    print('effect1 = {}'.format(ub.repr2(effect1, nl=1)))
    print('effect2 = {}'.format(ub.repr2(effect2, nl=1)))

    attacker1 = Pokemon.random('lucario', moves=['Counter', 'Power Up Punch', 'Aura Sphere']).maximize(2500, ivs='maximize').init_pvp_state()
    attacker2 = Pokemon.random('lucario', moves=['Counter', 'Power Up Punch', 'Aura Sphere']).maximize(2500, ivs=[15, 0, 0]).init_pvp_state()
    attacker1.modifiers['attack'] = 3
    attacker2.modifiers['attack'] = 3
    effect1 = compute_move_effect(attacker1, umbr1, attacker1.pvp_charge_moves[1])
    effect2 = compute_move_effect(attacker2, umbr2, attacker2.pvp_charge_moves[1])
    print('effect1 = {}'.format(ub.repr2(effect1, nl=1)))
    print('effect2 = {}'.format(ub.repr2(effect2, nl=1)))

    # Which pokemon in UL has the highest attack?
    import pypogo
    api = pypogo.global_api(new=True)
    all_mon_names = set(pypogo.api.name_to_stats.keys())
    hp_users = set()
    for name in ub.ProgIter(all_mon_names):
        fast_moves = pypogo.Pokemon(name).candidate_moveset()['fast']
        if 'Hidden Power' in fast_moves:
            hp_users.add(name)

    bad = set()
    name_to_ul_attack = {}
    for name in ub.ProgIter(all_mon_names - hp_users):
        try:
            mon = pypogo.Pokemon.random(name).maximize(2500, ivs=[15, 0, 0])
            name_to_ul_attack[name] = mon.adjusted['attack']
        except Exception:
            bad.add(name)

    top_attackers = ub.sorted_vals(name_to_ul_attack)
    print('top_attackers = {}'.format(ub.repr2(top_attackers, nl=1, precision=1)))

    attacker1 = pypogo.Pokemon.random('absol', moves=['megahorn']).maximize(2500)
    effect1 = compute_move_effect(attacker1, umbr1, attacker1.pvp_charge_moves[0])
    print('effect1 = {}'.format(ub.repr2(effect1, nl=1)))

    pypogo.Pokemon.random('archeops')
    attacker1 = pypogo.Pokemon.random('deoxys', moves=['Zap Cannon']).maximize(2500, ivs=[15, 0, 0])
    effect1 = compute_move_effect(attacker1, umbr1, attacker1.pvp_charge_moves[0])
    print('effect1 = {}'.format(ub.repr2(effect1, nl=1)))

    attacker2 = Pokemon.random('alakazam', moves=['psycho cut', 'Fire Punch', 'focus blast'], shadow=True).maximize(2500, ivs=[15, 0, 0]).init_pvp_state()
    effect2 = compute_move_effect(attacker2, umbr2, attacker2.pvp_charge_moves[1])
    print('effect2 = {}'.format(ub.repr2(effect2, nl=1)))

    attacker1 = pypogo.Pokemon.random('absol', moves=['snarl', 'megahorn'], shadow=True).maximize(2500, ivs=[15, 0, 0]).init_pvp_state()
    effect1 = compute_move_effect(attacker1, umbr1, attacker1.pvp_charge_moves[0])
    print('effect1 = {}'.format(ub.repr2(effect1, nl=1)))

    pypogo.Pokemon.random('rampardos')

    # FIXME deoxys forms doesn't work
    pypogo.Pokemon('deoxys', hints='attack')
    pypogo.Pokemon('deoxys', hints='defense')


def breakpoints():
    from pypogo.pokemon import Pokemon
    import numpy as np
    # import math
    mon1 = Pokemon.random('melmetal', ivs=[15, 15, 15], level=40, moves=['Thunder Shock', 'Super_power'])
    print('mon1.adjusted = {!r}'.format(mon1.adjusted))

    mon2 = Pokemon.random('dialga', ivs=[15, 15, 15], level=40, moves=['Dragon Breath', 'Iron Head'])

    from pypogo.battle import compute_move_effect
    move = mon1.pvp_fast_move
    move = mon1.pvp_charge_moves[0]

    for move_name in ub.flatten(mon1.candidate_moveset().values()):
        move = mon1.api.get_move_info(move_name)[1][0]
        #
        # Breakpoints for each move
        mon1.adjusted['attack']
        info = compute_move_effect(mon1, mon2, move)

        # adjusted_attack = info['adjusted_attack']
        attack_shadow_factor = info['attack_shadow_factor']
        pvp_bonus_multiplier = info['pvp_bonus_multiplier']
        effectiveness = info['effectiveness']
        stab = info['stab']
        attack_power = info['attack_power']

        # adjusted_defense = info['adjusted_defense']

        defense_power = info['defense_power']

        move_power = move['power']
        half = 0.5

        damage_points = np.arange(info['damage'] // 2, int(info['damage'] * 2))

        # damage_points = np.arange(1, 6)
        break_points = (
            ((damage_points - 1) * defense_power) /
            (half * move_power * stab * effectiveness * attack_shadow_factor *
             pvp_bonus_multiplier)
        )

        min_attack = mon1.adjusted['attack'] - 15
        max_attack = mon1.adjusted['attack'] + 15

        flags = break_points > min_attack
        flags &= break_points < max_attack

        damage_points_ = damage_points[flags]
        break_points_ = break_points[flags]

        print('move_name = {!r}'.format(move_name))
        print('damage_points_ = {!r}'.format(damage_points_))
        print('break_points_ = {!r}'.format(break_points_))

    #
    # Bulkpoints for each move
    for move_name in ub.flatten(mon2.candidate_moveset().values()):
        move = mon1.api.get_move_info(move_name)[1][0]

        info = compute_move_effect(mon2, mon1, move)
        attack_power = info['attack_power']
        defense_modifier_factor = info['defense_modifier_factor']
        defense_shadow_factor = info['defense_shadow_factor']
        move_power = move['power']

        damage_points = np.arange(info['damage'] // 2, int(info['damage'] * 2))
        half = 0.5

        bulk_points = (
            (half * move_power * attack_power) /
            ((damage_points - 1) * defense_modifier_factor * defense_shadow_factor)
        )

        min_defense = mon1.adjusted['defense'] - 15
        max_defense = mon1.adjusted['defense'] + 15
        flags = bulk_points > min_defense
        flags &= bulk_points < max_defense

        damage_points_ = damage_points[flags]
        bulk_points_ = bulk_points[flags]

        print('move_name = {!r}'.format(move_name))
        print('damage_points_ = {!r}'.format(damage_points_))
        print('bulk_points_ = {!r}'.format(bulk_points_))


def move_chart():
    import pypogo
    api = pypogo.api  # NOQA

    import kwplot
    kwplot.autompl()
    import seaborn as sns
    sns.set()

    longform = []
    # for move in api.pvp_fast_moves.values():
    for move in api.pvp_charged_moves.values():
        assert len(move) == 1
        move = move[0]
        if move.get('buffs', None):
            move['hasbuff'] = True
            move.get('buffs')['activation_chance']
            move.pop('buffs', None)
        longform.append(move)

    import pandas as pd
    df = pd.DataFrame(longform)

    # sns.scatterplot(data=df, x='energy_delta', y='power', color='type', label='name')
    sns.scatterplot(data=df,
                    x='energy_delta',
                    y='power',
                    label='name')

    df['dps'] = df['power'] / df['turn_duration']
    df['eps'] = df['energy_delta'] / df['turn_duration']
    df['dpe'] = df['dps'] / df['energy_delta']
    dpe = df['dpe'].copy()
    dpe[df.energy_delta == 0] = 0
    df['dpe'] = dpe
    df['prod'] = df['dps'] * df['eps']
    df = df.sort_values('prod')

    df = df.sort_values('dpe')
    # df = df[df['type'] == 'Steel']
    df = df[df['type'] == 'Ice']
    print(df.to_string())

    """

    import sympy as sym
    d, e, s = sym.symbols('d, e, s')

    dps = d / s
    eps = e / s
    dpe = d / e

    prod = dps * dpe * eps

    prod = dps * eps
    print('prod = {!r}'.format(prod))
    """

    # TODO: Seaborn table

    from matplotlib.table import Table
    # import numpy as np
    plt = kwplot.autoplt()
    xlabel = 'dps'
    ylabel = 'eps'

    # https://stackoverflow.com/questions/10194482/custom-matplotlib-plot-chess-board-like-table-with-colored-cells

    x_basis = df[xlabel].unique()
    y_basis = df[ylabel].unique()

    fig = kwplot.figure(fnum=1, doclf=True)
    ax = fig.gca()
    ax.set_axis_off()
    ax.set_axis_off()

    ax = plt.gca()
    tb = Table(ax, bbox=[0, 0, 1, 1])

    nrows = len(x_basis)
    ncols = len(y_basis)
    x_basis.max() / np.diff(sorted(x_basis)).min()
    y_basis.max() / np.diff(sorted(y_basis)).min()
    width = 1 / nrows
    height = 1 / ncols
    print('nrows = {!r}'.format(nrows))
    print('ncols = {!r}'.format(ncols))
    print('height = {!r}'.format(height))
    print('width = {!r}'.format(width))
    # , height = 1.0 / ncols, 1.0 / nrows

    print(df.to_string())

    table_cells = []
    for rval, row_group in df.groupby('eps'):
        for cval, cell_group in row_group.groupby('dps'):
            if len(cell_group) > 1:
                eps = cell_group['eps'].iloc[0]
                dps = cell_group['dps'].iloc[0]
                text = '\n'.join(cell_group['name'])
                # text += ('\neps = {:.2f}'.format(eps))
                # text += ('\ndps = {:.2f}'.format(dps))
                table_cells.append({
                    'eps': eps,
                    'dps': dps,
                    'score': (dps * eps) ** 0.5,
                    'text': text,
                })

    for i, label in enumerate(x_basis):
        tb.add_cell(i, -1, width, height, text='{:.2f}'.format(label),
                    loc='right', edgecolor='none', facecolor='none')
    # Column Labels...
    for j, label in enumerate(y_basis):
        tb.add_cell(-1, j, width, height / 2, text='{:.2f}'.format(label),
                    loc='center', edgecolor='none', facecolor='none')

    for rval in y_basis:
        for cval in x_basis:
            color = 'orange'
            tb.add_cell(rval, cval, width, height, loc='center',
                        facecolor=color)

    for cell in table_cells:
        color = 'pink'
        rval = cell['eps']
        cval = cell['dps']
        tb.add_cell(
            rval, cval, width, height, text=text, loc='center',
            facecolor=color, fontproperties={
                # 'size': 22
                'size': 'xx-large',
            })

    ax.add_table(tb)
    # ax.set_xlim(-1, 1)
    # ax.set_ylim(-1, 1)

    # dfcell = pd.DataFrame(table_cells)
    # pv = dfcell.pivot("eps", "dps", "score")

    # sns.heatmap(data=pv, annot=True, fmt="f", linewidths=.5, ax=ax)


def hundo_probability():
    """
    # https://www.reddit.com/r/PokemonGOBattleLeague/comments/niegs9/minimum_ivs_for_master_league_missing_out_while/

    # natural hundo 0.0244140625%
    # 1 way out of 16 possibilities for each stat
    ((1 / 16) ** 3) * 100

    # special hundo: 0.46296296296296285%
    # 1 ways out of 6 possibilities for each stat
    ((1 / 6) ** 3) * 100

    # purified hundo 0.6591796875%
    # 3 ways out of 16 posibilities result in a hundo stat
    ((3 / 16) ** 3) * 100
    """
    probs = {
        'natural_hundo': ((1 / 16) ** 3),
        'encounter_hundo': ((1 / 6) ** 3),
        'purified_hundo': ((3 / 16) ** 3),
    }

    import scipy.optimize
    import numpy as np

    def find_halfway_point(num_trials, p):
        num_trials = np.asarray(num_trials).ravel()[0]
        prob_failure = (1 - p) ** num_trials
        prob_success = 1 - prob_failure

        target = 0.5
        loss = float(prob_success - target) ** 2
        if prob_success < target:
            loss += 1
        return loss

    for k, p in probs.items():
        # num_trials = 100
        # prob_failure = (1 - p) ** num_trials
        # prob_success = 1 - prob_failure
        result = scipy.optimize.minimize(find_halfway_point, x0=1e1, args=(p,), method='Nelder-Mead')
        num_trials = np.asarray(np.ceil(result.x)).ravel()[0]
        # print('result = {!r}'.format(result))
        prob_failure = (1 - p) ** num_trials
        prob_success = 1 - prob_failure
        print(f'{k} after {num_trials} trials = {prob_success * 100:.2f} %')
