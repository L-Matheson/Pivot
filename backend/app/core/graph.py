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
