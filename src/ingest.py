import pandas as pd
from pathlib import Path
import logging

logger = logging.getLogger("olist_pipeline")

def ingest_raw_data(config):
    raw_dir = Path(config["paths"]["raw_dir"])
    expected_files = config["files"]["expected"]
    
    datasets = {}
    missing_files = []
    
    logger.info("Starting ingestion of raw CSV files...")
    
    for filename in expected_files:
        filepath = raw_dir / filename
        if not filepath.exists():
            missing_files.append(filename)
            logger.error(f"Missing required file: {filename}")
        else:
            df = pd.read_csv(filepath)
            name = filename.replace(".csv", "")
            datasets[name] = df
            logger.info(f"Loaded {filename}: {len(df)} rows")
            
    if missing_files:
        raise FileNotFoundError(f"Missing required source files: {missing_files}")
        
    return datasets
