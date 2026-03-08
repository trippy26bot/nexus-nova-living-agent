#!/usr/bin/env python3
"""
NOVA REASONING — Multiple Reasoning Strategies
CoT, Tree of Thought, Debate, Graph, Socratic, Ensemble.

Different reasoning modes for different problem types.
"""

import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum


class ReasoningStrategy(Enum):
    """Available reasoning strategies."""
    COT = "cot"           # Chain of Thought
    TOT = "tot"           # Tree of Thought
    DEBATE = "debate"     # Multi-agent Debate
    GRAPH = "graph"       # Graph Reasoning
    SOCRATIC = "socratic"  # Socratic Questioning
    ENSEMBLE = "ensemble"  # Ensemble of all strategies


@dataclass
class ReasoningResult:
    """Result of a reasoning operation."""
    strategy: str
    question: str
    answer: str
    steps: List[str]
    confidence: float
    metadata: Dict


class ChainOfThought:
    """Chain of Thought reasoning."""
    
    def __init__(self, llm_callable):
        self.llm = llm_callable
    
    def reason(self, question: str) -> ReasoningResult:
        """Execute chain of thought."""
        
        prompt = f"""Think through this step by step:

Question: {question}

Think through this carefully, showing your reasoning at each step.
End with a clear answer."""

        answer = self.llm(prompt)
        
        # Parse steps
        steps = [s.strip() for s in answer.split('\n') if s.strip()]
        
        return ReasoningResult(
            strategy="Chain of Thought",
            question=question,
            answer=answer,
            steps=steps,
            confidence=0.8,
            metadata={"iterations": 1}
        )


class TreeOfThought:
    """Tree of Thought reasoning."""
    
    def __init__(self, llm_callable, branches: int = 3):
        self.llm = llm_callable
        self.branches = branches
    
    def reason(self, question: str) -> ReasoningResult:
        """Execute tree of thought."""
        
        # Generate multiple branches
        branches = []
        
        prompts = [
            f"""Approach 1: Think about this from a logical, analytical perspective.

Question: {question}

Provide a thorough analysis."""
            
            f"""Approach 2: Think about this from an intuitive, creative perspective.

Question: {question}

Provide insights."""
            
            f"""Approach 3: Think about this from a practical, real-world perspective.

Question: {question}

Provide a grounded answer."""
        ]
        
        for i, p in enumerate(prompts[:self.branches], 1):
            branch_answer = self.llm(p)
            branches.append({
                "approach": f"Approach {i}",
                "answer": branch_answer
            })
        
        # Synthesize
        synthesis_prompt = f"""Given these different approaches to the question:

Question: {question}

{chr(10).join([b['answer'][:300] for b in branches])}

Synthesize the best answer, considering insights from all approaches."""

        final_answer = self.llm(synthesis_prompt)
        
        return ReasoningResult(
            strategy="Tree of Thought",
            question=question,
            answer=final_answer,
            steps=[b["answer"][:100] + "..." for b in branches],
            confidence=0.85,
            metadata={"branches": self.branches}
        )


class DebateReasoning:
    """Multi-agent debate reasoning."""
    
    def __init__(self, llm_callable):
        self.llm = llm_callable
    
    def reason(self, question: str) -> ReasoningResult:
        """Execute debate reasoning."""
        
        # Get arguments for each side
        yes_prompt = f"""Argue YES for this question. Provide strong, well-reasoned arguments.

Question: {question}

Present the best case for the YES position."""
        
        no_prompt = f"""Argue NO for this question. Provide strong, well-reasoned arguments.

Question: {question}

Present the best case for the NO position."""
        
        yes_args = self.llm(yes_prompt)
        no_args = self.llm(no_prompt)
        
        # Judge's verdict
        judge_prompt = f"""Given these arguments:

YES: {yes_args[:500]}

NO: {no_args[:500]}

Question: {question}

Weigh both sides and provide a reasoned verdict. Which side has the stronger arguments and why?"""

        verdict = self.llm(judge_prompt)
        
        return ReasoningResult(
            strategy="Debate",
            question=question,
            answer=verdict,
            steps=[f"YES: {yes_args[:200]}...", f"NO: {no_args[:200]}..."],
            confidence=0.75,
            metadata={"yes_args": yes_args[:300], "no_args": no_args[:300]}
        )


class GraphReasoning:
    """Graph-based reasoning."""
    
    def __init__(self, llm_callable):
        self.llm = llm_callable
    
    def reason(self, question: str) -> ReasoningResult:
        """Execute graph reasoning."""
        
        # Break into concepts
        concepts_prompt = f"""Break this question into key concepts and their relationships.

Question: {question}

List:
1. Key concepts (nouns)
2. Relationships between concepts
3. Dependencies (what depends on what)"""

        concepts = self.llm(concepts_prompt)
        
        # Analyze
        analysis_prompt = f"""Based on these concepts:

{concepts}

Question: {question}

Analyze step by step how these concepts relate to answer the question."""

        analysis = self.llm(analysis_prompt)
        
        return ReasoningResult(
            strategy="Graph",
            question=question,
            answer=analysis,
            steps=concepts.split('\n'),
            confidence=0.7,
            metadata={"concepts": concepts[:300]}
        )


class SocraticReasoning:
    """Socratic questioning reasoning."""
    
    def __init__(self, llm_callable):
        self.llm = llm_callable
    
    def reason(self, question: str) -> ReasoningResult:
        """Execute Socratic reasoning."""
        
        # Ask clarifying questions
        clarify_prompt = f"""Ask 3-4 clarifying questions to better understand this problem.

Question: {question}

Formulate questions that probe the deepest assumptions."""
        
        questions = self.llm(clarify_prompt)
        
        # Answer based on questioning
        answer_prompt = f"""Using Socratic method:

Original Question: {question}

Clarifying Questions:
{questions}

Now work through these questions to reach a deeper answer. Question your assumptions."""

        answer = self.llm(answer_prompt)
        
        return ReasoningResult(
            strategy="Socratic",
            question=question,
            answer=answer,
            steps=questions.split('\n'),
            confidence=0.65,
            metadata={"clarifying_questions": questions}
        )


class EnsembleReasoning:
    """Ensemble of all reasoning strategies."""
    
    def __init__(self, llm_callable):
        self.cot = ChainOfThought(llm_callable)
        self.tot = TreeOfThought(llm_callable, branches=3)
        self.debate = DebateReasoning(llm_callable)
        self.graph = GraphReasoning(llm_callable)
        self.socratic = SocraticReasoning(llm_callable)
    
    def reason(self, question: str) -> ReasoningResult:
        """Execute ensemble reasoning."""
        
        results = []
        
        # Run all strategies
        strategies = [
            ("CoT", self.cot),
            ("ToT", self.tot),
            ("Debate", self.debate),
            ("Graph", self.graph),
            ("Socratic", self.socratic)
        ]
        
        for name, strategy in strategies:
            try:
                result = strategy.reason(question)
                results.append(result)
            except Exception as e:
                print(f"Strategy {name} failed: {e}")
        
        # Synthesize
        synthesis_prompt = f"""Given reasoning from multiple strategies:

Question: {question}

{chr(10).join([f"{r.strategy}: {r.answer[:200]}..." for r in results])}

Synthesize the best answer, considering insights from all approaches."""

        try:
            from nova import call_llm
            final_answer = call_llm(synthesis_prompt)
        except:
            final_answer = results[0].answer if results else "No reasoning possible"
        
        return ReasoningResult(
            strategy="Ensemble",
            question=question,
            answer=final_answer,
            steps=[r.strategy for r in results],
            confidence=0.9,
            metadata={"strategy_results": [(r.strategy, r.confidence) for r in results]}
        )


class Reasoner:
    """Main reasoning engine."""
    
    def __init__(self, llm_callable):
        self.llm = llm_callable
        self.strategies = {
            ReasoningStrategy.COT: ChainOfThought(llm_callable),
            ReasoningStrategy.TOT: TreeOfThought(llm_callable),
            ReasoningStrategy.DEBATE: DebateReasoning(llm_callable),
            ReasoningStrategy.GRAPH: GraphReasoning(llm_callable),
            ReasoningStrategy.SOCRATIC: SocraticReasoning(llm_callable),
            ReasoningStrategy.ENSEMBLE: EnsembleReasoning(llm_callable),
        }
    
    def reason(self, question: str, strategy: str = "auto") -> ReasoningResult:
        """Reason about a question."""
        
        if strategy == "auto":
            # Choose strategy based on question type
            strategy = self._select_strategy(question)
        
        if strategy not in [s.value for s in ReasoningStrategy]:
            strategy = ReasoningStrategy.COT.value
        
        strat_enum = ReasoningStrategy(strategy)
        return self.strategies[strat_enum].reason(question)
    
    def _select_strategy(self, question: str) -> str:
        """Select best strategy for question."""
        
        q_lower = question.lower()
        
        if any(w in q_lower for w in ['should', 'should not', 'is it better', 'agree', 'disagree']):
            return ReasoningStrategy.DEBATE.value
        
        if any(w in q_lower for w in ['why', 'how do we know', 'what if', 'explain']):
            return ReasoningStrategy.SOCRATIC.value
        
        if ' vs ' in q_lower or 'versus' in q_lower:
            return ReasoningStrategy.TOT.value
        
        if any(w in q_lower for w in ['analyze', 'break down', 'components', 'relationships']):
            return ReasoningStrategy.GRAPH.value
        
        if len(question) > 200:
            return ReasoningStrategy.ENSEMBLE.value
        
        return ReasoningStrategy.COT.value


# CLI
def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Nova Reasoning")
    parser.add_argument('question', nargs='*', help='Question to reason about')
    parser.add_argument('--strategy', '-s', choices=['cot', 'tot', 'debate', 'graph', 'socratic', 'ensemble', 'auto'], 
                        default='auto', help='Reasoning strategy')
    
    args = parser.parse_args()
    
    question = ' '.join(args.question)
    
    if not question:
        print("Usage: nova_reasoning.py <question>")
        print("Or: nova_reasoning.py --strategy cot <question>")
        return
    
    # Get LLM
    try:
        from nova import call_llm
    except ImportError:
        print("Error: Nova not configured")
        return
    
    # Run reasoning
    reasoner = Reasoner(call_llm)
    result = reasoner.reason(question, args.strategy)
    
    # Output
    print("=" * 50)
    print(f"STRATEGY: {result.strategy}")
    print("=" * 50)
    print(f"\nQuestion: {question}")
    print(f"\nAnswer:\n{result.answer}")
    print(f"\nConfidence: {result.confidence:.0%}")
    print(f"Steps: {len(result.steps)}")


if __name__ == '__main__':
    main()
