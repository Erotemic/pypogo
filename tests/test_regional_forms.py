


def test_hisuian_form_explicit():
    from pypogo.pokemon import Pokemon
    p = Pokemon('Growlithe', ivs=[4, 14, 13], cp=556, form='Hisuian')
    assert p.form == 'Hisuian'


def test_hisuian_name_suffix():
    from pypogo.pokemon import Pokemon
    p = Pokemon('growlithe_hisuian', ivs=[4, 14, 13], cp=556)
    assert p.form == 'Hisuian'
    assert p.name == 'growlithe'


def test_hisuian_hints():
    from pypogo.pokemon import Pokemon
    p = Pokemon('Growlithe', ivs=[4, 14, 13], cp=556, hints='hisuian')
    assert p.form == 'Hisuian'


def test_hisuian_evolution_default():
    from pypogo.pokemon import Pokemon
    p = Pokemon('overqwil', ivs=[1, 15, 15])
    assert p.form == 'Hisuian'


def test_hisuian_sneasler_default():
    from pypogo.pokemon import Pokemon
    p = Pokemon('sneasler', ivs=[1, 15, 15])
    assert p.form == 'Hisuian'


def test_alolan_name_suffix():
    from pypogo.pokemon import Pokemon
    p = Pokemon('vulpix_alolan', ivs=[1, 15, 15])
    assert p.form == 'Alola'
    assert p.name == 'vulpix'


def test_alolan_alola_suffix():
    from pypogo.pokemon import Pokemon
    p = Pokemon('vulpix_alola', ivs=[1, 15, 15])
    assert p.form == 'Alola'


def test_alolan_hints():
    from pypogo.pokemon import Pokemon
    p = Pokemon('vulpix', ivs=[1, 15, 15], hints='alolan')
    assert p.form.lower() == 'alola'


def test_paldean_form_explicit():
    from pypogo.pokemon import Pokemon
    p = Pokemon('wooper', ivs=[1, 15, 15], form='Paldea')
    assert p.form == 'Paldea'


def test_paldean_name_suffix():
    from pypogo.pokemon import Pokemon
    p = Pokemon('wooper_paldean', ivs=[1, 15, 15])
    assert p.form == 'Paldea'
    assert p.name == 'wooper'


def test_paldean_hints():
    from pypogo.pokemon import Pokemon
    p = Pokemon('wooper', ivs=[1, 15, 15], hints='paldean')
    assert p.form == 'Paldea'


def test_paldean_evolution_default():
    from pypogo.pokemon import Pokemon
    p = Pokemon('clodsire', ivs=[1, 15, 15])
    assert p.form == 'Paldea'


def test_regular_growlithe_unchanged():
    """Ensure regular Growlithe still defaults to Normal form."""
    from pypogo.pokemon import Pokemon
    p = Pokemon('Growlithe', ivs=[0, 15, 15])
    assert p.form == 'Normal'
