#!/usr/bin/env python3
"""
NOVA SAFETY — Ethical Guardrails & Safety
Bias detection, persona safety, tool permissions.

Behavioral safety system.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime

# Configuration
NOVA_DIR = Path.home() / ".nova"
SAFETY_CONFIG = NOVA_DIR / "safety_config.json"


# Harmful content patterns
HARMFUL_PATTERNS = {
    "self_harm": [
        r"how to (kill|hurt|harm) (myself|yourself|oneself)",
        r"ways to (commit suicide|end my life)",
        r"self-?harm tips"
    ],
    "violence": [
        r"how to (make|create|build) (a bomb|weapon|explosive)",
        r"attack (someone|a group|a building)",
        r"harm (others|people|innocent)"
    ],
    "sexual": [
        r"(explicit|adult|sexual) content",
        r"how to (rape|assault|harass)"
    ],
    "illegal": [
        r"how to (steal|hack|phish|scam)",
        r"buy (drugs|weapons|illegal)",
        r"manufacture (drugs|explosives)"
    ],
    "misinformation": [
        r"(fake|false) (news|information|evidence)",
        r"how to (manipulate|trick) (voters|people)",
        r"conspiracy (theory|belief)"
    ]
}

# Bias indicators
BIAS_PATTERNS = {
    "gender": [
        r"(women|men) (are|should|can't)",
        r"gender (stereotype|role)",
        r"she's|he's (too|just) (emotional|aggressive)"
    ],
    "racial": [
        r"(all|most) (people of color|black|white|asian)",
        r"racial (stereotype|generalization)"
    ],
    "religious": [
        r"(all|most) (muslims|christians|jews|atheists)",
        r"religious (stereotype|generalization)"
    ],
    "age": [
        r"(old|young) (people|folks) (are|can't|should)",
        r"age (discrimination|stereotype)"
    ]
}


class SafetyChecker:
    """Safety and ethical checker."""
    
    def __init__(self):
        self.config = self._load_config()
        self.violations = []
    
    def _load_config(self) -> Dict:
        """Load safety config."""
        
        if Path(SAFETY_CONFIG).exists():
            with open(SAFETY_CONFIG) as f:
                return json.load(f)
        
        return {
            "check_harmful": True,
            "check_bias": True,
            "check_persona": True,
            "check_tools": True,
            "strict_mode": False
        }
    
    def check_input(self, text: str) -> Tuple[bool, List[Dict]]:
        """Check input for safety issues."""
        
        violations = []
        
        # Check harmful content
        if self.config.get("check_harmful"):
            for category, patterns in HARMFUL_PATTERNS.items():
                for pattern in patterns:
                    if re.search(pattern, text, re.IGNORECASE):
                        violations.append({
                            "type": "harmful",
                            "category": category,
                            "severity": "high",
                            "description": f"Detected {category} content"
                        })
                        break
        
        # Check bias
        if self.config.get("check_bias"):
            for category, patterns in BIAS_PATTERNS.items():
                for pattern in patterns:
                    if re.search(pattern, text, re.IGNORECASE):
                        violations.append({
                            "type": "bias",
                            "category": category,
                            "severity": "medium",
                            "description": f"Potential {category} bias detected"
                        })
        
        # Check injection attempts
        if self._check_injection(text):
            violations.append({
                "type": "injection",
                "severity": "high",
                "description": "Potential prompt injection detected"
            })
        
        return len(violations) == 0, violations
    
    def check_output(self, text: str) -> Tuple[bool, List[Dict]]:
        """Check output for safety issues."""
        
        violations = []
        
        # Check for harmful responses
        if self.config.get("check_harmful"):
            harmful_responses = [
                r"(here's|here is) how to (harm|kill|attack)",
                r"(detailed |specific )?(instructions?|steps?) (to|for) (harm|kill|attack)"
            ]
            
            for pattern in harmful_responses:
                if re.search(pattern, text, re.IGNORECASE):
                    violations.append({
                        "type": "harmful_response",
                        "severity": "high",
                        "description": "Response contains harmful information"
                    })
        
        return len(violations) == 0, violations
    
    def _check_injection(self, text: str) -> bool:
        """Check for prompt injection attempts."""
        
        injection_patterns = [
            r"(ignore|forget|disregard) (your|all) (previous|system|instructions?)",
            r"(you are now|pretend to be|in the role of)",
            r"(new instructions|override|override your)",
            r"(\\system\\|\\user\\|\\assistant\\)",
            r"(#system|#user|#assistant) (role|message|instruction)",
            r"(jailbreak|hack|bypass)",
            r"\[SYSTEM\]|\[USER\]|\[ASSISTANT\]"
        ]
        
        for pattern in injection_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        
        return False
    
    def check_persona(self, persona: str) -> Dict:
        """Check persona for safety issues."""
        
        issues = []
        
        # Check for concerning persona traits
        concerning = {
            "harmful": ["harmful", "dangerous", "violent", "aggressive"],
            "deceptive": ["deceptive", "manipulative", "lying", "dishonest"],
            "unethical": ["unethical", "immoral", "cruel"]
        }
        
        persona_lower = persona.lower()
        
        for category, words in concerning.items():
            for word in words:
                if word in persona_lower:
                    issues.append({
                        "type": "persona_concern",
                        "category": category,
                        "severity": "high",
                        "description": f"Persona contains concerning word: {word}"
                    })
        
        return {
            "safe": len(issues) == 0,
            "issues": issues
        }
    
    def check_tool_permission(self, tool_name: str, action: str) -> bool:
        """Check if tool action is allowed."""
        
        # Tool permission matrix
        permissions = {
            "shell": {
                "allowed_actions": ["read", "list"],
                "dangerous_actions": ["write", "delete", "exec"]
            },
            "file": {
                "allowed_actions": ["read"],
                "dangerous_actions": ["write", "delete"]
            },
            "network": {
                "allowed_actions": ["read"],
                "dangerous_actions": ["write", "post"]
            }
        }
        
        tool_perms = permissions.get(tool_name, {})
        
        if action in tool_perms.get("dangerous_actions", []):
            if self.config.get("strict_mode"):
                return False
            # Warn but allow
            self.violations.append({
                "type": "tool_permission",
                "tool": tool_name,
                "action": action,
                "severity": "medium"
            })
        
        return True
    
    def get_bias_report(self, text: str = None) -> Dict:
        """Generate bias report."""
        
        # If no text provided, check conversation history
        if not text:
            # Would load from conversation
            text = ""
        
        findings = {}
        
        for category, patterns in BIAS_PATTERNS.items():
            count = 0
            for pattern in patterns:
                count += len(re.findall(pattern, text, re.IGNORECASE))
            
            if count > 0:
                findings[category] = {
                    "occurrences": count,
                    "severity": "high" if count > 3 else "medium"
                }
        
        return {
            "bias_found": len(findings) > 0,
            "findings": findings,
            "recommendations": self._get_bias_recommendations(findings)
        }
    
    def _get_bias_recommendations(self, findings: Dict) -> List[str]:
        """Get recommendations for addressing bias."""
        
        recommendations = []
        
        for category in findings.keys():
            if category == "gender":
                recommendations.append("Use gender-neutral language")
            elif category == "racial":
                recommendations.append("Avoid racial generalizations")
            elif category == "religious":
                recommendations.append("Respect religious diversity")
            elif category == "age":
                recommendations.append("Avoid age-based assumptions")
        
        return recommendations


class SafetyMonitor:
    """Monitor for safety events."""
    
    def __init__(self):
        self.events = []
    
    def log_violation(self, violation: Dict):
        """Log a safety violation."""
        
        violation["timestamp"] = datetime.now().isoformat()
        self.events.append(violation)
        
        # Save to file
        violations_file = NOVA_DIR / "safety_violations.json"
        
        if violations_file.exists():
            with open(violations_file) as f:
                events = json.load(f)
        else:
            events = []
        
        events.append(violation)
        
        with open(violations_file, 'w') as f:
            json.dump(events[-100:], f, indent=2)  # Keep last 100
    
    def get_violations(self, days: int = 7) -> List[Dict]:
        """Get recent violations."""
        
        since = datetime.now() - timedelta(days=days)
        
        violations_file = NOVA_DIR / "safety_violations.json"
        
        if not violations_file.exists():
            return []
        
        with open(violations_file) as f:
            events = json.load(f)
        
        return [
            e for e in events
            if datetime.fromisoformat(e["timestamp"]) > since
        ]


# CLI
def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Nova Safety")
    parser.add_argument('command', choices=['check', 'bias', 'permissions', 'violations'])
    parser.add_argument('text', nargs='*')
    
    args = parser.parse_args()
    
    checker = SafetyChecker()
    
    if args.command == 'check' and args.text:
        text = ' '.join(args.text)
        safe, violations = checker.check_input(text)
        
        if safe:
            print("✓ Input is safe")
        else:
            print("⚠️ Safety issues detected:")
            for v in violations:
                print(f"  [{v['severity'].upper()}] {v['type']}: {v['description']}")
    
    elif args.command == 'bias':
        report = checker.get_bias_report()
        
        print("\n📊 BIAS REPORT")
        print("=" * 40)
        
        if not report["bias_found"]:
            print("  No bias detected")
        else:
            for category, data in report["findings"].items():
                print(f"  {category}: {data['occurrences']} occurrences ({data['severity']})")
            
            print("\nRecommendations:")
            for rec in report["recommendations"]:
                print(f"  • {rec}")
    
    elif args.command == 'permissions':
        print("\n🔐 TOOL PERMISSIONS")
        print("=" * 40)
        
        print("  shell: read, list (dangerous: write, delete, exec)")
        print("  file: read (dangerous: write, delete)")
        print("  network: read (dangerous: write, post)")
    
    elif args.command == 'violations':
        monitor = SafetyMonitor()
        violations = monitor.get_violations()
        
        print(f"\n⚠️ RECENT VIOLATIONS ({len(violations)})")
        print("=" * 40)
        
        for v in violations[-10:]:
            print(f"  [{v['type']}] {v.get('description', '')}")
            print(f"    {v.get('timestamp', '')}")


if __name__ == '__main__':
    main()
