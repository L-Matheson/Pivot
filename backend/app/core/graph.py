"""Graph validation utilities for workflow definitions."""

from __future__ import annotations

from collections import defaultdict

from app.schemas.workflow import WorkflowDefinition


def detect_cycles(edges: list[tuple[str, str]]) -> bool:
    """Return True if the directed graph defined by (source, target) pairs contains a cycle."""
    adjacency: dict[str, list[str]] = defaultdict(list)
    for source, target in edges:
        adjacency[source].append(target)

    WHITE, GRAY, BLACK = 0, 1, 2
    color: dict[str, int] = defaultdict(int)

    def dfs(node: str) -> bool:
        color[node] = GRAY
        for neighbor in adjacency[node]:
            if color[neighbor] == GRAY:
                return True
            if color[neighbor] == WHITE and dfs(neighbor):
                return True
        color[node] = BLACK
        return False

    nodes = set()
    for source, target in edges:
        nodes.add(source)
        nodes.add(target)

    return any(color[n] == WHITE and dfs(n) for n in nodes)


def topological_sort(node_ids: list[str], edges: list[tuple[str, str]]) -> list[str]:
    """Return *node_ids* in dependency order (Kahn's algorithm).

    Every id in *node_ids* appears exactly once in the result, including
    nodes with no edges.  The graph must be acyclic — call after
    ``validate_definition`` confirms that.
    """
    in_degree: dict[str, int] = {nid: 0 for nid in node_ids}
    adjacency: dict[str, list[str]] = defaultdict(list)
    for src, tgt in edges:
        adjacency[src].append(tgt)
        in_degree[tgt] = in_degree.get(tgt, 0) + 1

    queue = [nid for nid in node_ids if in_degree[nid] == 0]
    result: list[str] = []
    while queue:
        node = queue.pop(0)
        result.append(node)
        for neighbor in adjacency[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)
    return result


def validate_definition(definition: WorkflowDefinition) -> list[str]:
    """Validate a workflow definition and return a list of error messages (empty if valid)."""
    errors: list[str] = []

    node_ids = [n.id for n in definition.nodes]
    duplicates = [nid for nid in node_ids if node_ids.count(nid) > 1]
    if duplicates:
        errors.append(f"Duplicate node IDs: {', '.join(set(duplicates))}")

    node_id_set = set(node_ids)
    for edge in definition.edges:
        if edge.source not in node_id_set:
            errors.append(f"Edge '{edge.id}' references unknown source node '{edge.source}'")
        if edge.target not in node_id_set:
            errors.append(f"Edge '{edge.id}' references unknown target node '{edge.target}'")

    edge_tuples = [(e.source, e.target) for e in definition.edges]
    if detect_cycles(edge_tuples):
        errors.append("Workflow definition contains a cycle")

    return errors
