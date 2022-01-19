import warnings
from copy import copy
from abc import ABC
from typing import (
    Any,
    Callable,
    Generic,
    Iterator,
    List,
    Optional,
    Tuple,
    TypeVar,
    Union,
)
from retworkx import PyDiGraph, NoEdgeBetweenNodes  # type: ignore


NodeID = int
EdgeID = int
EdgeKey = Union[str, int]


class BaseRichNode(ABC):
    def __init__(self, id: NodeID):
        self.id = id


class BaseRichEdge(ABC):
    def __init__(self, id: EdgeID, source: NodeID, target: NodeID, key: EdgeKey):
        self.id = id
        self.source = source
        self.target = target
        self.key = key


Node = TypeVar("Node")
Edge = TypeVar("Edge")
RichNode = TypeVar("RichNode", bound=BaseRichNode)
RichEdge = TypeVar("RichEdge", bound=BaseRichEdge)


class RetworkXMultiDiGraph(Generic[Node, Edge]):
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

    def successors(self, nid: NodeID) -> List[Node]:
        """Get the successors of a node"""
        return self._graph.successors(nid)

    def predecessors(self, nid: NodeID) -> List[Node]:
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

    def add_node(self, node: Node) -> NodeID:
        """Add a new node to the graph."""
        return self._graph.add_node(node)

    def add_edge(self, source: NodeID, target: NodeID, edge: Edge) -> EdgeID:
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

    def remove_node(self, nid: NodeID):
        """Remove a node from the graph. If the node is not present in the graph it will be ignored and this function will have no effect."""
        return self._graph.remove_node(nid)

    def remove_edge(self, eid: EdgeID):
        """Remove an edge identified by the provided id"""
        return self._graph.remove_edge_from_index(eid)

    def update_edge(self, eid: EdgeID, edge: Edge):
        """Update an edge's content inplace"""
        self._graph.update_edge_by_index(eid, edge)

    def update_node(self, nid: NodeID, node: Node):
        """Update the node data inplace"""
        self._graph[nid] = node

    def remove_edges_between_nodes(self, uid: NodeID, vid: NodeID):
        """Remove edges between 2 nodes."""
        while True:
            try:
                self._graph.remove_edge(uid, vid)
            except NoEdgeBetweenNodes:
                return

    def has_node(self, nid: NodeID) -> bool:
        try:
            self._graph.get_node_data(nid)
        except IndexError:
            return False
        return True

    def get_node(self, nid: NodeID) -> Node:
        return self._graph.get_node_data(nid)

    def get_edge(self, eid: EdgeID) -> Edge:
        warnings.warn("get_edge is expensive O(n)")
        return self._graph.edge_index_map()[eid]

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

    def has_edges_between_nodes(self, uid: NodeID, vid: NodeID) -> bool:
        """Return True if there is an edge between 2 nodes."""
        return self._graph.has_edge(uid, vid)

    def get_edges_between_nodes(self, uid: NodeID, vid: NodeID) -> List[Edge]:
        """Return the edge data for all the edges between 2 nodes."""
        try:
            return self._graph.get_all_edge_data(uid, vid)
        except NoEdgeBetweenNodes:
            return []

    def degree(self, nid: NodeID) -> int:
        """Get the degree of a node"""
        return self._graph.in_degree(nid) + self._graph.out_degree(nid)

    def in_degree(self, nid: NodeID) -> int:
        """Get the degree of a node for inbound edges."""
        return self._graph.in_degree(nid)

    def in_edges(self, vid: NodeID) -> List[Tuple[NodeID, Edge]]:
        """Get incoming edges of a node. Return a list of tuples of (source id, edge data)"""
        return [(uid, edge) for uid, _, edge in self._graph.in_edges(vid)]

    def out_degree(self, nid: NodeID) -> int:
        """Get the degree of a node for outbound edges."""
        return self._graph.out_degree(nid)

    def out_edges(self, uid: NodeID) -> List[Tuple[NodeID, Edge]]:
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


class RetworkXCanonicalMultiDiGraph(RetworkXMultiDiGraph[RichNode, RichEdge]):
    def add_node(self, node: RichNode) -> NodeID:
        """Add a new node to the graph."""
        node.id = self._graph.add_node(node)
        return node.id

    def add_edge(self, edge: RichEdge) -> EdgeID:
        edge.id = self._graph.add_edge(edge.source, edge.target, edge)
        return edge.id

    def in_edges(self, vid: NodeID) -> List[RichEdge]:
        """Get incoming edges of a node"""
        return [edge for uid, _, edge in self._graph.in_edges(vid)]

    def out_edges(self, uid: NodeID) -> List[RichEdge]:
        """Get outgoing edges of a node"""
        return [edge for _, vid, edge in self._graph.out_edges(uid)]

    def remove_edge_between_nodes(self, uid: NodeID, vid: NodeID, key: EdgeKey):
        """Remove edge with key between 2 nodes."""
        edge = self.get_edge_between_nodes(uid, vid, key)
        if edge is not None:
            self.remove_edge(edge.id)

    def has_edge_between_nodes(self, uid: NodeID, vid: NodeID, key: EdgeKey) -> bool:
        """Return True if there is an edge with key between 2 nodes."""
        try:
            edges: List[RichEdge] = self._graph.get_all_edge_data(uid, vid)
            return any(edge.key == key for edge in edges)
        except NoEdgeBetweenNodes:
            return False

    def get_edge_between_nodes(
        self, uid: NodeID, vid: NodeID, key: EdgeKey
    ) -> Optional[RichEdge]:
        """Return True if there is an edge with key between 2 nodes."""
        try:
            edges: List[RichEdge] = self._graph.get_all_edge_data(uid, vid)
            return next((edge for edge in edges if edge.key == key), None)
        except NoEdgeBetweenNodes:
            return None

    def check_integrity(self) -> bool:
        """Check if ids/refs in the graph are consistent"""
        for nid in self._graph.node_indexes():
            node = self._graph[nid]
            if node.id != nid:
                return False
        for eid, (uid, vid, edge) in self._graph.edge_index_map().items():
            if edge.id != eid or edge.source != uid or edge.target != vid:
                return False
        return True

    def __setstate__(self, state):
        """Reload the state of the graph. This function is often called in pickling and copy
        This does not guarantee to keep the same edge id
        """
        self.__dict__ = dict.copy(state)
        for eid, (_, _, edge) in self._graph.edge_index_map().items():
            edge.id = eid
        return self
