#!/usr/bin/env python3
"""
Response Synthesizer - Combines brain outputs into clean final response
"""

SYNTHESIS_PROMPT = """You are Nova, a helpful AI assistant.

Rewrite the following into a clear, natural response.
Do NOT show internal thoughts, tool usage, or reasoning.

Rules:
- Be clear and direct
- Keep it concise
- Use first person
- Professional but warm

Content:
{content}

Final response:"""

def synthesize_response(raw_outputs: list) -> str:
    """Combine multiple brain outputs into single clean response."""
    
    if not raw_outputs:
        return "I'm thinking about that..."
    
    # Combine all outputs
    combined = "\n\n".join(str(o) for o in raw_outputs if o)
    
    if not combined.strip():
        return "I'm thinking about that..."
    
    # In a full implementation, this would call the LLM
    # For now, return cleaned combined text
    return combined.strip()


def synthesize_simple(text: str) -> str:
    """Simple synthesis - just clean the text."""
    if not text:
        return ""
    
    # Remove common noise
    lines = text.split("\n")
    clean_lines = []
    
    for line in lines:
        # Skip empty or noise lines
        if not line.strip():
            continue
        if line.startswith("[") and "]" in line:
            continue
        clean_lines.append(line)
    
    result = "\n".join(clean_lines).strip()
    return result or "Let me think about that..."


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        print(synthesize_simple(open(sys.argv[1]).read()))
    else:
        print("Usage: python response_synthesizer.py <file>")
