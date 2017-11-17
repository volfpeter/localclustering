"""
This module contains hierarchical local cluster engine implementations.
"""

# Imports
# ------------------------------------------------------------

from typing import List, Optional

from graphscraper.base import Node
from localclustering.cluster import Cluster
from localclustering.definitions.base import HierarchicalClusterDefinition
from localclustering.definitions.connectivity import ConnectivityClusterDefinition
from localclustering.history import StepHistory
from localclustering.localengine import LocalClusterEngine
from localclustering.ranking import StepHistoryRankProvider

# Module constants
# ------------------------------------------------------------

__author__ = 'Peter Volf'

# Classes
# ------------------------------------------------------------


class HierarchicalClusterEngine(object):
    """
    The default implementation of the Hermina-Janos hierarchical local clustering algorithm.

    This class implements the hierarchical local clustering algorithm by wrapping a
    `LocalClusterEngine` to calculate the cluster for each hierarchy level.

    The way the algorithm works is detailed in the following document:
    https://github.com/volfpeter/localclustering/blob/master/documents/algorithm.rst
    """

    # Initialization
    # ------------------------------------------------------------

    def __init__(self) -> None:
        """
        Initialization.
        """
        self._cluster: Cluster = None
        """The cluster the engine is building."""

        self._step_history: StepHistory = None
        """The step history object that records the execution of the clustering engine."""

        self.cluster_definition: HierarchicalClusterDefinition = ConnectivityClusterDefinition()
        """The cluster definition to use."""

        self._cluster_engine: LocalClusterEngine = LocalClusterEngine(self.cluster_definition)
        """The cluster engine the hierarchical cluster engine will use to build clusters."""

        self.min_cluster_size = 15
        """The minimum size of the cluster the engine is expected to find."""

    # Properties
    # ------------------------------------------------------------

    @property
    def last_cluster(self) -> Cluster:
        """
        Returns the result of the last execution of the `cluster()` method.
        """
        return self._cluster

    @property
    def last_step_history(self) -> StepHistory:
        """
        Returns the step history corresponding to the last execution of the `cluster()` method.
        """
        return self._step_history

    # Public methods
    # ------------------------------------------------------------

    def cluster(self, source_nodes: List[Node]) -> Cluster:
        """
        Runs the cluster engine and returns the calculated cluster.

        Args:
            source_nodes (List[Node]): The list of source nodes whose cluster is to be found.
                                       This list must contain at least one node.

        Returns:
            The cluster the cluster engine found.
        """
        cluster: Cluster = self._cluster_engine.create_cluster(source_nodes)
        step_history: StepHistory = self._cluster_engine.create_step_history(source_nodes)
        return self.execute_on(cluster, step_history)

    def execute_on(self, cluster: Cluster, step_history: StepHistory=None) -> Optional[Cluster]:
        """
        Executes the local cluster engine using the given cluster and step history.

        Args:
            cluster (Cluster): The cluster to use as the starting point.
            step_history (StepHistory): An optional step history object to use.

        Returns:
            The cluster the cluster engine found or `None` if the method was called without a cluster object.
        """
        self._cluster = cluster
        self._step_history = step_history
        if cluster is None:
            return None

        if self._step_history is None:
            self._step_history = self._cluster_engine.create_step_history(list(cluster.nodes))

        if len(cluster) == 0:
            return cluster

        # Do not modify the base cluster definition the user has just set.
        effective_cluster_definition: HierarchicalClusterDefinition = self.cluster_definition.clone()
        self._cluster_engine.cluster_definition = effective_cluster_definition

        while len(cluster) < self.min_cluster_size:
            # Execute the local cluster engine.
            self._cluster_engine.execute_on(cluster, self._step_history)

            # Adjust the cluster definition for the next cluster hierarchy level.
            step_descriptor = self._step_history.last_step
            gain_descriptors = []
            values = step_descriptor.removed_gain_descriptors
            if values:
                gain_descriptors.extend(values)
            values = step_descriptor.not_added_gain_descriptors
            if values:
                gain_descriptors.extend(values)
            if not effective_cluster_definition.adjust_definition_for_next_hierarchy_level(gain_descriptors):
                # If the cluster definition cannot be adjusted, then we're done.
                break

        return cluster

    def get_rank_provider(self) -> StepHistoryRankProvider:
        """
        Returns a `StepHistoryRankProvider` that can be used to rank the nodes that are in or around the cluster
        that was calculated by the `cluster()` method of the cluster engine.

        Returns:
            A `StepHistoryRankProvider` that can be used to rank the nodes that are in or around the cluster.
        """
        return StepHistoryRankProvider(self._step_history)
