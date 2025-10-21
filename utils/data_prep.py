from datetime import datetime
from collections import defaultdict

def calculate_basic_stats(transactions):
    """Pre-calculate common statistics from transaction data"""
    if not transactions or "transactions" not in transactions:
        return {}
    
    transaction_list = transactions["transactions"]
    
    if not transaction_list:
        return {
            "total_transactions": 0,
            "total_revenue": 0,
            "average_order_value": 0
        }
    
    total_revenue = sum(t.get("total_amount", 0) for t in transaction_list)
    total_transactions = len(transaction_list)
    avg_order_value = total_revenue / total_transactions if total_transactions > 0 else 0
    
    return {
        "total_transactions": total_transactions,
        "total_revenue": total_revenue,
        "average_order_value": avg_order_value
    }

def aggregate_product_sales(transactions):
    """Aggregate sales data by product"""
    if not transactions or "transactions" not in transactions:
        return []
    
    product_sales = defaultdict(lambda: {"quantity": 0, "revenue": 0})
    
    for transaction in transactions["transactions"]:
        for item in transaction.get("items", []):
            product_id = item.get("product_id")
            product_name = item.get("name")
            quantity = item.get("quantity", 0)
            price = item.get("price", 0)
            
            key = f"{product_id}_{product_name}"
            product_sales[key]["name"] = product_name
            product_sales[key]["quantity"] += quantity
            product_sales[key]["revenue"] += price * quantity
    
    # Convert to list and sort by revenue
    sales_list = [
        {
            "name": data["name"],
            "quantity": data["quantity"],
            "revenue": data["revenue"]
        }
        for data in product_sales.values()
    ]
    
    return sorted(sales_list, key=lambda x: x["revenue"], reverse=True)

def get_low_stock_products(inventory, threshold=10):
    """Get products with stock below threshold"""
    if not inventory or "products" not in inventory:
        return []
    
    low_stock = [
        {
            "id": p.get("id"),
            "name": p.get("name"),
            "quantity": p.get("quantity"),
            "price": p.get("price"),
            "category": p.get("category")
        }
        for p in inventory["products"]
        if p.get("quantity", 0) < threshold
    ]
    
    return sorted(low_stock, key=lambda x: x["quantity"])

def aggregate_by_category(inventory):
    """Aggregate inventory by category"""
    if not inventory or "products" not in inventory:
        return []
    
    category_stats = defaultdict(lambda: {"count": 0, "total_value": 0, "total_stock": 0})
    
    for product in inventory["products"]:
        category = product.get("category", "Unknown")
        price = product.get("price", 0)
        quantity = product.get("quantity", 0)
        
        category_stats[category]["count"] += 1
        category_stats[category]["total_value"] += price * quantity
        category_stats[category]["total_stock"] += quantity
    
    # Convert to list
    result = [
        {
            "category": category,
            "product_count": stats["count"],
            "total_value": stats["total_value"],
            "total_stock": stats["total_stock"]
        }
        for category, stats in category_stats.items()
    ]
    
    return sorted(result, key=lambda x: x["total_value"], reverse=True)

def get_promo_usage_stats(transactions, promocodes):
    """Calculate promo code usage statistics"""
    if not transactions or "transactions" not in transactions:
        return []
    
    promo_usage = defaultdict(int)
    
    for transaction in transactions["transactions"]:
        promo_code = transaction.get("promo_code")
        if promo_code:
            promo_usage[promo_code] += 1
    
    # Get promo code details
    promo_details = {}
    if promocodes and "codes" in promocodes:
        for promo in promocodes["codes"]:
            code = promo.get("code")
            promo_details[code] = {
                "discount_percent": promo.get("discount_percent"),
                "description": promo.get("description")
            }
    
    # Combine usage with details
    result = []
    for code, usage_count in promo_usage.items():
        result.append({
            "code": code,
            "usage_count": usage_count,
            "discount_percent": promo_details.get(code, {}).get("discount_percent", 0),
            "description": promo_details.get(code, {}).get("description", "")
        })
    
    return sorted(result, key=lambda x: x["usage_count"], reverse=True)
