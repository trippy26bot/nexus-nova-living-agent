#!/usr/bin/env python3
"""
NOVA ENVIRONMENT — Environment Awareness
The agent knows its environment: file structure, running processes, project deps.

Allows Nova to understand where she is and what's around her.
"""

import os
import sys
import json
import sqlite3
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# Configuration
WORKSPACE = Path.cwd()
NOVA_DIR = Path.home() / ".nova"
ENV_STATE = NOVA_DIR / "environment.json"


class EnvironmentAwareness:
    """Knows the environment the agent is running in."""
    
    def __init__(self):
        self.workspace = WORKSPACE
        self.load_state()
    
    def load_state(self):
        """Load cached environment state."""
        if ENV_STATE.exists():
            with open(ENV_STATE) as f:
                self.state = json.load(f)
        else:
            self.state = {}
    
    def save_state(self):
        """Save environment state."""
        self.state['last_scan'] = datetime.now().isoformat()
        with open(ENV_STATE, 'w') as f:
            json.dump(self.state, f, indent=2)
    
    def scan_workspace(self) -> Dict:
        """Scan the workspace directory structure."""
        
        structure = {
            'root': str(self.workspace),
            'files': [],
            'dirs': [],
            'total_files': 0
        }
        
        for root, dirs, files in os.walk(self.workspace):
            # Skip hidden and common ignorable directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules', 'venv']]
            
            rel_root = Path(root).relative_to(self.workspace)
            
            for d in dirs:
                structure['dirs'].append(str(rel_root / d))
            
            for f in files:
                if not f.startswith('.'):
                    structure['files'].append(str(rel_root / f))
        
        structure['total_files'] = len(structure['files'])
        
        self.state['structure'] = structure
        self.save_state()
        
        return structure
    
    def get_structure(self) -> Dict:
        """Get cached directory structure."""
        if 'structure' not in self.state:
            self.scan_workspace()
        return self.state.get('structure', {})
    
    def get_running_processes(self) -> List[Dict]:
        """Get running processes (limited info for security)."""
        
        processes = []
        
        try:
            if sys.platform == 'darwin':
                result = subprocess.run(
                    ['ps', 'aux'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                lines = result.stdout.strip().split('\n')[1:20]  # First 20
                
                for line in lines:
                    parts = line.split()
                    if len(parts) >= 11:
                        processes.append({
                            'pid': parts[1],
                            'cpu': parts[2],
                            'mem': parts[3],
                            'command': ' '.join(parts[10:])[:50]
                        })
            elif sys.platform == 'linux':
                result = subprocess.run(
                    ['ps', 'aux'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                lines = result.stdout.strip().split('\n')[1:20]
                
                for line in lines:
                    parts = line.split()
                    if len(parts) >= 11:
                        processes.append({
                            'pid': parts[1],
                            'cpu': parts[2],
                            'mem': parts[3],
                            'command': ' '.join(parts[10:])[:50]
                        })
        except Exception as e:
            processes = [{'error': str(e)}]
        
        self.state['processes'] = processes
        self.save_state()
        
        return processes
    
    def check_dependencies(self) -> Dict:
        """Check for common project dependencies."""
        
        deps = {
            'python': {'found': False, 'version': None},
            'node': {'found': False, 'version': None},
            'git': {'found': False, 'version': None},
            'docker': {'found': False, 'version': None},
        }
        
        # Check Python
        try:
            result = subprocess.run(
                ['python3', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                deps['python']['found'] = True
                deps['python']['version'] = result.stdout.strip()
        except:
            pass
        
        # Check Node
        try:
            result = subprocess.run(
                ['node', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                deps['node']['found'] = True
                deps['node']['version'] = result.stdout.strip()
        except:
            pass
        
        # Check Git
        try:
            result = subprocess.run(
                ['git', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                deps['git']['found'] = True
                deps['git']['version'] = result.stdout.strip()
        except:
            pass
        
        # Check Docker
        try:
            result = subprocess.run(
                ['docker', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                deps['docker']['found'] = True
                deps['docker']['version'] = result.stdout.strip()
        except:
            pass
        
        # Check project files
        project_files = []
        for f in ['requirements.txt', 'package.json', 'Cargo.toml', 'go.mod', 'pyproject.toml']:
            if (self.workspace / f).exists():
                project_files.append(f)
        
        deps['project_files'] = project_files
        
        self.state['dependencies'] = deps
        self.save_state()
        
        return deps
    
    def get_git_info(self) -> Optional[Dict]:
        """Get Git repository info."""
        
        try:
            # Check if in git repo
            result = subprocess.run(
                ['git', 'status'],
                cwd=self.workspace,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode != 0:
                return None
            
            info = {}
            
            # Branch
            result = subprocess.run(
                ['git', 'branch', '--show-current'],
                cwd=self.workspace,
                capture_output=True,
                text=True,
                timeout=5
            )
            info['branch'] = result.stdout.strip()
            
            # Last commit
            result = subprocess.run(
                ['git', 'log', '-1', '--oneline'],
                cwd=self.workspace,
                capture_output=True,
                text=True,
                timeout=5
            )
            info['last_commit'] = result.stdout.strip()
            
            # Status
            result = subprocess.run(
                ['git', 'status', '--short'],
                cwd=self.workspace,
                capture_output=True,
                text=True,
                timeout=5
            )
            info['status'] = result.stdout.strip()[:500]  # Limit
            
            self.state['git'] = info
            self.save_state()
            
            return info
        
        except Exception as e:
            return {'error': str(e)}
    
    def get_context_summary(self) -> str:
        """Get a summary of the current environment."""
        
        structure = self.get_structure()
        deps = self.check_dependencies()
        git = self.get_git_info()
        
        lines = [
            f"Workspace: {self.workspace}",
            f"Files: {structure.get('total_files', 0)}",
            f"Directories: {len(structure.get('dirs', []))}",
            "",
            "Dependencies:",
        ]
        
        for name, info in deps.items():
            if name == 'project_files':
                if info:
                    lines.append(f"  Project files: {', '.join(info)}")
            elif info.get('found'):
                lines.append(f"  ✓ {name}: {info.get('version', 'found')}")
            else:
                lines.append(f"  ✗ {name}: not found")
        
        if git and 'error' not in git:
            lines.extend([
                "",
                "Git:",
                f"  Branch: {git.get('branch', 'unknown')}",
                f"  Last: {git.get('last_commit', 'none')[:50]}"
            ])
        
        return "\n".join(lines)
    
    def knows_file(self, path: str) -> bool:
        """Check if a file exists in the workspace."""
        structure = self.get_structure()
        return path in structure.get('files', [])


# Singleton
_env = None

def get_environment() -> EnvironmentAwareness:
    """Get the environment awareness singleton."""
    global _env
    if _env is None:
        _env = EnvironmentAwareness()
    return _env


if __name__ == '__main__':
    env = get_environment()
    print("=" * 50)
    print("NOVA ENVIRONMENT AWARENESS")
    print("=" * 50)
    print(env.get_context_summary())
