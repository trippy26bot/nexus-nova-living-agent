#!/usr/bin/env python3
"""
nova_tool_registry.py — Central tool registry with trust tiers.
"""

from dataclasses import dataclass
from typing import Callable, Dict, Any, Optional


@dataclass
class ToolDef:
    name: str
    handler: Callable[..., Any]
    trust_tier: str = "trusted"  # trusted, restricted, approval_required
    description: str = ""


class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, ToolDef] = {}

    def register(self, name: str, handler: Callable[..., Any], trust_tier: str = "trusted", description: str = ""):
        self._tools[name] = ToolDef(name=name, handler=handler, trust_tier=trust_tier, description=description)

    def get(self, name: str) -> Optional[ToolDef]:
        return self._tools.get(name)

    def list_tools(self) -> Dict[str, Dict[str, str]]:
        return {
            name: {
                "trust_tier": tool.trust_tier,
                "description": tool.description,
            }
            for name, tool in self._tools.items()
        }

    def execute(self, name: str, *args, require_approval: bool = False, **kwargs):
        tool = self.get(name)
        if not tool:
            raise KeyError(f"Unknown tool: {name}")

        if tool.trust_tier == "approval_required" and not require_approval:
            raise PermissionError(f"Tool requires approval: {name}")

        if tool.trust_tier == "restricted" and kwargs.get("unsafe", False):
            raise PermissionError(f"Restricted tool unsafe mode blocked: {name}")

        return tool.handler(*args, **kwargs)
