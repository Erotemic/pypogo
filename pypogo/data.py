
def xl_candy_stats():
    import ubelt as ub
    import yaml
    import io
    file = io.StringIO()
    # Level: [num_transfered, num_xl_candies_got]
    file.write(ub.codeblock(
        '''
        # Level: [num_transfered, num_xl_candies_got]
        Beldum:
            6:  [1, 0]
            7:  [1, 0]
            9:  [2, 0]
            11: [1, 0]
            12: [1, 0]
            13: [1, 0]
            14: [2, 0]
            15: [2, 0]
            16: [3, 1]
            17: [1, 0]
            18: [2, 2]
            22: [2, 0]
            23: [2, 0]
            24: [1, 1]
            26: [1, 0]
            27: [1, 0]
            28: [3, 2]
            29: [1, 1]
            34: [1, 1]
        Meditite:
            2:  [1, 0]
            3:  [1, 0]
            4:  [1, 0]
            5:  [1, 0]
            6:  [5, 0]
            7:  [5, 1]
            8:  [1, 0]
            9:  [1, 0]
            10: [3, 0]
            11: [5, 0]
            12: [5, 1]
            13: [8, 1]
            14: [9, 1]
            15: [7, 0]
            16: [3, 1]
            17: [2, 0]
            18: [2, 1]
            19: [2, 1]
            20: [3, 1]
            21: [4, 2]
            22: [3, 0]
            23: [3, 3]
            24: [5, 2]
            25: [2, 0]
            26: [3, 2]
            27: [4, 2]
            28: [3, 2]
            29: [3, 1]
            30: [4, 1]
            31: [3, 1]
            32: [2, 2]
            33: [3, 3]
            34: [4, 4]
            35: [4, 3]
        Groudon:
            20: [15, 5]
            25: [5, 4]
        Kyurem:
            20: [2, 2]
            25: [1, 0]
        Kyogre:
            20: [27, 8]
        Heatran:
            25: [1, 1]
        Hooh:
            20: [2, 0]
        Lugia:
            20: [4, 2]
        Scraggy:
            15: [1, 0]
        Stunfisk_galarian:
            20: [2, 1]
        Snover_shadow:
            8: [1, 0]
        Karrablast:
            27: [1, 0]
        Registeel:
            20: [1, 0]
        Joltik:
            2: [1, 0]
            4: [1, 0]
            8: [1, 0]
            9: [1, 0]
            10: [1, 0]
            17: [1, 0]
            18: [1, 0]
            20: [2, 2]
        Mudkip:
            1: [1, 0]
            2: [3, 0]
            4: [1, 0]
            7: [1, 0]
            11: [1, 0]
            17: [1, 0]
            18: [3, 0]
            22: [1, 0]
            23: [1, 0]
            28: [2, 1]
            29: [2, 1]
        Ralts:
            8: [1, 0]
            16: [1, 0]
            25: [1, 1]
            33: [1, 1]
        Kirlia:
            8: [1, 0]
        Larvitar:
            20: [1, 1]
        Fennekin:
            20: [1, 0]
        Chespin:
            17: [1, 1]
            20: [1, 1]
        Ferroseed:
            10: [1, 0]
            20: [1, 0]
        Snorlax:
            1: [1, 0]
            17: [1, 0]
            35: [1, 1]
        Magnemite_shadow:
            8: [6, 0]
        Magnemite:
            20: [1, 0]
        Smoochum:
            15: [1, 0]
        Marill:
            6: [1, 0]
            15: [1, 0]
            25: [1, 1]
            28: [1, 1]
            31: [1, 0]
        Shieldon:
            2: [2, 0]
            4: [1, 0]
            8: [1, 0]
            9: [1, 0]
            11: [1, 0]
            18: [3, 1]
            20: [1, 1]
            22: [2, 1]
            25: [1, 0]
            26: [2, 1]
            27: [1, 0]
            28: [2, 1]
        Croagunk:
            18: [1, 0]
            20: [2, 0]
        Froakie:
            1: [1, 0]
            19: [2, 0]
            20: [5, 0]
            30: [1, 0]
        Gibble:
            20: [1, 1]
            25: [1, 1]
        '''))

    file.seek(0)
    data = yaml.load(file)
    print('data = {}'.format(ub.repr2(data, nl=1)))

    import pandas as pd
    dfs = []
    for name, dat in data.items():
        for i in range(1, 36):
            if i not in dat:
                dat[i] = [0, 0]
        df = pd.DataFrame.from_dict(dat, orient='index', columns=['num_tf', 'num_xl'])
        df.index.name = 'level'
        df.name = name
        dfs.append(df)
        print('df = {!r}'.format(df))

    import numpy as np
    agg = sum(dfs)
    agg['num_tf'] = agg['num_tf'].astype(np.float)
    agg['num_xl'] = agg['num_xl'].astype(np.float)
    agg['percent'] = (100 * agg['num_xl'] / agg['num_tf']).round(1)

    summary = pd.DataFrame(columns=agg.columns)
    summary.loc['1-14'] = agg[(1 <= agg.index) & (agg.index <= 14)].sum(axis=0)
    summary.loc['15-19'] = agg[(15 <= agg.index) & (agg.index <= 19)].sum(axis=0)
    summary.loc['20-22'] = agg[(20 <= agg.index) & (agg.index <= 22)].sum(axis=0)
    summary.loc['23'] = agg[(23 <= agg.index) & (agg.index <= 23)].sum(axis=0)
    summary.loc['24-25'] = agg[(24 <= agg.index) & (agg.index <= 25)].sum(axis=0)
    summary.loc['26-30'] = agg[(26 <= agg.index) & (agg.index <= 30)].sum(axis=0)
    summary.loc['31-35'] = agg[(31 <= agg.index) & (agg.index <= 35)].sum(axis=0)

    summary['num_tf'] = summary['num_tf'].astype(np.float)
    summary['num_xl'] = summary['num_xl'].astype(np.float)

    summary['percent'] = (100 * summary['num_xl'] / summary['num_tf']).round(1)
    print(summary)
