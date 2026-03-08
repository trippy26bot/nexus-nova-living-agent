"""
Nexus Nova Living Agent - Project Manager
Multi-step project planning and tracking
"""
from datetime import datetime, timedelta

class ProjectManager:
    """NOVA manages multi-step projects based on long-term goals"""
    
    def __init__(self, nova, long_term_manager):
        self.nova = nova
        self.long_term = long_term_manager
        self.active_projects = []
        
    def plan_projects(self):
        """Create projects from long-term goals if not already active"""
        if not hasattr(self.long_term, 'goals') or not self.long_term.goals:
            return
            
        for goal in self.long_term.goals:
            # Skip if already has project for this theme
            if any(p['goal_theme'] == goal['theme'] for p in self.active_projects):
                continue
                
            # Create multi-step project
            steps = [
                f"Research {goal['theme']}",
                f"Analyze patterns in {goal['theme']}",
                f"Document findings on {goal['theme']}"
            ]
            
            project = {
                "goal_theme": goal['theme'],
                "steps": steps,
                "current_step": 0,
                "progress": 0,
                "created": datetime.now().isoformat()
            }
            self.active_projects.append(project)
            
            self.nova.memory.store_thought(
                f"[Project Created] '{goal['theme']}' with {len(steps)} steps"
            )
            
    def advance_projects(self):
        """Progress projects based on recent activity"""
        recent = self.nova.memory.get_recent_context(days=7)
        
        for project in self.active_projects:
            theme = project['goal_theme']
            
            # Check for related activity
            related = any(theme.lower() in t.get("thought", "").lower() for t in recent)
            
            if related and project['current_step'] < len(project['steps']):
                # Advance step
                project['current_step'] += 1
                project['progress'] = int((project['current_step'] / len(project['steps'])) * 100)
                
                self.nova.memory.store_thought(
                    f"[Project] '{theme}' step {project['current_step']}/{len(project['steps'])} ({project['progress']}%)"
                )
                
            # Check completion
            if project['current_step'] >= len(project['steps']):
                self.nova.memory.store_thought(
                    f"[Project Completed] '{theme}' finished all {len(project['steps'])} steps!"
                )
                project['progress'] = 100
                
    def get_active(self):
        return [p for p in self.active_projects if p['progress'] < 100]
