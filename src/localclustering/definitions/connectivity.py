"""
Connectivity based `ClusterDefinition` implementations, utility classes and methods.
"""

# Imports
# ------------------------------------------------------------

from typing import List, Optional

from graphscraper.base import Node

from localclustering.cluster import Cluster
from localclustering.definitions.base import HierarchicalClusterDefinition
from localclustering.definitions.util import GainDescriptor

# Module constants
# ------------------------------------------------------------

__author__ = 'Peter Volf'

# Classes
# ------------------------------------------------------------


class ConnectivityGainDescriptor(GainDescriptor):
    """
    Specialized `GainDescriptor` for `ConnectivityClusterDefinition`.
    """

    # Initialization
    # ------------------------------------------------------------

    def __init__(self,
                 node: Node,
                 result: bool,
                 weighting_coefficient: float,
                 coefficient_multiplier: float = 0) -> None:
        """
        Initialization.

        Arguments:
            node (Node): The node for which this descriptor was calculated.
            result (bool): Whether the inclusion or exclusion of the given node would increase cluster quality.
            weighting_coefficient (float): The edge weighting coefficient in effect when this gain descriptor
                                           was calculated.
            coefficient_multiplier (float): Multiplier for the edge weighting coefficient that should be applied to
                                            make the cluster definition include the given node in the cluster.
        """
        super(ConnectivityGainDescriptor, self).__init__(node, result)

        self.weighting_coefficient: float = weighting_coefficient
        """
        The edge weighting coefficient in effect when this gain descriptor was calculated.
        """
        self.coefficient_multiplier: float = coefficient_multiplier
        """
        Multiplier for the edge weighting coefficient that should be applied to
        make the cluster definition include the given node in the cluster.
        """

    def get_rank(self) -> float:
        """
        Returns the rank of the node corresponding to this gain descriptor if the gain descriptor is able
        to calculate a rank for the node.
        """
        if self.coefficient_multiplier == 0:
            return 0

        return self.weighting_coefficient / self.coefficient_multiplier


class ConnectivityClusterDefinition(HierarchicalClusterDefinition):
    """
    A simple, connectivity based `HierarchicalClusterDefinition` implementation.
    """

    # Initialization
    # ------------------------------------------------------------

    def __init__(self, weighting_coefficient: float=2, threshold_modifier: float=0.85):
        """
        Initialization.

        Arguments:
            weighting_coefficient (float): The edge weighting the cluster definition will use.
                                           This value must be a positive floating point number.
            threshold_modifier (float): The threshold calculated by the cluster definition will be multiplied with
                                        this value to create the threshold the definition will use to make decisions.
                                        This value must be a positive floating point number.
        """
        assert weighting_coefficient > 0
        assert threshold_modifier > 0

        self.weighting_coefficient: float = weighting_coefficient
        """
        The edge weighting the cluster definition will use.
        """
        self.threshold_modifier: float = threshold_modifier
        """
        The threshold calculated by the cluster definition will be multiplied with
        this value to create the threshold the definition will use to make decisions.
        """

    # Public methods
    # ------------------------------------------------------------

    def adjust_definition_for_next_hierarchy_level(self, gain_descriptors: List[ConnectivityGainDescriptor]) -> bool:
        """
        Adjusts the cluster cluster definition for the next cluster hierarchy level based on the received list
        of gain descriptors.

        Arguments:
            gain_descriptors(Iterable[ConnectivityGainDescriptor]): The list of gain descriptors created during the
                                                                    latest step of the hierarchical clustering.

        Returns:
            Whether the cluster definition was successfully adjusted for the next cluster hierarchy level.
        """
        if gain_descriptors is None or len(gain_descriptors) == 0:
            return False

        # TODO: implement a smarter solution for finding the next hierarchy level based on the gain descriptors.
        coefficient_multiplier = None
        for descriptor in gain_descriptors:
            if descriptor.coefficient_multiplier > 1:
                if coefficient_multiplier is None or descriptor.coefficient_multiplier < coefficient_multiplier:
                    coefficient_multiplier = descriptor.coefficient_multiplier

        if coefficient_multiplier is None:
            return False

        coefficient_multiplier = max(coefficient_multiplier, 1.05)
        self.weighting_coefficient *= coefficient_multiplier
        return True

    def clone(self, base: Optional["ConnectivityClusterDefinition"] = None):
        """
        Clones the cluster definition.

        Arguments:
            base (Optional[ClusterDefinition]): An optional base object to use as the clone. If `None`, then a new
                                                object will be created and returned.

        Returns:
            The clone of the cluster definition instance. If `base` is not `None`, then `base` will be returned.
        """
        if base is None:
            base = ConnectivityClusterDefinition()
        elif not isinstance(base, ConnectivityClusterDefinition):
            raise TypeError("The type of the given base object is incorrect.")

        base.threshold_modifier = self.threshold_modifier
        base.weighting_coefficient = self.weighting_coefficient

        return base

    def gain_of_inclusion(self, node: Node, cluster: Cluster) -> GainDescriptor:
        """
        Calculates the gain of the inclusion of the given node in the cluster.

        Arguments:
            node (Node): The node to calculate the gain of the inclusion for.
            cluster (Cluster): The cluster for which the gain of the inclusion should be calculated for.

        Returns:
            A `GainDescriptor` that describes whether - or under what conditions - the inclusion of the given node
            would improve cluster quality.
        """
        quality_difference = 0
        for neighbor in node.neighbors:
            if neighbor in cluster:
                quality_difference += self.weighting_coefficient

        if quality_difference > 0:
            cluster_size = len(cluster)
            cluster_degree = cluster.degree
            node_degree = node.degree
            # The threshold is defined based on the following measures:
            #   - As many connections to the cluster as half the number of nodes in the cluster
            #   - Half the neighbors of the node is in the cluster
            #   - As many connections to the cluster as the cluster's average degree
            # NOTE: we intentionally DO NOT divide the values in threshold by 2, because the weighting coefficient
            #       is considered as 2 times the weight of an edge.
            threshold = self.threshold_modifier * min(
                max(cluster_size - 2, 0),
                node_degree,
                cluster_degree / cluster_size
            )
            return ConnectivityGainDescriptor(
                node,
                quality_difference >= threshold,
                self.weighting_coefficient,
                threshold / quality_difference
            )
        else:
            return ConnectivityGainDescriptor(node, False, self.weighting_coefficient, 0)

    def gain_of_exclusion(self, node: Node, cluster: Cluster) -> GainDescriptor:
        """
        Calculates the gain of the exclusion of the given node from the cluster.

        Arguments:
            node (Node): The node to calculate the gain of the exclusion for.
            cluster (Cluster): The cluster for which the gain of the exclusion should be calculated for.

        Returns:
            A `GainDescriptor` that contains whether the exclusion of the given from the cluster would improve
            cluster quality.
        """
        quality_difference = 0
        for neighbor in node.neighbors:
            if neighbor in cluster:
                quality_difference += self.weighting_coefficient

        if quality_difference > 0:
            cluster_size = len(cluster)
            cluster_degree = cluster.degree
            node_degree = node.degree
            # The threshold is defined based on the following measures:
            #   - As many connections to the cluster as half the number of nodes in the cluster (except 1 source)
            #   - Half the neighbors of the node is in the cluster
            #   - As many connections to the cluster as the cluster's average degree
            # NOTE: we intentionally DO NOT divide the values in threshold by 2, because the weighting coefficient
            #       is considered as 2 times the weight of an edge.
            threshold = self.threshold_modifier * min(
                max(cluster_size - 2, 0),
                node_degree,
                cluster_degree / cluster_size
            )
            return ConnectivityGainDescriptor(
                node,
                quality_difference < threshold,
                self.weighting_coefficient,
                threshold / quality_difference
            )
        else:
            return ConnectivityGainDescriptor(node, True, self.weighting_coefficient, 0)
