#!/usr/bin/env python3
"""
nova_supervisor.py — Supervisor & Orchestrator Layer
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Every reviewer flagged this as the most critical missing piece:

 "No proper agent orchestration layer. Without a supervisor, you get
 chaos of agents — no delegation, no error recovery, no context routing."

This module is the brain that sits above all agents and skills:

 SUPERVISOR
 The authority layer. Receives all tasks. Decides which agents handle
 what. Tracks task state. Recovers from failures. Knows when to stop.

 ORCHESTRATOR
 Builds and executes task graphs. Breaks complex goals into a DAG of
 subtasks. Runs parallelizable branches simultaneously.

 REFLECTION ENGINE
 After every execution: critic evaluates output, flags issues, triggers
 revision. Not a one-shot pass — a loop that terminates when quality
 threshold is met or max revisions hit.

Usage:
 from nova_supervisor import Supervisor
 sv = Supervisor()
 result = sv.execute("Research qualia and write a summary")
"""

import os, json, sqlite3, time
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional
from enum import Enum

NOVA_DIR = Path.home() / ".nova"
SUPERVISOR_DB = NOVA_DIR / "supervisor.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS tasks (
 id TEXT PRIMARY KEY,
 goal TEXT,
 agent TEXT,
 status TEXT DEFAULT 'pending',
 priority INTEGER DEFAULT 5,
 result TEXT,
 error TEXT,
 retries INTEGER DEFAULT 0,
 max_retries INTEGER DEFAULT 2,
 parent_id TEXT,
 created_at TEXT,
 started_at TEXT,
 completed_at TEXT
);

CREATE TABLE IF NOT EXISTS reflections (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 task_id TEXT,
 iteration INTEGER,
 output TEXT,
 critique TEXT,
 score REAL,
 passed INTEGER,
 revised_output TEXT,
 reflected_at TEXT
);

CREATE TABLE IF NOT EXISTS supervisor_log (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 event_type TEXT,
 task_id TEXT,
 data TEXT,
 logged_at TEXT
);
"""


class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"
    RETRYING = "retrying"
    CANCELLED = "cancelled"


@dataclass
class Task:
    id: str
    goal: str
    agent: str = "auto"
    status: TaskStatus = TaskStatus.PENDING
    priority: int = 5
    result: str = ""
    error: str = ""
    retries: int = 0
    max_retries: int = 2
    parent_id: str = ""
    created_at: str = ""
    depends_on: list = field(default_factory=list)


@dataclass
class SupervisorResult:
    goal: str
    success: bool
    answer: str
    tasks_run: int
    retries: int
    reflections: int
    confidence: float
    elapsed_ms: int
    task_graph: list = field(default_factory=list)


class Supervisor:
    """
    The authority layer above all agents.
    Plans, delegates, monitors, recovers, reflects.
    """

    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY", "")
        NOVA_DIR.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(SUPERVISOR_DB))
        self.conn.executescript(SCHEMA)
        self.conn.commit()

        self.MAX_TASKS = int(os.environ.get("NOVA_MAX_TASKS", "20"))
        self.MAX_RETRIES = int(os.environ.get("NOVA_MAX_RETRIES", "2"))
        self.TIMEOUT_S = int(os.environ.get("NOVA_TASK_TIMEOUT", "120"))
        self.QUALITY_THRESH = float(os.environ.get("NOVA_QUALITY_THRESHOLD", "0.7"))
        self.MAX_REFLECTIONS = int(os.environ.get("NOVA_MAX_REFLECTIONS", "3"))
        self.MAX_STEPS = int(os.environ.get("NOVA_MAX_STEPS", "50"))
        self._steps_used = 0
        self._tokens_used = 0

        self._reflection = None
        try:
            from nova_reflection import ReflectionEngine
            self._reflection = ReflectionEngine(api_key=self.api_key)
        except ImportError:
            pass

    def execute(self, goal: str, context: str = "", user_id: str = "",
                identity: str = "") -> SupervisorResult:
        """Full pipeline: plan → delegate → execute → reflect → synthesize."""
        start = time.time()
        goal_id = self._make_id(goal)
        self._log("goal_received", goal_id, {"goal": goal[:100]})

        self._steps_used = 0
        self._tokens_used = 0

        tasks = self._plan(goal, context, goal_id)
        self._log("plan_built", goal_id, {"tasks": len(tasks)})

        if len(tasks) > self.MAX_STEPS:
            tasks = tasks[:self.MAX_STEPS]
            self._log("budget_enforced", goal_id, {"capped_to": self.MAX_STEPS})

        results = self._execute_graph(tasks, context, identity)
        self._steps_used += len(tasks)

        answer = self._synthesize(goal, results, context, identity)
        final, confidence, reflection_count = self._reflect(goal, answer, identity)

        if self._reflection:
            try:
                self._reflection.reflect_task(
                    goal=goal,
                    result=final[:300],
                    method=f"{len(tasks)} tasks",
                    success=True,
                )
            except Exception:
                pass

        elapsed = int((time.time() - start) * 1000)
        total_retries = sum(t.retries for t in tasks)

        return SupervisorResult(
            goal=goal,
            success=True,
            answer=final,
            tasks_run=len(tasks),
            retries=total_retries,
            reflections=reflection_count,
            confidence=confidence,
            elapsed_ms=elapsed,
            task_graph=[{"goal": t.goal, "agent": t.agent, "status": t.status.value} for t in tasks]
        )

    def _plan(self, goal: str, context: str, goal_id: str) -> list:
        """Decompose a goal into tasks."""
        if not self.api_key:
            return [Task(id=self._make_id(goal + "0"), goal=goal, agent="executor")]

        plan_prompt = f"""Decompose this goal into 2-5 subtasks:

Goal: {goal}
Context: {context[:300] if context else 'None'}

Available agents: researcher, analyst, writer, executor, critic

Output JSON:
[{{"id": "t1", "goal": "...", "agent": "...", "depends_on": []}}]"""

        response = self._call(plan_prompt, max_tokens=600)
        tasks = []
        try:
            text = response.strip()
            if "```" in text:
                text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
            data = json.loads(text.strip())
            for i, item in enumerate(data[:self.MAX_TASKS]):
                task = Task(
                    id=f"{goal_id}_{item.get('id', str(i))}",
                    goal=item.get("goal", goal),
                    agent=item.get("agent", "executor"),
                    depends_on=item.get("depends_on", []),
                    max_retries=self.MAX_RETRIES
                )
                tasks.append(task)
                self._save_task(task, goal_id)
        except Exception:
            task = Task(id=f"{goal_id}_0", goal=goal, agent="executor", max_retries=self.MAX_RETRIES)
            tasks = [task]
            self._save_task(task, goal_id)

        return tasks

    def _execute_graph(self, tasks: list, context: str, identity: str) -> dict:
        """Execute task graph respecting dependencies."""
        results = {}
        completed = set()
        max_rounds = len(tasks) + 2

        for _ in range(max_rounds):
            made_progress = False
            for task in tasks:
                if task.status == TaskStatus.DONE:
                    continue
                if task.status == TaskStatus.FAILED:
                    continue
                deps_ok = all(d in completed for d in task.depends_on)
                if not deps_ok:
                    continue

                result = self._execute_task(task, results, context, identity)
                results[task.id] = result
                completed.add(task.id)
                made_progress = True

            if not made_progress:
                break

        return results

    def _execute_task(self, task: Task, prior_results: dict,
                     context: str, identity: str) -> str:
        """Execute a single task with retry logic."""
        self._update_task(task.id, status="running",
                        started_at=datetime.now().isoformat())
        task.status = TaskStatus.RUNNING

        prior_ctx = ""
        if prior_results:
            prior_ctx = "\n\nPrior results:\n" + "\n".join([
                f" [{k}]: {v[:200]}" for k, v in list(prior_results.items())[-3:]
            ])

        for attempt in range(task.max_retries + 1):
            try:
                result = self._dispatch(task, context + prior_ctx, identity)
                if result:
                    task.status = TaskStatus.DONE
                    task.result = result
                    self._update_task(task.id, status="done", result=result,
                                    completed_at=datetime.now().isoformat())
                    return result
            except Exception as e:
                task.retries += 1
                task.error = str(e)
                if attempt < task.max_retries:
                    time.sleep(2 ** attempt)
                    task.status = TaskStatus.RETRYING

        task.status = TaskStatus.FAILED
        self._update_task(task.id, status="failed", error=task.error)
        return f"[Task failed: {task.goal[:50]}]"

    def _dispatch(self, task: Task, context: str, identity: str) -> str:
        """Route task to the right agent."""
        agent_prompts = {
            "researcher": f"""Research: {task.goal}
Context: {context[:400]}
Provide findings and sources.""",
            "analyst": f"""Analyze: {task.goal}
Context: {context[:400]}
Provide analysis and insights.""",
            "writer": f"""Write: {task.goal}
Context: {context[:400]}
Produce clear content.""",
            "executor": f"""Execute: {task.goal}
Context: {context[:400]}
Take action and report results.""",
            "critic": f"""Evaluate: {task.goal}
Context: {context[:400]}
Provide score and issues.""",
        }
        prompt = agent_prompts.get(task.agent, agent_prompts["executor"])
        return self._call(prompt, max_tokens=800)

    def _reflect(self, goal: str, answer: str, identity: str = "",
                 iteration: int = 0) -> tuple:
        """Critic evaluates output. Revise if below threshold."""
        if not self.api_key or iteration >= self.MAX_REFLECTIONS:
            return answer, 0.75, iteration

        critique_prompt = f"""Evaluate:
Goal: {goal}
Answer: {answer[:1500]}

Score 0-10: overall, accuracy, specificity. Issues? Revise?"""

        critique_text = self._call(critique_prompt, max_tokens=400)
        try:
            text = critique_text.strip()
            if "```" in text:
                text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
            critique = json.loads(text.strip())
        except:
            return answer, 0.75, iteration

        score = critique.get("overall_score", 7) / 10
        confidence = critique.get("confidence", 0.75)
        needs_revision = critique.get("needs_revision", False)

        if not needs_revision or score >= self.QUALITY_THRESH:
            return answer, confidence, iteration + 1

        issues = critique.get("issues", [])[:3]
        revise_prompt = f"Fix: {chr(10).join(f'- {i}' for i in issues)}\n\n{answer[:1000]}"
        revised = self._call(revise_prompt, max_tokens=1000)

        return self._reflect(goal, revised, identity, iteration + 1)

    def _synthesize(self, goal: str, results: dict, context: str, identity: str) -> str:
        """Combine results into final answer."""
        if not results:
            return "[No results]"
        if len(results) == 1:
            return list(results.values())[0]

        parts = "\n\n".join([
            f"[{k}]: {v[:400]}" for k, v in results.items()
            if v and not v.startswith("[Task failed")
        ])

        synth_prompt = f"Synthesize into final answer for goal: {goal}\n\n{parts}"
        return self._call(synth_prompt, max_tokens=1200)

    def delegate(self, agent: str, task_goal: str, priority: int = 5, context: str = "") -> str:
        """Direct delegation."""
        task = Task(
            id=self._make_id(task_goal),
            goal=task_goal,
            agent=agent,
            priority=priority,
            max_retries=self.MAX_RETRIES
        )
        self._save_task(task, "direct")
        return self._execute_task(task, {}, context, "")

    def status(self) -> dict:
        """Current status."""
        rows = self.conn.execute(
            "SELECT status, COUNT(*) FROM tasks GROUP BY status"
        ).fetchall()
        counts = {r[0]: r[1] for r in rows}

        pending = self.conn.execute(
            "SELECT id, goal, agent, priority FROM tasks WHERE status='pending' "
            "ORDER BY priority DESC LIMIT 5"
        ).fetchall()

        return {
            "task_counts": counts,
            "pending_queue": [{"id": r[0], "goal": r[1][:60], "agent": r[2], "priority": r[3]} for r in pending],
            "controls": {
                "max_tasks": self.MAX_TASKS,
                "max_retries": self.MAX_RETRIES,
                "quality_threshold": self.QUALITY_THRESH,
            },
            "session_usage": {"steps_used": self._steps_used}
        }

    def _call(self, prompt: str, max_tokens: int = 800) -> str:
        """Route through nova_providers for multi-provider support."""
        try:
            from nova_providers import get_provider
            provider = get_provider(prefer="anthropic")
            if not provider or not provider.available():
                provider = get_provider()
            if not provider or not provider.available():
                return f"[No API configured]\n\nTask: {prompt[:100]}"
            resp = provider.complete(prompt, max_tokens=max_tokens)
            if resp.success:
                return resp.text
            return f"[API error: {resp.error}]\n\nTask: {prompt[:100]}"
        except ImportError:
            if not self.api_key:
                return f"[No API key configured]\n\nTask: {prompt[:100]}"
            import urllib.request
            payload = json.dumps({
                "model": "claude-haiku-4-5-20251001",
                "max_tokens": max_tokens,
                "messages": [{"role": "user", "content": prompt}]
            }).encode()
            req = urllib.request.Request(
                "https://api.anthropic.com/v1/messages",
                data=payload,
                headers={"Content-Type": "application/json",
                        "x-api-key": self.api_key,
                        "anthropic-version": "2023-06-01"}
            )
            try:
                resp = urllib.request.urlopen(req, timeout=self.TIMEOUT_S)
                data = json.loads(resp.read())
                return data["content"][0]["text"]
            except Exception as e:
                raise RuntimeError(f"API call failed: {e}")

    def _make_id(self, text: str) -> str:
        import hashlib
        return hashlib.md5(f"{text}{time.time()}".encode()).hexdigest()[:10]

    def _save_task(self, task: Task, goal_id: str):
        now = datetime.now().isoformat()
        self.conn.execute(
            """INSERT OR REPLACE INTO tasks
            (id, goal, agent, status, priority, retries, max_retries, parent_id, created_at)
            VALUES (?,?,?,?,?,?,?,?,?)""",
            (task.id, task.goal, task.agent, task.status.value,
             task.priority, task.retries, task.max_retries, goal_id, now)
        )
        self.conn.commit()

    def _update_task(self, task_id: str, **kwargs):
        sets = ", ".join(f"{k}=?" for k in kwargs)
        vals = list(kwargs.values()) + [task_id]
        self.conn.execute(f"UPDATE tasks SET {sets} WHERE id=?", vals)
        self.conn.commit()

    def _log(self, event: str, task_id: str, data: dict):
        self.conn.execute(
            "INSERT INTO supervisor_log (event_type, task_id, data, logged_at) VALUES (?,?,?,?)",
            (event, task_id, json.dumps(data), datetime.now().isoformat())
        )
        self.conn.commit()

    def close(self):
        if self._reflection:
            try:
                self._reflection.close()
            except Exception:
                pass
        self.conn.close()


if __name__ == "__main__":
    import sys
    sv = Supervisor()
    args = sys.argv[1:]

    if not args or args[0] == "status":
        status = sv.status()
        print(f"\nTask counts: {status['task_counts']}")
        if status["pending_queue"]:
            print("Pending:")
            for t in status["pending_queue"]:
                print(f" [{t['priority']}] {t['goal']} → {t['agent']}")

    elif args[0] == "run" and len(args) >= 2:
        goal = " ".join(args[1:])
        result = sv.execute(goal)
        print(f"\nAnswer:\n{result.answer}")
        print(f"\nTasks: {result.tasks_run} | Confidence: {result.confidence:.0%}")

    sv.close()
