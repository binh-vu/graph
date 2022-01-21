import warnings
from typing import Any, Callable, Generic, Iterator, List, Optional, Tuple, TypeVar

from retworkx import NoEdgeBetweenNodes, PyDiGraph  # type: ignore
from graph.interface import IGraph, Node, Edge


class RetworkXMultiDiGraph(Generic[Node, Edge], IGraph[int, int, Node, Edge]):
    def __init__(self, check_cycle: bool = False, multigraph: bool = True):
        self._graph = PyDiGraph(check_cycle=check_cycle, multigraph=multigraph)

    @property
    def check_cycle(self) -> bool:
        return self._graph.check_cycle

    @property
    def multigraph(self) -> bool:
        return self._graph.multigraph

    def num_edges(self) -> int:
        """Return the number of edges in the graph"""
        return self._graph.num_edges()

    def num_nodes(self) -> int:
        """Return the number of nodes in the graph"""
        return self._graph.num_nodes()

    def edges(self) -> List[Edge]:
        """Return a list of all edges"""
        return self._graph.edges()

    def nodes(self) -> List[Node]:
        """Return a list of all nodes, ordered by their id"""
        return self._graph.nodes()

    def successors(self, nid: int) -> List[Node]:
        """Get the successors of a node"""
        return self._graph.successors(nid)

    def predecessors(self, nid: int) -> List[Node]:
        """Get the predecessors of a node"""
        return self._graph.predecessors(nid)

    def filter_edges(self, fn: Callable[[Edge], bool]) -> List[Node]:
        """Get edges in the graph filtered by the given function"""
        return [e for e in self._graph.edges() if fn(e)]

    def filter_nodes(self, fn: Callable[[Node], bool]) -> List[Node]:
        """Get nodes in the graph filtered by the given function"""
        return [n for n in self._graph.nodes() if fn(n)]

    def iter_edges(self) -> Iterator[Edge]:
        """Iter edges in the graph. Still create a new list everytime it's called"""
        return self._graph.edges()

    def iter_nodes(self) -> Iterator[Node]:
        """Iter nodes in the graph. Still create a new list everytime it's called"""
        return self._graph.nodes()

    def iter_filter_edges(self, fn: Callable[[Edge], bool]) -> Iterator[Node]:
        """Iter edges in the graph filtered by the given function"""
        return (e for e in self._graph.edges() if fn(e))

    def iter_filter_nodes(self, fn: Callable[[Node], bool]) -> Iterator[Node]:
        """Iter nodes in the graph filtered by the given function"""
        return (n for n in self._graph.nodes() if fn(n))

    def add_node(self, node: Node) -> int:
        """Add a new node to the graph."""
        return self._graph.add_node(node)

    def add_edge(self, source: int, target: int, edge: Edge) -> int:
        """Add an edge between 2 nodes and return id of the new edge

        Args:
            source: Index of the parent node
            target: Index of the child node
            edge: The object to set as the data for the edge.

        Returns:
            id of the new edge

        Raises:
            When the new edge will create a cycle if `check_cycle` is True
        """
        return self._graph.add_edge(source, target, edge)

    def remove_node(self, nid: int):
        """Remove a node from the graph. If the node is not present in the graph it will be ignored and this function will have no effect."""
        return self._graph.remove_node(nid)

    def remove_edge(self, eid: int):
        """Remove an edge identified by the provided id"""
        return self._graph.remove_edge_from_index(eid)

    def update_edge(self, eid: int, edge: Edge):
        """Update an edge's content inplace"""
        self._graph.update_edge_by_index(eid, edge)

    def update_node(self, nid: int, node: Node):
        """Update the node data inplace"""
        self._graph[nid] = node

    def remove_edges_between_nodes(self, uid: int, vid: int):
        """Remove edges between 2 nodes."""
        while True:
            try:
                self._graph.remove_edge(uid, vid)
            except NoEdgeBetweenNodes:
                return

    def has_node(self, nid: int) -> bool:
        """Check if a node with given id exists in the graph"""
        try:
            self._graph.get_node_data(nid)
        except IndexError:
            return False
        return True

    def get_node(self, nid: int) -> Node:
        """Get the node by id"""
        return self._graph.get_node_data(nid)

    def get_edge(self, eid: int) -> Edge:
        """Get the edge by id"""
        return self._graph.get_edge_data_by_index(eid)

    def find_node(self, value: Any) -> Optional[Node]:
        """Find node in the graph that is equal (`==`) given a specific weight.

        The `__eq__` method of value is going to be used to compare the nodes.

        This algorithm has a worst case of O(n) since it searches the node indices in order.
        If there is more than one node in the graph with the same weight only the first match (by node index) will be returned.
        """
        nid = self._graph.find_node_by_weight(value)
        if nid is not None:
            return self._graph.get_node_data(nid)
        return None

    def has_edges_between_nodes(self, uid: int, vid: int) -> bool:
        """Return True if there is an edge between 2 nodes."""
        return self._graph.has_edge(uid, vid)

    def get_edges_between_nodes(self, uid: int, vid: int) -> List[Edge]:
        """Return the edge data for all the edges between 2 nodes."""
        try:
            return self._graph.get_all_edge_data(uid, vid)
        except NoEdgeBetweenNodes:
            return []

    def degree(self, nid: int) -> int:
        """Get the degree of a node"""
        return self._graph.in_degree(nid) + self._graph.out_degree(nid)

    def in_degree(self, nid: int) -> int:
        """Get the degree of a node for inbound edges."""
        return self._graph.in_degree(nid)

    def in_edges(self, vid: int) -> List[Tuple[int, Edge]]:
        """Get incoming edges of a node. Return a list of tuples of (source id, edge data)"""
        return [(uid, edge) for uid, _, edge in self._graph.in_edges(vid)]

    def out_degree(self, nid: int) -> int:
        """Get the degree of a node for outbound edges."""
        return self._graph.out_degree(nid)

    def out_edges(self, uid: int) -> List[Tuple[int, Edge]]:
        """Get outgoing edges of a node. Return a list of tuples of (target id, edge data)"""
        return [(vid, edge) for _, vid, edge in self._graph.out_edges(uid)]

    def copy(self):
        g = self.__class__.__new__(self.__class__)
        g.__dict__ = self.__dict__.copy()
        g._graph = g._graph.copy()
        return g

    def __eq__(self, other: "RetworkXMultiDiGraph"):
        """Check if content of two graphs are equal"""
        if (
            not isinstance(other, RetworkXMultiDiGraph)
            or self.num_nodes() != other.num_nodes()
            or self.num_edges() != other.num_edges()
        ):
            return False

        for nid in self._graph.node_indexes():
            if not other.has_node(nid) or self._graph[nid] != other._graph[nid]:
                return False

        return dict(self._graph.edge_index_map().items()) == dict(
            other._graph.edge_index_map().items()
        )
