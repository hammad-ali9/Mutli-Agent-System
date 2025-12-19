import sqlite3
import json
from typing import List
from src.agents.specialized_agents import BaseAgent
from src.agents.moderator_agent import ModeratorAgent
from src.models import DebateTurn
from src.database import Database

from src.services.voice_service import VoiceService

class DebateService:
    def __init__(self, agents: List[BaseAgent]):
        self.db = Database()
        self.moderator = ModeratorAgent()
        self.agents = {a.name: a for a in agents}
        self.voice_service = VoiceService()

    def _get_predictions_summary(self, event_id: str) -> str:
        with sqlite3.connect(self.db.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT agent_name, prediction, probability, data FROM predictions WHERE event_id = ?", (event_id,))
            rows = cursor.fetchall()
            
            summary = ""
            for name, pred, prob, data_str in rows:
                data = json.loads(data_str)
                facts = "\n".join([f"- {f['claim']} ({f['source']})" for f in data['key_facts']])
                summary += f"Agent: {name}\nPrediction: {pred}\nProbability: {prob*100}%\nRationale: {data['rationale']}\nKey Facts:\n{facts}\n\n"
            return summary

    def run_debate(self, event_id: str, rounds: int = 3, use_voice: bool = False):
        # 1. Fetch event and predictions
        with sqlite3.connect(self.db.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT title FROM events WHERE id = ?", (event_id,))
            event_row = cursor.fetchone()
            if not event_row:
                print("Event not found.")
                return
            event_title = event_row[0]

        predictions_summary = self._get_predictions_summary(event_id)
        if not predictions_summary:
            print("No predictions found for this event. Run 'predict' first.")
            return

        print(f"\n--- Starting Debate: {event_title} ---")
        transcript = []
        transcript_str = "No turns yet."

        # 2. Iterative turns
        for r in range(rounds):
            print(f"\n--- Round {r+1} ---")
            
            # Moderator provides direction
            direction = self.moderator.provide_direction(event_title, predictions_summary, transcript_str)
            print(f"Moderator: {direction}\n")
            
            if use_voice:
                self.voice_service.generate_audio(direction, "Moderator", f"{event_id}_round_{r+1}_moderator")

            # In a real debate, the moderator would pick the agent. 
            for name, agent in self.agents.items():
                if not agent.has_valid_config():
                    continue
                
                print(f"{name} is responding...")
                
                # Format other predictions for context
                other_preds = "\n".join([p for p in predictions_summary.split("\n\n") if name not in p])
                
                # Get response
                response = agent.debate_turn(direction, transcript_str, predictions_summary, other_preds)
                print(f"{name}: {response}\n")
                
                if use_voice:
                    # Clean agent name for filename
                    safe_name = name.replace(" ", "_")
                    self.voice_service.generate_audio(response, name, f"{event_id}_round_{r+1}_{safe_name}")

                # Update transcript
                turn = DebateTurn(agent_name=name, content=response)
                transcript.append(turn)
                
                # Update visual transcript string
                transcript_str = "\n".join([f"{t.agent_name}: {t.content}" for t in transcript])

        print("\n--- Debate Concluded ---")
        return transcript
