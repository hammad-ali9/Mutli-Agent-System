import argparse
from dotenv import load_dotenv
from src.services.prediction_service import PredictionService

def main():
    load_dotenv()
    
    parser = argparse.ArgumentParser(description="AI Prediction Battle")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Full Battle command (V0 + V1)
    run_parser = subparsers.add_parser("run", help="Run a full battle (Research + Debate) for an event")
    run_parser.add_argument("identifier", type=str, help="Polymarket Event ID, Slug, or URL")
    run_parser.add_argument("--rounds", type=int, default=2, help="Number of debate rounds")

    # Discover command
    discover_parser = subparsers.add_parser("discover", help="Discover active tech events on Polymarket")
    discover_parser.add_argument("--limit", type=int, default=10, help="Number of events to show")

    args = parser.parse_args()

    if args.command == "run":
        from src.services.prediction_service import PredictionService
        from src.services.debate_service import DebateService
        
        # 1. Prediction Phase (V0)
        pred_service = PredictionService()
        predictions = pred_service.run_battle(args.identifier)
        
        if not predictions:
            print("❌ Prediction phase failed. Cannot proceed to debate.")
            return

        # 2. Debate Phase (V1)
        print("\n" + "="*50)
        print("💡 Transitioning to Text Debate Layer (V1)...")
        print("="*50)
        
        debate_service = DebateService(pred_service.all_agents)
        debate_service.run_debate(args.identifier, rounds=args.rounds)
        
    elif args.command == "discover":
        from src.services.polymarket_service import PolymarketService
        print("\n🔍 Searching for active tech events on Polymarket...")
        events = PolymarketService.search_tech_events(limit=args.limit)
        if not events:
            print("No events found.")
        else:
            print(f"{'ID':<10} | {'Title':<45} | {'Ends'}")
            print("-" * 75)
            for e in events:
                date_str = e.resolution_date.split("T")[0] if "T" in e.resolution_date else e.resolution_date
                print(f"{e.event_id:<10} | {e.title[:45]:<45} | {date_str}")
            print("\n💡 Tip: Use 'python main.py run <ID|slug|url>' to start a battle for one of these events.")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
