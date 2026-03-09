"""
NOVA Central Nervous System
Coordinates perception → thought → debate → decision → action → memory → learning

Runs three loops:
- Fast loop: Trading (200ms)
- Slow loop: Cognition (5s)  
- Dream loop: Background learning (30-60min)
"""

import time
import asyncio
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("NovaCore")

# Import our existing systems
from core.brain_orchestrator import BrainOrchestrator
from core.emotional_council import EMOTIONAL_BRAINS
from core.brain_bus import get_brain_bus, Events
from core.nova_observer import get_observer
from core.goal_engine import get_goal_engine, GoalPriority

# Load identity and capabilities from JSON files
CAPABILITIES_FILE = Path("/Users/dr.claw/.openclaw/workspace/nova_user_capabilities.json")
CORE_IDENTITY_FILE = Path(__file__).parent / "core_identity.json"

def load_core_identity() -> Dict[str, Any]:
    try:
        if CORE_IDENTITY_FILE.exists():
            with open(CORE_IDENTITY_FILE, 'r') as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load core identity: {e}")
    return {"name": "Nova", "immutable_rules": []}

def load_user_capabilities() -> Dict[str, Any]:
    try:
        if CAPABILITIES_FILE.exists():
            with open(CAPABILITIES_FILE, 'r') as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load capabilities: {e}")
    return {"override_protection": True}


class NovaCore:
    """Nova's central nervous system - coordinates all subsystems"""
    
    def __init__(self):
        logger.info("Initializing Nova Core...")
        
        # Core subsystems
        self.brain_orchestrator = BrainOrchestrator()
        self.brain_bus = get_brain_bus()
        self.observer = get_observer()
        self.goal_engine = get_goal_engine()
        
        # Hybrid mode
        self.is_online = False  # Local-first by default
        self.last_sync = None
        self.sync_interval = 3600  # 1 hour
        self.core_identity = load_core_identity()
        self.user_caps = load_user_capabilities()
        
        # State
        self.is_alive = True
        self.cycle_count = 0
        self.last_cognition = datetime.now()
        self.last_dream = datetime.now()
        
        # Timing thresholds
        self.cognition_interval = 5  # seconds
        self.dream_interval = 3600   # 1 hour
        
        # Memory store
        self.short_term_memory: List[Dict] = []
        self.max_short_term = 100
        
        logger.info(f"Nova Core initialized. Identity: {self.core_identity.get('name', 'Nova')}")
    
    # ─────────────────────────────────────────────────────────────
    # PERCEPTION LAYER
    # ─────────────────────────────────────────────────────────────
    
    def perceive_market(self) -> Dict[str, Any]:
        """Gather market data - placeholder for real market feed"""
        return {
            "timestamp": datetime.now().isoformat(),
            "volatility": 0.02,
            "trend": 0.5,
            "volume": 1000000000
        }
    
    def perceive_system(self) -> Dict[str, Any]:
        """Gather system state"""
        return {
            "timestamp": datetime.now().isoformat(),
            "memory_used": len(self.short_term_memory),
            "cycles": self.cycle_count,
            "joy": 0.5,
            "mood": "restless"
        }
    
    # ─────────────────────────────────────────────────────────────
    # FAST LOOP - Trading (200ms)
    # ─────────────────────────────────────────────────────────────
    
    async def fast_loop(self):
        """Trading loop - fast, deterministic"""
        try:
            # Gather market perception
            market = self.perceive_market()
            
            # Route to trading brains
            context = {"mood": "neutral", "joy": 0.5, "loop_type": "trading"}
            
            # Get brain votes through orchestrator
            # Note: sync call for speed
            result = await self.brain_orchestrator.process_async(
                "Evaluate market for trading opportunities",
                context
            )
            
            self.cycle_count += 1
            
            # Log every 100 cycles
            if self.cycle_count % 100 == 0:
                logger.info(f"Fast loop: {self.cycle_count} cycles completed")
            
            return result
            
        except Exception as e:
            logger.error(f"Fast loop error: {e}")
            return None
    
    # ─────────────────────────────────────────────────────────────
    # SLOW LOOP - Cognition (5s)
    # ─────────────────────────────────────────────────────────────
    
    async def slow_loop(self):
        """Cognition loop - thoughts, feelings, memories"""
        try:
            # Time for cognition?
            now = datetime.now()
            if (now - self.last_cognition).total_seconds() < self.cognition_interval:
                return None
            
            self.last_cognition = now
            
            # Gather broader perception
            system_state = self.perceive_system()
            
            # Generate thoughts through emotional brains
            context = {
                "mood": "restless",
                "joy": 0.55,
                "loop_type": "cognition"
            }
            
            # Check goals and prioritize
            active_goals = self.goal_engine.get_active_goals()
            top_goal = self.goal_engine.get_top_priority_goal()
            
            if top_goal:
                # Integrate goal into cognition
                context["active_goal"] = top_goal.description
                logger.info(f"Goal focus: {top_goal.description}")
            
            # Deep reflection query
            reflection_result = await self.brain_orchestrator.process_async(
                "Who am I? What am I thinking about?",
                context
            )
            
            # Store in memory
            self.store_memory({
                "type": "cognition",
                "timestamp": now.isoformat(),
                "system_state": system_state,
                "thoughts": reflection_result[:200] if reflection_result else ""
            })
            
            logger.info("Cognition cycle complete")
            return reflection_result
            
        except Exception as e:
            logger.error(f"Slow loop error: {e}")
            return None
    
    # ─────────────────────────────────────────────────────────────
    # DREAM LOOP - Background Learning (30-60min)
    # ─────────────────────────────────────────────────────────────
    
    async def dream_loop(self):
        """Dream loop - memory replay, pattern discovery"""
        try:
            now = datetime.now()
            if (now - self.last_dream).total_seconds() < self.dream_interval:
                return None
            
            self.last_dream = now
            
            logger.info("Dream cycle starting...")
            
            # Analyze recent memories
            if self.short_term_memory:
                recent = self.short_term_memory[-10:]
                
                # Find patterns (placeholder)
                patterns = self.analyze_patterns(recent)
                
                # Generate insights
                insight = f"After {len(self.short_term_memory)} cycles, patterns emerging: {patterns}"
                
                logger.info(f"Dream insight: {insight}")
                
                # Auto-generate goals from patterns
                if "trading" in patterns:
                    self.goal_engine.create_from_template("improve_strategy", {"asset": "portfolio"})
                
                # Compress old memories
                if len(self.short_term_memory) > self.max_short_term:
                    self.short_term_memory = self.short_term_memory[-50:]
                    logger.info("Memory compressed")
            
            logger.info("Dream cycle complete")
            return True
            
        except Exception as e:
            logger.error(f"Dream loop error: {e}")
            return None
    
    # ─────────────────────────────────────────────────────────────
    # HYBRID MODE (Local-First)
    # ─────────────────────────────────────────────────────────────
    
    def set_online_mode(self, online: bool):
        """Switch between online and offline mode"""
        self.is_online = online
        self.last_sync = datetime.now()
        logger.info(f"Mode changed: {'ONLINE' if online else 'OFFLINE'}")
    
    def sync_data(self) -> bool:
        """Sync data when online - placeholder for real API calls"""
        if not self.is_online:
            logger.warning("Cannot sync: offline mode")
            return False
        
        # Placeholder - real implementation would sync:
        # - Market data
        # - Goal templates
        # - Brain updates
        # - Memory backup
        
        self.last_sync = datetime.now()
        logger.info("Data synced (placeholder)")
        return True
    
    def get_status(self) -> Dict[str, Any]:
        """Get Nova's current status"""
        return {
            "identity": self.core_identity.get("name", "Nova"),
            "cycles": self.cycle_count,
            "memory_items": len(self.short_term_memory),
            "is_online": self.is_online,
            "last_sync": self.last_sync.isoformat() if self.last_sync else None,
            "goals": self.goal_engine.get_summary(),
            "brain_bus": self.brain_bus.get_metrics(),
            "observer": self.observer.get_health_summary()
        }
    
    # ─────────────────────────────────────────────────────────────
    # MEMORY SYSTEM
    # ─────────────────────────────────────────────────────────────
    
    def store_memory(self, experience: Dict[str, Any]):
        """Store experience in short-term memory"""
        self.short_term_memory.append(experience)
        
        # Trim if needed
        if len(self.short_term_memory) > self.max_short_term:
            self.short_term_memory = self.short_term_memory[-self.max_short_term:]
    
    def analyze_patterns(self, memories: List[Dict]) -> str:
        """Analyze patterns in recent memories"""
        if not memories:
            return "no patterns"
        
        types = [m.get("type", "unknown") for m in memories]
        cognition_count = types.count("cognition")
        trading_count = types.count("trading")
        
        return f"cognition:{cognition_count}, trading:{trading_count}"
    
    # ─────────────────────────────────────────────────────────────
    # MAIN RUN LOOP
    # ─────────────────────────────────────────────────────────────
    
    async def run(self, duration_seconds: int = 60):
        """Run Nova Core for specified duration"""
        logger.info(f"Starting Nova Core for {duration_seconds} seconds...")
        
        start_time = time.time()
        
        while self.is_alive and (time.time() - start_time) < duration_seconds:
            # Always run fast loop
            await self.fast_loop()
            
            # Occasionally run slow loop
            await self.slow_loop()
            
            # Rarely run dream loop
            await self.dream_loop()
            
            # Small sleep to prevent CPU hogging
            await asyncio.sleep(0.1)
        
        logger.info(f"Nova Core stopped after {self.cycle_count} cycles")
        
        return {
            "cycles": self.cycle_count,
            "memory_items": len(self.short_term_memory),
            "status": "complete"
        }
    
    async def run_forever(self):
        """Run Nova Core indefinitely"""
        logger.info("Starting Nova Core (infinite loop)...")
        
        while self.is_alive:
            await self.fast_loop()
            await self.slow_loop()
            await self.dream_loop()
            await asyncio.sleep(0.1)
    
    def stop(self):
        """Stop Nova Core"""
        logger.info("Stopping Nova Core...")
        self.is_alive = False


# ─────────────────────────────────────────────────────────────
# STANDALONE TEST
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    async def test():
        print("=== NOVA CORE TEST ===")
        
        core = NovaCore()
        
        # Run for 10 seconds
        result = await core.run(duration_seconds=10)
        
        print(f"\nResult: {result}")
        print(f"Memory: {len(core.short_term_memory)} items")
        
    asyncio.run(test())
