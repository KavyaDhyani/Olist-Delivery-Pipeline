import logging
import pandas as pd
from src.config import load_config
from src.logging_config import setup_logging
from src.ingest import ingest_raw_data
from src.retrieve import sql_retrieve
from src.validate import run_validations
from src.clean import clean_data
from src.transform import transform_data
from src.metrics import calculate_metrics
from src.publish import publish_outputs

def run(run_date, chaos=None):
    config = load_config()
    logger = setup_logging(config, run_date)
    
    logger.info(f"Pipeline started for run_date: {run_date}")
    if chaos:
        logger.info(f"Chaos mode enabled: {chaos}")
        
    # EXTRACT / INGEST
    datasets = ingest_raw_data(config)
    
    # Apply chaos before validation if requested
    if chaos == "missing_column":
        if "olist_orders_dataset" in datasets:
            datasets["olist_orders_dataset"] = datasets["olist_orders_dataset"].drop(columns=["order_status"])
    elif chaos == "duplicate_order":
        if "olist_orders_dataset" in datasets:
            orders = datasets["olist_orders_dataset"]
            dup = orders.iloc[[0]].copy()
            datasets["olist_orders_dataset"] = pd.concat([orders, dup], ignore_index=True)
    elif chaos == "stale_data":
        if "olist_orders_dataset" in datasets:
            datasets["olist_orders_dataset"]["order_purchase_timestamp"] = "2016-01-01 10:00:00"
            
    # VALIDATE
    validation_reports, has_critical_failure = run_validations(datasets)
    
    if has_critical_failure:
        logger.error("Critical validation failure detected. Pipeline stopping before publish.")
        return 1

    # CLEAN
    datasets = clean_data(datasets, validation_reports)
    
    # SQL RETRIEVAL
    sql_features = sql_retrieve(config, datasets)
    
    # TRANSFORM
    order_features = transform_data(datasets, config, sql_features)
    
    # METRICS
    metrics = calculate_metrics(order_features, run_date)
    
    # SAVE / PUBLISH
    publish_outputs(config, run_date, order_features, metrics, validation_reports)
    
    logger.info("Pipeline completed successfully.")
    return 0
