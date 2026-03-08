"""
Nexus Nova Core Package

Memory systems, knowledge graphs, and world modeling for living agents.
"""

from .knowledge_graph import KnowledgeGraph
from .world_model import WorldModel

__version__ = "2.0.0"

__all__ = [
    "KnowledgeGraph",
    "WorldModel",
]
