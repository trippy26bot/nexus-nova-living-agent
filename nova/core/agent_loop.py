"""
NOVA Agent Loop - The continuous thinking cycle
This makes NOVA a living, thinking entity
"""
import time
from datetime import datetime


class AgentLoop:
    """
    The main loop that keeps NOVA alive and thinking.
    Runs: observe -> think -> decide -> act -> remember -> reflect
    """
    
    def __init__(self, meta_brain, memory, connector=None):
        self.meta_brain = meta_brain
        self.memory = memory
        self.connector = connector
        self.running = False
        self.cycle_count = 0
        self.last_decision = None
    
    def start(self, interval=60):
        """
        Start the agent loop.
        interval: seconds between cycles
        """
        self.running = True
        print(f"🚀 NOVA Agent Loop started (interval: {interval}s)")
        
        while self.running:
            try:
                self.cycle(interval)
            except KeyboardInterrupt:
                print("\n⚠️ Stopping NOVA...")
                self.running = False
            except Exception as e:
                print(f"❌ Error in cycle: {e}")
                time.sleep(5)  # Brief pause before retry
    
    def stop(self):
        """Stop the agent loop"""
        self.running = False
    
    def cycle(self, interval=60):
        """One complete thinking cycle"""
        self.cycle_count += 1
        print(f"\n🧠 Cycle {self.cycle_count}")
        
        # Step 1: Observe (get context)
        context = self.observe()
        
        # Step 2: Think (process through brains)
        decision = self.think(context)
        
        # Step 3: Decide (meta brain makes final call)
        final_decision = self.decide(context, decision)
        
        # Step 4: Act (execute if needed)
        result = self.act(final_decision)
        
        # Step 5: Remember (store in memory)
        self.remember(context, final_decision, result)
        
        # Step 6: Reflect (optional)
        reflection = self.reflect()
        
        # Store last decision
        self.last_decision = final_decision
        
        # Wait for next cycle
        time.sleep(interval)
    
    def observe(self):
        """Observe the world - gather context"""
        context = {
            "timestamp": datetime.utcnow().isoformat(),
            "cycle": self.cycle_count,
            # In production, this would fetch real market data
            "price_change": 0,
            "volatility": 1,
            "sentiment": 0,
            "liquidity": 5,
            "risk_level": 0.3
        }
        
        # Try to get real data from connector if available
        if self.connector and hasattr(self.connector, 'broker') and self.connector.broker:
            try:
                # Get current market state
                positions = self.connector.broker.get_positions()
                context["open_positions"] = positions.get("position_counts", {}).get("active", 0)
            except:
                pass
        
        return context
    
    def think(self, context):
        """Think through the context using brains"""
        # Get memory context
        memory_context = {
            "system_health": 1.0,
            "portfolio_exposure": self.memory.remember_short("portfolio_exposure", 0.5)
        }
        
        # Process through meta brain
        decision = self.meta_brain.decide(context, memory_context)
        
        return decision
    
    def decide(self, context, brain_decision):
        """Make final decision (meta brain handles this)"""
        # The meta brain already made the decision in think()
        return brain_decision
    
    def act(self, decision):
        """Act on the decision"""
        if not decision:
            return {"status": "no_decision"}
        
        action = decision.get("action", "HOLD")
        
        # Don't act on HOLD or HALT
        if action in ["HOLD", "HALT"]:
            return {
                "status": "skipped",
                "action": action,
                "reason": decision.get("reason", "brain consensus")
            }
        
        # Execute trade if connector available
        if self.connector:
            try:
                result = self.connector.execute_decision(decision)
                return result
            except Exception as e:
                return {"status": "error", "reason": str(e)}
        
        return {
            "status": "no_connector",
            "decision": decision
        }
    
    def remember(self, context, decision, result):
        """Store this cycle in memory"""
        # Store in short term
        self.memory.store_short(f"cycle_{self.cycle_count}", {
            "context": context,
            "decision": decision,
            "result": result
        })
        
        # Record episode
        self.memory.store_episode(context, decision, result)
        
        # Important decisions go to long term
        if decision.get("confidence", 0) > 0.7:
            self.memory.store_long(
                "significant_decision",
                f"Cycle {self.cycle_count}: {decision.get('action')} with {decision.get('confidence'):.2f} confidence",
                importance=0.8
            )
    
    def reflect(self):
        """Reflect on recent activity"""
        if self.cycle_count % 10 == 0:  # Every 10 cycles
            reflection = self.meta_brain.reflect()
            memory_reflection = self.memory.reflect()
            
            return {
                "meta_reflection": reflection,
                "memory_reflection": memory_reflection
            }
        
        return None
    
    def get_status(self):
        """Get agent status"""
        return {
            "running": self.running,
            "cycles": self.cycle_count,
            "last_decision": self.last_decision.get("action") if self.last_decision else None,
            "memory_status": self.memory.get_status()
        }
