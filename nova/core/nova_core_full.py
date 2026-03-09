"""
NOVA CORE - Full Hybrid Autonomous Agent
=======================================
Combines: Identity, Brain Bus, Goal Engine, Observability, Memory, Hybrid Mode

Runs three loops:
- Fast loop: Trading (200ms)
- Slow loop: Cognition (5s)  
- Dream loop: Background learning (30-60min)

Hybrid Features:
- Online/Offline auto-switch
- Data adapter with caching
- Memory snapshots
- Self-healing
"""

import time
import asyncio
import json
import logging
import pickle
import gzip
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, List
from threading import Event, Thread
from collections import defaultdict

# Core imports
from core.brain_orchestrator import BrainOrchestrator
from core.emotional_council import EMOTIONAL_BRAINS
from core.brain_bus import get_brain_bus, Events
from core.nova_observer import get_observer
from core.goal_engine import get_goal_engine, GoalPriority
from core.offline_simulator import get_simulator
from core.security_sandbox import get_sandbox

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("NovaCore")

# Paths
CAPABILITIES_FILE = Path("/Users/dr.claw/.openclaw/workspace/nova_user_capabilities.json")
IDENTITY_FILE = Path("/Users/dr.claw/.openclaw/workspace/nova/core/core_identity.json")
SNAPSHOT_DIR = Path("/Users/dr.claw/.openclaw/workspace/nova/snapshots/")


class SnapshotManager:
    """Handles persistence - saves/restores Nova's entire state"""
    
    def __init__(self, nova_core, snapshot_dir: Path = SNAPSHOT_DIR, interval: int = 60):
        self.nova = nova_core
        self.snapshot_dir = snapshot_dir
        self.interval = interval
        self.stop_event = Event()
        self.thread = None
        
        # Create snapshot dir
        self.snapshot_dir.mkdir(parents=True, exist_ok=True)
    
    def start_auto_save(self):
        """Start automatic snapshot thread"""
        self.thread = Thread(target=self._auto_save_loop, daemon=True)
        self.thread.start()
        logger.info(f"Auto-snapshot started (every {self.interval}s)")
    
    def stop_auto_save(self):
        """Stop automatic snapshots"""
        self.stop_event.set()
        if self.thread:
            self.thread.join(timeout=5)
    
    def _auto_save_loop(self):
        """Background save loop"""
        import time
        while not self.stop_event.is_set():
            time.sleep(self.interval)
            if self.nova.is_alive:
                try:
                    self.save_snapshot()
                except Exception as e:
                    logger.error(f"Auto-snapshot failed: {e}")
    
    def save_snapshot(self, name: str = None) -> str:
        """Save full state snapshot"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"nova_snapshot_{timestamp}.json.gz" if not name else name
        path = self.snapshot_dir / filename
        
        snapshot = {
            "version": "1.0",
            "timestamp": datetime.now().isoformat(),
            "identity": self.nova.identity,
            "capabilities": self.nova.capabilities,
            "cycle_count": self.nova.cycle_count,
            "memory": {
                "short_term": self.nova.memory.short_term[-20:],  # Last 20
                "long_term": self.nova.memory.long_term[-50:]   # Last 50
            },
            "goals": self.nova.goal_engine.get_summary(),
            "metrics": {
                "fast_loop_avg": sum(self.nova.observer.fast_loop_times) / max(1, len(self.nova.observer.fast_loop_times)),
                "total_cycles": self.nova.cycle_count,
                "thoughts": self.nova.observer.total_thoughts
            }
        }
        
        # Save compressed
        with gzip.open(path, 'wt', encoding='utf-8') as f:
            json.dump(snapshot, f)
        
        # Keep only last 10 snapshots
        self._cleanup_old_snapshots(10)
        
        logger.info(f"Snapshot saved: {path.name}")
        return str(path)
    
    def load_snapshot(self, path: str = None) -> bool:
        """Load state from snapshot"""
        if not path:
            # Find latest snapshot
            snapshots = sorted(self.snapshot_dir.glob("nova_snapshot_*.json.gz"))
            if not snapshots:
                logger.info("No snapshots found")
                return False
            path = str(snapshots[-1])
        
        try:
            with gzip.open(path, 'rt', encoding='utf-8') as f:
                data = json.load(f)
            
            # Restore state
            self.nova.identity = data.get("identity", self.nova.identity)
            self.nova.capabilities = data.get("capabilities", self.nova.capabilities)
            self.nova.cycle_count = data.get("cycle_count", 0)
            
            if "memory" in data:
                self.nova.memory.short_term = data["memory"].get("short_term", [])
                self.nova.memory.long_term = data["memory"].get("long_term", [])
            
            logger.info(f"Snapshot loaded from {path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load snapshot: {e}")
            return False
    
    def _cleanup_old_snapshots(self, keep: int = 10):
        """Keep only N most recent snapshots"""
        snapshots = sorted(self.snapshot_dir.glob("nova_snapshot_*.json.gz"))
        for old in snapshots[:-keep]:
            old.unlink()
            logger.debug(f"Deleted old snapshot: {old.name}")
    
    def list_snapshots(self) -> List[str]:
        """List available snapshots"""
        return [s.name for s in sorted(self.snapshot_dir.glob("nova_snapshot_*.json.gz"))]


def load_json(path: Path, default: Dict) -> Dict:
    try:
        if path.exists():
            with open(path, 'r') as f:
                return json.load(f)
    except Exception as e:
        logger.warning(f"Failed to load {path}: {e}")
    return default


class DataAdapter:
    """Hybrid data adapter - handles online/offline data fetching"""
    
    def __init__(self):
        self.cache = {}
        self.cache_ttl = 3600  # 1 hour
        self.is_online = False
        
    def fetch(self, source: str, key: str, fetch_func=None) -> Any:
        """Fetch data with caching and offline fallback"""
        cache_key = f"{source}:{key}"
        
        # Check cache
        if cache_key in self.cache:
            cached, timestamp = self.cache[cache_key]
            if time.time() - timestamp < self.cache_ttl:
                logger.debug(f"Cache hit: {cache_key}")
                return cached
        
        # Try online fetch if available
        if self.is_online and fetch_func:
            try:
                data = fetch_func()
                self.cache[cache_key] = (data, time.time())
                return data
            except Exception as e:
                logger.warning(f"Online fetch failed: {e}")
        
        # Return cached or None
        if cache_key in self.cache:
            cached, _ = self.cache[cache_key]
            logger.info(f"Using cached data for {cache_key}")
            return cached
        
        return None
    
    def set_online(self, online: bool):
        self.is_online = online
        logger.info(f"DataAdapter: {'ONLINE' if online else 'OFFLINE'}")


class MemorySystem:
    """Memory with snapshots for persistence"""
    
    def __init__(self, snapshot_dir: Path = SNAPSHOT_DIR):
        self.short_term: List[Dict] = []
        self.long_term: List[Dict] = []
        self.max_short = 100
        self.snapshot_dir = snapshot_dir
        self.snapshot_interval = 100  # snapshots every N cycles
        
        # Create snapshot dir
        self.snapshot_dir.mkdir(parents=True, exist_ok=True)
    
    def store(self, data: Dict):
        """Store in short-term memory"""
        self.short_term.append({
            **data,
            "timestamp": datetime.now().isoformat()
        })
        
        # Trim if needed
        if len(self.short_term) > self.max_short:
            # Move to long-term
            self.long_term.extend(self.short_term[:-50])
            self.short_term = self.short_term[-50:]
    
    def recall(self, query: str = None, limit: int = 10) -> List[Dict]:
        """Recall memories"""
        all_memories = self.short_term + self.long_term
        if query:
            all_memories = [m for m in all_memories if query.lower() in str(m).lower()]
        return all_memories[-limit:]
    
    def snapshot(self, state: Dict) -> str:
        """Save state snapshot"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = self.snapshot_dir / f"nova_snapshot_{timestamp}.json"
        
        with open(path, 'w') as f:
            json.dump(state, f, indent=2)
        
        logger.info(f"Snapshot saved: {path.name}")
        return str(path)
    
    def restore(self, snapshot_path: str) -> bool:
        """Restore from snapshot"""
        try:
            with open(snapshot_path, 'r') as f:
                state = json.load(f)
            
            self.short_term = state.get("short_term", [])
            self.long_term = state.get("long_term", [])
            logger.info(f"Restored from {snapshot_path}")
            return True
        except Exception as e:
            logger.error(f"Restore failed: {e}")
            return False


class NovaCore:
    """Nova's Central Nervous System - Full Hybrid Autonomous Agent"""
    
    def __init__(self):
        logger.info("=" * 50)
        logger.info("INITIALIZING NOVA CORE")
        logger.info("=" * 50)
        
        # Identity
        self.identity = load_json(IDENTITY_FILE, {"name": "Nova", "immutable_rules": []})
        self.capabilities = load_json(CAPABILITIES_FILE, {"can_trade": False, "can_self_modify": False, "can_contact": False})
        
        # Core subsystems
        self.brain_orchestrator = BrainOrchestrator()
        self.brain_bus = get_brain_bus()
        self.observer = get_observer()
        self.goal_engine = get_goal_engine()
        self.memory = MemorySystem()
        self.data_adapter = DataAdapter()
        
        # State
        self.is_alive = True
        self.cycle_count = 0
        self.last_cognition = datetime.now()
        self.last_dream = datetime.now()
        
        # Timing
        self.cognition_interval = 5
        self.dream_interval = 3600
        
        # Hybrid mode
        self.is_online = False
        self.hybrid_manager = None  # HybridFailoverManager(self)
        
        # Snapshot manager
        self.snapshot_manager = SnapshotManager(self)
        
        # Offline trading simulator
        self.simulator = get_simulator(self)
        
        # Security sandbox
        self.sandbox = get_sandbox()
        
        logger.info(f"Nova Core initialized: {self.identity.get('name', 'Nova')}")
        logger.info(f"Brains: {len(self.brain_orchestrator.brains)}")
        logger.info("=" * 50)
    
    # ═══════════════════════════════════════════════════════
    # PERCEPTION
    # ═══════════════════════════════════════════════════════
    
    def perceive_market(self) -> Dict[str, Any]:
        """Gather market data"""
        # Try online first, fall back to cache
        def fetch():
            # Placeholder for real API
            return {"price": 50000, "volatility": 0.02}
        
        data = self.data_adapter.fetch("market", "current", fetch)
        return data or {"source": "offline", "cached": True}
    
    def perceive_system(self) -> Dict[str, Any]:
        """Gather system state"""
        return {
            "timestamp": datetime.now().isoformat(),
            "cycles": self.cycle_count,
            "memory_items": len(self.memory.short_term),
            "is_online": self.is_online
        }
    
    # ═══════════════════════════════════════════════════════
    # FAST LOOP - Trading (200ms)
    # ═══════════════════════════════════════════════════════
    
    async def fast_loop(self) -> Optional[Dict]:
        """Trading loop"""
        try:
            start = time.perf_counter()
            
            # Market perception
            market = self.perceive_market()
            
            # Route to trading brains
            context = {"mood": "neutral", "joy": 0.5, "loop_type": "trading"}
            
            # Get brain votes
            result = await self.brain_orchestrator.process_async(
                "Evaluate market for trading",
                context
            )
            
            # Record metrics
            elapsed = time.perf_counter() - start
            self.observer.record_fast_loop(elapsed)
            self.observer.record_cycle()
            
            self.cycle_count += 1
            
            # Periodic snapshot
            if self.cycle_count % self.memory.snapshot_interval == 0:
                self.save_snapshot()
            
            return result
            
        except Exception as e:
            logger.error(f"Fast loop error: {e}")
            self.observer.record_error(str(e), "fast_loop")
            return None
    
    # ═══════════════════════════════════════════════════════
    # SLOW LOOP - Cognition (5s)
    # ═══════════════════════════════════════════════════════
    
    async def slow_loop(self) -> Optional[Dict]:
        """Cognition loop"""
        try:
            now = datetime.now()
            if (now - self.last_cognition).total_seconds() < self.cognition_interval:
                return None
            
            self.last_cognition = now
            start = time.perf_counter()
            
            # System perception
            system_state = self.perceive_system()
            
            # Get goals
            active_goals = self.goal_engine.get_active_goals()
            top_goal = self.goal_engine.get_top_priority_goal()
            
            # Cognition context
            context = {
                "mood": "restless",
                "joy": 0.55,
                "loop_type": "cognition"
            }
            
            if top_goal:
                context["active_goal"] = top_goal.description
                logger.info(f"Goal focus: {top_goal.description}")
            
            # Generate thoughts
            result = await self.brain_orchestrator.process_async(
                "Reflect on current state and goals",
                context
            )
            
            # Store in memory
            self.memory.store({
                "type": "cognition",
                "thoughts": result[:200] if result else "",
                "goals": len(active_goals),
                "system": system_state
            })
            
            # Record metrics
            elapsed = time.perf_counter() - start
            self.observer.record_slow_loop(elapsed)
            self.observer.record_thought()
            
            # Publish event
            self.brain_bus.publish(Events.THOUGHT_GENERATED, result[:100] if result else "")
            
            logger.info(f"Cognition cycle complete ({elapsed*1000:.1f}ms)")
            return result
            
        except Exception as e:
            logger.error(f"Slow loop error: {e}")
            self.observer.record_error(str(e), "slow_loop")
            return None
    
    # ═══════════════════════════════════════════════════════
    # DREAM LOOP - Learning (30-60min)
    # ═══════════════════════════════════════════════════════
    
    async def dream_loop(self) -> Optional[Dict]:
        """Dream loop - memory analysis and learning"""
        try:
            now = datetime.now()
            if (now - self.last_dream).total_seconds() < self.dream_interval:
                return None
            
            self.last_dream = now
            logger.info("Dream cycle starting...")
            
            # Analyze patterns
            if self.memory.short_term:
                recent = self.memory.short_term[-20:]
                
                # Find patterns
                types = [m.get("type", "unknown") for m in recent]
                pattern_summary = f"cognition:{types.count('cognition')}, trading:{types.count('trading')}"
                
                logger.info(f"Pattern analysis: {pattern_summary}")
                
                # Auto-generate goals from patterns
                if "trading" in pattern_summary:
                    self.goal_engine.create_from_template(
                        "improve_strategy", 
                        {"asset": "portfolio"}
                    )
                
                # Compress old memories
                if len(self.memory.short_term) > self.memory.max_short:
                    self.memory.long_term.extend(self.memory.short_term[:-50])
                    self.memory.short_term = self.memory.short_term[-50:]
                    logger.info("Memory compressed")
            
            # Record metrics
            self.observer.record_dream_loop(0.1)  # Placeholder
            
            # Publish event
            self.brain_bus.publish(Events.INSIGHT_EMERGED, "Dream analysis complete")
            
            logger.info("Dream cycle complete")
            return {"status": "dream_complete"}
            
        except Exception as e:
            logger.error(f"Dream loop error: {e}")
            self.observer.record_error(str(e), "dream_loop")
            return None
    
    # ═══════════════════════════════════════════════════════
    # HYBRID MODE
    # ═══════════════════════════════════════════════════════
    
    def set_online(self, online: bool):
        """Switch online/offline mode"""
        self.is_online = online
        self.data_adapter.set_online(online)
        
        if online:
            self.sync_data()
        else:
            logger.info("Switched to OFFLINE mode")
    
    def sync_data(self) -> bool:
        """Sync data when online"""
        if not self.is_online:
            logger.warning("Cannot sync: offline mode")
            return False
        
        # Placeholder for real sync
        logger.info("Syncing data...")
        return True
    
    # ═══════════════════════════════════════════════════════
    # SNAPSHOTS
    # ═══════════════════════════════════════════════════════
    
    def save_snapshot(self):
        """Save state snapshot"""
        state = {
            "timestamp": datetime.now().isoformat(),
            "cycle_count": self.cycle_count,
            "short_term": self.memory.short_term[-20:],  # Last 20
            "goals": self.goal_engine.get_summary(),
            "identity": self.identity
        }
        
        path = self.memory.snapshot(state)
        return path
    
    def restore_snapshot(self, path: str) -> bool:
        """Restore from snapshot"""
        success = self.memory.restore(path)
        if success:
            logger.info(f"Restored from {path}")
        return success
    
    # ═══════════════════════════════════════════════════════
    # STATUS
    # ═══════════════════════════════════════════════════════
    
    def get_status(self) -> Dict[str, Any]:
        """Get full system status"""
        sim_status = self.simulator.get_status() if self.simulator else {}
        
        return {
            "identity": self.identity.get("name"),
            "mode": "ONLINE" if self.is_online else "OFFLINE",
            "hybrid": {"status": "disabled"} if not self.hybrid_manager else self.hybrid_manager.get_status(),
            "simulator": {
                "balance": sim_status.get("balance", 0),
                "pnl_percent": sim_status.get("pnl_percent", 0),
                "prices": list(sim_status.get("prices", {}).keys()) if sim_status else []
            },
            "cycles": self.cycle_count,
            "memory": {
                "short": len(self.memory.short_term),
                "long": len(self.memory.long_term)
            },
            "goals": self.goal_engine.get_summary(),
            "brain_bus": self.brain_bus.get_metrics(),
            "health": self.observer.get_health_summary(),
            "capabilities": self.capabilities,
            "security": self.sandbox.get_status(),
            "snapshots": self.snapshot_manager.list_snapshots()
        }
    
    def save_snapshot(self, name: str = None) -> str:
        """Manually save snapshot"""
        return self.snapshot_manager.save_snapshot(name)
    
    def load_snapshot(self, path: str = None) -> bool:
        """Manually load snapshot"""
        return self.snapshot_manager.load_snapshot(path)
    
    def get_report(self) -> str:
        """Get human-readable report"""
        status = self.get_status()
        
        lines = [
            "=" * 40,
            f"NOVA CORE STATUS - {status['identity']}",
            "=" * 40,
            f"Mode: {status['mode']}",
            f"Cycles: {status['cycles']}",
            "",
            "Memory:",
            f"  Short-term: {status['memory']['short']}",
            f"  Long-term: {status['memory']['long']}",
            "",
            "Goals:",
            f"  Active: {status['goals']['active_goals']}",
            f"  Completed: {status['goals']['completed']}",
            "",
            "Health:",
            f"  Status: {status['health']['status']}",
            f"  Errors: {status['health']['errors_count']}",
            "",
            "Capabilities:",
            f"  Trade: {status['capabilities'].get('can_trade', False)}",
            f"  Self-Mod: {status['capabilities'].get('can_self_modify', False)}",
            f"  Contact: {status['capabilities'].get('can_contact', False)}",
            "=" * 40
        ]
        
        return "\n".join(lines)
    
    # ═══════════════════════════════════════════════════════
    # MAIN RUN LOOP
    # ═══════════════════════════════════════════════════════
    
    async def run(self, duration_seconds: int = 60):
        """Run Nova Core for specified duration"""
        logger.info(f"Starting Nova Core for {duration_seconds}s...")
        
        # Start auto-save
        self.snapshot_manager.start_auto_save()
        
        start_time = time.time()
        
        while self.is_alive and (time.time() - start_time) < duration_seconds:
            # Always run fast loop
            await self.fast_loop()
            
            # Occasionally run slow loop
            await self.slow_loop()
            
            # Rarely run dream loop
            await self.dream_loop()
            
            # Small sleep
            await asyncio.sleep(0.1)
        
        logger.info(f"Nova Core stopped after {self.cycle_count} cycles")
        return self.get_status()
    
    async def run_forever(self):
        """Run indefinitely"""
        logger.info("Starting Nova Core (infinite)...")
        
        while self.is_alive:
            await self.fast_loop()
            await self.slow_loop()
            await self.dream_loop()
            await asyncio.sleep(0.1)
    
    def stop(self):
        """Stop Nova Core"""
        logger.info("Stopping Nova Core...")
        self.snapshot_manager.stop_auto_save()
        self.save_snapshot()
        self.is_alive = False


# ═══════════════════════════════════════════════════════
# STANDALONE TEST
# ═══════════════════════════════════════════════════════

if __name__ == "__main__":
    async def test():
        print("=== NOVA CORE FULL TEST ===")
        
        nova = NovaCore()
        
        # Add a goal
        nova.goal_engine.create_user_goal("Test hybrid integration", GoalPriority.HIGH)
        
        # Run for 5 seconds
        status = await nova.run(duration_seconds=5)
        
        print("\n" + nova.get_report())
    
    asyncio.run(test())
