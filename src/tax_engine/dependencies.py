"""Small deterministic dependency graph checks; no tax classifications are inferred."""
from __future__ import annotations
import json
from pathlib import Path


def load_dependencies(path: Path) -> dict:
    graph = json.loads(path.read_text(encoding="utf-8"))["stages"]
    validate_acyclic(graph)
    return graph


def validate_acyclic(graph: dict) -> None:
    visiting, visited = set(), set()

    def visit(node):
        if node in visiting:
            raise ValueError(f"dependency cycle includes {node}")
        if node in visited:
            return
        if node not in graph:
            # Leaf fact prerequisites are named explicitly but are not decision stages.
            return
        visiting.add(node)
        for dep in graph[node].get("depends_on", []):
            visit(dep)
        visiting.remove(node)
        visited.add(node)

    for name in graph:
        visit(name)


def unmet_dependencies(stage: str, graph: dict, states: dict[str, str]) -> list[str]:
    """List prerequisites not explicitly determined; callers must fail closed."""
    if stage not in graph:
        raise KeyError(f"unknown stage: {stage}")
    return [dep for dep in graph[stage].get("depends_on", []) if states.get(dep) != "determined"]
