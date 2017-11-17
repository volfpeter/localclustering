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

    # Initialization
    # ------------------------------------------------------------

    def __init__(self, node: Node, result: bool) -> None:
        """
        Initialization.

        Arguments:
            node (Node): The node for which this descriptor was calculated.
            result (bool): Whether the inclusion or exclusion of the given node would increase cluster quality.
        """
        self.node: Node = node
        """
        The node the gain descriptor was created for.
        """
        self.result: bool = result
        """
        Whether the inclusion or exclusion of the given node would increase cluster quality.
        """

    def get_rank(self) -> float:
        """
        Returns the rank of the node corresponding to this gain descriptor if the gain descriptor is able
        to calculate a rank for the node.
        """
        # The default implementation doesn't support rank calculation.
        return 0
