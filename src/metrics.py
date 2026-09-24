import pandas as pd
import logging

logger = logging.getLogger("olist_pipeline")

def calculate_metrics(order_features, run_date):
    logger.info("Calculating business metrics...")
    
    validated = order_features["is_late"].notna()
    population_size = int(validated.sum())
    
    late_rate = float(order_features.loc[validated, "is_late"].mean())
    median_variance = float(order_features.loc[validated, "delivery_variance_days"].median())
    median_purchase_carrier = float(order_features.loc[validated, "purchase_to_carrier_days"].median())
    median_carrier_customer = float(order_features.loc[validated, "carrier_to_delivery_days"].median())
    
    metrics = [
        {
            "metric": "Late delivery rate",
            "value": late_rate,
            "denominator": population_size,
            "definition": "Percentage of validated delivered orders arriving after the estimated delivery date.",
            "calculation_run": run_date
        },
        {
            "metric": "Median delivery variance (days)",
            "value": median_variance,
            "denominator": population_size,
            "definition": "Median days between actual delivery and estimated delivery. Positive means late.",
            "calculation_run": run_date
        },
        {
            "metric": "Median purchase to carrier (days)",
            "value": median_purchase_carrier,
            "denominator": population_size,
            "definition": "Median days from purchase to carrier handoff.",
            "calculation_run": run_date
        },
        {
            "metric": "Median carrier to customer (days)",
            "value": median_carrier_customer,
            "denominator": population_size,
            "definition": "Median days from carrier handoff to customer delivery.",
            "calculation_run": run_date
        }
    ]
    
    if "has_valid_seller" in order_features.columns:
        valid_seller_mask = validated & order_features["has_valid_seller"]
        valid_seller_pop = int(valid_seller_mask.sum())
        if valid_seller_pop > 0:
            seller_late_rate = float(order_features.loc[valid_seller_mask, "is_late"].mean())
            metrics.append({
                "metric": "Late delivery rate (Threshold Sellers)",
                "value": seller_late_rate,
                "denominator": valid_seller_pop,
                "definition": "Late delivery rate for orders involving sellers meeting the minimum delivered order threshold.",
                "calculation_run": run_date
            })
    
    logger.info(f"Calculated {len(metrics)} metrics for population of {population_size}.")
    return metrics
