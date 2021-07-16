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


def element_cup():
    elements = {'Water', 'Grass', 'Fire'}
    import pypogo
    candidates = []
    for mon in ub.ProgIter(pypogo.api.enumerate_all_pokemon()):
        if mon.can_evolve and not mon.is_evolved:
            if set(mon.typing) & elements:
                candidates.append(mon)

    # candidates = [mon.maximize(500) for mon in ub.ProgIter(candidates, desc='maximizing')]

    print('\n'.join(ub.oset([mon.to_pvpoke_import_line() for mon in candidates])))

    # # ub.argmin([mon.cp for mon in candidates])
    cand_names = {
        # mon.name.capitalize() + (' (Shadow)' if mon.shadow else '')
        mon.name
        for mon in candidates
    }
    liststr = ', '.join(cand_names)
    print(liststr)


def obstagoon():
    import pypogo
    mon = pypogo.Pokemon('obstagoon')

    mon.league_ranking_table(max_cp=1500, min_iv=10)
    z = mon.league_ranking_table(max_cp=2500, min_iv=10)

    have_ivs = [
        [10, 15, 14],
        [11, 13, 14],
        [10, 14, 14],
        [10, 11, 15],
        [10, 12, 13],
        [11, 10, 12],
        # [12, 11, 15],
    ]

    z.set_index(['iva', 'ivd', 'ivs']).iloc[have_ivs]


def lapras():
    import pypogo
    mon = pypogo.Pokemon.random('lapras', ivs=[1, 15, 12], level=41.5)
    mon = pypogo.Pokemon.random('lapras', ivs=[1, 15, 12], level=40.5)

    table = mon.league_ranking_table(2500)
    print('mon.stat_product_k = {!r}'.format(mon.stat_product_k))

    mon = pypogo.Pokemon.random('lapras', ivs=[1, 15, 12], level=40.5)
    mon = pypogo.Pokemon.random('lapras', ivs=[1, 15, 12], level=41)
    mon = pypogo.Pokemon.random('lapras', ivs=[1, 15, 12], level=41.5)
    mon = pypogo.Pokemon.random('lapras', ivs=[1, 15, 12], level=42)
    mon = pypogo.Pokemon.random('lapras', ivs=[1, 15, 12], level=42.5)
    print(table[table.stat_product_k >= mon.stat_product_k])

    # z = mon.league_ranking_table(max_cp=2500, min_iv=10)


def wild_lucky_encounter_rank_breakdown(mon, max_cp):
    print('\n\n!!!-----------')
    print('max_cp = {!r}'.format(max_cp))

    tables0 = {
        'wild_51': mon.league_ranking_table(max_cp, min_iv=0, max_level=51),
        'encounter_51': mon.league_ranking_table(max_cp, min_iv=10, max_level=51),
        # 'lucky_51': mon.league_ranking_table(max_cp, min_iv=12, max_level=51),

        # 'wild_47': mon.league_ranking_table(max_cp, min_iv=0, max_level=47),
        # 'encounter_47': mon.league_ranking_table(max_cp, min_iv=10, max_level=47),
        # 'lucky_47': mon.league_ranking_table(max_cp, min_iv=12, max_level=47),

        # 'wild_50': mon.league_ranking_table(max_cp, min_iv=0, max_level=50),
        # 'encounter_50': mon.league_ranking_table(max_cp, min_iv=10, max_level=50),
        # 'lucky_50': mon.league_ranking_table(max_cp, min_iv=12, max_level=50),

        # 'wild_41': mon.league_ranking_table(max_cp, min_iv=0, max_level=41),
        # 'encounter_41': mon.league_ranking_table(max_cp, min_iv=10, max_level=41),
        # 'lucky_41': mon.league_ranking_table(max_cp, min_iv=12, max_level=41),

        # 'wild_40': mon.league_ranking_table(max_cp, min_iv=0, max_level=40),
        # 'encounter_40': mon.league_ranking_table(max_cp, min_iv=10, max_level=40),
        # 'lucky_40': mon.league_ranking_table(max_cp, min_iv=12, max_level=40),
    }

    tables = {}
    rank_cols = []
    for key, val in tables0.items():
        col = key + '_rank'
        rank_cols.append(col)
        val.index.name = col
        val = val.set_index(['iva', 'ivd', 'ivs'])
        # val.drop
        val[col] = val['rank']
        val = val.drop('rank', axis=1)
        val = val.drop('percent', axis=1)
        tables[key] = val.copy()

    for key, val in tables.items():
        col = key + '_rank'
        for key1, val1 in tables.items():
            col1 = key1 + '_rank'
            if key != key1:
                common = val1.index.intersection(val.index)
                val.loc[common, col1] = val1.loc[common, col1]

    for key, table in tables.items():
        print('\n--key = {!r}'.format(key))
        first_part = ub.oset(table.columns) - rank_cols
        table = table.reindex(list(first_part) + rank_cols, axis=1)

        #
        if 1:
            # Add info about
            raid_level_base = 20
            # raid_level_boost = 25
            raid_cps = []
            for ivs in table.index:
                raid_mon = mon.copy(level=raid_level_base, ivs=ivs)
                raid_cps.append(raid_mon.cp)
            table['raid_cp'] = raid_cps

        tables[key] = table
        print(table.to_string(max_rows=50))

    return tables


def compute_breakpoints(mon1, mon2, move):
    """
    TODO:
        - [ ] Search over the range of mon1 attack ivs and mon2 defense ivs
        while still maximizing for the CP cap.

    Example:
        import pypogo
        mon1 = pypogo.Pokemon.random('deoxys', form='defense', moves=['counter', 'psycho boost', 'rock slide']).maximize(1500)
        mon2 = pypogo.Pokemon.random('ninetales', form='alola').maximize(1500)

        move = mon1.pvp_fast_move
        compute_breakpoints(mon1, mon2, move)
    """
    import numpy as np
    from pypogo.battle import compute_move_effect
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

    # Solve for points where the damage will change

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

    print('move = {!r}'.format(move))
    print('damage_points_ = {!r}'.format(damage_points_))
    print('break_points_ = {!r}'.format(break_points_))


def attack_breakpoint_grid(mon1, mon2, move):
    """
    Looks over the range of possible attack / defense stats two mon could
    have and looks for how much damage they are doing
    """
    league_cp = 1500

    mon1_min_iv = 10
    mon2_min_iv = 0

    mon1_ranks = mon1.league_ranking_table(league_cp, min_iv=mon1_min_iv)
    mon2_ranks = mon2.league_ranking_table(league_cp, min_iv=mon2_min_iv)

    mon2_ranks = mon2_ranks[mon2_ranks['rank'] > 200]

    attack_range = mon1_ranks.attack.unique()
    defense_range = mon2_ranks.defense.unique()
    attack_range.sort()
    defense_range.sort()

    import numpy as np
    from pypogo.battle import compute_move_effect
    #
    # Breakpoints for each move
    mon1.adjusted['attack']
    info = compute_move_effect(mon1, mon2, move)

    attack_shadow_factor = info['attack_shadow_factor']
    pvp_bonus_multiplier = info['pvp_bonus_multiplier']
    effectiveness = info['effectiveness']
    defense_shadow_factor = info['defense_shadow_factor']
    defense_modifier_factor = info['defense_modifier_factor']
    attack_modifier_factor = info['attack_modifier_factor']
    stab = info['stab']
    charge = 1

    attack_power = (
        pvp_bonus_multiplier *
        charge *
        stab *
        attack_range[:, None] *
        attack_modifier_factor *
        attack_shadow_factor *
        effectiveness
    )

    defense_power = (
        defense_range[None, :] *
        defense_modifier_factor *
        defense_shadow_factor
    )

    half = 0.5  # not sure why a half is in the formula
    move_power = move['power']

    damage = np.floor(half * move_power * attack_power / defense_power) + 1
    import xarray as xr
    xr.DataArray(damage, dims=['a', 'd'], coords={'a': attack_range.ravel(), 'd': defense_range.ravel()})
    import pandas as pd
    df = pd.DataFrame(damage, index=attack_range.ravel(), columns=defense_range.ravel())
    df.index.name = 'atk'
    df.columns.name = 'def'
    print(df.T.to_string())

    damage_vals = np.unique(df.values)
    max_damage = damage_vals.max()
    df >= max_damage

    # TODO: write code such that the takeaways are more interpretable here


def deoxys():
    import pypogo
    # mon = pypogo.Pokemon.random('registeel', moves=['lock on', 'flash cannon', 'focus blast'])
    mon = pypogo.Pokemon.random('deoxys', form='defense')

    # https://gamepress.gg/pokemongo/deoxys-defense-pvp-iv-deep-dive-analysis

    #https://www.reddit.com/r/TheSilphRoad/comments/oc6wtn/deoxys_defense_pvp_iv_deep_dive_analysis/h3tc4jq/?context=3
    great_optimal_spreads = [
        tuple([int(x) for x in p.strip().split(',') if x])
        for p in ub.codeblock(
            '''
            10,15,13
            10,10,15
            11,10,13
            12,15,15
            11,13,12
            13,15,13
            13,11,15
            12,13,10
            11,15,11
            11,15,10
            14,12,13
            15,14,10
            15,10,12
            ''').split('\n')]

    optimal_spreads_ultra = [
        tuple([int(x) for x in p.strip().split(',') if x])
        for p in ub.codeblock(
            '''
            15,11,12
            15,11,10
            15,13,11
            15,10,12
            15,15,10
            15,10,10
            15,12,11
            15,12,15
            14,10,14
            15,11,15
            15,10,15
            ''').split('\n')]

    have_ivs = [tuple([int(x) for x in p.strip().split(',') if x]) for p in ub.codeblock(
        '''
        12,10,14
        12,15,13,
        10,11,13
        11,13,14,
        12,12,12,
        11,12,14,
        13,14,12,
        11,10,12
        11,15,10,
        13,12,15,
        13,14,13,
        13,10,14
        10,14,15
        13,10,10,
        11,11,13,
        15,15,13,
        13,11,12
        15,13,15
        11,14,13,
        10,11,12,
        10,13,15,
        12,11,11,
        11,10,14
        14,10,14
        13,15,15,
        13,11,14
        15,12,12
        11,10,10
        14,10,15,
        10,13,11
        10,10,12,
        10,13,12,
        15,14,13
        15,13,10,
        12,14,14,
        11,12,11
        15,12,11
        11,12,10,
        15,12,10,
        12,10,12,
        11,10,11,
        15,15,12,
        13,12,12,
        11,12,12
        15,12,13,
        10,15,15
        11,13,12,
        10,10,13,
        10,11,13,
        14,15,15,
        14,11,11
        13,11,12
        11,10,12
        13,13,14
        15,11,14
        14,12,10
        11,14,12
        14,11,10,
        12,11,13,
        10,12,14,
        11,12,13,
        13,12,12
        11,13,11
        10,15,15,
        14,11,10,
        14,14,11,
        13,10,12
        12,10,15
        10,13,15,
        10,13,11,
        12,11,11,
        12,10,10
        12,10,14,
        10,11,13
        12,10,12,
        12,14,10,
        15,14,11,
        10,14,15
        14,10,13,
        11,14,12,
        14,12,15,
        11,12,11
        13,14,13
        13,10,11,
        10,12,12,
        15,12,12
        14,10,10,
        11,10,15,
        15,12,10,
        15,14,11,
        14,15,10,
        15,14,13,
        15,12,10,
        15,13,13,
        13,14,15,
        11,13,13,
        13,10,12,
        14,13,12,
        14,10,13,
        10,10,14,
        15,15,13,
        10,12,14,
        14,11,14,
        12,15,11,
        14,14,13,
        13,12,15
        13,11,13
        12,15,10
        15,15,12
        15,12,14
        10,13,15,
        11,14,12
        10,13,13,
        11,11,12,
        10,11,11
        15,12,14,
        13,12,11,
        13,12,15,
        10,12,13
        10,10,12
        11,15,11
        10,10,12,
        10,12,14,
        10,12,14,
        10,13,10,
        10,13,12,
        10,14,14,
        11,12,14,
        11,14,12,
        11,14,15,
        11,15,11,
        11,15,11,
        11,15,12,
        11,15,12,
        12,10,12,
        12,11,12,
        12,12,15,
        12,14,11,
        12,14,15,
        12,15,11,
        12,15,12
        12,15,12,
        13,11,13
        13,12,10
        13,12,13,
        13,13,10,
        13,13,11,
        13,15,10,
        13,15,11,
        13,15,11,
        14,10,12,
        14,11,10,
        14,11,10,
        14,13,11
        14,13,14,
        15,10,12
        15,11,10,
        15,11,11,
        15,12,11
        ''').split('\n')]
    print(ub.repr2(ub.find_duplicates(have_ivs), nl=-1))
    print(len(set(have_ivs)) / 216)

    print(set(great_optimal_spreads) & (set(have_ivs)))
    print(set(optimal_spreads_ultra) & (set(have_ivs)))
    # wild_lucky_encounter_rank_breakdown(mon)
    # def wild_lucky_encounter_rank_breakdown(mon):
    max_cp = 1500
    tables = wild_lucky_encounter_rank_breakdown(mon, max_cp)
    great_table = table = tables['encounter_51']
    ultra_tables = wild_lucky_encounter_rank_breakdown(mon, 2500)
    ultra_table = ultra_tables['encounter_51']

    if 1:
        # The DD breakpoint attributes we care about
        # Seems like only 13, 11, 15, and 13, 10, 15 satisfy this
        print(table[(table.stamina >= 98) & (table.attack >= 101.5)])
        print(table[(table.stamina >= 98) & (table.attack >= 101)])
        print(table[(table.stamina >= 98)])

    if great_optimal_spreads:

        print('have')
        print(table.loc[table.index.intersection(have_ivs)].to_string())

        print(table.loc[table.index.intersection(have_ivs)].iloc[0:9].to_string())

        print('interest')
        print(table.loc[table.index.intersection(great_optimal_spreads)])

        print('have-great-of-interest')
        print(table.loc[table.index.intersection(great_optimal_spreads).intersection(have_ivs)])

        print('have-ultra-of-interest')
        print(ultra_table.loc[ultra_table.index.intersection(optimal_spreads_ultra).intersection(have_ivs)])


    have = table.loc[set(have_ivs)]
    efficient_have_ivs = []
    for ivs, row in have.iterrows():
        is_worse = row[['attack', 'defense', 'stamina']] < have[['attack', 'defense', 'stamina']]
        worse_than = is_worse.all(axis=1).sum()
        if worse_than == 0:
            efficient_have_ivs.append(ivs)
    have = table.loc[efficient_have_ivs].sort_values('encounter_51_rank')
    print(have[(have.stamina >= 98)])

    if have_ivs:
        table.loc[set(have_ivs)].sort_values('encounter_51_rank')
        x = table.loc[set(have_ivs)].sort_values('encounter_51_rank')
        print(x[(x.stamina >= 98)])
        print(x[(x.attack >= 102)])
        print(x[(x.defense >= 224)])
        # import pandas as pd
        # combo = pd.concat(list(tables.values()))
    # combo = combo.sort_values('stat_product_k')

    # https://www.reddit.com/r/TheSilphRoad/comments/oc6wtn/deoxys_defense_pvp_iv_deep_dive_analysis/h3tc4jq/?context=3
    max_cp = 2500
    ultra_tables = wild_lucky_encounter_rank_breakdown(mon, max_cp)
    ultra_table = ultra_tables['encounter_51']
    print('ultra interest')
    print(ultra_table.loc[ultra_table.index.intersection(optimal_spreads_ultra)])

    print('great interest')
    print(great_table.loc[great_table.index.intersection(great_optimal_spreads)])

    if 1:
        from pypogo.pvpoke_experiment import run_pvpoke_simulation
        # Test in PVP Poke
        top = table.loc[table.index.intersection(have_ivs)].iloc[0:2]
        interest = table.loc[table.index.intersection(great_optimal_spreads).intersection(have_ivs)]
        cands = ub.oset(top.index.values.tolist()) | ub.oset(interest.index.values.tolist())
        mons = [
            # pypogo.Pokemon('Deoxys', form='defense', ivs=ivs, moves=['Counter', 'Rock Slide', 'Psycho Boost']).maximize(1500)
            pypogo.Pokemon('Deoxys', form='defense', ivs=ivs, moves=['Counter', 'Thunderbolt', 'Psycho Boost']).maximize(1500)
            for ivs in cands
        ]
        results = run_pvpoke_simulation(mons)

        rows = []
        for (nas, nds), data in results.items():
            print('nas, nds = {}, {}'.format(nas, nds))
            print(data.sum(axis=1))

            for name, row_ in data.iterrows():
                row = {}
                row['name'] = name
                row['score'] = row_.sum()

                x = (row_ > 500)
                win_vs = x[x].index

                row['wins'] = (row_ > 500).sum()
                row['losses'] = (row_ < 500).sum()
                row['ties'] = (row_ == 500).sum()
                row['win_vs'] = set(win_vs.tolist())

                row['nas'] = nas
                row['nds'] = nds
                rows.append(row)

        # TODO: write the proper analysis for dropped matchups

        df2 = pd.DataFrame(rows)
        summary = {}
        rows2 = []
        for name, subdf in df2.groupby('name'):
            row3 = {'name': name}
            for _, row2_ in subdf.iterrows():
                winkey = 'wins-{}-{}'.format(row2_['nas'], row2_['nds'])
                row3[winkey] = row2_['wins']
                winvskey = 'wins-vs-{}-{}'.format(row2_['nas'], row2_['nds'])
                row3[winvskey] = row2_['win_vs']
            row3['score'] = subdf['score'].sum()
            row3['total_wins'] = subdf['wins'].sum()
            row3['total_ties'] = subdf['ties'].sum()
            rows2.append(row3)
        df3 = pd.DataFrame(rows2).set_index('name')
        print(df3)

        summary = {}
        rows2 = []
        for name, subdf in df2.groupby('name'):
            row3 = {'name': name}
            drops = {}
            for _, row2_ in subdf.iterrows():
                winkey = 'wins-{}-{}'.format(row2_['nas'], row2_['nds'])
                row3[winkey] = row2_['wins']
                winvskey = 'wins-vs-{}-{}'.format(row2_['nas'], row2_['nds'])
                dropvskey = 'drop-vs-{}-{}'.format(row2_['nas'], row2_['nds'])
                all_wins_vs = set.union(*df3[winvskey])
                drops[dropvskey] = all_wins_vs - row2_['win_vs']

            row3['drops'] = set.union(*drops.values())
            row3['score'] = subdf['score'].sum()
            row3['total_wins'] = subdf['wins'].sum()
            row3['total_ties'] = subdf['ties'].sum()
            rows2.append(row3)
        df4 = pd.DataFrame(rows2).set_index('name')
        print(df4.sort_values('total_wins'))
        print(ub.repr2(df4.drops.to_dict()))


        df['drops-vs-0-0'] = df['wins-vs-0-0'].apply(lambda x: all_wins_vs - x)

    # Prob getting it
    # https://math.stackexchange.com/questions/102673/what-is-the-expected-number-of-trials-until-x-successes
    p_success = 1 / (6 ** 3)
    expected_num_trials = 1 / p_success
    print('expected_num_trials = {!r}'.format(expected_num_trials))

    1 - ((1 - (2 / (6 ** 3))) ** 20)
    table[table.raid_cp == 1275]
    table[table.raid_cp == 1274]
    table[table.raid_cp == 1245]

    targets = table.loc[great_optimal_spreads + optimal_spreads_ultra]
    optimal_raid_cps = targets.sort_values('raid_cp').raid_cp
    print('optimal_raid_cps = {!r}'.format(optimal_raid_cps))
    flags = (table.raid_cp.values[:, None] == optimal_raid_cps.values[None, :]).sum(axis=1).ravel() > 0
    candidates = table.iloc[flags]

    to_check_mons = [
        pypogo.Pokemon('Deoxys', form='defense', ivs=ivs, moves=['Counter', 'Rock Slide', 'Psycho Boost']).maximize(1500)
        for ivs in have_ivs
    ]



    import scipy.stats
    scipy.stats.nbinom.cdf(1, 10, p_success)
    # scipy.stats.nbinom?
    # scipy.stats.nbinom.stats(100, p)
    # z = scipy.stats.binom(20, p)
    # 1 - z.cdf(1)
