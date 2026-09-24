import pandas as pd
import logging

logger = logging.getLogger("olist_pipeline")

def transform_data(datasets, config, sql_features):
    logger.info("Starting order-level transformation...")
    
    orders = datasets["olist_orders_dataset"]
    payments = datasets.get("olist_order_payments_dataset")
    reviews = datasets.get("olist_order_reviews_dataset")
    customers = datasets.get("olist_customers_dataset")

    order_features = orders.copy()
    
    # 1. Integrate SQL-derived features (Replaces manual order_items aggregation)
    if sql_features is not None:
        logger.info("Integrating SQL-derived order item features...")
        order_features = order_features.merge(sql_features, on="order_id", how="left", validate="one_to_one")

    # 2. Aggregate Payments
    if payments is not None:
        payment_features = payments.groupby("order_id").agg(
            payment_count=("payment_sequential", "count"),
            payment_method_count=("payment_type", "nunique"),
            total_payment=("payment_value", "sum"),
            max_installments=("payment_installments", "max")
        ).reset_index()
        order_features = order_features.merge(payment_features, on="order_id", how="left", validate="one_to_one")

    # 3. Aggregate Reviews
    if reviews is not None:
        review_features = reviews.groupby("order_id").agg(
            review_count=("review_id", "count"),
            average_review_score=("review_score", "mean")
        ).reset_index()
        order_features = order_features.merge(review_features, on="order_id", how="left", validate="one_to_one")

    # 4. Customers
    if customers is not None:
        customer_features = customers[["customer_id", "customer_unique_id", "customer_city", "customer_state"]]
        order_features = order_features.merge(customer_features, on="customer_id", how="left", validate="one_to_one")

    # 5. Timing features and lifecycle validation flags
    order_features["purchase_to_carrier_days"] = (
        order_features["order_delivered_carrier_date"] - order_features["order_purchase_timestamp"]
    ).dt.total_seconds() / (24 * 3600)
    
    order_features["carrier_to_delivery_days"] = (
        order_features["order_delivered_customer_date"] - order_features["order_delivered_carrier_date"]
    ).dt.total_seconds() / (24 * 3600)
    
    order_features["delivery_variance_days"] = (
        order_features["order_delivered_customer_date"] - order_features["order_estimated_delivery_date"]
    ).dt.total_seconds() / (24 * 3600)

    order_features["is_late"] = pd.Series(pd.NA, index=order_features.index, dtype="boolean")
    
    # KPI Population Rule
    valid_delivery = (
        order_features["order_status"].eq("delivered") &
        order_features["order_purchase_timestamp"].notna() &
        order_features["order_delivered_carrier_date"].notna() &
        order_features["order_delivered_customer_date"].notna() &
        order_features["order_estimated_delivery_date"].notna() &
        (order_features["order_delivered_carrier_date"] >= order_features["order_purchase_timestamp"]) &
        (order_features["order_delivered_customer_date"] >= order_features["order_delivered_carrier_date"])
    )
    
    order_features.loc[valid_delivery, "is_late"] = (
        order_features.loc[valid_delivery, "delivery_variance_days"] > 0
    )
    
    # 6. Configurable Seller Analysis
    # The config variable seller_min_orders was unused. Let's compute a metric for it.
    # To compute this, we need to know the number of delivered orders per seller.
    # We can get seller order counts from order_items.
    seller_min_orders = config["settings"].get("seller_min_orders", 10)
    logger.info(f"Applying seller threshold of {seller_min_orders}")
    
    order_items = datasets.get("olist_order_items_dataset")
    if order_items is not None:
        # Get delivered orders per seller
        delivered_orders = order_features[order_features["order_status"] == "delivered"][["order_id"]]
        delivered_items = order_items.merge(delivered_orders, on="order_id", how="inner")
        
        seller_counts = delivered_items.groupby("seller_id")["order_id"].nunique().reset_index(name="delivered_orders")
        valid_sellers = seller_counts[seller_counts["delivered_orders"] >= seller_min_orders]["seller_id"]
        
        # Tag order features with whether they involve a valid seller (for simple metric reporting)
        # Note: an order can have multiple sellers, so we just check if ANY seller in the order meets the threshold.
        order_sellers = order_items.groupby("order_id")["seller_id"].apply(lambda x: any(s in valid_sellers.values for s in x)).reset_index(name="has_valid_seller")
        order_features = order_features.merge(order_sellers, on="order_id", how="left")
        order_features["has_valid_seller"] = order_features["has_valid_seller"].fillna(False)

    logger.info(f"Transformation complete. Resulting order_features has {len(order_features)} rows.")
    return order_features
