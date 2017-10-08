LocalClustering
====================

The library implements multiple variations of a local graph clustering algorithm_
named the *Hermina-Janos algorithm* in memory of my beloved grandparents.

Besides the clustering algorithms themselves, the library also contains a cluster
implementation (obviously) and utility classes for i) ranking the nodes the algorithms
have seen during the clustering process and ii) recording the steps the clustering
algorithms have taken.

See the documents_ included in the library for more details.

Local clustering
---------------------

A graph clustering algorithm is called local if its goal is to find the cluster
of one or more "source" nodes without looking at whole graph. In other words
a local algorithm starts out from the source nodes and at each step only looks
at the nodes it has seen so far and their neighbors to find the cluster the
source nodes belong to.

Demo
---------

The library contains a demo module that shows the basic usage of this project.
If you wish to run the demo, you will first need to install the igraph_ and
cairo_ libraries and their Python interfaces besides the default dependencies
of the library.

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


.. _algorithm: https://github.com/volfpeter/localclustering/blob/master/documents/algorithm.rst
.. _AGPLv3: https://choosealicense.com/licenses/agpl-3.0/
.. _documents: https://github.com/volfpeter/localclustering/tree/master/documents
.. _Flask-SQLAlchemy: http://flask-sqlalchemy.pocoo.org/
.. _library: https://github.com/volfpeter/graphscraper
.. _License: https://choosealicense.com/licenses/agpl-3.0/
.. _GraphScraper: https://pypi.python.org/pypi/graphscraper
.. _igraph: http://igraph.org
.. _cairo: https://www.cairographics.org/pycairo/
.. _SQLAlchemy: https://www.sqlalchemy.org/
