import json
import ubelt as ub
import networkx as nx


def normalize(n):
    return n.upper().replace(' ', '_')


class PogoAPI(ub.NiceRepr):
    """
    Object to help with access to data from pogoapi.net

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
    """
    def __init__(api):
        api.base = 'https://pogoapi.net/api/v1/'
        api.routes = {
            'pokemon_stats': api.base + 'pokemon_stats.json',
            'current_pokemon_moves': api.base + 'current_pokemon_moves.json',
            'pokemon_evolutions': api.base + 'pokemon_evolutions.json',
            'cp_multiplier': api.base + 'cp_multiplier.json',
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

        _name_to_items = ub.group_items(
            api.data['current_pokemon_moves'],
            lambda item: item['pokemon_name'].lower())
        _name_to_items.default_factory = None
        _name_to_items = dict(_name_to_items)

        # base = 'http://pokeapi.co/api/v2/pokemon/'
        api.name_to_moves = _name_to_items

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

        if name == 'farfetchd':
            name = "farfetch\u2019d"

        if form is None:
            form = 'Normal'

        return name, form

    def get_info(api, name, form=None):
        """
        """
        try:
            name_, form_ = api.normalize_name_and_form(name, form)
        except Exception:
            raise Exception('name={name}, form={form}'.format(**locals()))

        try:
            infos = [
                api.name_to_stats[name_],
                api.name_to_moves[name_],
                api.name_to_evolutions[name_],
            ]
        except Exception:
            raise Exception(
                'name={name}, form={form}, name_={name_}, form_={form_}'.format(**locals()))

        info = {}
        for all_infos in infos:
            part = None
            for _info in all_infos:
                if _info['form'] == form_:
                    part = _info
            if part is None:
                raise KeyError
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

            if form_ == 'Normal':
                if info['form'] == 'Shadow':
                    charge_moves.add('FRUSTRATION')
                    charge_moves.add('RETURN')

            if name_ not in api.learnable:
                api.learnable[name_] = {}
            api.learnable[name_]['fast'] = sorted(fast_moves)
            api.learnable[name_]['charge'] = sorted(charge_moves)
        return info


# HACK: Make a global API variable
# we should likey do some lazy initialization or something better
api = PogoAPI()
