pypogo - The Python Pokemon Go Module
=====================================

|GithubActions| 

.. .. |Codecov| |Pypi| |Downloads| |ReadTheDocs|


The ``pypogo`` module.

The goal is a Python module to run Pokemon Go calculations and simulations.
This module interfaces with ``https://pogoapi.net/api/v1/`` to obtain data like
pokemon stats and stuff. It can currently do CP calculations, and check the
rank of IVs based on the stats product of the mons at various levels.

I'm currently working on a battle simulator, and I plan to train agents to play
PVP using neural networks and reinforcement learning. But it will be a while
before that's done.

In the meantime, there are still useful things you can do with this package.

The main way to interface is using the ``Pokemon`` class. 

You can find IVs and levels to maximize CP under constraints:

.. code:: python

    >>> from pypogo.pokemon import Pokemon
    >>> base = Pokemon('eevee')
    >>> print('base = {}'.format(base))
    >>> #
    >>> max_cp = 1500
    >>> #
    >>> for mon in base.family():
    >>>     mon.maximize(max_cp, ivs='maximize', max_level=51)
    >>>     print('mon = {}'.format(mon))
    base = <Pokemon(eevee, None, None, None, None)>
    mon = <Pokemon(leafeon, 1497, 19.0, [1, 15, 14], None)>
    mon = <Pokemon(espeon, 1498, 17.5, [0, 15, 15], None)>
    mon = <Pokemon(umbreon, 1497, 27.5, [0, 15, 14], None)>
    mon = <Pokemon(flareon, 1500, 18.5, [0, 15, 13], None)>
    mon = <Pokemon(glaceon, 1500, 18.0, [0, 15, 12], None)>
    mon = <Pokemon(jolteon, 1500, 19.5, [0, 12, 15], None)>
    mon = <Pokemon(vaporeon, 1500, 18.0, [1, 15, 15], None)>


You can do purification and evolution operations.

.. code:: python

    >>> from pypogo.pokemon import Pokemon
    >>> self = Pokemon('ralts', ivs=[6, 13, 15], level=20,
    >>>                 shadow=True, shiny=True)
    >>> new = self.purify()
    >>> print('self = {}'.format(self))
    >>> print('new  = {}'.format(new))
    >>> evos = new.evolved()[0].evolved()
    >>> print(evos[0])
    >>> print(evos[1])
    self = <Pokemon(ralts(😈,✨), 274, 20, [6, 13, 15], None)>
    new  = <Pokemon(ralts(👼,✨), 285, 20, (8, 15, 15), None)>
    <Pokemon(gallade(👼,✨), 1718, 20, (8, 15, 15), None)>
    <Pokemon(gardevoir(👼,✨), 1718, 20, (8, 15, 15), None)>

You can do build a table of league rankings for different IV combinations

.. code:: python

    >>> from pypogo.pokemon import Pokemon
    >>> self = Pokemon('beedrill')
    >>> beedrill_df = self.league_ranking_table(max_cp=1500)
    >>> print(beedrill_df)
          iva  ivd  ivs    cp  level      attack     defense  stamina  stat_product_k  rank     percent
    rank
    1       0   13   14  1499   32.5  126.206025  106.789714      132     1779.030702     1  100.000000
    2       0   14   13  1500   32.5  126.206025  107.536495      131     1777.899723     2   99.316671
    3       0   14   15  1496   32.0  125.700414  107.105679      132     1777.146120     3   98.861349
    4       0   15   14  1497   32.0  125.700414  107.849468      131     1775.930690     4   98.126996
    5       1   13   15  1500   32.0  126.444204  106.361889      132     1775.247460     5   97.714193
    ...   ...  ...  ...   ...    ...         ...         ...      ...             ...   ...         ...
    4092   14    2    1  1489   32.0  136.113467   98.180205      121     1617.001419  4092    2.103120
    4093   15    0    2  1490   32.0  136.857256   96.692626      122     1614.436679  4093    0.553523
    4094   15    0    0  1493   32.5  137.407744   97.081558      121     1614.110696  4094    0.356567
    4095   15    1    3  1488   31.5  136.304546   97.042911      122     1613.741564  4095    0.133540
    4096   15    1    1  1492   32.0  136.857256   97.436416      121     1613.520542  4096    0.000000
    ...
    [4096 rows x 11 columns]


This module is being developed mainly for fun and personal use. Features as
added as I need them to answer questions mostly to do with my own personal
min-maxing. Feel free to fork, contribute, or use as you'd like.

+------------------+----------------------------------------------+
| Read the docs    | https://pypogo.readthedocs.io                |
+------------------+----------------------------------------------+
| Github           | https://github.com/Erotemic/pypogo           |
+------------------+----------------------------------------------+
| Pypi             | https://pypi.org/project/pypogo              |
+------------------+----------------------------------------------+


.. |Pypi| image:: https://img.shields.io/pypi/v/pypogo.svg
   :target: https://pypi.python.org/pypi/pypogo

.. |Downloads| image:: https://img.shields.io/pypi/dm/pypogo.svg
   :target: https://pypistats.org/packages/pypogo

.. |ReadTheDocs| image:: https://readthedocs.org/projects/pypogo/badge/?version=release
    :target: https://pypogo.readthedocs.io/en/release/

.. # See: https://ci.appveyor.com/project/jon.crall/pypogo/settings/badges
.. |Appveyor| image:: https://ci.appveyor.com/api/projects/status/py3s2d6tyfjc8lm3/branch/master?svg=true
   :target: https://ci.appveyor.com/project/jon.crall/pypogo/branch/master

.. |GitlabCIPipeline| image:: https://gitlab.kitware.com/utils/pypogo/badges/master/pipeline.svg
   :target: https://gitlab.kitware.com/utils/pypogo/-/jobs

.. |GitlabCICoverage| image:: https://gitlab.kitware.com/utils/pypogo/badges/master/coverage.svg?job=coverage
    :target: https://gitlab.kitware.com/utils/pypogo/commits/master

.. |CircleCI| image:: https://circleci.com/gh/Erotemic/pypogo.svg?style=svg
    :target: https://circleci.com/gh/Erotemic/pypogo

.. |Travis| image:: https://img.shields.io/travis/Erotemic/pypogo/master.svg?label=Travis%20CI
   :target: https://travis-ci.org/Erotemic/pypogo

.. |Codecov| image:: https://codecov.io/github/Erotemic/pypogo/badge.svg?branch=master&service=github
   :target: https://codecov.io/github/Erotemic/pypogo?branch=master

.. |GithubActions| image:: https://github.com/Erotemic/pypogo/actions/workflows/tests.yml/badge.svg?branch=main
    :target: https://github.com/Erotemic/pypogo/actions?query=branch%3Amain
