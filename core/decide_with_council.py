"""
core/decide_with_council.py
Drop-in council-enhanced decision wrapper.
Imported by decide.py when COUNCIL_MODE != "off".
"""
from core.decide import DecisionEngine
from core.council import Council
from core import settings


class DecideWithCouncil(DecisionEngine):
    """
    Wraps DecisionEngine with the 16-brain council.
    Fires the council on high-risk decisions per COUNCIL_MODE settings.
    """

    def __init__(self):
        super().__init__()
        self.council = Council()
        self.risk_threshold = settings.COUNCIL_RISK_THRESHOLD

    def _score_risk(self, decision):
        """Heuristic risk score 0.0–1.0. Override with model-based scoring."""
        if decision is None:
            return 0.0
        risk = 0.1
        if decision.get("action") == "execute":
            risk += 0.2
        for prefix in ("deploy", "delete", "rm", "sudo", "exec", "push", "publish"):
            if decision.get("subtask_id", "").startswith(prefix):
                risk += 0.4
                break
        if decision.get("action") in ("http_request", "send", "post", "put"):
            risk += 0.25
        return min(risk, 1.0)

    def decide(self):
        base = super().decide()

        if settings.COUNCIL_MODE == "off":
            return base

        risk = self._score_risk(base)

        if settings.COUNCIL_MODE == "always" or risk > self.risk_threshold:
            return self.council.decide(base)

        return base
