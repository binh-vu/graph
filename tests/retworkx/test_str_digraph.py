from graph.retworkx.digraph import RetworkXDiGraph
import pytest, pickle
from dataclasses import dataclass
from tests.retworkx.conftest import (
    Node,
    Edge,
    TestDiGraph,
    to_str_graph,
    StrNode,
    StrEdge,
)


def test_subgraph_from_nodes(graph1: TestDiGraph):
    graph1_ = to_str_graph(graph1)
    g = graph1_.subgraph_from_nodes(["A", "C"])
    assert g.check_integrity()
    assert g.nodes() == [
        StrNode("A"),
        StrNode("C"),
    ]
    assert g.edges() == [StrEdge("A", "C", id=1)]


class TestCopy:
    @staticmethod
    def test_copy_do_not_share(graph1: TestDiGraph):
        graph1_ = to_str_graph(graph1)
        for i in range(3):
            g = graph1_.copy()
            assert g.check_integrity() and g == graph1_
            g.remove_node("B")
            assert g.check_integrity() and g != graph1_
            assert g.nodes() == [
                StrNode("A"),
                StrNode("C"),
            ]
            assert g.edges() == [
                StrEdge("A", "C", id=1),
            ]

    @staticmethod
    def test_copy_retain_id(graph1: TestDiGraph):
        graph1_ = to_str_graph(graph1)
        graph1_.remove_node("B")
        for i in range(3):
            g = graph1_.copy()
            assert g.check_integrity() and g == graph1_
            assert g.nodes() == [
                StrNode("A"),
                StrNode("C"),
            ]
            assert g.edges() == [
                StrEdge("A", "C", id=1),
            ]


class TestPickle:
    @staticmethod
    def test_pickle_does_not_keep_original_edge_id(graph1: TestDiGraph):
        graph1_ = to_str_graph(graph1)
        g = pickle.loads(pickle.dumps(graph1_))
        assert g.check_integrity()
        assert g.nodes() == [
            StrNode("A"),
            StrNode("B"),
            StrNode("C"),
        ]
        assert g.edges() == [
            StrEdge("A", "B", id=0),
            StrEdge("B", "C", id=1),
            StrEdge("A", "C", id=2),
        ]
        assert g != graph1_
