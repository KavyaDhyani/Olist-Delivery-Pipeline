// dashboard.js

// Static data object sourced directly from the final validated pipeline outputs.
// This ensures GitHub Pages compatibility without requiring an active backend or complex path resolution.
const metricsData = {
    lateDeliveryRate: 8.12,         // 8.12%
    medianDeliveryVariance: -11.93, // days
    purchaseToCarrier: 2.20,        // days
    carrierToCustomer: 7.10,        // days
    validatedOrders: 96281          // population
};

document.addEventListener('DOMContentLoaded', () => {
    
    // 1. Populate top-level metrics
    document.getElementById('val-late-rate').textContent = metricsData.lateDeliveryRate + '%';
    document.getElementById('val-variance').textContent = metricsData.medianDeliveryVariance + ' days';
    document.getElementById('val-p2c').textContent = metricsData.purchaseToCarrier + ' days';
    document.getElementById('val-c2c').textContent = metricsData.carrierToCustomer + ' days';
    document.getElementById('val-population').textContent = metricsData.validatedOrders.toLocaleString();

    // 2. Populate Fulfillment Stage Visualization
    // We scale the bars relative to the maximum stage duration for a clean visual.
    const maxStage = Math.max(metricsData.purchaseToCarrier, metricsData.carrierToCustomer);
    
    const p2cPercent = (metricsData.purchaseToCarrier / maxStage) * 100;
    document.getElementById('bar-p2c').style.width = p2cPercent + '%';
    document.getElementById('text-p2c').textContent = metricsData.purchaseToCarrier + 'd';

    const c2cPercent = (metricsData.carrierToCustomer / maxStage) * 100;
    document.getElementById('bar-c2c').style.width = c2cPercent + '%';
    document.getElementById('text-c2c').textContent = metricsData.carrierToCustomer + 'd';

    // 3. Populate Delivery Performance Visualization
    const onTimeRate = (100 - metricsData.lateDeliveryRate).toFixed(2);
    
    document.getElementById('bar-ontime').style.width = onTimeRate + '%';
    document.getElementById('text-ontime').textContent = onTimeRate + '%';

    document.getElementById('bar-late').style.width = metricsData.lateDeliveryRate + '%';
    document.getElementById('text-late').textContent = metricsData.lateDeliveryRate + '%';
});
