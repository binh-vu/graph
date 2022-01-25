from graph.retworkx.api import (
    digraph_all_simple_paths,
    digraph_find_cycle,
    has_cycle,
    is_weakly_connected,
    weakly_connected_components,
)
from tests.retworkx.conftest import Node, Edge, get_edge_fn, to_str_graph


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


def test_is_weakly_connected(graph1, graph2, graph3):
    assert is_weakly_connected(graph1)
    assert is_weakly_connected(graph2)
    assert not is_weakly_connected(graph3)


def test_weakly_connected_components(graph1, graph2, graph3):
    assert weakly_connected_components(graph1) == [{0, 1, 2}]
    assert weakly_connected_components(graph2) == [{0, 1, 2, 3}]
    assert weakly_connected_components(graph3) == [{0, 1, 2, 3}, {4, 5}]

    assert weakly_connected_components(to_str_graph(graph1)) == [{"A", "B", "C"}]
    assert weakly_connected_components(to_str_graph(graph2)) == [{"A", "B", "C", "D"}]
    assert weakly_connected_components(to_str_graph(graph3)) == [
        {"A", "B", "C", "D"},
        {"E", "F"},
    ]


def test_has_cycle(graph1, graph2, graph3, graph4):
    assert not any(has_cycle(g) for g in [graph1, graph2, graph3])
    assert has_cycle(graph4)


def test_digraph_find_cycle(graph4):
    e = get_edge_fn(graph4)
    assert digraph_find_cycle(graph4, 0) == [
        e("1 -> 2"),
        e("2 -> 3"),
        e("3 -> 1"),
    ]
    assert digraph_find_cycle(graph4, 5) == [
        e("5 -> 4"),
        e("4 -> 5"),
    ]
    assert digraph_find_cycle(graph4, 6) == []
