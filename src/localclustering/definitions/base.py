"""
Cluster definition interface specifications.
"""

# Imports
# ------------------------------------------------------------

from typing import List, Optional

from localclustering.cluster import Cluster
from localclustering.definitions.util import GainDescriptor
from graphscraper.base import Node

# Module constants
# ------------------------------------------------------------

__author__ = 'Peter Volf'

# Classes
# ------------------------------------------------------------


class ClusterDefinition(object):
    """Abstract base class that defines the interface that all cluster definitions must implement."""

    # Public methods
    # ------------------------------------------------------------

    def clone(self, base: Optional["ClusterDefinition"] = None) -> "ClusterDefinition":
        """
        Clones the cluster definition.

        Arguments:
            base (Optional[ClusterDefinition]): An optional base object to use as the clone. If `None`, then a new
                                                object will be created and returned.

        Returns:
            The clone of the cluster definition instance. If `base` is not `None`, then `base` will be returned.
        """
        raise NotImplementedError("ClusterDefinition is abstract, child classes must override its methods.")

    def gain_of_inclusion(self, node: Node, cluster: Cluster) -> GainDescriptor:
        """
        Calculates the gain of the inclusion of the given node in the cluster.

        Args:
            node (Node): The node to calculate the gain of the inclusion for.
            cluster (Cluster): The cluster for which the gain of the inclusion should be calculated for.

        Returns:
            A `GainDescriptor` that describes whether - or under what conditions - the inclusion of the given node
            would improve cluster quality.
        """
        raise NotImplementedError("ClusterDefinition is abstract, child classes must override its methods.")

    def gain_of_exclusion(self, node: Node, cluster: Cluster) -> GainDescriptor:
        """
        Calculates the gain of the exclusion of the given node from the cluster.

        Args:
            node (Node): The node to calculate the gain of the exclusion for.
            cluster (Cluster): The cluster for which the gain of the exclusion should be calculated for.

        Returns:
            A `GainDescriptor` that contains whether the exclusion of the given from the cluster would improve
            cluster quality.
        """
        raise NotImplementedError("ClusterDefinition is abstract, child classes must override its methods.")


class HierarchicalClusterDefinition(ClusterDefinition):
    """
    Abstract base class that defines the interface to be implemented by cluster definitions that can be used to
    create a hierarchy of clusters.
    """

    def adjust_definition_for_next_hierarchy_level(self, gain_descriptors: List[GainDescriptor]) -> bool:
        """
        Adjusts the cluster cluster definition for the next cluster hierarchy level based on the received list
        of gain descriptors.

        Args:
            gain_descriptors(List[GainDescriptor]): The list of gain descriptors created during the latest
                                                        step of the hierarchical clustering.

        Returns:
            Whether the cluster definition was successfully adjusted for the next cluster hierarchy level.
        """
        raise NotImplementedError("HierarchicalClusterDefinition is abstract, child must override its methods.")
