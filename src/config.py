import yaml
import os
from pathlib import Path

def load_config():
    root_dir = Path(__file__).resolve().parent.parent
    config_path = root_dir / "config" / "config.yaml"
    
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
        
    # Resolve paths relative to project root ONLY for directories and db path
    for key in ["raw_dir", "staging_dir", "processed_dir", "logs_dir", "db_path"]:
        if key in config["paths"]:
            config["paths"][key] = str(root_dir / config["paths"][key])
        
    # Environment overrides
    if "LOG_LEVEL" in os.environ:
        config["settings"]["log_level"] = os.environ["LOG_LEVEL"]
    if "SELLER_MIN_ORDERS" in os.environ:
        config["settings"]["seller_min_orders"] = int(os.environ["SELLER_MIN_ORDERS"])
        
    return config
