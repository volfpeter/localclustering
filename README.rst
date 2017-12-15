LocalClustering
====================

The library implements multiple variations of a local graph clustering algorithm
named the *Hermina-Janos algorithm* in memory of my beloved grandparents.

For the description of the algorithms, have a look at `this document <https://github.com/volfpeter/localclustering/blob/master/documents/algorithm.rst>`_.
For an evaluation and demo of the algorithms using the Spotify artist similarity graph, look at the attached `IPython notebook`_.

Besides the clustering algorithms themselves, the library also contains a specialized cluster
implementation, cluster definitions and a ranking module.

Demo
---------

Besides the already mentioned `IPython notebook`_, the library contains a demo module
that shows the basic usage of this project. If you wish to run the demo, you will first
need to install the igraph_ and cairo_ libraries and their Python interfaces besides
the default dependencies of the library.

Dependencies
-----------------

The library's only requirement is the GraphScraper_ library_ that you can install
with pip (``pip install graphscraper``). As a consequence, you will also need
SQLAlchemy_ or Flask-SQLAlchemy_ to be installed.

License - GNU AGPLv3
-------------------------

The library is open-sourced under the conditions of the GNU Affero General Public
License_ v3.0, which is the strongest copyleft license. The reason for using this
license is that this library is the "publication" of the *Hermina-Janos algorithm*
and it should be referenced accordingly.

Contribution
-----------------

Any form of constructive contribution is welcome. Besides the usual things
(feedback, features, bug fixes, tests, additional documentation, etc.), the
following types of contributions are especially appreciated:

- Algorithm analysis and evaluation (algorithmic complexity, accuracy with different
  cluster definitions, etc.).

- Analysis of how the weighting coefficients of the connectivity based cluster
  definition corresponding to the different hierarchy levels relate to each-other
  in different real-world graphs.

- Implementation of new cluster definitions (modularity or conductance based for example).

- etc.

.. _AGPLv3: https://choosealicense.com/licenses/agpl-3.0/
.. _Flask-SQLAlchemy: http://flask-sqlalchemy.pocoo.org/
.. _`IPython notebook`: https://github.com/volfpeter/localclustering/blob/master/documents/Algorithm%20Analysis%20with%20the%20Spotify%20Related%20Artists%20Graph.ipynb
.. _library: https://github.com/volfpeter/graphscraper
.. _License: https://choosealicense.com/licenses/agpl-3.0/
.. _GraphScraper: https://pypi.python.org/pypi/graphscraper
.. _igraph: http://igraph.org
.. _cairo: https://www.cairographics.org/pycairo/
.. _SQLAlchemy: https://www.sqlalchemy.org/
