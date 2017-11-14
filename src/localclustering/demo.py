"""
Demo script that shows the basic usage of the localclustering project using an `IGraphWrapper` from
the graphscraper project.
"""

from typing import Any, Dict, List

try:
    import cairo
except ImportError:
    cairo = None
    raise ImportError("The cairo project and its python bindings (pycairo) must be installed in order "
                      "to run this demo. See igraph's installation instructions for more details.")

import igraph

from graphscraper.base import Node
from graphscraper.igraphwrapper import IGraphWrapper
from localclustering.definitions.connectivity import ConnectivityClusterDefinition
from localclustering.hierarchicalengine import HierarchicalClusterEngine
from localclustering.localengine import LocalClusterEngine
from localclustering.ranking import BaseRankProvider

from localclustering.cluster import Cluster

default_node_color: str = "#3F51B5"
"""
The default color of nodes.
"""

default_visited_node_color: str = "#2196F3"
"""
The color of nodes that have been visited by the cluster engine but were not included in the final cluster.
"""

cluster_node_color: str = "#F44336"
"""
The color of nodes within the calculated cluster.
"""

cluster_1: List[int] = [0, 1, 2, 3, 4, 5, 6, 7, 10, 11, 12, 13, 16, 17, 19, 21]
"""
The indices of the nodes in cluster 1 of the Zachary karate club
(igraph's node indices because they are fixed after the graph is created).
"""

cluster_2: List[int] = [8, 9, 14, 15, 18, 20, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33]
"""
The indices of the nodes in cluster 2 of the Zachary karate club.
(igraph's node indices because they are fixed after the graph is created)
"""

easy_node_indices: List[int] = [12, 15, 20, 24, 31]
"""
The indices of some nodes whose cluster should be easy to find.
"""

interesting_node_indices: List[int] = [1, 2, 6, 8, 28]
"""
The indices of some nodes that are located at interesting points within the social network.
"""

default_colors: List[str] = [default_node_color] * 34
"""
The list of node colors to use when the graph is plotted.
"""

default_shapes: List[str] = ["circle"] * 34
"""
The list of node shapes to use when the graph is plotted.
"""

default_sizes: List[int] = [15] * 34
"""
The list of default node sizes to use when the graph is plotted.
"""

visual_style: Dict = {
    "bbox": (800, 800),
    "margin": 40,
    "vertex_label": [str(i) for i in range(34)]
}
"""
The base visual style to use when igraph draws a graph.
"""


def do_cluster(graph: IGraphWrapper,
               engine: Any,
               source_index: int,
               layout: Any,
               file_name: str):
    """
    Does the actual cluster on the given graph using the given cluster engine.

    Arguments:
         graph (IGraphWrapper): The graph to cluster.
         engine (Any): The cluster engine to use.
         source_index (int): The index of the source node of the clustering.
         layout (Any): The layout to use to plot the result of the clustering.
         file_name (str): The file name to save plot to.
    """
    print("Finding cluster of {}...".format(source_index))

    # Retrieve the source node. The can_validate_and_load argument must be True
    # otherwise the wrapper wouldn't load the node from the igraph graph instance.
    source_node: Node = graph.nodes.get_node_by_name(str(source_index), can_validate_and_load=True)

    # Do the clustering with the specified source node.
    cluster: Cluster = engine.cluster([source_node])
    rank_provider: BaseRankProvider = engine.get_rank_provider()

    # Check whether the cluster's internal state is valid. This is not necessary at all,
    # it's here only for debugging purposes.
    if len(cluster.validate()) > 0:
        raise ValueError("The created cluster is invalid.")

    # Calculate the visual properties of the nodes.
    colors = default_colors[:]
    shapes = default_shapes[:]
    sizes = default_sizes[:]

    for node in cluster.nodes:
        igraph_index: int = node.igraph_index
        colors[igraph_index] = cluster_node_color
        sizes[igraph_index] *= rank_provider.get_node_rank(node)

    for node in cluster.neighborhood:
        igraph_index: int = node.igraph_index
        colors[igraph_index] = default_visited_node_color
        rank = rank_provider.get_node_rank(node)
        if rank > 0:
            sizes[igraph_index] *= rank

    shapes[source_index] = "diamond"

    # Plot the result.
    igraph.plot(
        graph.wrapped_graph,
        file_name,
        layout=layout,
        vertex_color=colors,
        vertex_shape=shapes,
        vertex_size=sizes,
        **visual_style)


def test_local_clustering():
    """
    Shows the usage of the local cluster engine.
    """
    # Create the igraph Graph and calculate a layout.
    ig_graph: igraph.Graph = igraph.Graph.Famous("Zachary")
    layout = ig_graph.layout("kk")

    # Wrap the igraph Graph in an IGraphWrapper instance.
    graph: IGraphWrapper = IGraphWrapper(ig_graph)

    # Set up the local cluster engine.
    engine: LocalClusterEngine = LocalClusterEngine(
        ConnectivityClusterDefinition(1.5, 0.85),
        source_nodes_in_result=True,
        max_cluster_size=34
    )

    # Do the actual clustering.
    for index in easy_node_indices:
        do_cluster(graph, engine, index, layout, "local_{}.pdf".format(index))
    for index in interesting_node_indices:
        do_cluster(graph, engine, index, layout, "local_{}.pdf".format(index))


def test_hierarchical_clustering():
    """
    Shows the usage of the hierarchical local cluster engine.
    """
    # Create the igraph Graph and calculate a layout.
    ig_graph: igraph.Graph = igraph.Graph.Famous("Zachary")
    layout = ig_graph.layout("kk")

    # Wrap the igraph Graph in an IGraphWrapper instance.
    graph: IGraphWrapper = IGraphWrapper(ig_graph)

    # Set up the hierarchical cluster engine.
    cluster_definition: ConnectivityClusterDefinition = ConnectivityClusterDefinition(
        weighting_coefficient=1.1,
        threshold_modifier=0.85
    )
    engine: HierarchicalClusterEngine = HierarchicalClusterEngine()
    engine.cluster_definition = cluster_definition

    # Do the actual clustering.
    for min_cluster_size in [4, 8, 12]:
        engine.min_cluster_size = min_cluster_size
        for index in easy_node_indices:
            do_cluster(graph, engine, index, layout, "hierarchical_{}_{}.pdf".format(index, min_cluster_size))
        for index in interesting_node_indices:
            do_cluster(graph, engine, index, layout, "hierarchical_{}_{}.pdf".format(index, min_cluster_size))


def demo():
    """
    Runs both the local and hierarchical cluster engine test/demos.
    """
    # Imports must be here because of the path hacking.
    test_local_clustering()
    test_hierarchical_clustering()
