from typing import Dict, Generic, List, Optional, Tuple, TypeVar, Union
from retworkx import NoEdgeBetweenNodes  # type: ignore
from graph.retworkx.canonical import (
    RetworkXMultiDiGraph,
    BaseRichNode,
    BaseRichEdge,
)
from graph.interface import ICanonicalGraph, EdgeKey


Node = TypeVar("Node", bound=BaseRichNode[str])
Edge = TypeVar("Edge", bound=BaseRichEdge[str])


class RetworkXStrCanonicalMultiDiGraph(
    Generic[Node, Edge],
    ICanonicalGraph[str, str, Node, Edge],
    RetworkXMultiDiGraph[Node, Edge],
):
    def __init__(self, check_cycle: bool = False, multigraph: bool = True):
        super().__init__(check_cycle, multigraph)
        # mapping from string id to integer id
        self.idmap: Dict[str, int] = {}

    def successors(self, nid: str) -> List[Node]:
        """Get the successors of a node"""
        return self._graph.successors(self.idmap[nid])

    def predecessors(self, nid: str) -> List[Node]:
        """Get the predecessors of a node"""
        return self._graph.predecessors(self.idmap[nid])

    def add_node(self, node: Node) -> str:
        """Add a new node to the graph."""
        nid = self._graph.add_node(node)
        self.idmap[node.id] = nid
        return node.id

    def add_edge(self, edge: Edge) -> int:
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
        uid = self.idmap[edge.source]
        vid = self.idmap[edge.target]
        try:
            edges: List[Edge] = [
                e for e in self._graph.get_all_edge_data(uid, vid) if e.key == edge.key
            ]
            if len(edges) > 0:
                # duplicated edges
                return edges[0].id
        except (NoEdgeBetweenNodes, KeyError):
            pass
        edge.id = self._graph.add_edge(uid, vid, edge)
        return edge.id

    def remove_node(self, nid: str):
        """Remove a node from the graph. If the node is not present in the graph it will be ignored and this function will have no effect."""
        return self._graph.remove_node(self.idmap.pop(nid))

    def update_node(self, node: Node):
        """Update the node data inplace"""
        self._graph[self.idmap[node.id]] = node

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

    def remove_edges_between_nodes(self, uid: str, vid: str):
        """Remove edges between 2 nodes."""
        super().remove_edges_between_nodes(self.idmap[uid], self.idmap[vid])

    def has_node(self, nid: str) -> bool:
        """Check if a node with given id exists in the graph"""
        return nid in self.idmap

    def get_node(self, nid: str) -> Node:
        """Get the node by id"""
        return self._graph.get_node_data(self.idmap[nid])

    def has_edges_between_nodes(self, uid: str, vid: str) -> bool:
        """Return True if there is an edge between 2 nodes."""
        return self._graph.has_edge(self.idmap[uid], self.idmap[vid])

    def get_edges_between_nodes(self, uid: str, vid: str) -> List[Edge]:
        """Return the edge data for all the edges between 2 nodes."""
        try:
            return self._graph.get_all_edge_data(self.idmap[uid], self.idmap[vid])
        except (NoEdgeBetweenNodes, KeyError):
            return []

    def degree(self, nid: str) -> int:
        """Get the degree of a node"""
        _nid = self.idmap[nid]
        return self._graph.in_degree(_nid) + self._graph.out_degree(_nid)

    def in_degree(self, nid: str) -> int:
        """Get the degree of a node for inbound edges."""
        return self._graph.in_degree(self.idmap[nid])

    def in_edges(self, vid: str) -> List[Edge]:
        """Get incoming edges of a node. Return a list of tuples of (source id, edge data)"""
        return [edge for uid, _, edge in self._graph.in_edges(self.idmap[vid])]

    def group_in_edges(self, vid: str) -> List[Tuple[Node, Dict[EdgeKey, Edge]]]:
        """Get incoming edges of a node, but group edges by their predecessors and key of each edge"""
        return [
            (
                u,
                {
                    e.key: e  # type: ignore
                    for e in self.get_edges_between_nodes(u.id, vid)
                },
            )
            for u in self.predecessors(vid)
        ]

    def out_degree(self, nid: str) -> int:
        """Get the degree of a node for outbound edges."""
        return self._graph.out_degree(self.idmap[nid])

    def out_edges(self, uid: str) -> List[Edge]:
        """Get outgoing edges of a node. Return a list of tuples of (target id, edge data)"""
        return [edge for _, vid, edge in self._graph.out_edges(self.idmap[uid])]

    def group_out_edges(self, uid: str) -> List[Tuple[Node, Dict[EdgeKey, Edge]]]:
        """Get outgoing edges of a node, but group edges by their successors and key of each edge"""
        return [
            (
                v,
                {
                    e.key: e  # type: ignore
                    for e in self.get_edges_between_nodes(uid, v.id)
                },
            )
            for v in self.successors(uid)
        ]

    def remove_edge_between_nodes(self, uid: str, vid: str, key: EdgeKey):
        """Remove edge with key between 2 nodes."""
        edge = self.get_edge_between_nodes(uid, vid, key)
        if edge is not None:
            self.remove_edge(edge.id)

    def has_edge_between_nodes(self, uid: str, vid: str, key: EdgeKey) -> bool:
        """Return True if there is an edge with key between 2 nodes."""
        try:
            return any(
                edge.key == key
                for edge in self._graph.get_all_edge_data(
                    self.idmap[uid], self.idmap[vid]
                )
            )
        except (NoEdgeBetweenNodes, KeyError):
            return False

    def get_edge_between_nodes(self, uid: str, vid: str, key: EdgeKey) -> Edge:
        """Get an edge with key between 2 nodes. Raise KeyError if not found."""
        try:
            edges: List[Edge] = [
                edge
                for edge in self._graph.get_all_edge_data(
                    self.idmap[uid], self.idmap[vid]
                )
                if edge.key == key
            ]
        except NoEdgeBetweenNodes:
            raise KeyError((uid, vid, key))
        if len(edges) == 0:
            raise KeyError((uid, vid, key))
        return edges[0]

    def check_integrity(self) -> bool:
        """Check if ids/refs in the graph are consistent"""
        if self.num_nodes() != len(self.idmap):
            return False
        for nid in self._graph.node_indexes():
            node = self._graph[nid]
            if self.idmap.get(node.id, None) != nid:
                return False
        for eid, (uid, vid, edge) in self._graph.edge_index_map().items():
            if (
                edge.id != eid
                or self.idmap[edge.source] != uid
                or self.idmap[edge.target] != vid
            ):
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
