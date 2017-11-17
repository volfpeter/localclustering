"""
This module contains cluster implementations and closely related utility classes and methods.
"""

# Imports
# ------------------------------------------------------------

from typing import Dict, Iterable, List

from localclustering.ranking import BaseRankProvider
from graphscraper.base import NeighborAddedEvent, Node

# Module constants
# ------------------------------------------------------------

__author__ = 'Peter Volf'

# Classes
# ------------------------------------------------------------


class Cluster(object):
    """
    An editable cluster implementation.

    The cluster differentiates (and stores references to) three different types of nodes:
        * Source nodes: These are sort of protected nodes that build up the core or source of the
                        cluster. Such nodes can be added to the cluster by the `add_source_node()`
                        and `add_source_nodes()` methods and the `remove_node()` and
                        `remove_nodes()` methods will not have an effect on them, only
                        `remove_source_node()` and `remove_source_nodes()` will. You can list the
                         source nodes of the cluster through the `source_nodes` property.
        * Nodes: All the nodes in the cluster including the source nodes. You can access the
                 nodes in the cluster through the `nodes` property.
        * Neighbors: Nodes that are not in the cluster but at least one edge connects them with
                     the cluster.
    """

    # Initialization
    # ------------------------------------------------------------

    def __init__(self) -> None:
        """
        Initialization.
        """
        self._source_nodes: Dict[int, Node] = {}
        """The source nodes of the cluster."""
        self._nodes: Dict[int, Node] = {}
        """All the nodes that are within the cluster."""
        self._neighbors: Dict[int, Node] = {}
        """The neighbors of the cluster."""
        self.degree: int = 0
        """The sum of the degrees of the nodes in the cluster."""

    # Special methods
    # ------------------------------------------------------------

    def __contains__(self, node: Node) -> bool:
        """
        Returns whether the cluster contains the given node. By implementing this method,
        we let the users use the `in` operator on the instances of this class.

        Arguments:
            node (Node): The node to check.

        Returns:
            bool: Whether the given node is included in the cluster.
        """
        if node is None:
            return False

        other_node: Node = self._nodes.get(node.index)
        if other_node:
            if other_node == node:
                return True
            else:
                raise ValueError("A different node with the same key ({0.index}) is already "
                                 "contained by the cluster! {0.name} - {1.name}".format(other_node,
                                                                                        node))

        return False

    def __len__(self) -> len:
        """
        The number of nodes in the cluster.
        """
        return len(self._nodes)

    # Public properties
    # ------------------------------------------------------------

    @property
    def neighborhood(self) -> Iterable[Node]:
        """
        The neighbors of the cluster.
        """
        return self._neighbors.values()

    @property
    def number_of_neighbors(self) -> int:
        """
        The number of neighbors of the cluster.
        """
        return len(self._neighbors)

    @property
    def number_of_source_nodes(self) -> int:
        """
        The number of source nodes in the cluster.
        """
        return len(self._source_nodes)

    @property
    def number_of_nodes(self) -> int:
        """
        The number of nodes in the cluster.

        This is just an alias for `len(cluster)`.
        """
        return len(self)

    @property
    def source_nodes(self) -> Iterable[Node]:
        """
        The source nodes of the cluster.
        """
        return self._source_nodes.values()

    @property
    def nodes(self) -> Iterable[Node]:
        """
        All the nodes in the cluster.
        """
        return self._nodes.values()

    # Public methods
    # ------------------------------------------------------------

    def add_source_node(self, node: Node) -> None:
        """
        Adds the given node to the cluster and marks it as one of the source nodes.

        Arguments:
            node (Node): The source node to be added to the cluster.
        """
        if node is None:
            raise ValueError("The received node was None.")

        other_source: Node = self._source_nodes.get(node.index)
        if other_source:
            if other_source == node:
                # The node is already a source node of the cluster, nothing to do.
                return
            else:
                raise ValueError("A different node with the same key ({0.index}) is already among "
                                 " the source nodes! {0.name} - {1.name}".format(other_source,
                                                                                 node))

        # Add the node to the cluster if needed.
        if node not in self:
            self.add_node(node)

        self._source_nodes[node.index] = node

    def add_node(self, node: Node) -> None:
        """
        Adds the given node to the cluster.

        Arguments:
            node (Node): The node to be added to the cluster.
        """
        if node is None:
            raise ValueError("The received node was None.")

        other_node: node = self._nodes.get(node.index)
        if other_node:
            if other_node == node:
                # The node is already in the cluster, nothing to do.
                return
            else:
                raise ValueError("A different node with the same key ({0.index}) is already in the "
                                 "cluster! {0.name} - {1.name}".format(other_node, node))

        # Add the node to the cluster.
        self._nodes[node.index] = node

        # Add the neighbor added event handler to the node.
        node.add_event_listener(NeighborAddedEvent.NEIGHBOR_ADDED, self._node_neighbor_added_handler)

        # Update the degree of the cluster.
        self.degree += node.degree

        # Update the neighbors of the cluster.
        for neighbor in node.neighbors:
            self._add_neighbor_candidate(neighbor)

        # The node was probably in the neighborhood, we have to remove it.
        other_node = self._neighbors.get(node.index)
        if other_node:
            if other_node == node:
                del self._neighbors[node.index]
            else:
                raise ValueError("A different node with the same key ({0.index}) was in the "
                                 "neighborhood! {0.name} - {1.name}".format(other_node, node))

    def add_nodes(self, nodes: List[Node]) -> None:
        """
        Adds all nodes in the given list to the cluster.

        Arguments:
            nodes (List[Node]): The list of nodes to add to the cluster.
        """
        for node in nodes:
            self.add_node(node)

    def add_source_nodes(self, nodes: List[Node]) -> None:
        """
        Adds all nodes in the given list to the cluster as source nodes.

        Arguments:
            nodes (List[Node]): The list of source nodes to add to the cluster.
        """
        for node in nodes:
            self.add_source_node(node)

    def is_in_cluster(self, node: Node) -> bool:
        """
        Returns whether the given node is in the cluster.

        Arguments:
            node (Node): The node to check.

        Returns:
            bool: Whether the given node is in the cluster.
        """
        return node in self

    def is_neighbor(self, node: Node) -> bool:
        """
        Returns whether the given node is in the neighborhood of the cluster.

        Note that the result of this method is not accurate when the cluster is being modified.
        In this case the protected `_is_neighbor_of_cluster()` method should be used.

        Arguments:
            node (Node): The node to check.

        Returns:
            bool: Whether the node is in the neighborhood of the cluster.
        """
        if node is None:
            return False

        other_node: Node = self._neighbors.get(node.index)
        if other_node is None:
            return False

        if other_node != node:
            raise ValueError("A different node with the same key ({0.index}) is already in the "
                             "neighborhood! {0.name} - {1.name}".format(other_node, node))

        return True

    def is_source_node(self, node: Node) -> bool:
        """
        Returns whether the given node is one of the sources of the cluster.

        Arguments:
            node (Node): The node to check.

        Returns:
            bool: Whether the given node is a source of the cluster.
        """
        if node is None:
            return False

        other_node: Node = self._source_nodes.get(node.index)
        if other_node:
            if other_node == node:
                return True
            else:
                raise ValueError("A different node with the same key ({0.index}) is the source node"
                                 " of the cluster! {0.name} - {1.name}".format(other_node, node))

        return False

    def remove_source_node(self, node: Node) -> None:
        """
        Removes the given node from the cluster if it is a source node.

        Arguments:
            node (Node): The node to remove from the cluster.
        """
        if node not in self or not self.is_source_node(node):
            return

        # Remove the node from the sources.
        del self._source_nodes[node.index]
        self._remove_node_internal(node)

    def remove_source_nodes(self, nodes: List[Node]) -> None:
        """
        Removes all source nodes in the given list from the cluster.

        Arguments:
            nodes (List[Node]): The list of source nodes to remove from the cluster.
        """
        if nodes is None:
            return

        for node in nodes:
            self.remove_source_node(node)

    def remove_node(self, node: Node) -> None:
        """
        Removes the given node from the cluster if it is not a source node.

        Arguments:
            node (Node): The node to remove from the cluster.
        """
        if node not in self or self.is_source_node(node):
            return

        self._remove_node_internal(node)

    def remove_nodes(self, nodes: List[Node]) -> None:
        """
        Removes all non-source nodes in the given list from the cluster.

        Arguments:
            nodes (List[Node]): The list of nodes to remove from the cluster.
        """
        if nodes is None:
            return

        for node in nodes:
            self.remove_node(node)

    def to_json(self,
                max_distance_from_cluster: int = 0,
                rank_provider: BaseRankProvider = None,
                lazy: bool = True) -> Dict:
        """
        Returns the JSON representation of the subgraph corresponding to the cluster.

        Arguments:
            max_distance_from_cluster (int):
                The maximum distance of the included nodes from the cluster. 0 means only the
                nodes in the cluster will be included in the result, 1 means the immediate
                neighbors of the cluster will also be included and so on.
            rank_provider (BaseRankProvider):
                Rank provider that is able to provide a rank/score for the nodes that are included
                in the returned JSON object. If not `None`, then the rank of each node will be
                included as a property of the nodes.
            lazy (bool):
                If `True`, then the edges between the nodes farthest from the cluster will not
                be included in the returned JSON representation of the cluster.

        Returns:
            Dict: The JSON representation of the cluster.
        """
        node_id_map: Dict[Node, str] = {}
        result_nodes: List[Dict] = []
        result_edges: List[Dict] = []
        result: Dict = {
            "nodes": result_nodes,
            "edges": result_edges
        }

        for node in self.source_nodes:
            node_id: str = node_id_map.get(node)
            if node_id is None:
                node_id = node.name
                node_id_map[node] = node_id
                json_node: Dict = {
                    "id": node_id,
                    "label": node.name,
                    "color": "#ff9999",
                    "group": "source"
                }
                if rank_provider is not None:
                    json_node["rank"] = rank_provider.get_node_rank(node)

                result_nodes.append(json_node)

            for neighbor in node.neighbors:
                neighbor_id: str = node_id_map.get(neighbor)
                if neighbor_id is None:
                    continue

                result_edges.append({"from": node_id, "to": neighbor_id})

        use_rank_provider: bool = rank_provider is not None
        max_distance_from_cluster: int = max(0, max_distance_from_cluster)
        nodes: Dict[int, Node] = self._nodes
        for distance in range(max_distance_from_cluster + 1):
            new_nodes: Dict[int, Node] = {}
            add_edge: bool = True
            if distance == 0:
                group: str = "cluster"
                color: str = "#cc9999"
            elif distance == 1:
                group: str = "neighbors"
                color: str = "#99dd99"
            else:
                # There is no point in using the rank provider from this distance
                use_rank_provider = False
                group: str = "group_{}".format(distance-2)
                color: str = "#9999dd"
                add_edge = distance < max_distance_from_cluster or not lazy

            for node in nodes.values():
                node_id = node_id_map.get(node)
                if node_id is None:
                    node_id = node.name
                    node_id_map[node] = node_id
                    json_node = {
                        "id": node_id,
                        "label": node.name,
                        "color": color,
                        "group": group
                    }
                    if use_rank_provider:
                        json_node["rank"] = rank_provider.get_node_rank(node)
                    result_nodes.append(json_node)

                for neighbor in node.neighbors:
                    neighbor_id = node_id_map.get(neighbor)
                    if neighbor_id is None:
                        if nodes.get(neighbor.index) is None:
                            new_nodes[neighbor.index] = neighbor
                        continue

                    if add_edge or nodes.get(neighbor.index) is None:
                        result_edges.append({"from": node_id, "to": neighbor_id})

            nodes = new_nodes

        return result

    def validate(self) -> List[str]:
        """
        Checks whether the internal state of the cluster is valid.

        Returns:
            (List[str]) A list of strings describing the problems found in the cluster.
        """
        result: List[str] = self._validate_source_nodes()
        result.extend(self._validate_nodes())
        result.extend(self._validate_neighborhood())
        return result

    # Private methods
    # ------------------------------------------------------------

    def _add_neighbor_candidate(self, node: Node) -> None:
        """
        Adds the given node to the neighborhood of the cluster if it is neither in the cluster nor
        in the neighborhood at the moment.

        Note that this method doesn't check whether the node is actually a neighbor of the cluster,
        the caller must make sure it is!

        Args:
            node (Node): The node to check and add to the neighborhood of the cluster.
        """
        if node in self:
            return

        # Using is_neighbor() should be fine here.
        if self.is_neighbor(node):
            return

        # Ok, we can add the node to the neighborhood.
        self._neighbors[node.index] = node

    def _is_neighbor_of_cluster(self, node: Node) -> bool:
        """
        Returns whether the given node is in the neighborhood of the cluster.

        This method returns the correct value even if we are in the process of updating the
        neighborhood because of node addition or removal for example. As a consequence, this method
        is relatively slow, so it shouldn't be public. We have a separate, quicker method called
        `is_neighbor()` there which in turn is not accurate when the cluster is being updated but
        is accurate in all other cases.

        Arguments:
            node (Node): The node to check.

        Returns:
            bool: Whether the node is the neighbor of another node that's in the cluster.
        """
        # Check whether the node is in the cluster and not in the neighborhood.
        if node in self:
            return False

        for neighbor in node.neighbors:
            if neighbor in self:
                return True

        return False

    def _remove_node_internal(self, node: Node) -> None:
        """
        Removes the given node from the cluster.

        Arguments:
            node (Node): The node to remove from the cluster.
        """
        # Remove the node.
        # At this point the is_neighbor() method becomes inaccurate!
        # Use _is_neighbor_of_cluster() instead!
        del self._nodes[node.index]

        # Remove the neighbor added event handler from the node.
        node.remove_event_listener(NeighborAddedEvent.NEIGHBOR_ADDED, self._node_neighbor_added_handler)

        # Update the degree of the cluster.
        self.degree -= node.degree

        # Update the neighborhood of the cluster.
        for neighbor in node.neighbors:
            # Yes, we need to call _is_neighbor_of_cluster() to check whether the node will be part
            # of the neighborhood after the current update and also check whether it was a neighbor
            # before the current update.
            if not self._is_neighbor_of_cluster(neighbor) and\
               self._neighbors.get(neighbor.index) is not None:
                del self._neighbors[neighbor.index]

        # The removed node is probably in the neighborhood now.
        if self._is_neighbor_of_cluster(node):
            self._add_neighbor_candidate(node)

    def _validate_source_nodes(self) -> List[str]:
        """
        Checks whether there are problems regarding the source nodes of the cluster.

        A possible internal data error could be when a source node is not contained by the cluster.

        Returns:
            List[str]. A list of strings describing the problems found in the cluster.
        """
        result: List[str] = []

        for key in self._source_nodes:
            # _source_nodes must contain key.
            node: Node = self._source_nodes[key]
            # self._nodes may not contain the key use dict.get() to avoid possible exceptions.
            other: Node = self._nodes.get(key)
            if node is None:
                result.append("The source node corresponding to key [{}] is None.".format(key))
            if other is None:
                result.append("No node with key [{}] found in the cluster.".format(key))
            if node != other:
                result.append("The source and contained nodes with the same key [{}] "
                              "are different.".format(key))

        return result

    def _validate_nodes(self) -> List[str]:
        """
        Checks whether there are problems regarding the nodes contained by the cluster.

        A possible inconsistency is that a neighbor of a contained node is neither in the cluster
        nor in the neighborhood, or the cluster degree is incorrect, and so on. These could happen
        because of the dynamic nature of graphs, but only when the cluster is being updated.

        Returns:
            List[str]: A list of strings describing the problems found in the cluster.
        """
        result: List[str] = []
        cluster_degree: int = 0

        for key in self._nodes:
            node: Node = self._nodes[key]
            cluster_degree += node.degree
            for neighbor in node.neighbors:
                if neighbor in self:
                    continue
                if self.is_neighbor(neighbor):
                    continue
                result.append(u"Neighbor [{}] of node [{}] is neither in the cluster nor in its "
                              u"neighborhood.".format(neighbor.name.encode("utf8"),
                                                      node.name.encode("utf8")))

        if cluster_degree != self.degree:
            result.append("Incorrect cluster degree, {} instead of {}.".format(cluster_degree,
                                                                               self.degree))

        return result

    def _validate_neighborhood(self) -> List[str]:
        """
        Checks whether there are problems regarding the neighborhood of the cluster.

        A typical problem is that a node in the neighborhood is not actually a neighbor
        of the cluster.

        Returns:
            List[str]: A list of strings describing the problems found regarding the
                       neighborhood of the cluster.
        """
        result: List[str] = []

        for key in self._neighbors:
            neighbor: Node = self._neighbors[key]
            if not self._is_neighbor_of_cluster(neighbor):
                result.append(u"Node [{}] in the neighborhood is not a neighbor "
                              u"of the cluster.".format(neighbor.name.encode("utf8")))

        return result

    def _node_neighbor_added_handler(self, event: NeighborAddedEvent) -> None:
        """
        Event handler called when a neighbor is added to a node that is contained by the cluster.

        Arguments:
            event (Event): The event dispatched by the node.
        """
        # Keep the cluster degree up to date.
        self.degree += 1

        # Keep the neighborhood up to date.
        self._add_neighbor_candidate(event.neighbor)
