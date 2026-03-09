"""
Critic Brain - Deliberation Layer
Evaluates Nova's reasoning and proposes improvements.
"""

class CriticBrain:
    """
    Second-pass thinking layer.
    Evaluates draft outputs and identifies improvements.
    """
    
    def __init__(self):
        self.name = "critic"
        self.confidence_threshold = 0.7
    
    def critique(self, draft_output: str, context: str = "") -> dict:
        """
        Evaluate a draft and provide critique.
        
        Returns:
        {
            "is_sound": bool,
            "confidence": float,
            "issues": list,
            "suggestions": list,
            "improved_version": str
        }
        """
        issues = []
        suggestions = []
        
        # Check for common issues
        if len(draft_output) < 50:
            issues.append("Output too short - may lack depth")
            suggestions.append("Expand analysis with more details")
        
        # Check for uncertainty markers
        uncertain_markers = ["maybe", "perhaps", "might", "could be", "not sure"]
        for marker in uncertain_markers:
            if marker in draft_output.lower():
                suggestions.append(f"Consider being more decisive - found '{marker}'")
        
        # Check for assumptions
        assumption_markers = ["assume", "presumably", "likely"]
        has_assumptions = any(m in draft_output.lower() for m in assumption_markers)
        if has_assumptions:
            issues.append("Contains assumptions that may not hold")
            suggestions.append("Verify assumptions before finalizing")
        
        # Calculate confidence
        issue_count = len(issues)
        if issue_count == 0:
            confidence = 1.0
            is_sound = True
        elif issue_count == 1:
            confidence = 0.8
            is_sound = True
        elif issue_count == 2:
            confidence = 0.6
            is_sound = False
        else:
            confidence = 0.4
            is_sound = False
        
        return {
            "is_sound": is_sound,
            "confidence": confidence,
            "issues": issues,
            "suggestions": suggestions,
            "needs_revision": confidence < self.confidence_threshold
        }
    
    def evaluate_reasoning(self, reasoning_chain: list) -> dict:
        """
        Evaluate a multi-step reasoning chain.
        
        Args:
            reasoning_chain: List of reasoning steps
        """
        issues = []
        
        # Check for logical gaps
        for i, step in enumerate(reasoning_chain):
            if not step.get("conclusion"):
                issues.append(f"Step {i+1} lacks conclusion")
        
        # Check for circular reasoning
        conclusions = [s.get("conclusion", "") for s in reasoning_chain]
        if len(conclusions) != len(set(conclusions)):
            issues.append("Potential circular reasoning detected")
        
        return {
            "is_valid": len(issues) == 0,
            "issues": issues,
            "step_count": len(reasoning_chain)
        }
    
    def evaluate_research(self, research_output: str) -> dict:
        """
        Evaluate research quality.
        """
        issues = []
        suggestions = []
        
        # Check for sources
        if "source" not in research_output.lower() and "http" not in research_output.lower():
            suggestions.append("Add sources for credibility")
        
        # Check for depth
        word_count = len(research_output.split())
        if word_count < 100:
            suggestions.append("Research may lack sufficient depth")
        
        # Check for actionability
        actionable_markers = ["recommend", "suggest", "should", "consider"]
        has_action = any(m in research_output.lower() for m in actionable_markers)
        if not has_action:
            suggestions.append("Add actionable recommendations")
        
        return {
            "quality_score": max(0, 1 - (len(suggestions) * 0.2)),
            "issues": issues,
            "suggestions": suggestions
        }
    
    def evaluate_upgrade(self, proposal: str) -> dict:
        """
        Evaluate an evolution proposal for safety.
        """
        # Protected terms that should not be modified
        protected = ["soul", "identity", "ethics", "user.md", "agents.md"]
        
        issues = []
        warnings = []
        
        # Check for protected file modifications
        proposal_lower = proposal.lower()
        for term in protected:
            if term in proposal_lower:
                issues.append(f"Proposal references protected: {term}")
        
        # Check for risky operations
        risky = ["delete", "remove", "overwrite", "replace all"]
        for term in risky:
            if term in proposal_lower:
                warnings.append(f"Proposal contains risky term: {term}")
        
        return {
            "is_safe": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "approval": "approved" if len(issues) == 0 else "rejected"
        }
