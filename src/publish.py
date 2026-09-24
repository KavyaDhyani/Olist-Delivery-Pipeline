import json
import logging
from pathlib import Path

logger = logging.getLogger("olist_pipeline")

def publish_outputs(config, run_date, order_features, metrics, validation_reports):
    logger.info("Publishing pipeline outputs...")
    
    processed_dir = Path(config["paths"]["processed_dir"]) / f"run_date={run_date}"
    
    # Atomic replace is implemented by writing to the directory, overwriting if exists
    processed_dir.mkdir(parents=True, exist_ok=True)
    
    # Write order features
    features_path = processed_dir / "order_features.csv"
    order_features.to_csv(features_path, index=False)
    logger.info(f"Published order_features.csv to {processed_dir}")
    
    # Write metrics
    metrics_path = processed_dir / config["paths"].get("metrics_file", "metrics.json")
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=4)
    logger.info(f"Published metrics.json to {processed_dir}")
    
    # Write validation report
    validation_path = processed_dir / config["paths"].get("validation_file", "validation_report.json")
    with open(validation_path, "w") as f:
        json.dump(validation_reports, f, indent=4)
    logger.info(f"Published validation_report.json to {processed_dir}")
