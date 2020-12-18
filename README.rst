The pypogo Module
================

|CircleCI| 

.. |Codecov| |Pypi| |Downloads| |ReadTheDocs|


The ``pypogo`` module.

The goal is a Python module to run Pokemon Go calculations and simulations.
This module interfaces with ``https://pogoapi.net/api/v1/`` to obtain data like
pokemon stats and stuff. It can currently do CP calculations, and check the
rank of IVs based on the stats product of the mons at various levels.

Battle simulation and other statistics like knowing the cost of powering up a
particular mon to PVP level given its IV ranking would be interesting.


+------------------+----------------------------------------------+
| Read the docs    | https://pypogo.readthedocs.io                 |
+------------------+----------------------------------------------+
| Github           | https://github.com/Erotemic/pypogo            |
+------------------+----------------------------------------------+
| Pypi             | https://pypi.org/project/pypogo               |
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
