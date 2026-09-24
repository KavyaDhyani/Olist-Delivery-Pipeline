import argparse
import sys
from src.pipeline import run

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the Olist Delivery Pipeline")
    parser.add_argument("--run-date", required=True, help="Run date in YYYY-MM-DD format")
    parser.add_argument("--chaos", choices=["missing_column", "duplicate_order", "stale_data"], help="Inject chaos to test validation")
    
    args = parser.parse_args()
    exit_code = run(args.run_date, args.chaos)
    sys.exit(exit_code)
