import json
import ubelt as ub
import networkx as nx


def master():
    master_fpath = ub.grabdata('https://raw.githubusercontent.com/pokemongo-dev-contrib/pokemongo-game-master/master/versions/latest/V2_GAME_MASTER.json', expires=24 * 60 * 60)
    with open(master_fpath) as file:
        master = json.load(file)

    master.keys()

    def item_type(item):
        data = item['data']
        if 'move' in data:
            return 'move'
        if 'pokemon' in data:
            return 'pokemon'

    type_to_items = ub.group_items(master['template'], key=item_type)

    pokemon_items = type_to_items['pokemon']  # NOQA
    move_items = type_to_items['move']

    for item in move_items:
        uid = item['data']['move']['uniqueId']
        if 'MOONBLAST' in uid:
            print('item = {}'.format(ub.repr2(item, nl=3)))


def normalize(n):
    return n.lower().replace(' ', '_')


class PogoAPI(ub.NiceRepr):
    """
    Object to help with access to data from pogoapi.net

    References:
        https://pogoapi.net/documentation/

        api.data['current_pokemon_moves']

    Example:
        >>> from pypogo.pogo_api import *  # NOQA
        >>> api = PogoAPI()
        >>> name = 'machamp-shadow'
        >>> print(ub.repr2(api.get_pokemon_info(name)))
        >>> form = None
        >>> name = 'beedrill'
        >>> print(ub.repr2(api.get_pokemon_info(name)))
        >>> name = 'farfetchd_galarian'
        >>> print(ub.repr2(api.get_pokemon_info(name)))
        >>> name = 'stunfisk_galarian'
        >>> print(ub.repr2(api.get_pokemon_info(name)))
    """
    def __init__(api):
        api.base = 'https://pogoapi.net/api/v1/'
        api.routes = {
            'pokemon_stats': api.base + 'pokemon_stats.json',
            'current_pokemon_moves': api.base + 'current_pokemon_moves.json',
            'pokemon_evolutions': api.base + 'pokemon_evolutions.json',
            'cp_multiplier': api.base + 'cp_multiplier.json',
            'pokemon_types': api.base + 'pokemon_types.json',

            'charged_moves': api.base + 'charged_moves.json',
            'fast_moves': api.base + 'fast_moves.json',
            'type_effectiveness': api.base + 'type_effectiveness.json',

            'pokemon_powerup_requirements': api.base + 'pokemon_powerup_requirements.json',
            'pokemon_candy_to_evolve': api.base + 'pokemon_candy_to_evolve.json',
            'pokemon_buddy_distances': api.base + 'pokemon_buddy_distances.json',

            'shadow_pokemon': api.base + 'shadow_pokemon.json',
            'pokemon_forms': api.base + 'pokemon_forms.json',
            'pvp_exclusive_pokemon': api.base + 'pvp_exclusive_pokemon.json',
            'galarian_pokemon': api.base + 'galarian_pokemon.json',
            'alolan_pokemon': api.base + 'alolan_pokemon.json',
            'shiny_pokemon': api.base + 'shiny_pokemon.json',
            'mega_pokemon': api.base + 'mega_pokemon.json',
            'baby_pokemon': api.base + 'baby_pokemon.json',
            'nesting_pokemon': api.base + 'nesting_pokemon.json',
            'released_pokemon': api.base + 'released_pokemon.json',
            'pokemon_names': api.base + 'pokemon_names.json',
            'api_hashes': api.base + 'api_hashes.json',

            'pvp_fast_moves':  api.base + 'pvp_fast_moves.json',
            'pvp_charged_moves': api.base + 'pvp_charged_moves.json',
        }

        # TODO: determine when to redownload
        cache_dpath_root = ub.Path.appdir('pypogo/pogoapi').ensuredir()
        # Keep backups of the API every month
        today = ub.timeparse(ub.timestamp()).date()
        month_stamp = today.replace(day=1)
        cache_dpath = (cache_dpath_root / month_stamp.isoformat()).ensuredir()

        api.data = {}
        for key, url in api.routes.items():
            redo = 0
            data_fpath = ub.grabdata(
                url, dpath=cache_dpath, verbose=1, redo=redo, expires=24 * 60 * 60)

            with open(data_fpath, 'r') as file:
                data = json.load(file)
            api.data[key] = data

        # Make the API global for now
        pokemon_stats = api.data['pokemon_stats']
        _name_to_stats = ub.group_items(pokemon_stats, lambda item: item['pokemon_name'].lower())
        _name_to_stats = dict(_name_to_stats)
        api.name_to_stats = _name_to_stats

        _name_to_moves = ub.group_items(
            api.data['current_pokemon_moves'],
            lambda item: item['pokemon_name'].lower())
        _name_to_moves.default_factory = None
        _name_to_moves = dict(_name_to_moves)

        # base = 'http://pokeapi.co/api/v2/pokemon/'
        api.name_to_moves = _name_to_moves

        evolutions = api.data['pokemon_evolutions']
        _name_to_evolutions = ub.group_items(evolutions, lambda item: item['pokemon_name'].lower())
        _name_to_evolutions = dict(_name_to_evolutions)

        for key, form_stats in api.name_to_stats.items():
            if key not in _name_to_evolutions:
                noevos = []
                for s in form_stats:
                    empty = ub.dict_isect(s, {'form', 'pokemon_name', 'pokemon_id'})
                    empty['evolutions'] = []
                    noevos.append(empty)
                _name_to_evolutions[key] = noevos

        _name_to_types = ub.group_items(
            api.data['pokemon_types'],
            lambda item: item['pokemon_name'].lower())
        _name_to_types = dict(_name_to_types)
        api.name_to_type = _name_to_types

        evo_graph = nx.DiGraph()
        for name, form_evo_list in _name_to_evolutions.items():
            for form_evo in form_evo_list:
                u = form_evo['pokemon_name'].lower()
                evo_graph.add_node(u)
                for evo in form_evo['evolutions']:
                    v = evo['pokemon_name'].lower()
                    evo_graph.add_edge(u, v)

        api.shadow_names = [normalize(d['name']) for d in api.data['shadow_pokemon'].values()]

        api.name_to_family = {}
        api.name_to_base = {}

        evo_graph.remove_edges_from(nx.selfloop_edges(evo_graph))
        api.evo_graph = evo_graph
        for cc in list(nx.connected_components(api.evo_graph.to_undirected())):
            bases = [n for n in cc if len(evo_graph.pred[n]) == 0]
            base = bases[0]
            for n in cc:
                api.name_to_family[n] = cc
                api.name_to_base[n] = base

        api.name_to_evolutions = _name_to_evolutions

        api.pve_fast_moves = ub.group_items(
            api.data['fast_moves'],
            lambda item: normalize(item['name'].lower()))
        api.pve_fast_moves.default_factory = None

        api.pve_charged_moves = ub.group_items(
            api.data['charged_moves'],
            lambda item: normalize(item['name'].lower()))
        api.pve_charged_moves.default_factory = None

        api.pvp_fast_moves = ub.group_items(
            api.data['pvp_fast_moves'],
            lambda item: normalize(item['name'].lower()))
        api.pvp_fast_moves.default_factory = None

        # Fairywind is a placeholder
        # https://gamepress.gg/pokemongo/pokemon-move/fairy-wind
        if 'fairy_wind' not in api.pve_fast_moves:
            api.pve_fast_moves['fairy_wind'] = [{
                'duration': 3000,
                'move_id': None,
                'power': 1,
                'energy_delta': 100,
                'stamina_loss_scaler': 0.01,
                'name': 'Fairy Wind',
                'type': 'Fairy'
            }]

        if 'fairy_wind' not in api.pvp_fast_moves:
            api.pvp_fast_moves['fairy_wind'] = [{
                'energy_delta': 1,
                'move_id': None,
                'power': 1,
                'turn_duration': 1,
                'name': 'Fairy Wind',
                'type': 'Fairy'
            }]

        api.pvp_charged_moves = ub.group_items(
            api.data['pvp_charged_moves'],
            lambda item: normalize(item['name'].lower()))
        api.pvp_charged_moves.default_factory = None

        if 0:
            ub.map_vals(len, api.pve_fast_moves)
            ub.map_vals(len, api.pve_charged_moves)

        api.learnable = {
            # TODO: remove
            'stunfisk_galarian': {
                'fast': [
                    'MUD_SHOT',
                    'METAL_CLAW',
                ],
                'charge': [
                    'EARTHQUAKE',
                    'FLASH_CANNON',
                    'MUDDY_WATER',
                    'ROCK_SLIDE',
                ]
            }
        }

        api.type_colors = {
            #https://www.epidemicjohto.com/t882-type-colors-hex-colors
            'Water': '#6390F0',
            'Grass': '#7AC74C',
            'Ghost': '#735797',
            'Dragon': '#6F35FC',
            'Dark': '#705746',
            'Steel': '#B7B7CE',
            'Ice': '#96D9D6',
            'Fire': '#EE8130',
            'Poison': '#A33EA1',
            'Ground': '#E2BF65',
            'Flying': '#A98FF3',
            'Psychic': '#F95587',
            'Bug': '#A6B91A',
            'Rock': '#B6A136',
            'Fighting': '#C22E28',
            'Normal': '#A8A77A',
            'Electric': '#F7D02C',
            'Fairy': '#D685AD',
        }

    def normalize(api, x):
        return normalize(x)

    def __nice__(api):
        return str(list(api.routes.keys()))

    def normalize_name_and_form(api, name, form=None, hints=''):
        """
        Do some normalization and handle special cases

        (which might only be special because of bad initial programming, better
         use of the pogo api might make some of this not necessary)
        """
        hints_ = hints.lower()
        if name.endswith('-shadow'):
            # if form is None:
            #     form = 'Shadow'
            # else:
            #     assert form == 'Shadow', '{}, {}'.format(api, name)
            name = name.split('-shadow')[0]

        if name.endswith('galarian'):
            if form is None:
                form = 'Galarian'
            if form == 'Normal':
                form = 'Galarian'  # hack
            # else:
            #     assert form == 'Galarian', '{}, {}'.format(api, name)
            name = name.split('_galarian')[0]

        if name.endswith('snowy'):
            if form is None:
                form = 'snowy'
            name = name.split('_' + form)[0]

        if name.endswith('sunny'):
            if form is None:
                form = 'sunny'
            name = name.split('_' + form)[0]

        if name.endswith('rainy'):
            if form is None:
                form = 'rainy'
            name = name.split('_' + form)[0]

        if name == 'farfetchd':
            name = "farfetch\u2019d"

        if form is None:
            form = 'Normal'

        if name.lower().startswith('mr '):
            name = 'mr. ' + name[:3]

        if name.lower() in {'sirfetchd', 'sirfetch\'d'}:
            name = b'sirfetch\xe2\x80\x99d'.decode('utf8')

        if name.lower() in {'farfetchd', 'farfetch\'d'}:
            name = b'farfetch\xe2\x80\x99d'.decode('utf8')

        # For some pokemon we have to "choose a default form"
        if form == 'Normal':
            name_ = name.lower()
            if name_ == 'cherrim':
                form = 'sunny'

            if 'galarian' in hints_:
                form = 'galarian'

            if 'alolan' in hints_:
                form = 'alola'

            if name_ == 'runerigus':
                form = 'galarian'

            if name_ == 'tornadus':
                form = 'incarnate'
                if 'incarnate' in hints_:
                    form = 'incarnate'
                elif 'therian' in hints_:
                    form = 'therian'

            if name_ == 'landorus':
                form = 'incarnate'
                if 'incarnate' in hints_:
                    form = 'incarnate'
                elif 'therian' in hints_:
                    form = 'therian'

            if name_ == 'thundurus':
                form = 'incarnate'
                if 'incarnate' in hints_:
                    form = 'incarnate'
                elif 'therian' in hints_:
                    form = 'therian'

            if name_ == 'sawsbuck':
                form = 'autumn'

            if name_ == 'darmanitan':
                form = 'galarian_standard'

            if name_ == 'gastrodon':
                form = 'east_sea'

            if name_ == 'mr. rime':
                form = 'galarian'

            if name_ == 'perrserker':
                form = 'galarian'

            if name_.startswith('sirfetch'):
                form = 'galarian'

            if name_ == 'obstagoon':
                form = 'galarian'

            if name_ == 'giratina':
                form = 'altered'
                if 'altered' in hints_:
                    form = 'altered'
                elif 'origin' in hints_:
                    form = 'origin'

        return name, form

    def get_move_info(api, move_name):
        """
        Example:
            >>> from pypogo.pogo_api import *  # NOQA
            >>> api = PogoAPI()
            >>> move_name = 'super power'
            >>> print(ub.repr2(api.get_move_info(move_name)))
            >>> move_name = 'struggle'
            >>> print(ub.repr2(api.get_move_info(move_name)))

            # with pytest.raises
            # >>> move_name = 'superpower'
            # >>> print(ub.repr2(api.get_move_info(move_name)))
        """
        pvp_cand = []
        pve_cand = []
        try:
            move = api.normalize(move_name)
            if move in api.pve_fast_moves:
                fast = api.pve_fast_moves[move]
                pve_cand.append((fast, 'fast'))
            elif move in api.pve_charged_moves:
                charged = api.pve_charged_moves[move]
                pve_cand.append((charged, 'charged'))
            else:
                raise KeyError('unknown move {}'.format(move))
            if move in api.pvp_fast_moves:
                fast = api.pvp_fast_moves[move]
                pvp_cand.append((fast, 'fast'))
            elif move in api.pvp_charged_moves:
                charged = api.pvp_charged_moves[move]
                pvp_cand.append((charged, 'charged'))
            else:
                raise KeyError('unknown move {}'.format(move))

            if len(pve_cand) != 1:
                raise Exception('ambiguous pve_cand move')
            if len(pvp_cand) != 1:
                raise Exception('ambiguous pvp_cand move')
        except Exception:
            suggest_spelling_correction(move_name, api.all_move_names, top=3)
            raise

        move_type1 = pve_cand[0][1]
        move_type2 = pvp_cand[0][1]
        assert move_type2 == move_type1
        move_type = move_type1

        move_info = {
            'move_type': move_type,
            'pve': pve_cand[0][0],
            'pvp': pvp_cand[0][0],
        }
        return move_info

    @ub.memoize_property
    def all_move_names(api):
        move_names = sorted(
            set(api.pve_fast_moves.keys()) |
            set(api.pve_charged_moves) |
            set(api.pvp_fast_moves) |
            set(api.pvp_charged_moves)
        )
        return move_names

    def get_pokemon_info(api, name, form=None):
        """
        Example:
            >>> from pypogo.pogo_api import *  # NOQA
            >>> api = PogoAPI()
            >>> name = 'stunfisk_galarian'
            >>> print(ub.repr2(api.get_pokemon_info(name)))
            >>> name = 'stunfisk'
            >>> print(ub.repr2(api.get_pokemon_info(name)))
            >>> name = 'umbreon'
            >>> print(ub.repr2(api.get_pokemon_info(name)))
            >>> name = 'eevee'
            >>> print(ub.repr2(api.get_pokemon_info(name)))
            >>> name = 'castform_snowy'
            >>> print(ub.repr2(api.get_pokemon_info(name)))

            >>> name = 'smeargle'
            >>> print(ub.repr2(api.get_pokemon_info(name)))

            >>> name = 'wormadam'
            >>> print(ub.repr2(api.get_pokemon_info(name)))

        """
        try:
            name_, form_ = api.normalize_name_and_form(name, form)
            form_ = form_.lower()
        except Exception:
            raise Exception('name={name}, form={form}'.format(**locals()))

        try:
            infos = {
                'stats': api.name_to_stats[name_],
                'evolutions': api.name_to_evolutions[name_],
                'type': api.name_to_type[name_],
                'moves': api.name_to_moves[name_],
            }
        except Exception:
            if True:
                all_names = list(api.name_to_stats.keys())
                suggest_spelling_correction(name, all_names, top=10)
            raise Exception(
                'name={name}, form={form}, name_={name_}, form_={form_}'.format(**locals()))

        info = {}
        for info_type, all_infos in infos.items():
            part = None
            form_to_info = ub.group_items(all_infos, lambda _info: _info['form'].lower())

            api.shadow_names

            if form_ in form_to_info:
                parts = form_to_info[form_]
            else:
                if info_type != 'evolutions':
                    print('info_type = {!r}'.format(info_type))
                    print('form_to_info = {}'.format(ub.repr2(form_to_info, nl=1)))
                    import warnings
                    msg = 'Unable to find name={} form_={} form={}, info_type={}'.format(name, form_, form, info_type)
                    print(msg)
                    warnings.warn(msg)
                    parts = ub.peek(form_to_info.values())
                else:
                    parts = None

            if parts is None:
                part = []
            else:
                if len(parts) != 1:
                    print('parts = {!r}'.format(parts))
                    raise Exception
                part = parts[0]
            info.update(part)

        if 1:
            # TODO: remove
            fast_moves = set()
            charge_moves = set()

            for move in info['fast_moves']:
                fast_moves.add(normalize(move))
            for move in info['elite_fast_moves']:
                fast_moves.add(normalize(move))
            for move in info['charged_moves']:
                charge_moves.add(normalize(move))
            for move in info['elite_charged_moves']:
                charge_moves.add(normalize(move))

            if form_ == 'normal':
                if info['form'] == 'Shadow':
                    charge_moves.add('FRUSTRATION')
                    charge_moves.add('RETURN')

            if name_ not in api.learnable:
                api.learnable[name_] = {}
            api.learnable[name_]['fast'] = sorted(fast_moves)
            api.learnable[name_]['charge'] = sorted(charge_moves)

        api.LEVEL_CAP = 51
        return info

    def enumerate_all_pokemon(api):
        import pypogo
        # api.data['pokemon_forms']
        for name in api.name_to_type.keys():
            infos1 = api.name_to_type[name]
            infos2 = api.name_to_stats[name]
            assert {d['form'] for d in infos2} == {d['form'] for d in infos1}
            for info in infos1:
                info['form']
                shadow = info['form'] == 'Shadow'
                mon = pypogo.Pokemon(name, form=info['form'], shadow=shadow)
                yield mon


def suggest_spelling_correction(name, all_names, top=10):
    from xdev.algo import edit_distance
    distances = edit_distance(name, all_names)
    idxs = ub.argsort(distances)[0:top]
    candidates = list(ub.take(all_names, idxs))
    print('did you mean on of: {}?'.format(ub.repr2(candidates, nl=1)))
    return candidates


# HACK: Make a global API variable
# we should likey do some lazy initialization or something better


_api = None


def global_api(new=False):
    global _api
    if _api is None or new:
        _api = PogoAPI()
    return _api

# api = global_api()


def __getattr__(key):
    if key == 'api':
        return global_api()
    else:
        raise AttributeError
