"""
Cluster definition related utility classes.
"""

# Imports
# ------------------------------------------------------------

from graphscraper.base import Node

# Module constants
# ------------------------------------------------------------

__author__ = 'Peter Volf'

# Classes
# ------------------------------------------------------------


class GainDescriptor(object):
    """Helper class that stores the result of `ClusterDefinition` method calls."""

    __slots__ = ("node", "result", "weighting_coefficient", "coefficient_multiplier")

    # Initialization
    # ------------------------------------------------------------

    def __init__(self, node: Node, result: bool, weighting_coefficient: float, coefficient_multiplier: float = 0):
        """
        Initialization.

        Args:
            node (Node): The node for which this descriptor was calculated.
            result (bool): Whether the inclusion or exclusion of the given node would increase cluster quality.
            weighting_coefficient (float): The edge weighting coefficient in effect when this gain descriptor
                                           was calculated.
            coefficient_multiplier (float): Multiplier for the edge weighting coefficient that should be applied to
                                            make the cluster definition include the given node in the cluster.
        """
        self.node: Node = node
        """
        The node the gain descriptor was created for.
        """
        self.result: bool = result
        """
        Whether the inclusion or exclusion of the given node would increase cluster quality.
        """
        self.weighting_coefficient: float = weighting_coefficient
        """
        The edge weighting coefficient in effect when this gain descriptor was calculated.
        """
        self.coefficient_multiplier: float = coefficient_multiplier
        """
        Multiplier for the edge weighting coefficient that should be applied to
        make the cluster definition include the given node in the cluster.
        """
