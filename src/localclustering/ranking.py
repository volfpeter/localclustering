"""
This module contains the interface to be implemented by classes that are able to return the rank or score of a node,
generic implementations of this interface and related utility classes and methods.
"""

# Imports
# ------------------------------------------------------------

from typing import Iterable, List, Optional

from operator import attrgetter

from graphscraper.base import Node

from localclustering.history import StepHistory

# Module constants
# ------------------------------------------------------------

__author__ = "Peter Volf"

# Classes
# ------------------------------------------------------------


class BaseRankProvider(object):
    """Base class that defines the interface that all node rank providers must implement."""

    # Public methods
    # ------------------------------------------------------------

    def get_rank_for_nodes(self, nodes: Iterable[Node]) -> Optional[List[float]]:
        """
        Returns the list of ranks/scores for the given nodes. The ith item in the returned list of ranks
        corresponds to the ith node in the received list of nodes.

        Arguments:
            nodes (Iterable[Node]): The list of nodes to rank.

        Returns:
             The list of ranks/scores for the given nodes or `None` if `nodes` is `None`.
        """
        return [self.get_node_rank(node) for node in nodes]

    def get_node_rank(self, node: Node) -> float:
        """
        Returns the rank/score of the given node.

        Arguments:
            node (Node): The node to rank.

        Returns:
            The rank of the given node as a floating point number or a negative number if the rank provider cannot
            determine the rank of the node.
        """
        raise NotImplementedError("BaseRankProvider is abstract, child classes must override its methods.")

    def sort_nodes_by_rank(self, nodes: Optional[List[Node]], reverse: bool=True) -> Optional[List[Node]]:
        """
        Sorts the given nodes by their rank. If multiple nodes have the same rank, then they will be
        sorted by their name, in ascending order.

        Arguments:
            nodes (Optional[List[Node]]): The list of nodes to sort.
            reverse (bool): If `True`, then the nodes will be ordered in descending order, otherwise
                            in ascending order.

        Returns:
            The list of nodes sorted by their rank.
        """
        if nodes is None or len(nodes) == 0:
            return nodes

        # TODO:
        # Sorting the nodes by their name first. This only matters if multiple nodes have the same rank, and
        # we could do it much smarter (with a custom compare function or by only reordering the nodes with equal
        # rank after they'be been ordered by rank), but it's ok for now.
        nodes = sorted(nodes, key=attrgetter("name"))
        nodes.sort(key=self.get_node_rank, reverse=reverse)
        return nodes


class StepHistoryRankProvider(BaseRankProvider):
    """`BaseRankProvider` implementation that calculates a node's rank using a `StepHistory` object."""

    # Initialization
    # ------------------------------------------------------------

    def __init__(self, step_history: StepHistory) -> None:
        """
        Initialization.

        Arguments:
            step_history (StepHistory): The `StepHistory` object the rank provider
                                        is using to determine the rank of nodes.
        """
        self._step_history = step_history

    # Public methods
    # ------------------------------------------------------------

    def get_node_rank(self, node: Node) -> float:
        """
        Returns the rank/score of the given node.

        Arguments:
            node (Node): The node to rank.

        Returns:
            The rank of the given node as a floating point number or a negative number if the rank provider cannot
            determine the rank of the node.
        """
        if self._step_history is None or node is None:
            return -3

        step_descriptor = self._step_history.last_step
        if step_descriptor is None:
            return -2

        gain_descriptor = step_descriptor.get_gain_descriptor_for_node(node)
        return gain_descriptor.get_rank() if gain_descriptor is not None else -1
