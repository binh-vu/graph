import pytest, pickle
from dataclasses import dataclass
from graph.retworkx_graph import (
    BaseRichEdge,
    BaseRichNode,
    RetworkXCanonicalMultiDiGraph,
    RetworkXMultiDiGraph,
)


@dataclass(eq=True)
class Node(BaseRichNode):
    id: int = -1


@dataclass(eq=True)
class Edge(BaseRichEdge):
    source: int
    target: int
    key: str = ""
    id: int = -1

    def __repr__(self) -> str:
        return f"{self.id}:{self.source}->{self.target}:{self.key}"


@pytest.fixture
def graph1():
    g: RetworkXCanonicalMultiDiGraph[Node, Edge] = RetworkXCanonicalMultiDiGraph()
    g.add_node(Node())
    g.add_node(Node())
    g.add_node(Node())

    g.add_edge(Edge(0, 1))
    g.add_edge(Edge(0, 2))
    g.add_edge(Edge(1, 2))
    return g


class TestCopy:
    @staticmethod
    def test_copy_do_not_share(graph1: RetworkXCanonicalMultiDiGraph[Node, Edge]):
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

    @staticmethod
    def test_copy_retain_id(graph1: RetworkXCanonicalMultiDiGraph[Node, Edge]):
        graph1.remove_node(1)
        g = graph1.copy()
        assert g.check_integrity()
        assert g.nodes() == [
            Node(0),
            Node(2),
        ]
        assert g.edges() == [
            Edge(0, 2, id=1),
        ]
        assert g == graph1


class TestPickle:
    @staticmethod
    def test_pickle_does_not_keep_original_edge_id(
        graph1: RetworkXCanonicalMultiDiGraph[Node, Edge]
    ):
        g = pickle.loads(pickle.dumps(graph1))
        assert g.check_integrity()
        assert g.nodes() == [
            Node(0),
            Node(1),
            Node(2),
        ]
        assert g.edges() == [
            Edge(0, 1, id=0),
            Edge(1, 2, id=1),
            Edge(0, 2, id=2),
        ]
        assert g != graph1
