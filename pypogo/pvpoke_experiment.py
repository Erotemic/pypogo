
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
    from selenium import webdriver
    from selenium.webdriver.common.keys import Keys
    import networkx as nx
    import ubelt as ub

    # os.environ['webdriver.chrome.driver'] = str(ensure_selenium_chromedriver())

    url = 'https://pvpoke.com/battle/matrix/'
    # chrome_exe = ub.find_exe("google-chrome")
    driver = webdriver.Chrome()
    driver.get(url)

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

