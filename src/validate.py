import logging
import pandas as pd

logger = logging.getLogger("olist_pipeline")

def run_validations(datasets):
    logger.info("Starting validation checks...")
    reports = []
    has_critical_failure = False
    
    orders = datasets.get("olist_orders_dataset")
    items = datasets.get("olist_order_items_dataset")
    payments = datasets.get("olist_order_payments_dataset")
    
    # 1. Uniqueness
    if orders is not None:
        duplicate_orders = orders["order_id"].duplicated().sum()
        if duplicate_orders > 0:
            reports.append({
                "check_name": "orders_uniqueness",
                "severity": "WARN",
                "status": "FAIL",
                "message": f"Found {duplicate_orders} duplicate order_ids."
            })
            logger.warning(f"Validation WARN: Found {duplicate_orders} duplicate order_ids.")
        else:
            reports.append({"check_name": "orders_uniqueness", "severity": "PASS", "status": "PASS"})
            
        # Schema check for all datasets
        required_cols = {
            "olist_orders_dataset": ['order_id', 'customer_id', 'order_status', 'order_purchase_timestamp'],
            "olist_order_items_dataset": ['order_id', 'order_item_id', 'product_id', 'seller_id', 'price'],
            "olist_order_payments_dataset": ['order_id', 'payment_value']
        }
        for ds_name, cols in required_cols.items():
            ds = datasets.get(ds_name)
            if ds is not None:
                missing_cols = [c for c in cols if c not in ds.columns]
                if missing_cols:
                    has_critical_failure = True
                    reports.append({"check_name": f"{ds_name}_schema", "severity": "FAIL", "status": "FAIL", "message": f"Missing columns: {missing_cols}"})
                    logger.error(f"Validation FAIL: {ds_name} missing {missing_cols}")
                else:
                    reports.append({"check_name": f"{ds_name}_schema", "severity": "PASS", "status": "PASS"})
            
        # Freshness Check
        if "order_purchase_timestamp" in orders.columns:
            try:
                max_date = pd.to_datetime(orders["order_purchase_timestamp"]).max()
                # Olist data goes up to late 2018.
                if max_date < pd.Timestamp("2018-01-01"):
                    has_critical_failure = True
                    reports.append({"check_name": "freshness", "severity": "FAIL", "status": "FAIL", "message": f"Data is stale. Max date: {max_date}"})
                    logger.error("Validation FAIL: Data is stale.")
                else:
                    reports.append({"check_name": "freshness", "severity": "PASS", "status": "PASS"})
            except Exception as e:
                logger.warning("Could not parse dates for freshness check.")
                
        # Referential Integrity
        if items is not None:
            orphans = (~items["order_id"].isin(orders["order_id"])).sum()
            if orphans > 0:
                has_critical_failure = True
                reports.append({"check_name": "fk_items_orders", "severity": "FAIL", "status": "FAIL", "message": f"{orphans} item rows without order."})
                logger.error(f"Validation FAIL: {orphans} orphan order items.")
            else:
                reports.append({"check_name": "fk_items_orders", "severity": "PASS", "status": "PASS"})
                
        if payments is not None:
            orphans = (~payments["order_id"].isin(orders["order_id"])).sum()
            if orphans > 0:
                has_critical_failure = True
                reports.append({"check_name": "fk_payments_orders", "severity": "FAIL", "status": "FAIL", "message": f"{orphans} payment rows without order."})
                logger.error(f"Validation FAIL: {orphans} orphan payments.")
            else:
                reports.append({"check_name": "fk_payments_orders", "severity": "PASS", "status": "PASS"})
                
        # Chronology validation
        if "order_delivered_carrier_date" in orders.columns and "order_purchase_timestamp" in orders.columns:
            invalid_carrier = (pd.to_datetime(orders["order_delivered_carrier_date"], errors='coerce') < pd.to_datetime(orders["order_purchase_timestamp"], errors='coerce')).sum()
            if invalid_carrier > 0:
                reports.append({"check_name": "chrono_carrier", "severity": "WARN", "status": "FAIL", "message": f"{invalid_carrier} orders with carrier before purchase."})
                logger.warning(f"Validation WARN: {invalid_carrier} chronological violations (carrier < purchase).")
            else:
                reports.append({"check_name": "chrono_carrier", "severity": "PASS", "status": "PASS"})

    return reports, has_critical_failure
