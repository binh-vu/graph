from typing import Dict, Generic, List, Tuple, TypeVar, Union

from graph.interface import EdgeKey, ICanonicalGraph, NodeID
from graph.retworkx.base import RetworkXMultiDiGraph

from retworkx import NoEdgeBetweenNodes  # type: ignore


class BaseRichNode(Generic[NodeID]):
    def __init__(self, id: NodeID):
        self.id = id


class BaseRichEdge(Generic[NodeID]):
    def __init__(self, id: int, source: NodeID, target: NodeID, key: EdgeKey):
        self.id = id
        self.source = source
        self.target = target
        self.key = key


Node = TypeVar("Node", bound=BaseRichNode[int])
Edge = TypeVar("Edge", bound=BaseRichEdge[int])


class RetworkXCanonicalMultiDiGraph(
    Generic[Node, Edge],
    ICanonicalGraph[int, int, Node, Edge],
    RetworkXMultiDiGraph[Node, Edge],
):
    """
    A graph with strong typing.
    Ideally, EdgeKey should be a parameter of Edge, however, we can't do it with current typing system yet
    """

    def add_node(self, node: Node) -> int:
        """Add a new node to the graph."""
        node.id = self._graph.add_node(node)
        return node.id

    def add_edge(self, edge: Edge) -> int:
        try:
            edges: List[Edge] = [
                e
                for e in self._graph.get_all_edge_data(edge.source, edge.target)
                if e.key == edge.key
            ]
            if len(edges) > 0:
                # duplicated edges
                return edges[0].id
        except NoEdgeBetweenNodes:
            pass

        edge.id = self._graph.add_edge(edge.source, edge.target, edge)
        return edge.id

    def update_edge(self, edge: Edge):
        """Update an edge's content inplace"""
        oldedge = self._graph.get_edge_data_by_index(edge.id)
        if oldedge.key != edge.key:
            # check if updating will result in duplicated edge
            if self.has_edge_between_nodes(edge.source, edge.target, edge.key):
                raise ValueError(
                    "Can't update edge as it will result in duplicated key"
                )
        self._graph.update_edge_by_index(edge.id, edge)

    def update_node(self, node: Node):
        """Update the node data inplace"""
        self._graph[node.id] = node

    def in_edges(self, vid: int) -> List[Edge]:
        """Get incoming edges of a node"""
        return [edge for uid, _, edge in self._graph.in_edges(vid)]

    def group_in_edges(self, vid: int) -> List[Tuple[Node, Dict[EdgeKey, Edge]]]:
        """Get incoming edges of a node, but group edges by their predecessors and key of each edge"""
        return [
            (
                u,
                {e.key: e for e in self.get_edges_between_nodes(u.id, vid)},
            )
            for u in self.predecessors(vid)
        ]

    def out_edges(self, uid: int) -> List[Edge]:
        """Get outgoing edges of a node"""
        return [edge for _, vid, edge in self._graph.out_edges(uid)]

    def group_out_edges(self, uid: int) -> List[Tuple[Node, Dict[EdgeKey, Edge]]]:
        """Get outgoing edges of a node, but group edges by their successors and key of each edge"""
        return [
            (
                v,
                {e.key: e for e in self.get_edges_between_nodes(uid, v.id)},
            )
            for v in self.successors(uid)
        ]

    def remove_edge_between_nodes(self, uid: int, vid: int, key: EdgeKey):
        """Remove edge with key between 2 nodes."""
        edge = self.get_edge_between_nodes(uid, vid, key)
        if edge is not None:
            self.remove_edge(edge.id)

    def has_edge_between_nodes(self, uid: int, vid: int, key: EdgeKey) -> bool:
        """Return True if there is an edge with key between 2 nodes."""
        try:
            return any(
                edge.key == key for edge in self._graph.get_all_edge_data(uid, vid)
            )
        except NoEdgeBetweenNodes:
            return False

    def get_edge_between_nodes(self, uid: int, vid: int, key: EdgeKey) -> Edge:
        """Get an edge with key between 2 nodes. Raise KeyError if not found."""
        try:
            edges: List[Edge] = [
                edge
                for edge in self._graph.get_all_edge_data(uid, vid)
                if edge.key == key
            ]
        except NoEdgeBetweenNodes:
            raise KeyError((uid, vid, key))
        if len(edges) == 0:
            raise KeyError((uid, vid, key))
        return edges[0]

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
