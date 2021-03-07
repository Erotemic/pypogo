import json
import ubelt as ub
import networkx as nx


def normalize(n):
    return n.upper().replace(' ', '_')


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
        >>> print(ub.repr2(api.get_info(name)))
        >>> form = None
        >>> name = 'beedrill'
        >>> print(ub.repr2(api.get_info(name)))
        >>> name = 'farfetchd_galarian'
        >>> print(ub.repr2(api.get_info(name)))
        >>> name = 'stunfisk_galarian'
        >>> print(ub.repr2(api.get_info(name)))

        api.data['current_pokemon_moves']

        api
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
        }
        api.data = {}
        for key, url in api.routes.items():

            redo = 0
            data_fpath = ub.grabdata(url, verbose=1, redo=redo)

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

        api.fast_moves = ub.group_items(
            api.data['fast_moves'],
            lambda item: normalize(item['name'].lower()))

        api.charged_moves = ub.group_items(
            api.data['charged_moves'],
            lambda item: normalize(item['name'].lower()))

        if 0:
            ub.map_vals(len, api.fast_moves)
            ub.map_vals(len, api.charged_moves)

        api.learnable = {
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

    def normalize(self, x):
        return normalize(x)

    def __nice__(self):
        return str(list(api.routes.keys()))

    def normalize_name_and_form(api, name, form=None):
        if name.endswith('-shadow'):
            if form is None:
                form = 'Shadow'
            else:
                assert form == 'Shadow', '{}, {}'.format(api, name)

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

        return name, form

    def get_info(api, name, form=None):
        """
        Example:
            >>> from pypogo.pogo_api import *  # NOQA
            >>> api = PogoAPI()
            >>> name = 'stunfisk_galarian'
            >>> print(ub.repr2(api.get_info(name)))
            >>> name = 'stunfisk'
            >>> print(ub.repr2(api.get_info(name)))
            >>> name = 'umbreon'
            >>> print(ub.repr2(api.get_info(name)))
            >>> name = 'eevee'
            >>> print(ub.repr2(api.get_info(name)))
            >>> name = 'castform_snowy'
            >>> print(ub.repr2(api.get_info(name)))

            >>> name = 'smeargle'
            >>> print(ub.repr2(api.get_info(name)))

            >>> name = 'wormadam'
            >>> print(ub.repr2(api.get_info(name)))

        """
        try:
            name_, form_ = api.normalize_name_and_form(name, form)
            form_ = form_.lower()
        except Exception:
            raise Exception('name={name}, form={form}'.format(**locals()))

        try:
            infos = [
                api.name_to_stats[name_],
                api.name_to_evolutions[name_],
                api.name_to_type[name_],
                api.name_to_moves[name_]
            ]
        except Exception:
            raise Exception(
                'name={name}, form={form}, name_={name_}, form_={form_}'.format(**locals()))

        info = {}
        for all_infos in infos:
            part = None
            form_to_info = ub.group_items(all_infos, lambda _info: _info['form'].lower())
            if form_ in form_to_info:
                parts = form_to_info[form_]
            else:
                import warnings
                warnings.warn('Unable to find name={} form_={} form={}'.format(name, form_, form))
                parts = ub.peek(form_to_info.values())

            if len(parts) != 1:
                print('parts = {!r}'.format(parts))
                raise Exception
            part = parts[0]
            info.update(part)

        if 1:
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


# HACK: Make a global API variable
# we should likey do some lazy initialization or something better


api = None


def global_api():
    global api
    if api is None:
        api = PogoAPI()
    return api

api = global_api()
