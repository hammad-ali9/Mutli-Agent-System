import os
from typing import List
from src.agents.specialized_agents import ChatGPTAgent, GrokAgent, GeminiAgent
from src.services.polymarket_service import PolymarketService
from src.database import Database
from src.models import PredictionOutput

class PredictionService:
    def __init__(self):
        self.db = Database()
        self.all_agents = [
            ChatGPTAgent(),
            GrokAgent(),
            GeminiAgent()
        ]

    def _get_active_agents(self):
        active = []
        inactive = []
        for agent in self.all_agents:
            if agent.has_valid_config():
                active.append(agent)
            else:
                inactive.append(agent.name)
        return active, inactive

    def run_battle(self, event_id: str):
        # 1. Fetch Event
        event = PolymarketService.get_event_details(event_id)
        if not event:
            print(f"Failed to fetch event {event_id}")
            return

        print(f"\n--- Starting Prediction Battle: {event.title} ---")
        self.db.save_event(event)

        # 2. Filter Active Agents
        active_agents, inactive_names = self._get_active_agents()
        if inactive_names:
            print(f"⚠️  Note: Skipping agents due to missing API keys: {', '.join(inactive_names)}")
        
        if not active_agents:
            print("❌ No agents are configured with API keys. Please update your .env file.")
            return

        # 3. Check Research API
        if not os.getenv("TAVILY_API_KEY"):
            print("⚠️  Warning: TAVILY_API_KEY is missing. Agents will not be able to perform research.")

        # 4. Run Agents independently
        predictions: List[PredictionOutput] = []
        for agent in active_agents:
            print(f"\n🤖 Agent {agent.name} ({agent.model_name}) is researching...")
            try:
                pred = agent.generate_prediction(event)
                self.db.save_prediction(agent.name, pred)
                predictions.append(pred)
                print(f"✅ Agent {agent.name} predicts {pred.prediction} with {pred.probability*100:.1f}% probability")
            except Exception as e:
                print(f"❌ Error for agent {agent.name}: {e}")

        return predictions
