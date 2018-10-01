Introduction
"""""""""""""""""

The primary aim of this document is to give an overview of the *Hermina-Janos* local clustering
algorithm, its variants and to some extent their implementations. Besides the algorithms themselves,
the utilities that are included in the library will also be discussed briefly such as cluster
definitions, node ranking and step history keeping.

It is assumed that the reader has some knowledge in graph or network theory, cluster analysis,
and graph cluster analysis, although some concepts will be briefly described here.

Note that in this document it is assumed that graphs are *undirected*. This is because the code
in this library was designed with undirected graphs in mind; the included *algorithms do not have
this limitation*.

Local graph clustering
===========================

*Graph clustering* algorithms aim to divide the nodes of a graph into one or more groups or
clusters based on some measure of similarity as best as possible. There are many different
ways to define a cluster depending on the goal of the analysis. In graph cluster analysis
the usual definition of a cluster is a group of nodes that are relatively densely
interconnected but have few connections towards the nodes outside the cluster.

*Global clustering* algorithms get a whole graph as input and assign each node of the graph
to a (or in some cases more) cluster. Over the years, many fast and accurate global clustering
algorithms have been developed, but in some cases using a global algorithm is not practical
(or not possible), so we have to turn to local algorithms.

*Local clustering* algorithms get a small set of *source nodes* (typically a single node) as
input and calculate the cluster they belong to in the graph. While doing so, local algorithms
are only allowed to look at the already visited nodes of the graph and their neighbourhood.

The Hermina-Janos local clustering algorithm
=================================================

The Hermina-Janos algorithm is a simple iterative process that repeats the following two steps
until it reaches a stable state:

1. *Expansion step*: For each node in the neighbourhood of the cluster, decide whether *adding*
   it to the cluster would *increase the cluster's quality*, collect all the neighbours whose
   *addition* would improve the cluster and *add them to the cluster in one step*.
2. *Reduction step*: For each node on the border of the cluster, decide whether *removing* it
   from the cluster would *increase the cluster's quality*, collect all the nodes whose
   *removal* would improve the cluster and *remove them from the cluster in one step*.

The algorithm stops if either of the following conditions are met:

- The cluster didn't change during the latest iteration (an expansion and reduction step pair).
  In this case the same (potentially empty) set of nodes must have been added to and removed
  from the cluster in the expansion and reduction steps of the latest iteration.
- The algorithm ends up in a cycle, that is the same set of nodes were added to and removed
  from the cluster as in a previous iteration and the cluster didn't change either.
- Other conditions for stopping the algorithms can of course be defined such as max-size criteria.

Some things to note about the algorithm:

- All the nodes that should be added to the cluster in the expansion or removed from the cluster
  in the reduction step are added or removed in one go. This is to remove the random factor from
  the algorithm.
- Nothing was said about how the algorithm decides whether a node should be added to or removed
  from the cluster. This strategy - termed *cluster definition* in this document - is not part
  of the algorithm; any cluster definition that is capable of making these two decisions can be
  used by the algorithm.

The Hermina-Janos *hierarchical* local clustering algorithm
================================================================

The *hierarchical* version of the Hermina-Janos local clustering algorithm extends the base
version with an extra layer that allows it uncover clusters at different hierarchy levels or
"distances" from the source nodes of the cluster analysis. To do so, the hierarchical algorithm
needs a "hierarchical" cluster definition that will be described below, after the description
of the algorithm.

Similarly to the base algorithm, the hierarchical Hermina-Janos algorithm is also an iterative
process with two steps, that starts with a cluster - that contains only the source nodes of the
cluster analysis - and which the algorithm will continuously expand:

1. *Local clustering step*: use the Hermina-Janos local clustering algorithm with the current
   configuration of the used cluster definition to *extend the cluster* to the next hierarchy
   level. Note that this step only extends the already existing cluster and not recalculates
   it starting from the source nodes (that is also a viable option, just another flavour of
   the same hierarchical algorithm).
2. *Cluster definition relaxation step*: this is a highly cluster definition-dependent step
   where the algorithm adjusts or relaxes the cluster definition's parameters so in the next
   iteration the local clustering algorithm will be able to further extend the cluster - to
   the next hierarchy level - using the adjusted cluster definition.

The algorithm stops if either of the following conditions are met:

- The cluster definition can not be relaxed anymore.
- If a desired cluster size was specified and the calculated cluster's size surpassed it or
  the cluster includes all the nodes of the graph.

As mentioned earlier, the Hermina-Janos hierarchical local clustering algorithm needs a
hierarchical cluster definition that can be specified by the following requirements:

- First of all it must be a cluster definition the Hermina-Janos local clustering algorithm can
  use (that is it can decide whether a node should be added to or removed from the cluster at a
  given state).
- It must be able to adjust or relax its parameters - based on the last execution of the local
  clustering algorithm - in a way that allows the local clustering algorithm to further extend
  the cluster in the next iteration of the hierarchical algorithm.

In general the fewer free parameters cluster definitions - or in general a clustering algorithm -
have the better, but in most cases they do have some that alter their behaviour. If any these
parameters - or a combination of them - can be modified to allow a larger cluster, then the cluster
definition is suitable for the Hermina-Janos hierarchical clustering algorithm. Actually, in a sense
the algorithm removes some free parameters from the cluster definition and turns them into cluster
hierarchy level definitions.

In the following sections first the various algorithm implementations - called *cluster engines*
in the document - included in this library will be described, then the cluster definitions will
be discussed.

Cluster engines
====================

This section describes the various local clustering algorithm implementations termed *cluster engines*.

Local cluster engine
-------------------------

In this library, *local cluster engine* is the default implementation of the Hermina-Janos
local clustering algorithm. It just needs a cluster definition to use in the iterative
cluster building process and it works exactly as described in the corresponding section.

By default the cluster engine will use the connectivity based cluster definition to calculate
a cluster.

Hierarchical local cluster engine
--------------------------------------

The *hierarchical local cluster engine* is the default implementation of the Hermina-Janos
hierarchical local clustering algorithm. It needs a hierarchical cluster definition to be
functional and a minimum cluster size to serve as a stopping condition.

By default the hierarchical cluster engine uses the local cluster engine to expand the cluster
to the next hierarchy level and uses the connectivity based cluster definition to find clusters.

Multi-step local cluster engine
------------------------------------

The *multi-step local cluster engine* is a generalisation of the Hermina-Janos algorithm in
the sense that here the user can define how many expansion steps should be taken before moving
on to the - also configurable amount of - reduction steps within one iteration of the algorithm.

By default the cluster engine will use the connectivity based cluster definition to calculate
a cluster.

Cluster definitions
========================

As already mentioned in the previous sections, a cluster definition - that is suitable for the
various Hermina-Janos local clustering algorithms - must implement a cluster quality metric such
as min-cut in a way that allows it to answer the following two questions for the clustering algorithms:

1. Given a node that is in the neighbourhood of the current cluster and the current cluster
   itself, would adding the node to the cluster improve the cluster's quality?
2. Given a node that is in the current cluster and the current cluster itself, would removing
   the node from the cluster improve the cluster's quality?

Furthermore, for a cluster definition to be hierarchical, it must be able to adjust or relax
its parameters and to do so in a way that allows more nodes to be included in the cluster during
the next local clustering with the definition.

Connectivity based cluster definition
-----------------------------------------

The connectivity based cluster definition is the default cluster definition implementation in
this library that also happens to be a hierarchical one.

The cluster definition broadly works the following way:

1. It calculates the *quality difference* the node provides or would provide for the cluster.
2. It calculates the minimum quality difference - the *threshold* - to compare the quality
   difference to.
3. *Addition*: if the quality difference of the addition is greater than or equal to the
   threshold, then the node should be added. *Removal*: if the quality difference of the
   removal is less than the threshold, then the node should be removed.

The cluster definition has the following configurable parameters:

- *Weighting coefficient*: An edge weight multiplier for the edges that have at least one of
  their endpoints within the cluster. This is the parameter the cluster definition adjusts
  during hierarchical clustering.
- *Threshold modifier*: The calculated base threshold is multiplied by the value of this
  parameter before being used to make a decision regarding the given node.

The quality difference is calculated in the following way: sum the edge weights multiplied by
the weighting coefficient for each edge that connects the given node to the cluster.

The threshold is calculated in the following way: take the minimum of the following values
and multiply it by the threshold modifier:

- Half the number of nodes in the cluster minus 1.
- Half the degree of the given node.
- The sum of the degrees of the nodes within the cluster divided by 2 times the number of
  nodes within the cluster.

The cluster definition adjusts itself to the next hierarchy level by finding the value to
multiply the weighting coefficient by in order for the cluster definition to be able to
include at least one more node in the cluster.

For more details, see the actual implementation.

Other
----------

There are many cluster quality metrics that could be turned into (herarchical) cluster
definitions for this algorithm. The most obvious choices that should (will) be implemented
and tested in this library are *modularity* and *conductance*. As mentioned in the
contribution section of the readme file, implementations of these cluster definitions
would be very welcome.

Utilities
==============

The library contains a ``history`` and a ``ranking`` module that will be introduced very
briefly in this section.

Ranking
------------

The ranking module can be used to *rank* the nodes in the cluster and broadly speaking their
neighbours by their importance or contribution to the cluster. Ranking - in its current form -
needs a cluster definition to be similarly implemented to the connectivity cluster definition.
Cluster engines are able to create a so called rank provider that - given a step history
described later in this section - can calculate a single numerical value - the rank of the
node - for each node that was seen during the last step of the clustering.

For more details, see the ``ranking`` module of the library.

History
------------

The history module is responsible for recording the steps a cluster engine has taken while
calculating a cluster. History recording is done automatically by the local cluster engine.
Actually, history recording is not only an optional extension to the local cluster engine,
it is also used find out if the cluster engine has entered a loop and should therefore be
terminated.

For more details, see the ``history`` module of the library.

Example - the Zachary karate club
======================================

The library includes a ``demo`` module that illustrates the usage of both the local and
the hierarchical local cluster engines on the Zachary karate club.
See the readme file for installation instructions and the ``demo`` module for more details.
