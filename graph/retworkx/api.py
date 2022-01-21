from typing import List, Any, Optional
from graph.retworkx.base import RetworkXMultiDiGraph, Node, Edge
import retworkx
from itertools import product


NodeID = int


def digraph_all_simple_paths(
    g: RetworkXMultiDiGraph[Any, Edge],
    source: NodeID,
    target: NodeID,
    min_depth: Optional[int] = None,
    cutoff: Optional[int] = None,
) -> List[List[Edge]]:
    """
    Return all simple paths between 2 nodes in a PyDiGraph object
    A simple path is a path with no repeated nodes.

    Args:
        g: The graph to find the path in
        source: The node index to find the paths from
        target: The node index to find the paths to
        min_depth: The minimum depth of the path to include in the output
            list of paths. By default all paths are included regardless of depth,
            set to None will behave like the default.
        cutoff: The maximum depth of path (number of edges) to include in the output list
            of paths. By default includes all paths regardless of depth, setting to
            None will behave like default.

    Return a list of lists where each inner list is a path containing edges
    """
    if cutoff is not None:
        cutoff += 1

    output = []
    for nodes in retworkx.digraph_all_simple_paths(  # type: ignore
        g._graph, source, target, min_depth, cutoff
    ):
        path = []
        for i in range(1, len(nodes)):
            path.append(g.get_edges_between_nodes(nodes[i - 1], nodes[i]))
        for x in product(*path):
            output.append(list(x))
    return output
