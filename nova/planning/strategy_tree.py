#!/usr/bin/env python3
"""
Nova Strategic Planning Tree
Tree search for better decision making
"""

from typing import Dict, List, Any, Optional
import random

class PlanNode:
    """A node in the planning tree"""
    
    def __init__(self, name: str, value: float = 0.0, parent=None):
        self.name = name
        self.value = value
        self.parent = parent
        self.children = []
    
    def add_child(self, child):
        child.parent = self
        self.children.append(child)
    
    def get_path(self) -> List[str]:
        """Get path from root to this node"""
        path = [self.name]
        node = self.parent
        while node:
            path.insert(0, node.name)
            node = node.parent
        return path


class StrategyTree:
    """
    Tree search for strategic planning.
    Nova can explore multiple futures.
    """
    
    def __init__(self, root_name: str = "goal"):
        self.root = PlanNode(root_name)
        self.current = self.root
        self.max_depth = 5
    
    def add_option(self, name: str, predicted_value: float = 0.5):
        """Add an option to current node"""
        if self._depth() < self.max_depth:
            child = PlanNode(name, predicted_value, self.current)
            self.current.add_child(child)
            return child
        return None
    
    def _depth(self, node=None) -> int:
        """Get depth of tree"""
        if node is None:
            node = self.current
        if not node.children:
            return 1
        return 1 + max(self._depth(c) for c in node.children)
    
    def simulate(self, path: List[str]) -> float:
        """Simulate a path and get predicted value"""
        node = self.root
        total = node.value
        
        for step in path:
            found = False
            for child in node.children:
                if child.name == step:
                    node = child
                    total += child.value
                    found = True
                    break
            if not found:
                return 0.0
        
        return total
    
    def choose_best(self) -> str:
        """Choose best option from current node"""
        if not self.current.children:
            return None
        
        best = max(self.current.children, key=lambda c: c.value)
        return best.name
    
    def get_all_options(self) -> List[Dict]:
        """Get all options from current node"""
        return [{"name": c.name, "value": c.value} for c in self.current.children]
    
    def move_to(self, option: str) -> bool:
        """Move to a child option"""
        for child in self.current.children:
            if child.name == option:
                self.current = child
                return True
        return False
    
    def backtrack(self):
        """Move back to parent"""
        if self.current.parent:
            self.current = self.current.parent


# Global instance
_strategy_tree = None

def get_strategy_tree() -> StrategyTree:
    global _strategy_tree
    if _strategy_tree is None:
        _strategy_tree = StrategyTree()
    return _strategy_tree
