from graph.retworkx.digraph import RetworkXDiGraph
import pytest, pickle
from dataclasses import dataclass
from tests.retworkx.conftest import Node, Edge, TestDiGraph, to_str_graph


def test_subgraph_from_nodes(graph1: TestDiGraph):
    g = graph1.subgraph_from_nodes([0, 2])
    assert g.check_integrity()
    assert g.nodes() == [
        Node(0),
        Node(2),
    ]
    assert g.edges() == [Edge(0, 2, id=1)]


class TestCopy:
    @staticmethod
    def test_copy_do_not_share(graph1: TestDiGraph):
        for i in range(3):
            g = graph1.copy()
            assert g.check_integrity() and g == graph1
            g.remove_node(1)
            assert g.check_integrity() and g != graph1
            assert g.nodes() == [
                Node(0),
                Node(2),
            ]
            assert g.edges() == [
                Edge(0, 2, id=1),
            ]

            g2 = graph1.copy()
            g2.remove_node(0)
            assert g2.check_integrity()
            assert g2.nodes() == [Node(1), Node(2)]
            assert g2.edges() == [
                Edge(1, 2, id=2),
            ]

    @staticmethod
    def test_copy_retain_node_id(graph1: TestDiGraph):
        graph1.remove_node(1)
        g = graph1.copy()
        assert g.check_integrity() and g == graph1
        assert g.nodes() == [
            Node(0),
            Node(2),
        ]
        assert g.edges() == [
            Edge(0, 2, id=1),
        ]

    @staticmethod
    def test_copy_retain_edge_id(graph1: TestDiGraph):
        assert graph1.edges() == [
            Edge(0, 1, id=0),
            Edge(0, 2, id=1),
            Edge(1, 2, id=2),
        ]
        graph1.remove_edges_between_nodes(0, 1)

        g = graph1.copy()
        assert g.check_integrity() and g == graph1
        assert g.nodes() == [
            Node(0),
            Node(1),
            Node(2),
        ]
        assert g.edges() == [
            Edge(0, 2, id=1),
            Edge(1, 2, id=2),
        ]


class TestPickle:
    @staticmethod
    def test_pickle_keep_original_edge_id(graph1: TestDiGraph):
        g = pickle.loads(pickle.dumps(graph1))
        assert g.check_integrity()
        # node id is the same
        assert g.nodes() == [
            Node(0),
            Node(1),
            Node(2),
        ]
        # but edge id is different
        assert g.edges() == [
            Edge(0, 1, id=0),
            Edge(0, 2, id=1),
            Edge(1, 2, id=2),
        ]
        assert g == graph1

    @staticmethod
    def test_pickle_node_deletion(graph1: TestDiGraph):
        graph1.remove_node(1)
        g = pickle.loads(pickle.dumps(graph1))
        assert g.check_integrity()
        assert g.nodes() == [
            Node(0),
            Node(2),
        ]
        assert g.edges() == [
            Edge(0, 2, id=1),
        ]
        assert g == graph1

    @staticmethod
    def test_pickle_edge_deletion(graph1: TestDiGraph):
        graph1.remove_edges_between_nodes(0, 1)
        g = pickle.loads(pickle.dumps(graph1))
        assert g.check_integrity()
        assert g.nodes() == [
            Node(0),
            Node(1),
            Node(2),
        ]
        assert g.edges() == [
            Edge(0, 2, id=1),
            Edge(1, 2, id=2),
        ]
        assert g == graph1
