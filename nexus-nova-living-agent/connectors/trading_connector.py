"""
Trading Connector - Bridges brain decisions to trading execution
"""
import sys
import os

# Add paths for imports
sys.path.insert(0, os.path.expanduser("~/.nova"))
sys.path.insert(0, os.path.expanduser("~/.openclaw/workspace/nexus-nova-living-agent"))

class TradingConnector:
    def __init__(self):
        self.broker = None
        self.brain_manager = None
        self.learning_engine = None
    
    def connect_brains(self, brain_manager):
        """Connect the brain system"""
        self.brain_manager = brain_manager
    
    def connect_broker(self, adapter):
        """Connect the broker adapter"""
        self.broker = adapter
    
    def connect_learning(self, learning_engine):
        """Connect the learning system"""
        self.learning_engine = learning_engine
    
    def analyze_market(self, market_data):
        """Run brains on market data"""
        if not self.brain_manager:
            raise Exception("Brains not connected")
        
        # Run the brain system
        result = self.brain_manager.run(market_data, {})
        return result
    
    def execute_decision(self, decision, market_data=None):
        """
        Execute a trading decision.
        Returns: trade result
        """
        if not self.broker:
            raise Exception("Broker not connected")
        
        if not decision or decision.get("action") == "HOLD":
            return {"status": "skipped", "reason": "no valid signal"}
        
        if decision.get("action") == "HALT":
            return {"status": "halted", "reason": "guardian halt"}
        
        action = decision.get("action", "").lower()
        
        # Get market for trading
        markets = self.broker.get_markets(limit=10)
        if not markets:
            return {"status": "error", "reason": "no markets available"}
        
        # Pick a market (in production, this would be smarter)
        market = markets[0]
        
        try:
            # Execute trade
            result = self.broker.place_order(
                market_id=market["id"],
                side="yes" if action == "buy" else "no",
                amount=10.0,  # Default position size
                reasoning=f"Brain decision: {decision.get('action')}, confidence: {decision.get('confidence', 0)}"
            )
            
            return {
                "status": "success",
                "trade_id": result.get("trade_id"),
                "action": action,
                "market": market.get("question"),
                "shares": result.get("shares_bought"),
                "cost": result.get("cost")
            }
            
        except Exception as e:
            return {"status": "error", "reason": str(e)}
    
    def run_cycle(self, market_data):
        """
        Full cycle: analyze -> decide -> execute -> learn
        """
        # Step 1: Analyze with brains
        decision = self.analyze_market(market_data)
        
        # Step 2: Execute if signal
        if decision.get("action") not in ["HOLD", "HALT"]:
            result = self.execute_decision(decision, market_data)
            
            # Step 3: Learn from result
            if self.learning_engine and result.get("status") == "success":
                # Would update learning with actual P&L when position resolves
                pass
            
            return {
                "decision": decision,
                "execution": result
            }
        
        return {
            "decision": decision,
            "execution": {"status": "skipped"}
        }
    
    def get_status(self):
        """Get system status"""
        status = {
            "brains": self.brain_manager is not None,
            "broker": self.broker is not None,
            "learning": self.learning_engine is not None
        }
        
        if self.broker:
            try:
                health = self.broker.health_check()
                status["broker_healthy"] = health.get("valid", False)
            except:
                status["broker_healthy"] = False
        
        return status
