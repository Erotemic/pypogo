


def test_api_consistency():
    import pypogo
    import ubelt as ub
    api = pypogo.api

    all_pokemon = list(api.enumerate_all_pokemon())

    cm_move_hist = ub.ddict(lambda: 0)
    fm_move_hist = ub.ddict(lambda: 0)
    for pkmn in ub.ProgIter(all_pokemon):
        candidate_moves = pkmn.candidate_moveset()
        assert set(candidate_moves.keys()) == {'fast', 'charged'}
        for fm_name in candidate_moves['fast']:
            fm_name = api.normalize(fm_name)
            fm_move_hist[fm_name] += 1
        for cm_name in candidate_moves['charged']:
            cm_name = api.normalize(cm_name)
            cm_move_hist[cm_name] += 1

        if pkmn.name not in {'smeargle'}:
            for i in range(10):
                pop = pkmn.copy()
                pop.populate_moves()
                if pop.moves[0] == 'Struggle':
                    # not handled.
                    continue
                pop.populate_stats()
                pop.populate_move_stats()

    common = set(fm_move_hist) & set(cm_move_hist)
    assert common == {'struggle'}, 'shouldnt have much in comon here'
    move_hist = ub.dict_union(fm_move_hist, cm_move_hist)
    unregistered = set(move_hist) - set(api.all_move_names)
    unused = set(api.all_move_names) - set(move_hist)
