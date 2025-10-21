#!/usr/bin/env python3
"""
Update product prices based on transaction history and configured pricing strategies

This script:
1. Loads all products from inventory.json
2. Loads all transactions from transactions.json
3. Applies dynamic pricing strategies (popularity, clearance, flash)
4. Updates inventory.json with new prices
5. Generates a report of price changes
"""

import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import read_data, write_data
from services.pricing_engine import PricingEngine


class SimpleProduct:
    """Lightweight product class without Streamlit dependencies"""
    def __init__(self, id, name, price, quantity, description, category, image, 
                 base_price=None, pricing_metadata=None):
        self.id = id
        self.name = name
        self.base_price = base_price if base_price is not None else price
        self.price = price
        self.quantity = quantity
        self.description = description
        self.category = category
        self.image = image
        self.pricing_metadata = pricing_metadata or {}


def load_products():
    """Load products from inventory.json"""
    inventory_data = read_data('inventory.json')
    if not inventory_data or 'products' not in inventory_data:
        print("❌ Error: Could not load inventory.json")
        return None, None
    
    products = []
    for p_data in inventory_data['products']:
        product = SimpleProduct(
            id=p_data['id'],
            name=p_data['name'],
            price=p_data['price'],
            quantity=p_data['quantity'],
            description=p_data['description'],
            category=p_data['category'],
            image=p_data['image'],
            base_price=p_data.get('base_price'),
            pricing_metadata=p_data.get('pricing_metadata', {})
        )
        products.append(product)
    
    return products, inventory_data


def save_products(products, inventory_data):
    """Save updated products back to inventory.json"""
    # Update products in inventory data
    for i, product in enumerate(products):
        inventory_data['products'][i]['price'] = product.price
        inventory_data['products'][i]['base_price'] = product.base_price
        inventory_data['products'][i]['pricing_metadata'] = product.pricing_metadata
    
    return write_data('inventory.json', inventory_data)


def print_price_change_report(stats):
    """Print a formatted report of price changes"""
    print("\n" + "=" * 80)
    print("PRICE UPDATE REPORT")
    print("=" * 80)
    
    print(f"\n📊 Summary:")
    print(f"   Total products: {stats['total_products']}")
    print(f"   Prices changed: {stats['prices_changed']}")
    print(f"   Price increases: {stats['price_increases']}")
    print(f"   Price decreases: {stats['price_decreases']}")
    print(f"   No change: {stats['no_change']}")
    
    if stats['changes']:
        print(f"\n📝 Detailed Changes:")
        print(f"{'ID':<5} {'Product Name':<35} {'Old Price':<12} {'New Price':<12} {'Change':<10} {'Tier':<10} {'Badges'}")
        print("-" * 110)
        
        for change in stats['changes']:
            change_str = f"{change['change_percent']:+.1f}%"
            badges_str = ', '.join(change['badges']) if change['badges'] else '-'
            
            # Color coding
            color_code = ''
            if change['change_percent'] < 0:
                color_code = '🟢'  # Price decrease (discount)
            else:
                color_code = '🔴'  # Price increase
            
            print(f"{color_code} {change['product_id']:<3} {change['product_name']:<35} "
                  f"${change['old_price']:<11.2f} ${change['new_price']:<11.2f} "
                  f"{change_str:<10} {change['tier']:<10} {badges_str}")
    
    print("\n" + "=" * 80)


def main():
    """Main function to update prices"""
    print("=" * 80)
    print("KSMD Store - Dynamic Price Update")
    print("=" * 80)
    
    # Check files exist
    if not os.path.exists('inventory.json'):
        print("❌ Error: inventory.json not found")
        return False
    
    if not os.path.exists('transactions.json'):
        print("⚠️  Warning: transactions.json not found, using empty transaction history")
        transactions = []
    else:
        txn_data = read_data('transactions.json')
        transactions = txn_data.get('transactions', [])
    
    if not os.path.exists('pricing_config.json'):
        print("❌ Error: pricing_config.json not found")
        print("💡 Please create pricing_config.json first")
        return False
    
    # Load products
    print("\n1. Loading products...")
    products, inventory_data = load_products()
    if not products:
        return False
    print(f"✅ Loaded {len(products)} products")
    
    # Load transactions
    print(f"\n2. Loading transaction history...")
    print(f"✅ Loaded {len(transactions)} transactions")
    
    # Initialize pricing engine
    print(f"\n3. Initializing pricing engine...")
    engine = PricingEngine()
    print(f"✅ Pricing engine ready")
    
    # Check which strategies are enabled
    print(f"\n4. Active pricing strategies:")
    if engine.config['popularity_pricing']['enabled']:
        print(f"   ✅ Popularity-based pricing")
    if engine.config['clearance_pricing']['enabled']:
        print(f"   ✅ Inventory clearance pricing")
    if engine.config['flash_pricing']['enabled']:
        print(f"   ✅ Time-based flash pricing")
    if engine.config['bundle_discounts']['enabled']:
        print(f"   ✅ Bundle discounts (applies at checkout)")
    
    # Update prices
    print(f"\n5. Calculating new prices...")
    stats = engine.update_all_prices(products, transactions)
    print(f"✅ Price calculation complete")
    
    # Show report
    print_price_change_report(stats)
    
    # Ask for confirmation
    if stats['prices_changed'] > 0:
        print(f"\n⚠️  This will update {stats['prices_changed']} product prices in inventory.json")
        response = input("Continue? (yes/no): ").strip().lower()
        
        if response not in ['yes', 'y']:
            print("❌ Price update cancelled")
            return False
    
    # Save updates
    print(f"\n6. Saving updated prices to inventory.json...")
    if save_products(products, inventory_data):
        print(f"✅ Prices updated successfully!")
        print(f"\n📝 Next steps:")
        print(f"   1. Restart the Streamlit app to see updated prices")
        print(f"   2. Check product pages for discount badges")
        print(f"   3. Test checkout flow with bundle discounts")
        return True
    else:
        print(f"❌ Error saving updated prices")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
