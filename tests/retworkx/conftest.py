import pytest, pickle, re
from dataclasses import dataclass
from graph.retworkx.canonical import (
    BaseRichEdge,
    BaseRichNode,
    RetworkXCanonicalMultiDiGraph,
)


@dataclass(eq=True)
class Node(BaseRichNode[int]):
    id: int = -1


@dataclass(eq=True)
class Edge(BaseRichEdge[int, int, str]):
    source: int
    target: int
    key: str = ""
    id: int = -1

    def __repr__(self) -> str:
        return f"{self.id}:{self.source}->{self.target}:{self.key}"


def parse_graph(struct: str) -> RetworkXCanonicalMultiDiGraph[Node, Edge, str]:
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
    g = RetworkXCanonicalMultiDiGraph()
    for i in range(n_nodes):
        g.add_node(Node())
    for edge in edges:
        g.add_edge(edge)
    return g


@pytest.fixture
def graph1():
    return parse_graph(
        """
    0 -> 1; 0 -> 2
    1 -> 2
    """
    )


@pytest.fixture
def graph2():
    return parse_graph(
        """
    0 -> 1; 0 -> 2; 0 -> 3
    1 -> 2;
    2 -> 3
    """
    )
