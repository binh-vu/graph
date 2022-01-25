from typing import Any, Callable
from graph.retworkx.str_digraph import RetworkXStrDiGraph
import pytest, pickle, re
from dataclasses import dataclass
from graph.retworkx import (
    BaseEdge,
    BaseNode,
    RetworkXDiGraph,
)

from graph import interface


@dataclass(eq=True)
class Node(BaseNode[int]):
    id: int = -1


@dataclass(eq=True)
class StrNode(BaseNode[str]):
    id: str


@dataclass(eq=True)
class Edge(BaseEdge[int, str]):
    source: int
    target: int
    key: str = ""
    id: int = -1

    def __repr__(self) -> str:
        return f"{self.key}:{self.source}->{self.target}"


@dataclass(eq=True)
class StrEdge(BaseEdge[str, str]):
    source: str
    target: str
    key: str = ""
    id: int = -1

    def __repr__(self) -> str:
        return f"{self.id}:{self.source}->{self.target}:{self.key}"


TestDiGraph = RetworkXDiGraph[str, Node, Edge]
TestStrDiGraph = RetworkXStrDiGraph[str, StrNode, StrEdge]


def parse_graph(struct: str) -> TestDiGraph:
    edges = []
    for line in struct.split("\n"):
        for edge in line.strip().split(";"):
            edge = edge.strip()
            if edge == "":
                continue
            m = re.match(r"(\d+) *-> *(\d+)", edge)
            assert m is not None, edge
            edges.append(Edge(int(m.group(1)), int(m.group(2))))

    n_nodes = max(max(edge.source, edge.target) for edge in edges) + 1
    g: TestDiGraph = RetworkXDiGraph()
    for i in range(n_nodes):
        g.add_node(Node())
    for edge in edges:
        g.add_edge(edge)
    return g


def to_str_graph(g: TestDiGraph) -> TestStrDiGraph:
    g1 = RetworkXStrDiGraph()
    idmap = lambda x: chr(ord("A") + x)
    for n in g.iter_nodes():
        g1.add_node(StrNode(id=idmap(n.id)))
    for e in g.iter_edges():
        g1.add_edge(StrEdge(source=idmap(e.source), target=idmap(e.target), key=e.key))
    return g1


def get_edge_fn(
    g: interface.IGraph[
        Any,
        Any,
        Any,
        interface.Node,
        interface.Edge,
    ]
) -> Callable[[str], interface.Edge]:
    def get_edge(estring: str) -> interface.Edge:
        m = re.match(
            r"(?:(?P<key>[^ ]+):)?(?P<source>[^ ]+) *-> *(?P<target>[^ ]+)", estring
        )
        assert m is not None, estring
        key = m.group("key") or ""
        source = m.group("source")
        target = m.group("target")
        if source.isdigit():
            source = int(source)
        if target.isdigit():
            target = int(target)
        return g.get_edge_between_nodes(source, target, key)

    return get_edge


@pytest.fixture
def graph1():
    # default simple graph
    return parse_graph(
        """
    0 -> 1; 0 -> 2
    1 -> 2
    """
    )


@pytest.fixture
def graph2():
    # testing all simple paths with cut-offs
    return parse_graph(
        """
    0 -> 1; 0 -> 2; 0 -> 3
    1 -> 2;
    2 -> 3
    """
    )


@pytest.fixture
def graph3():
    # graph contains two connected components
    return parse_graph(
        """
    0 -> 1; 0 -> 2; 0 -> 3
    1 -> 2;
    2 -> 3;
    4 -> 5;
    """
    )


@pytest.fixture
def graph4():
    # graph for testing cycles
    return parse_graph(
        """
        0 -> 1; 1 -> 2; 2 -> 3;
        3 -> 1;
        4 -> 5; 4 -> 6;
        5 -> 4;
        """
    )
