import itertools as it
import ubelt as ub
import pathlib
import time
import os
import stat


def ensure_selenium_chromedriver():
    """
    os.environ['webdriver.chrome.driver'] = ensure_selenium_chromedriver()
    """
    import requests
    import zipfile
    timeout = 5.0

    def latest_version():
        rsp = requests.get('http://chromedriver.storage.googleapis.com/LATEST_RELEASE', timeout=timeout)
        if rsp.status_code != 200:
            raise Exception
        version = rsp.text.strip()
        return version

    # version = latest_version()
    # version = '91.0.4472.19'
    # version = '90.0.4430.24'
    version = '92.0.4515.107'

    known_hashs = {
        '91.0.4472.19': '49622b740b1c7e66b87179a2642f6c57f21a97fc844c84b30a48',
        '90.0.4430.24': 'b85313de6abc1b44f26a0e12e20cb66657b840417f5ac6018946',
        '92.0.4515.107': '844c0e04bbbfd286617af2d7facd3d6cf7d3491b1e78120f8e0',
    }
    url = 'http://chromedriver.storage.googleapis.com/{}/chromedriver_linux64.zip'.format(version)
    bin_dpath = pathlib.Path(ub.expandpath('~/.local/bin'))
    download_dpath = bin_dpath / f'chromedriver_{version}'
    download_dpath.mkdir(exist_ok=True, parents=True)

    zip_fpath = ub.grabdata(
        url, hash_prefix=known_hashs.get(version, 'unknown-version'),
        dpath=download_dpath,
    )
    zip_fpath = pathlib.Path(zip_fpath)
    # dpath = zip_fpath.parent

    # TODO: version the binary
    chromedriver_fpath_real = download_dpath / 'chromedriver'
    chromedriver_fpath_link = bin_dpath / 'chromedriver'

    if not chromedriver_fpath_real.exists() or not chromedriver_fpath_link.exists():
        # Also check hash?

        zfile = zipfile.ZipFile(str(zip_fpath))
        try:
            fpath = zfile.extract(
                'chromedriver', path=chromedriver_fpath_real.parent)
        finally:
            zfile.close()

        chromedriver_fpath_real_ = pathlib.Path(fpath)
        assert chromedriver_fpath_real_.exists()
        ub.symlink(chromedriver_fpath_real_, chromedriver_fpath_link,
                   overwrite=True)

        if not ub.WIN32:
            print('add permission chromedriver_fpath_real_ = {!r}'.format(chromedriver_fpath_real_))
            st = os.stat(chromedriver_fpath_real_)
            os.chmod(chromedriver_fpath_real_, st.st_mode | stat.S_IEXEC)

        os.environ['PATH'] = os.pathsep.join(
            ub.oset(os.environ['PATH'].split(os.pathsep)) |
            ub.oset([str(chromedriver_fpath_link.parent)]))
    return chromedriver_fpath_link


def run_pvpoke_simulation(mons, league='auto'):
    """
    Args:
        mons (List[pypogo.Pokemon]): pokemon to simulate.
            Must have IVS, movesets, level, etc... fields populated.
    """
    from selenium import webdriver
    from selenium.webdriver.common.keys import Keys
    # from selenium.webdriver.support.ui import Select
    import pandas as pd
    # import pypogo

    if league == 'auto':
        for mon in mons:
            if mon.cp <= 1500:
                league = 'great'
            elif mon.cp <= 2500:
                league = 'ultra'
            elif mon.level <= 41:
                league = 'master-classic'
            elif mon.level <= 51:
                league = 'master'
            else:
                raise AssertionError
            break
    # for mon in mons:
    #     mon.populate_all
    mon_cachers = {}
    have_results = {}
    to_check_mons = []
    for mon in mons:
        mon._slug = mon.slug()
        mon_cachers[mon._slug] = cacher = ub.Cacher(
            'pvpoke_sim', depends=[mon._slug, league], appname='pypogo')
        mon_results = cacher.tryload()
        if mon_results is None:
            to_check_mons.append(mon)
        else:
            have_results[mon._slug] = mon_results

    if to_check_mons:
        # Requires the driver be in the PATH
        ensure_selenium_chromedriver()

        url = 'https://pvpoke.com/battle/matrix/'
        driver = webdriver.Chrome()
        driver.get(url)
        time.sleep(2.0)

        if league == 'great':
            league_box_target = 'Great League (CP 1500)'
            meta_text = 'Great League Meta'
        elif league == 'ultra':
            league_box_target = 'Ultra League (Level 50)'
            meta_text = 'Ultra League Meta'
            # meta_text = 'Premier Cup Meta'
            # meta_text = 'Remix Cup Meta'
            # meta_text = 'Premier Classic Cup Meta'
        elif league == 'master-classic':
            league_box_target = 'Master League (Level 40)'
            meta_text = 'Master League Meta'
        elif league == 'master':
            league_box_target = 'Master League (Level 50)'
            meta_text = 'Master League Meta'
        else:
            raise NotImplementedError

        leage_select = driver.find_elements_by_class_name('league-select')[0]
        leage_select.click()
        leage_select.send_keys(league_box_target)
        leage_select.click()
        leage_select.send_keys(Keys.ENTER)

        # leage_select.text.split('\n')
        # leage_select.send_keys('\n')
        # leage_select.send_keys('\n')

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

            # USE_MOVES = 1
            if mon.moves is not None:
                # mon.populate_all()

                fast_select = driver.find_element_by_xpath('/html/body/div[5]/div/div[3]/div[1]/div[2]/div[10]/select[1]')
                fast_select.click()
                fast_select.send_keys(mon.pvp_fast_move['name'])
                fast_select.send_keys(Keys.ENTER)

                charge1_select = driver.find_element_by_xpath('/html/body/div[5]/div/div[3]/div[1]/div[2]/div[10]/select[2]')
                charge1_select.click()
                charge1_select.send_keys(mon.pvp_charge_moves[0]['name'])
                charge1_select.send_keys(Keys.ENTER)

                charge2_select = driver.find_element_by_xpath('/html/body/div[5]/div/div[3]/div[1]/div[2]/div[10]/select[3]')
                charge2_select.click()
                charge2_select.send_keys(mon.pvp_charge_moves[1]['name'])
                charge2_select.send_keys(Keys.ENTER)

            save_button = driver.find_elements_by_class_name('save-poke')[0]
            save_button.click()

        quickfills = driver.find_elements_by_class_name('quick-fill-select')
        quickfill = quickfills[1]
        quickfill.text.split('\n')
        quickfill.click()
        quickfill.send_keys(meta_text)
        quickfill.click()

        for mon in to_check_mons:
            add_pokemon(mon)

        shield_num_to_text = {
            0: 'No shields',
            1: '1 shield',
            2: '2 shields',
        }

        shield_case_to_data = {}

        for atk_num_shields, def_num_sheids in it.product(shield_num_to_text, shield_num_to_text):
            shield_selectors = driver.find_elements_by_class_name('shield-select')
            shield_selectors[2].click()
            shield_selectors[2].send_keys(shield_num_to_text[atk_num_shields])
            shield_selectors[2].send_keys(Keys.ENTER)

            shield_selectors[3].click()
            shield_selectors[3].send_keys(shield_num_to_text[def_num_sheids])
            shield_selectors[3].send_keys(Keys.ENTER)

            #shield_selectors[0].click()

            battle_btn = driver.find_elements_by_class_name('battle-btn')[0]
            battle_btn.click()

            # Clear previous downloaded files
            dlfolder = pathlib.Path(ub.expandpath('$HOME/Downloads'))
            for old_fpath in list(dlfolder.glob('_vs*.csv')):
                old_fpath.unlink()

            time.sleep(2.0)

            # Download new data
            dl_btn = driver.find_element_by_xpath('//*[@id="main"]/div[4]/div[9]/div/a')
            dl_btn.click()

            while len(list(dlfolder.glob('_vs*.csv'))) < 1:
                pass

            new_fpaths = list(dlfolder.glob('_vs*.csv'))
            assert len(new_fpaths) == 1
            fpath = new_fpaths[0]

            data = pd.read_csv(fpath, header=0, index_col=0)
            shield_case_to_data[(atk_num_shields, def_num_sheids)] = data

        for idx, mon in enumerate(to_check_mons):
            mon_results = {ss: scores.iloc[idx] for ss, scores in shield_case_to_data.items()}
            cacher = mon_cachers[mon._slug]
            cacher.save(mon_results)
            have_results[mon._slug] = mon_results

    _tojoin = ub.ddict(list)
    _joined = ub.ddict(list)
    for mon_results in have_results.values():
        for ss, scores in mon_results.items():
            _tojoin[ss].append(scores)

    for ss, vals in _tojoin.items():
        _joined[ss] = pd.concat([v.to_frame().T for v in vals])
    _joined.default_factory = None
    results = _joined
    return results
