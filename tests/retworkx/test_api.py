from graph.retworkx import digraph_all_simple_paths
from tests.retworkx.conftest import Node, Edge


def test_digraph_all_simple_paths(graph2):
    assert digraph_all_simple_paths(graph2, 0, 3) == [
        [Edge(0, 3, id=2)],
        [Edge(0, 2, id=1), Edge(2, 3, id=4)],
        [Edge(0, 1, id=0), Edge(1, 2, id=3), Edge(2, 3, id=4)],
    ]
    assert digraph_all_simple_paths(graph2, 0, 3, cutoff=2) == [
        [Edge(0, 3, id=2)],
        [Edge(0, 2, id=1), Edge(2, 3, id=4)],
    ]
