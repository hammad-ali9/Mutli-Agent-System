import os
from pathlib import Path
from openai import OpenAI
from typing import Dict

class VoiceService:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.output_dir = Path("output/audio")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Voce mapping for agents
        self.voice_map = {
            "Agent A": "shimmer",
            "Agent B": "onyx",
            "Agent C": "fable",
            "Moderator": "nova"
        }

    def generate_audio(self, text: str, agent_name: str, filename: str) -> str:
        """
        Generates TTS audio for a specific agent.
        """
        voice = self.voice_map.get(agent_name, "alloy")
        output_path = self.output_dir / f"{filename}.mp3"
        
        try:
            response = self.client.audio.speech.create(
                model="tts-1",
                voice=voice,
                input=text
            )
            response.stream_to_file(output_path)
            return str(output_path)
        except Exception as e:
            print(f"Error generating audio for {agent_name}: {e}")
            return ""
