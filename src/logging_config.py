import logging
import sys
from pathlib import Path
from datetime import datetime

def setup_logging(config, run_date=None):
    log_level = getattr(logging, config["settings"]["log_level"].upper(), logging.INFO)
    
    logger = logging.getLogger("olist_pipeline")
    logger.setLevel(log_level)
    
    if logger.hasHandlers():
        logger.handlers.clear()
        
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Console handler
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(log_level)
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    
    # File handler
    if run_date:
        logs_dir = Path(config["paths"]["logs_dir"])
        logs_dir.mkdir(parents=True, exist_ok=True)
        log_file = logs_dir / f"pipeline_{run_date}.log"
        
        fh = logging.FileHandler(log_file)
        fh.setLevel(log_level)
        fh.setFormatter(formatter)
        logger.addHandler(fh)
        
    return logger
