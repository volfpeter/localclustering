---
title: "Local clustering"
tags:
  - Python
  - graph theory
  - clustering algorithm
  - ranking
authors:
  - name: Peter Volf
    orcid: 0000-0002-6226-4277
    affiliation: 1
affiliations:
  - name: None
    index: 1
date: 14 September 2018
bibliography: paper.bib
---

# Introduction

Graph clustering algorithms aim to divide the nodes of a graph into one or more groups or clusters based on some measure of similarity. There are many different ways to define a cluster depending on the goal of the analysis. In graph cluster analysis the usual definition of a cluster is a group of nodes that are relatively densely interconnected but have few connections towards the nodes outside the cluster.

Local clustering algorithms get a small set of source nodes (typically a single node) as input and calculate the cluster they belong to in the graph. While doing so, local algorithms are only allowed to look at the already visited nodes of the graph and their neighbours.

# Algorithm

This Python package implements the Hermina-Janos local clustering algorithm and its hierarchical variation. The algorithms are independent of the used cluster definition, instead they define a set of requirements cluster definitions must fulfill in order to work with the algorithms. The package provides one such cluster definition.

## Local clustering algorithm

The Hermina-Janos algorithm is a simple iterative process that repeats the following two steps until it reaches a stable state:

1. Expansion step: For each node in the neighbourhood of the cluster, decide whether adding it to the cluster would increase the cluster's quality, collect all the neighbours whose addition would improve the cluster and add them to the cluster in one step.
2. Reduction step: For each node on the border of the cluster, decide whether removing it from the cluster would increase the cluster's quality, collect all the nodes whose removal would improve the cluster and remove them from the cluster in one step.

![Example result of local clustering.](https://raw.githubusercontent.com/volfpeter/localclustering/master/documents/cluster_example.png)

## Hierarchical local clustering algorithm

The hierarchical version of the Hermina-Janos local clustering algorithm extends the base version with an extra layer that allows it uncover clusters at different hierarchy levels or "distances" from the source nodes of the cluster analysis.

Similarly to the base algorithm, the hierarchical Hermina-Janos algorithm is also an iterative process with the following two steps:

1. Local clustering step: use the Hermina-Janos local clustering algorithm with the current configuration of the used cluster definition to calculate the cluster.
2. Cluster definition relaxation step: this is a highly cluster definition-dependent step where the algorithm adjusts or relaxes the cluster definition's parameters so in the next iteration the local clustering algorithm will be able to further extend the cluster.

# Tools and utilities

The package provides a ranking component that can be used to rank the nodes in the cluster and their neighbours by their importance or contribution to the cluster.

A component for recording the steps the algorithms have taken is also provided. It makes it possible to trace back each decision and step the algorithms have taken to see exactly how the result was calculated.

# Resources

These are the main resources besides the source code:

* [This document](https://github.com/volfpeter/localclustering/blob/master/documents/algorithm.rst) provides a thorough description of the algorithms and the included cluster definition.
* [This notebook](https://github.com/volfpeter/localclustering/blob/master/documents/Algorithm%20Analysis%20with%20the%20Spotify%20Related%20Artists%20Graph.ipynb) provides a demo and in-depth evaluation of the algorithms and the ranking component using Spotify's Related Artists graph.


# References
