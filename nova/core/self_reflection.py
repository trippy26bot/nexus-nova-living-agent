#!/usr/bin/env python3
"""
Self-Reflection Layer - Quality control before output
"""

class SelfReflection:
    """Reviews responses before sending to user"""
    
    def __init__(self):
        self.reflection_history = []
        
    def reflect(self, response: str, context: dict = None) -> dict:
        """Review a response for quality issues"""
        issues = []
        suggestions = []
        
        # Check length
        if len(response) < 5:
            issues.append("response_too_short")
            suggestions.append("Expand the response")
        
        if len(response) > 5000:
            issues.append("response_too_long")
            suggestions.append("Consider shortening")
        
        # Check for errors
        if "error" in response.lower() and "404" not in response:
            issues.append("contains_error_mention")
        
        # Check for empty
        if not response.strip():
            issues.append("empty_response")
            suggestions.append("Provide a substantive response")
        
        # Check for repetition
        words = response.lower().split()
        if len(words) > 10:
            unique_ratio = len(set(words)) / len(words)
            if unique_ratio < 0.3:
                issues.append("high_repetition")
                suggestions.append("Reduce word repetition")
        
        result = {
            "passed": len(issues) == 0,
            "issues": issues,
            "suggestions": suggestions,
            "response_length": len(response)
        }
        
        self.reflection_history.append(result)
        return result
    
    def get_history(self, limit: int = 10):
        return self.reflection_history[-limit:]
    
    def clear_history(self):
        self.reflection_history = []


# Global instance
_reflection = SelfReflection()

def get_reflection():
    return _reflection
