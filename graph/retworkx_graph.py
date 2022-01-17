from typing import Callable, Generic, Iterator, List, TypeVar
from retworkx import PyDiGraph, NoEdgeBetweenNodes  # type: ignore

NodeID = int
EdgeID = int
Node = TypeVar("Node")
Edge = TypeVar("Edge")


class RetworkXMultiDiGraph(Generic[Node, Edge]):
    def __init__(self, check_cycle = False, multigraph = True):
        self._graph = PyDiGraph(check_cycle=check_cycle, multigraph=multigraph)  # type: ignore
    
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
        """Return a list of all nodes"""
        return self._graph.nodes()
    
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
            When the new edge will create a cycle
        """
        return self._graph.add_edge(source, target, edge)

    def remove_node(self, nid: NodeID):
        """Remove a node from the graph. If the node is not present in the graph it will be ignored and this function will have no effect."""
        return self._graph.remove_node(nid)
    
    def remove_edge(self, eid: EdgeID):
        """Remove an edge identified by the provided id"""
        return self._graph.remove_edge_from_index(eid)

    def remove_edges_between_nodes(self, uid: NodeID, vid: NodeID):
        """Remove edges between 2 nodes."""
        while True:
            try:
                self._graph.remove_edge(uid, vid)
            except NoEdgeBetweenNodes:
                return

    def get_node(self, nid: NodeID) -> Node:
        return self._graph.get_node_data(nid)
    
    def in_degree(self, nid: NodeID) -> int:
        """Get the degree of a node for inbound edges."""
        return self._graph.in_degree(nid)
    
    def in_edges(self, vid: NodeID) -> List[Edge]:
        """Get incoming edges of a node"""
        return [edge for uid, _, edge in self._graph.in_edges(vid)]
    
    def out_degree(self, nid: NodeID) -> int:
        """Get the degree of a node for outbound edges."""
        return self._graph.out_degree(nid)

    def out_edges(self, uid: NodeID) -> List[Edge]:
        """Get outgoing edges of a node"""
        return [edge for _, vid, edge in self._graph.out_edges(uid)]
