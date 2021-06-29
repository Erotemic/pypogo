
def ensure_selenium_chromedriver():
    """
    os.environ['webdriver.chrome.driver'] = ensure_selenium_chromedriver()
    """
    import ubelt as ub
    import os
    import stat
    timeout = 5.0

    def latest_version():
        import requests
        rsp = requests.get('http://chromedriver.storage.googleapis.com/LATEST_RELEASE', timeout=timeout)
        if rsp.status_code != 200:
            raise Exception
        version = rsp.text.strip()
        return version

    # version = latest_version()
    # version = '91.0.4472.19'
    version = '90.0.4430.24'

    known_hashs = {
        '91.0.4472.19': '49622b740b1c7e66b87179a2642f6c57f21a97fc844c84b30a48',
        '90.0.4430.24': 'b85313de6abc1b44f26a0e12e20cb66657b840417f5ac6018946'
    }
    url = 'http://chromedriver.storage.googleapis.com/{}/chromedriver_linux64.zip'.format(version)
    zip_fpath = ub.grabdata(
        url, hash_prefix=known_hashs.get(version, 'unknown-version'),
        dpath=ub.expandpath('~/.local/bin')
    )
    import zipfile
    import pathlib
    zip_fpath = pathlib.Path(zip_fpath)
    dpath = zip_fpath.parent

    zfile = zipfile.ZipFile(str(zip_fpath))
    try:
        fpath = zfile.extract('chromedriver', path=dpath)
    finally:
        zfile.close()

    chromedriver_fpath = pathlib.Path(fpath)
    assert chromedriver_fpath.exists()

    if not ub.WIN32:
        st = os.stat(chromedriver_fpath)
        os.chmod(chromedriver_fpath, st.st_mode | stat.S_IEXEC)
    return chromedriver_fpath


def run_pvpoke_ultra_experiment():
    """
    https://pvpoke.com/battle/matrix/

    !pip install selenium
    """
    """
    Relevant page items:

    <button class="add-poke-btn button">+ Add Pokemon</button>
    '//*[@id="main"]/div[3]/div[3]/div/div[1]/button[1]'
    '/html/body/div[1]/div/div[3]/div[3]/div/div[1]/button[1]'

    <input class="poke-search" type="text" placeholder="Search name">
    /html/body/div[5]/div/div[3]/div[1]/input


    /html/body/div[5]/div/div[3]/div[1]/div[2]/div[9]/a/span[1]


    Level Cap
    /html/body/div[5]/div/div[3]/div[1]/div[2]/div[9]/div/div[2]/div[2]/div[5]


    # IV GROUP
    ivs-group

    save-poke
    """
    from selenium import webdriver
    from selenium.webdriver.common.keys import Keys
    import networkx as nx
    import ubelt as ub
    import os

    # Requires the driver be in the PATH
    fpath = ensure_selenium_chromedriver()
    os.environ['PATH'] = os.pathsep.join(
        ub.oset(os.environ['PATH'].split(os.pathsep)) |
        ub.oset([str(fpath.parent)]))

    url = 'https://pvpoke.com/battle/matrix/'
    # chrome_exe = ub.find_exe("google-chrome")
    driver = webdriver.Chrome()
    driver.get(url)

    from selenium.webdriver.support.ui import Select

    leage_select = driver.find_elements_by_class_name('league-select')[0]
    leage_select.click()
    leage_select.send_keys('Master League (Level 40)')
    leage_select.click()

    leage_select.text.split('\n')
    leage_select.send_keys('\n')
    leage_select.send_keys('\n')

    import time

    def add_pokemon(mon):
        add_poke1_button = driver.find_elements_by_class_name('add-poke-btn')[0]
        add_poke1_button.click()

        select_drop = driver.find_element_by_xpath('/html/body/div[5]/div/div[3]/div[1]/select')

        if 1:
            import xdev
            all_names = select_drop.text.split('\n')
            distances = xdev.edit_distance(mon.display_name(), all_names)
            chosen_name = all_names[ub.argmin(distances)]
        else:
            chosen_name = mon.name

        search_box = driver.find_element_by_xpath('/html/body/div[5]/div/div[3]/div[1]/input')
        search_box.send_keys(chosen_name)

        advanced_ivs_arrow = driver.find_element_by_xpath('/html/body/div[5]/div/div[3]/div[1]/div[2]/div[9]/a/span[1]')
        advanced_ivs_arrow.click()

        level40_cap = driver.find_element_by_xpath('/html/body/div[5]/div/div[3]/div[1]/div[2]/div[9]/div/div[2]/div[2]/div[2]')
        level41_cap = driver.find_element_by_xpath('/html/body/div[5]/div/div[3]/div[1]/div[2]/div[9]/div/div[2]/div[2]/div[3]')
        level50_cap = driver.find_element_by_xpath('/html/body/div[5]/div/div[3]/div[1]/div[2]/div[9]/div/div[2]/div[2]/div[4]')
        level51_cap = driver.find_element_by_xpath('/html/body/div[5]/div/div[3]/div[1]/div[2]/div[9]/div/div[2]/div[2]/div[5]')

        if mon.level >= 51:
            level51_cap.click()
        elif mon.level >= 50:
            level50_cap.click()
        elif mon.level >= 41:
            level41_cap.click()
        elif mon.level >= 40:
            level40_cap.click()

        level_box = driver.find_element_by_xpath('/html/body/div[5]/div/div[3]/div[1]/div[2]/div[9]/div/div[1]/input')
        level_box.click()
        level_box.clear()
        level_box.clear()
        level_box.send_keys(str(mon.level))

        iv_a = driver.find_element_by_xpath('/html/body/div[5]/div/div[3]/div[1]/div[2]/div[9]/div/div[1]/div/input[1]')
        iv_d = driver.find_element_by_xpath('/html/body/div[5]/div/div[3]/div[1]/div[2]/div[9]/div/div[1]/div/input[2]')
        iv_s = driver.find_element_by_xpath('/html/body/div[5]/div/div[3]/div[1]/div[2]/div[9]/div/div[1]/div/input[3]')

        # TODO
        # driver.find_elements_by_class_name('move-select')

        iv_a.clear()
        iv_a.send_keys(str(mon.ivs[0]))

        iv_d.clear()
        iv_d.send_keys(str(mon.ivs[1]))

        iv_s.clear()
        iv_s.send_keys(str(mon.ivs[2]))

        save_button = driver.find_elements_by_class_name('save-poke')[0]
        save_button.click()

    quickfills = driver.find_elements_by_class_name('quick-fill-select')
    quickfill = quickfills[1]
    quickfill.text.split('\n')
    quickfill.click()
    quickfill.send_keys('Master League Meta')
    quickfill.click()

    import pypogo
    # mon1 = pypogo.Pokemon('Mewtwo', ivs=[15, 15, 15], level=40)
    # mon2 = pypogo.Pokemon('Mewtwo', ivs=[15, 15, 15], level=41)

    # Test the effect of best buddies vs the master league
    mons = [
        pypogo.Pokemon('Mewtwo', ivs=[15, 15, 15], level=40),
        pypogo.Pokemon('Mewtwo', ivs=[15, 15, 15], level=41),
        pypogo.Pokemon('Garchomp', ivs=[15, 15, 15], level=40),
        pypogo.Pokemon('Garchomp', ivs=[15, 15, 15], level=41),
        pypogo.Pokemon('Dragonite', ivs=[15, 14, 15], level=40),
        pypogo.Pokemon('Dragonite', ivs=[15, 14, 15], level=41),
        pypogo.Pokemon('Giratina', form='origin', ivs=[15, 14, 15], level=40),
        pypogo.Pokemon('Giratina', form='origin', ivs=[15, 14, 15], level=41),
        pypogo.Pokemon('Kyogre', ivs=[15, 15, 14], level=40),
        pypogo.Pokemon('Kyogre', ivs=[15, 15, 14], level=41),
        pypogo.Pokemon('Groudon', ivs=[14, 14, 13], level=40),
        pypogo.Pokemon('Groudon', ivs=[14, 14, 13], level=41),
        pypogo.Pokemon('Togekiss', ivs=[15, 15, 14], level=40),
        pypogo.Pokemon('Togekiss', ivs=[15, 15, 14], level=41),
    ]
    for mon in mons:
        add_pokemon(mon)

    battle_btn = driver.find_elements_by_class_name('battle-btn')[0]
    battle_btn.click()

    # Clear previous downloaded files
    import pathlib
    dlfolder = pathlib.Path(ub.expandpath('$HOME/Downloads'))
    for old_fpath in list(dlfolder.glob('_vs*.csv')):
        old_fpath.unlink()

    import time
    time.sleep(2.0)

    # Download new data
    dl_btn = driver.find_element_by_xpath('//*[@id="main"]/div[4]/div[9]/div/a')
    dl_btn.click()

    while len(list(dlfolder.glob('_vs*.csv'))) < 1:
        pass

    new_fpaths = list(dlfolder.glob('_vs*.csv'))
    assert len(new_fpaths) == 1
    fpath = new_fpaths[0]

    import pandas as pd
    data = pd.read_csv(fpath, header=0, index_col=0)

    pairs = list(ub.iter_window(range(len(data)), step=2))

    for i, j in pairs:
        print('-----')
        matchup0 = data.iloc[i]
        matchup1 = data.iloc[j]

        wins0 = matchup0 > 500
        wins1 = matchup1 > 500
        flips = (wins0 != wins1)
        flipped_vs = matchup0.index[flips]
        num_flips = sum(flips)
        print('flipped_vs = {!r}'.format(flipped_vs))
        print('num_flips = {!r}'.format(num_flips))
        print(matchup0.mean())
        print(matchup1.mean())
        print(matchup0.mean())
        print(matchup1.mean() / matchup0.mean())




def _oldstuff():
    # import lxml
    # parser = lxml.etree.HTMLParser()
    # html = driver.execute_script("return document.documentElement.outerHTML")
    # tree = lxml.etree.parse(StringIO(html), parser)
    # dom = tree.findall('//*')
    # item = dom[len(dom) // 2]

    # for child in iteme:
    #     pas

    import pypogo
    import pandas as pd
    mon = base = pypogo.Pokemon.random('registeel', moves=['lock on', 'flash cannon', 'focus blast'])

    max_cp = 2500
    tables0 = {
        'wild': mon.league_ranking_table(max_cp, min_iv=0),
        'encounter': mon.league_ranking_table(max_cp, min_iv=10),
        'lucky': mon.league_ranking_table(max_cp, min_iv=12),
    }

    tables = {}
    for key, val in tables0.items():
        col = key + '_rank'
        val.index.name = col
        val = val.reset_index()
        val = val.set_index(['iva', 'ivd', 'ivs'])
        val = val[[col]]
        # val = val.drop('rank', axis=1)
        # val = val.drop([
        #     'cp',
        #     'level',
        #     'attack',
        #     'defense',
        #     'stamina',
        #     'stat_product_k',
        #     'rak',
        #     'percent'], axis=1)
        tables[key] = val

    a, b, c = tables.values()
    combo = a.join(b).join(c)

    combo_idxs = set()
    import numpy as np

    qq = np.quantile(combo.wild_rank.values, np.linspace(0, 1, 16)).astype(int) - 1
    combo_idxs.update(qq)

    if 1:
        import numpy as np
        topk = 10
        botk = 1
        for key, val in tables0.items():
            col = key + '_rank'
            flags = ~combo[col].isnull()
            idxs = np.where(flags.values)[0].tolist()
            combo_idxs.update(idxs[0:topk])
            combo_idxs.update(idxs[-botk:])
            # sub = (combo.loc[flags])
            # print(sub)

    len(combo_idxs)

    extremek_merge = combo.iloc[sorted(combo_idxs)]
    print(extremek_merge)

    variants = []
    for ivs in extremek_merge.index:
        new = base.copy(ivs=list(ivs))
        new = new.maximize(2500)
        variants.append(new)

    for mon, i in zip(variants, range(100)):
        line = mon.to_pvpoke_import_line()
        print(line)

    # combo = pd.concat(tables.values(), join='inner', axis=0)




    dom = driver.find_elements_by_xpath("//*")

    def build_graph(graph, item):
        item_id = item.id
        print('item_id = {!r}'.format(item_id))
        graph.add_node(item_id)
        children = item.getchildren()
        # children = list(item.find_elements_by_xpath('//*'))
        for child in children:
            child_id = build_graph(graph, child)
            graph.add_edge(item_id, child_id)
        return item_id

    graph = nx.DiGraph()
    for item in ub.ProgIter(dom):
        item.tag_name
        print('item.tag_name = {!r}'.format(item.tag_name))

        # pass
        # build_graph(graph, item)

    item = dom[0]

    elem = driver.find_element_by_class_name("league-select")

    elem.clear()
    elem.send_keys("pycon")
    elem.send_keys(Keys.RETURN)

