"""
This module contains local cluster engine implementations along with the related utility and helper classes.
"""

# Imports
# ------------------------------------------------------------

from typing import List, Optional

from graphscraper.base import Node
from localclustering.cluster import Cluster
from localclustering.definitions.base import ClusterDefinition, GainDescriptor
from localclustering.definitions.connectivity import ConnectivityClusterDefinition
from localclustering.history import StepDescriptor, StepHistory
from localclustering.ranking import StepHistoryRankProvider

# Module constants
# ------------------------------------------------------------

__author__ = 'Peter Volf'

# Classes
# ------------------------------------------------------------


class LocalClusterEngine(object):
    """
    The default implementation of the Hermina-Janos local clustering algorithm.

    The way the algorithm works is detailed in the following document:
    https://github.com/volfpeter/localclustering/blob/master/documents/algorithm.rst
    """

    # Initialization
    # ------------------------------------------------------------

    def __init__(self,
                 cluster_definition: ClusterDefinition = None,
                 source_nodes_in_result: bool = True,
                 max_cluster_size: int = 100) -> None:
        """
        Initialization.

        Args:
            cluster_definition (ClusterDefinition): The cluster definition the cluster engine should use.
                                                    If `None`, then a default cluster definition will be used.
            source_nodes_in_result (bool): Whether the given source nodes must be in the result of the clustering.
            max_cluster_size (int): The upper limit of the size of the calculated cluster.
        """
        self._cluster: Cluster = None
        """
        The cluster the engine is building.
        """
        self._step_history: StepHistory = None
        """
        The step history object that records the execution of the clustering engine.
        """
        self.source_nodes_in_result: bool = source_nodes_in_result
        """
        Whether the given source nodes must be in the result of the clustering.
        """
        self.max_cluster_size: int = max_cluster_size
        """
        The upper limit of the size of the calculated cluster.
        """

        self.cluster_definition: ClusterDefinition = None
        """
        The cluster definition the cluster engine is using to build a cluster.
        """
        if cluster_definition is not None:
            self.cluster_definition = cluster_definition
        else:
            self.cluster_definition = ConnectivityClusterDefinition()

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
        cluster = self.create_cluster(source_nodes)
        step_history = self.create_step_history(source_nodes)
        return self.execute_on(cluster, step_history)

    def create_cluster(self, source_nodes: List[Node]) -> Cluster:
        """
        Convenience method for creating a `Cluster` object that will contain the given nodes.

        Note that this method doesn't execute the cluster engine and as a consequence the value of the
        `last_cluster` and `last_step_history` properties will not be updated.

        Args:
            source_nodes (List[Node]): The list of source nodes to add to the cluster.
                                            This list must contain at least one node.

        Returns:
            A `Cluster` object containing the given list of nodes.
        """
        cluster = Cluster()

        if source_nodes is not None and len(source_nodes) > 0:
            if self.source_nodes_in_result:
                cluster.add_source_nodes(source_nodes)
            else:
                cluster.add_nodes(source_nodes)

        return cluster

    def create_step_history(self, source_nodes: List[Node]) -> StepHistory:
        """
        Convenience method for creating a `StepHistory` object initialized with the given list of source nodes.

        Note that this method doesn't execute the cluster engine and as a consequence the value of the
        `last_cluster` and `last_step_history` properties will not be updated.

        Args:
            source_nodes (List[Node]): The list of source nodes the `StepHistory` object should be
                                            initialized with.

        Returns:
            A `StepHistory` object initialized with the given list of source nodes.
        """
        return StepHistory(source_nodes, self.source_nodes_in_result)

    def execute_on(self, cluster: Cluster, step_history: StepHistory = None) -> Optional[Cluster]:
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
            self._step_history = StepHistory(list(cluster.source_nodes), self.source_nodes_in_result)

        if len(cluster) == 0:
            return cluster

        while True:
            step_descriptor = self._step_history.step()

            self._expand_cluster(step_descriptor)
            self._reduce_cluster(step_descriptor)

            if self.max_cluster_size <= len(self._cluster) or self._step_history.find_loop():
                # TODO: Could we do some polishing on the created cluster here?
                break

        return self._cluster

    def get_rank_provider(self) -> StepHistoryRankProvider:
        """
        Returns a `StepHistoryRankProvider` that can be used to rank the nodes that are in or around the cluster
        that was calculated by the `cluster()` method of the cluster engine.

        Returns:
            A `StepHistoryRankProvider` that can be used to rank the nodes that are in or around the cluster.
        """
        return StepHistoryRankProvider(self._step_history)

    # Protected methods
    # ------------------------------------------------------------

    def _expand_cluster(self, step_descriptor: StepDescriptor):
        """
        Executes one expansion step on the cluster.

        Args:
            step_descriptor (StepDescriptor): The step descriptor where this method should record the changes
                                              it made to the cluster.
        """
        nodes: List[Node] = self._cluster.neighborhood
        result: List[GainDescriptor] =\
            [self.cluster_definition.gain_of_inclusion(node, self._cluster) for node in nodes]
        step_descriptor.record_expansion_result(result)
        self._cluster.add_nodes(step_descriptor.added_nodes)

    def _reduce_cluster(self, step_descriptor):
        """
        Executes one reduction step on the cluster.

        Args:
            step_descriptor (StepDescriptor): The step descriptor where this method should record the changes
                                              it made to the cluster.
        """
        # Instead of nodes we could use non_source_nodes. I'm not sure it's worth it though,
        # since usually there is only 1 source node and maybe we'll be interested in the gain
        # descriptors that were calculated for the source nodes as well.
        nodes: List[Node] = self._cluster.nodes
        result: List[GainDescriptor] =\
            [self.cluster_definition.gain_of_exclusion(node, self._cluster) for node in nodes]
        step_descriptor.record_reduction_result(result)
        self._cluster.remove_nodes(step_descriptor.removed_nodes)


class MultiStepLocalClusterEngine(LocalClusterEngine):
    """
    A `LocalClusterEngine` variant that executes a configurable number of cluster expansion and cluster reduction
    steps in a single step of the algorithm. First the given number of expansion steps, then the given number of
    reduction steps will be executed.

    The number of steps taken in one iteration of the algorithm can be configured by setting the
    `expansion_step_count` and `reduction_step_count` properties of the cluster engine.
    """

    # Initialization
    # ------------------------------------------------------------

    def __init__(self,
                 cluster_definition: ClusterDefinition = None,
                 source_nodes_in_result: bool = True,
                 max_cluster_size: int = 100,
                 expansion_step_count: int = 1,
                 reduction_step_count: int = 1):
        """
        Initialization.

        Args:
            cluster_definition (ClusterDefinition): The cluster definition the cluster engine should use.
                                                    If `None`, then a default cluster definition will be used.
            source_nodes_in_result (bool): Whether the given source nodes must be in the result of the clustering.
            max_cluster_size (int): The upper limit of the size of the calculated cluster.
            expansion_step_count (int): The maximum number of cluster expansion steps to execute in a single step
                                        of the algorithm. If no node is added to the cluster at an expansion step,
                                        then the algorithm will move on to the reduction phase.
            reduction_step_count (int): The maximum number of cluster reduction steps to execute in a single step
                                        of the algorithm. If no node is removed from the cluster at a reduction step,
                                        then the algorithm will move on to its next phase.
        """
        LocalClusterEngine.__init__(self,
                                    cluster_definition,
                                    source_nodes_in_result,
                                    max_cluster_size)
        self.expansion_step_count: int = expansion_step_count
        """The maximum number of cluster expansion steps to execute in a single step of the algorithm."""
        self.reduction_step_count: int = reduction_step_count
        """The maximum number of cluster reduction steps to execute in a single step of the algorithm."""

    def execute_on(self, cluster: Cluster, step_history: StepHistory = None) -> Optional[Cluster]:
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
            self._step_history = StepHistory(list(cluster.source_nodes), self.source_nodes_in_result)

        if len(cluster) == 0:
            return cluster

        while True:
            step_descriptor = self._step_history.step()

            # Execute the desired number of expansion steps
            for _ in range(self.expansion_step_count):
                self._expand_cluster(step_descriptor)
                if step_descriptor.number_of_added_nodes == 0:
                    break

            for _ in range(self.reduction_step_count):
                self._reduce_cluster(step_descriptor)
                if step_descriptor.number_of_removed_nodes == 0:
                    break

            if self._step_history.find_loop() or self.max_cluster_size <= len(self._cluster):
                # TODO: Could we do some polishing on the created cluster here?
                break

        return self._cluster
