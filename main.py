import argparse
from dotenv import load_dotenv
from src.services.prediction_service import PredictionService

def main():
    load_dotenv()
    
    parser = argparse.ArgumentParser(description="AI Prediction Battle - Tech Events")
    subparsers = parser.add_subparsers(dest="command")

    # Predict command
    predict_parser = subparsers.add_parser("predict", help="Run a prediction battle for a given event ID")
    predict_parser.add_argument("event_id", type=str, help="Polymarket Gamma Event ID")

    args = parser.parse_args()

    if args.command == "predict":
        service = PredictionService()
        service.run_battle(args.event_id)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
