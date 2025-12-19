import requests
from typing import Optional
from src.models import EventMetadata

class PolymarketService:
    BASE_URL = "https://gamma-api.polymarket.com"

    @classmethod
    def get_event_details(cls, event_id: str) -> Optional[EventMetadata]:
        """
        Fetches event details from the Polymarket Gamma API.
        Note: event_id here refers to the 'id' in Gamma API, which might be different from CLOB ID.
        """
        try:
            # First, try to get the event by ID
            response = requests.get(f"{cls.BASE_URL}/events/{event_id}")
            if response.status_code != 200:
                print(f"Error fetching event {event_id}: {response.status_code}")
                return None
            
            data = response.json()
            
            # Extract relevant fields
            # Note: Gamma API structure might vary slightly, adapting to common fields
            return EventMetadata(
                event_id=str(data.get("id")),
                title=data.get("title", ""),
                description=data.get("description", ""),
                resolution_rules=data.get("rules", ""),
                market_probability=data.get("market_probability"), # This might come from markets list
                liquidity=data.get("liquidity"),
                resolution_date=data.get("ends_at", "")
            )
        except Exception as e:
            print(f"Exception fetching event: {e}")
            return None

    @classmethod
    def search_tech_events(cls, query: str = "technology"):
        """
        Future: Automated discovery of tech events.
        """
        pass
