"""
This module contains the utility classes cluster engines use to record the steps they have taken.
"""

# Imports
# ------------------------------------------------------------

from typing import Dict, Iterable, List, Optional

from operator import attrgetter

from graphscraper.base import Node

from localclustering.definitions.util import GainDescriptor

# Module constants
# ------------------------------------------------------------

__author__ = "Peter Volf"

# Classes
# ------------------------------------------------------------


class StepDescriptor(object):
    """
    Class that describes the changes that were made to the cluster during one execution step of the cluster engine.
    """

    # Initialization
    # ------------------------------------------------------------

    def __init__(self) -> None:
        """
        Initialization.
        """
        self._added_nodes: Dict[int, GainDescriptor] = {}
        self._not_added_nodes: Dict[int, GainDescriptor] = {}
        self._removed_nodes: Dict[int, GainDescriptor] = {}
        self._not_removed_nodes: Dict[int, GainDescriptor] = {}

    # Special methods
    # ------------------------------------------------------------

    def __str__(self) -> str:
        """
        The string representation of the object.
        """
        result: List[str] =\
            ["Added: {}".format(descriptor.node.name.encode("utf8"))
             for descriptor in sorted(self._added_nodes.values(), key=attrgetter("node.name"))]
        result.extend(
            ["Not added: {}".format(descriptor.node.name.encode("utf8"))
             for descriptor in sorted(self._not_added_nodes.values(), key=attrgetter("node.name"))])
        result.extend(
            ["Removed: {}".format(descriptor.node.name.encode("utf8"))
             for descriptor in sorted(self._removed_nodes.values(), key=attrgetter("node.name"))])
        result.extend(
            ["Not removed: {}".format(descriptor.node.name.encode("utf8"))
             for descriptor in sorted(self._not_removed_nodes.values(), key=attrgetter("node.name"))])
        return "\n".join(result)

    # Public properties
    # ------------------------------------------------------------

    @property
    def added_gain_descriptors(self) -> Iterable[GainDescriptor]:
        """
        The gain descriptors corresponding to the nodes that were added to the cluster in this step.
        """
        return self._added_nodes.values()

    @property
    def added_nodes(self) -> List[Node]:
        """
        The nodes that were added to the cluster at this step.
        """
        return [descriptor.node for descriptor in self._added_nodes.values()]

    @property
    def is_deadlock(self) -> bool:
        """
        Whether the steps recorded in this descriptor create a deadlock.
        """
        # We take the liberty of ignoring the nodes that were neither added nor removed in this step.
        # In some very special cases this could lead to invalid results, but we'll take that risk.
        if self.number_of_added_nodes != self.number_of_removed_nodes:
            return False

        for key in self._added_nodes:
            if self._removed_nodes.get(key) is None:
                return False

        # True will be returned if no nodes were added or removed, which is fine.
        return True

    @property
    def not_added_gain_descriptors(self) -> Iterable[GainDescriptor]:
        """
        Returns the gain descriptors corresponding to the nodes that were not added to the cluster in this step.
        """
        return self._not_added_nodes.values()

    @property
    def not_removed_gain_descriptors(self) -> Iterable[GainDescriptor]:
        """
        The gain descriptors corresponding to the nodes that were not removed from the cluster in this step.
        """
        return self._not_removed_nodes.values()

    @property
    def number_of_added_nodes(self) -> int:
        """
        The number of nodes that were added to the cluster at this step.
        """
        return len(self._added_nodes)

    @property
    def number_of_removed_nodes(self) -> int:
        """
        The number of nodes that were removed from the cluster at this step.
        """
        return len(self._removed_nodes)

    @property
    def removed_gain_descriptors(self) -> Iterable[GainDescriptor]:
        """
        The gain descriptors corresponding to the nodes that were removed from the cluster in this step.
        """
        return self._removed_nodes.values()

    @property
    def removed_nodes(self) -> List[Node]:
        """
        The nodes that were removed from the cluster at this step.
        """
        return [descriptor.node for descriptor in self._removed_nodes.values()]

    # Public methods
    # ------------------------------------------------------------

    def get_gain_descriptor_for_node(self, node: Node) -> Optional[GainDescriptor]:
        """
        Returns the `GainDescriptor` that corresponds to the given node or `None` if no such descriptor is found.

        Args:
            node (Node): The node the gain descriptor is required for.

        Returns:
            The `GainDescriptor` corresponding to the given node or `None` if no such descriptor is found.
        """
        if node is None:
            return None

        descriptor = self._not_removed_nodes.get(node.index)
        if descriptor is not None:
            return descriptor

        descriptor = self._not_added_nodes.get(node.index)
        if descriptor is not None:
            return descriptor

        descriptor = self._added_nodes.get(node.index)
        if descriptor is not None:
            return descriptor

        descriptor = self._removed_nodes.get(node.index)
        if descriptor is not None:
            return descriptor

        return None

    def is_equivalent_to(self, other: "StepDescriptor") -> bool:
        """
        Returns whether the content of this step descriptor is equivalent to the content of `other`.

        Args:
            other (StepDescriptor): The step descriptor this one should be compared to.

        Returns:
            `True` if this step descriptor is equivalent to `other`, `False` otherwise.
        """
        if other is None or\
           self.number_of_added_nodes != other.number_of_added_nodes or \
           self.number_of_removed_nodes != other.number_of_removed_nodes or\
           len(self._not_added_nodes) != len(other._not_added_nodes) or\
           len(self._not_removed_nodes) != len(other._not_removed_nodes):
            return False

        for key in self._added_nodes:
            if other._added_nodes.get(key) is None:
                return False

        for key in self._removed_nodes:
            if other._removed_nodes.get(key) is None:
                return False

        # Don't compare the not added or not removed nodes one-by-one.

        return True

    def record_expansion_result(self, gain_descriptors: List[GainDescriptor]) -> None:
        """
        Records the results - `GainDescriptor`s - the cluster definition calculated during the current
        cluster expansion step of the local cluster engine.

        Args:
            gain_descriptors (List[GainDescriptor]): The gain descriptors the cluster definition calculated.
        """
        for descriptor in gain_descriptors:
            if descriptor.result:
                self._added_nodes[descriptor.node.index] = descriptor
            else:
                self._not_added_nodes[descriptor.node.index] = descriptor

    def record_reduction_result(self, gain_descriptors: List[GainDescriptor]) -> None:
        """
        Records the results - `GainDescriptor`s - the cluster definition calculated during the current
        cluster reduction step of the local cluster engine.

        Args:
            gain_descriptors (list[GainDescriptor]): The gain descriptors the cluster definition calculated.
        """
        for descriptor in gain_descriptors:
            if descriptor.result:
                self._removed_nodes[descriptor.node.index] = descriptor
            else:
                self._not_removed_nodes[descriptor.node.index] = descriptor


class StepHistory(object):
    """
    Class that keeps the history of all the steps that were made by the cluster engine.
    """

    # Initialization
    # ------------------------------------------------------------

    def __init__(self, source_nodes: List[Node], source_nodes_in_result: bool):
        """
        Initialization.

        Args:
            source_nodes (Node): The list of source nodes the cluster engine was initialized with.
            source_nodes_in_result (bool): Whether the given source nodes must be in the result of the clustering.
        """
        self._history: List[StepDescriptor] = []
        """The recorded step history."""
        self._source_nodes: List[Node] = source_nodes
        """The list of source nodes the cluster engine was initialized with."""
        self._source_nodes_in_result: bool = source_nodes_in_result
        """Whether the source nodes must be in the result of the clustering."""

    # Special methods
    # ------------------------------------------------------------

    def __getitem__(self, index: int) -> StepDescriptor:
        """
        Returns the item at the given index in the step history.
        """
        return self._history[index]

    def __len__(self) -> int:
        """
        The number of items in the step history.
        """
        return len(self._history)

    def __repr__(self) -> str:
        """
        The string representation of the step history object.
        """
        return "StepHistory([source_nodes = {0}], source_nodes_in_result = {1}), {2} steps".format(
            "; ".join(node.name for node in self._source_nodes),
            self._source_nodes_in_result,
            len(self)
        )

    def __str__(self) -> str:
        """
        The string representation of the recorded step history.
        """
        result: List[str] = []
        for i, step_descriptor in enumerate(self._history):
            result.extend(["STEP {}".format(i), str(step_descriptor)])
        return "\n".join(result)

    # Properties
    # ------------------------------------------------------------

    @property
    def last_step(self) -> StepDescriptor:
        """
        The last step descriptor from the history.
        """
        return self._history[-1]

    @property
    def source_nodes(self) -> List[Node]:
        """
        The list of source nodes the cluster engine - and hence the this step history object -
        was initialized with.
        """
        return self._source_nodes

    @property
    def source_nodes_in_result(self) -> bool:
        """
        Whether the given source nodes must be in the result of the clustering.
        """
        return self._source_nodes_in_result

    # Public methods
    # ------------------------------------------------------------

    def find_loop(self, max_sequence_length: int=2) -> Optional[List[StepDescriptor]]:
        """
        Checks if there is a "loop" - i.e. a repeated step descriptor sequence - in the history and returns the
        list of `StepDescriptor` utility that are part of this sequence or `None` if there is no loop.

        Note that even a single `StepDescriptor` can create a loop if the nodes that were added and removed
        are the same. Also note that this method depends on the deterministic nature of the cluster engine, which
        means it detects loops by checking whether a step descriptor equivalent to the last one can be found in
        the step history. If there is such a descriptor and the algorithm is deterministic, then equivalent
        step descriptors should follow these, and so on, so there is a loop.

        Args:
            max_sequence_length (int): The maximum number of items to check before the last one.

        Return:
            A list of ``StepDescriptor`` utility that form the found loop or ``None`` if there is no loop.
        """
        if len(self._history) == 0:
            return None

        last_descriptor: StepDescriptor = self._history[-1]
        if last_descriptor.is_deadlock:
            return [last_descriptor]

        length: int = len(self)
        for index in range(max(length - 1 - max_sequence_length, 0), length - 1):
            descriptor: StepDescriptor = self._history[index]
            if last_descriptor.is_equivalent_to(descriptor):
                return self._history[index:]

        return None

    def step(self) -> StepDescriptor:
        """
        Adds a new step descriptor to the history and returns it.

        Returns:
            The `StepDescriptor` that was added to the history.
        """
        step_descriptor: StepDescriptor = StepDescriptor()
        self._history.append(step_descriptor)
        return step_descriptor
