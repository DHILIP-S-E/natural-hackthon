"""AURA Agent System — 100+ specialized business logic agents.

Each agent is a self-contained action handler with metadata for discovery,
routing, and orchestration. Organized by the 6 hackathon challenge tracks.

Architecture:
- Each agent file exports an `agent` dict with metadata + a `handler` async function
- Agents are auto-discovered and registered as FastAPI endpoints
- Agents can call other agents via the AgentOrchestrator
"""
from typing import Any, Callable, Coroutine
from dataclasses import dataclass, field


@dataclass
class AgentAction:
    """Single business logic agent/action."""
    name: str
    description: str
    track: str  # "standardization", "staff", "personalization", "trends", "experience", "intelligence"
    feature: str  # e.g. "consultation", "sop", "quality"
    method: str  # "get", "post", "patch", "delete"
    path: str  # API path
    handler: Callable[..., Coroutine[Any, Any, Any]]
    roles: list[str] = field(default_factory=lambda: ["super_admin"])
    ps_codes: list[str] = field(default_factory=list)  # Problem statements addressed e.g. ["PS-01.01"]
    requires_ai: bool = False
    offline_capable: bool = False


# Global agent registry
_AGENTS: list[AgentAction] = []


def register_agent(agent: AgentAction):
    """Register an agent action in the global registry."""
    _AGENTS.append(agent)
    return agent


def get_all_agents() -> list[AgentAction]:
    """Get all registered agents."""
    return _AGENTS


def get_agents_by_track(track: str) -> list[AgentAction]:
    """Get agents filtered by challenge track."""
    return [a for a in _AGENTS if a.track == track]


def get_agents_by_feature(feature: str) -> list[AgentAction]:
    """Get agents filtered by feature."""
    return [a for a in _AGENTS if a.feature == feature]


def get_agents_by_ps(ps_code: str) -> list[AgentAction]:
    """Get agents that address a specific problem statement."""
    return [a for a in _AGENTS if ps_code in a.ps_codes]
