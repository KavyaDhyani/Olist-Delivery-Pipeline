import logging

logger = logging.getLogger("olist_pipeline")

def clean_data(datasets, validation_reports):
    logger.info("Starting data cleaning...")
    
    orders = datasets.get("olist_orders_dataset")
    if orders is not None:
        # Deduplicate orders as per agreed rule in Instructor_Readme
        initial_len = len(orders)
        orders = orders.drop_duplicates(subset=["order_id"])
        if len(orders) < initial_len:
            logger.info(f"Cleaned {initial_len - len(orders)} duplicate orders.")
        datasets["olist_orders_dataset"] = orders
        
        # Convert dates
        date_cols = [
            "order_purchase_timestamp",
            "order_approved_at",
            "order_delivered_carrier_date",
            "order_delivered_customer_date",
            "order_estimated_delivery_date"
        ]
        import pandas as pd
        for col in date_cols:
            if col in orders.columns:
                orders[col] = pd.to_datetime(orders[col], errors="coerce")
                
    return datasets
