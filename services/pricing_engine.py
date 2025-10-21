"""
Pricing Engine - Central pricing calculation system
Implements dynamic pricing strategies including:
- Popularity-based pricing
- Inventory-based clearance pricing
- Time-based flash pricing
- Category-based bundle discounts
"""

from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
from utils import read_data, write_data
import json


class PricingEngine:
    """Central pricing calculation engine for dynamic pricing strategies"""
    
    def __init__(self, config_path='pricing_config.json'):
        """Initialize the pricing engine with configuration"""
        self.config = self.load_config(config_path)
        self.config_path = config_path
    
    def load_config(self, config_path: str) -> dict:
        """Load pricing configuration from JSON file"""
        try:
            config = read_data(config_path)
            if not config:
                print(f"Warning: Could not load pricing config from {config_path}, using defaults")
                return self._get_default_config()
            return config
        except Exception as e:
            print(f"Error loading pricing config: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> dict:
        """Return default configuration if config file is missing"""
        return {
            "popularity_pricing": {"enabled": False},
            "clearance_pricing": {"enabled": False},
            "flash_pricing": {"enabled": False},
            "bundle_discounts": {"enabled": False}
        }
    
    def get_popularity_score(self, product_id: int, transactions: list, days: int = 30) -> int:
        """
        Calculate purchase count for a product in the last N days
        
        Args:
            product_id: Product ID to check
            transactions: List of transaction records
            days: Time window in days (default 30)
        
        Returns:
            Number of times product was purchased in time window
        """
        if not transactions:
            return 0
        
        cutoff_date = datetime.now() - timedelta(days=days)
        purchase_count = 0
        
        for txn in transactions:
            try:
                # Parse transaction date
                txn_date = datetime.strptime(txn['date'], "%Y-%m-%d %H:%M:%S")
                
                # Check if transaction is within time window
                if txn_date >= cutoff_date:
                    # Count how many times this product appears in this transaction
                    for item in txn.get('items', []):
                        if item['product_id'] == product_id:
                            purchase_count += item.get('quantity', 1)
            except (ValueError, KeyError) as e:
                # Skip transactions with invalid dates
                continue
        
        return purchase_count
    
    def get_popularity_tier(self, purchase_count: int) -> str:
        """
        Determine popularity tier based on purchase count
        
        Args:
            purchase_count: Number of purchases in time window
        
        Returns:
            Tier name: 'hot', 'trending', 'normal', 'slow', or 'cold'
        """
        if not self.config['popularity_pricing']['enabled']:
            return 'normal'
        
        tiers = self.config['popularity_pricing']['tiers']
        
        # Check tiers from highest to lowest
        if purchase_count >= tiers['hot']['min_purchases']:
            return 'hot'
        elif purchase_count >= tiers['trending']['min_purchases']:
            return 'trending'
        elif purchase_count >= tiers['normal']['min_purchases']:
            return 'normal'
        elif purchase_count >= tiers['slow']['min_purchases']:
            return 'slow'
        else:
            return 'cold'
    
    def calculate_popularity_multiplier(self, tier: str) -> float:
        """Get price multiplier for a popularity tier"""
        if not self.config['popularity_pricing']['enabled']:
            return 1.0
        
        tiers = self.config['popularity_pricing']['tiers']
        return tiers.get(tier, {}).get('multiplier', 1.0)
    
    def calculate_clearance_discount(self, product, transactions: list) -> Tuple[float, str]:
        """
        Calculate clearance discount based on inventory levels
        
        Args:
            product: ProductItem object
            transactions: List of transaction records
        
        Returns:
            Tuple of (discount_multiplier, label)
        """
        if not self.config['clearance_pricing']['enabled']:
            return 1.0, ""
        
        stock = product.quantity
        time_window = self.config['popularity_pricing']['time_window_days']
        purchases = self.get_popularity_score(product.id, transactions, time_window)
        
        # Check for low stock premium first
        low_stock_threshold = self.config['clearance_pricing'].get('low_stock_threshold', 5)
        if stock < low_stock_threshold and stock > 0:
            premium = self.config['clearance_pricing'].get('low_stock_premium', 1.05)
            label = self.config['clearance_pricing'].get('low_stock_label', '⚡ LOW STOCK')
            return premium, label
        
        # Check clearance rules (sorted by priority)
        rules = sorted(
            self.config['clearance_pricing']['rules'], 
            key=lambda x: x.get('priority', 999)
        )
        
        for rule in rules:
            if stock >= rule['stock_threshold'] and purchases <= rule['max_purchases']:
                discount_multiplier = 1.0 - (rule['discount_percent'] / 100)
                return discount_multiplier, rule.get('label', f"{rule['discount_percent']}% OFF")
        
        return 1.0, ""
    
    def calculate_flash_multiplier(self, tier: str) -> Tuple[float, str]:
        """
        Calculate time-based flash pricing multiplier
        
        Args:
            tier: Current popularity tier of product
        
        Returns:
            Tuple of (multiplier, label)
        """
        if not self.config['flash_pricing']['enabled']:
            return 1.0, ""
        
        current_day = datetime.now().isoweekday()  # 1=Monday, 7=Sunday
        
        for rule in self.config['flash_pricing']['rules']:
            # Check if today matches the rule
            if current_day in rule['day_of_week']:
                # Check if tier matches (if tier_filter exists)
                if 'tier_filter' in rule:
                    if tier == rule['tier_filter']:
                        return rule['multiplier'], rule.get('label', '')
                else:
                    # No tier filter, applies to all
                    return rule['multiplier'], rule.get('label', '')
        
        return 1.0, ""
    
    def calculate_product_price(self, product, transactions: list) -> Dict:
        """
        Calculate final price for a product based on all active strategies
        """
        base_price = getattr(product, 'base_price', product.price)
        
        # 1. Calculate popularity score and tier
        time_window = self.config['popularity_pricing']['time_window_days']
        popularity_score = self.get_popularity_score(product.id, transactions, time_window)
        popularity_tier = self.get_popularity_tier(popularity_score)
        
        # 2. Get popularity multiplier
        popularity_mult = self.calculate_popularity_multiplier(popularity_tier)
        
        # 3. Get clearance discount (overrides popularity if applicable)
        clearance_mult, clearance_label = self.calculate_clearance_discount(product, transactions)
        
        # 4. Get flash pricing multiplier
        flash_mult, flash_label = self.calculate_flash_multiplier(popularity_tier)
        
        # 5. Combine multipliers (clearance overrides popularity)
        if clearance_mult != 1.0:
            # Clearance pricing takes priority
            combined_mult = clearance_mult * flash_mult
            active_tier_mult = clearance_mult
        else:
            # Use popularity pricing
            combined_mult = popularity_mult * flash_mult
            active_tier_mult = popularity_mult
        
        # 6. Apply maximum deviation cap
        max_deviation = self.config['popularity_pricing'].get('max_deviation_percent', 20) / 100
        max_mult = 1 + max_deviation
        min_mult = 1 - max_deviation
        combined_mult = max(min_mult, min(max_mult, combined_mult))
        
        # 7. Calculate final price
        final_price = base_price * combined_mult
        
        # 8. Collect badges
        badges = []
        if self.config.get('pricing_display', {}).get('show_badges', True):
            # Add popularity/clearance badge
            if clearance_label:
                badges.append(clearance_label)
            elif popularity_tier != 'normal':
                tier_config = self.config['popularity_pricing']['tiers'][popularity_tier]
                if tier_config.get('label'):
                    badges.append(tier_config['label'])
            
            # Add flash pricing badge
            if flash_label:
                badges.append(flash_label)
        
        # 9. Calculate savings percentage
        savings_percent = ((base_price - final_price) / base_price * 100) if base_price > 0 else 0
        
        return {
            'final_price': round(final_price, 2),
            'base_price': round(base_price, 2),
            'popularity_tier': popularity_tier,
            'popularity_score': popularity_score,
            'multipliers': {
                'popularity': popularity_mult,
                'clearance': clearance_mult,
                'flash': flash_mult,
                'combined': combined_mult
            },
            'badges': badges,
            'savings_percent': round(savings_percent, 2),
            'last_updated': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def update_all_prices(self, products: list, transactions: list) -> Dict[str, any]:
        """
        Batch update prices for all products
        
        Args:
            products: List of ProductItem objects
            transactions: List of transaction records
        
        Returns:
            Dictionary with update statistics
        """
        stats = {
            'total_products': len(products),
            'prices_changed': 0,
            'price_increases': 0,
            'price_decreases': 0,
            'no_change': 0,
            'changes': []
        }
        
        for product in products:
            old_price = product.price
            pricing_data = self.calculate_product_price(product, transactions)
            new_price = pricing_data['final_price']
            
            # Update product pricing metadata
            if not hasattr(product, 'pricing_metadata'):
                product.pricing_metadata = {}
            
            product.pricing_metadata.update({
                'popularity_tier': pricing_data['popularity_tier'],
                'popularity_score': pricing_data['popularity_score'],
                'pricing_multiplier': pricing_data['multipliers']['combined'],
                'badges': pricing_data['badges'],
                'last_updated': pricing_data['last_updated']
            })
            
            # Update base_price if not set
            if not hasattr(product, 'base_price') or product.base_price is None:
                product.base_price = old_price
            
            # Update current price
            product.price = new_price
            
            # Track statistics
            if abs(new_price - old_price) > 0.01:  # Changed
                stats['prices_changed'] += 1
                if new_price > old_price:
                    stats['price_increases'] += 1
                else:
                    stats['price_decreases'] += 1
                
                stats['changes'].append({
                    'product_id': product.id,
                    'product_name': product.name,
                    'old_price': round(old_price, 2),
                    'new_price': round(new_price, 2),
                    'change_percent': round(((new_price - old_price) / old_price * 100), 2),
                    'tier': pricing_data['popularity_tier'],
                    'badges': pricing_data['badges']
                })
            else:
                stats['no_change'] += 1
        
        return stats
    
    def calculate_bundle_discount(self, cart_items: dict) -> Dict:
        """
        Calculate bundle discount based on cart composition
        """
        if not self.config['bundle_discounts']['enabled']:
            return {
                'discount_percent': 0,
                'discount_amount': 0,
                'label': '',
                'qualified_rule': None
            }
        
        # Calculate cart composition
        total_items = sum(item['quantity'] for item in cart_items.values())
        categories = set(item['product'].category for item in cart_items.values())
        
        # Check rules (sorted by priority)
        rules = sorted(
            self.config['bundle_discounts']['rules'],
            key=lambda x: x.get('priority', 999)
        )
        
        for rule in rules:
            # Check minimum items requirement
            if total_items < rule['min_items']:
                continue
            
            # Check category requirements if specified
            if 'categories' in rule:
                required_categories = set(rule['categories'])
                if not required_categories.issubset(categories):
                    continue
            
            # Rule matched!
            return {
                'discount_percent': rule['discount_percent'],
                'discount_amount': 0,  # Will be calculated based on subtotal
                'label': rule.get('label', f"{rule['discount_percent']}% Bundle Discount"),
                'qualified_rule': rule
            }
        
        # No rules matched
        return {
            'discount_percent': 0,
            'discount_amount': 0,
            'label': '',
            'qualified_rule': None
        }
    
    def get_next_bundle_tier(self, cart_items: dict) -> Optional[Dict]:
        """
        Get information about the next bundle discount tier
        """
        if not self.config['bundle_discounts']['enabled']:
            return None
        
        total_items = sum(item['quantity'] for item in cart_items.values())
        categories = set(item['product'].category for item in cart_items.values())
        
        current_discount = self.calculate_bundle_discount(cart_items)
        current_discount_percent = current_discount['discount_percent']
        
        # Find next better discount
        rules = sorted(
            self.config['bundle_discounts']['rules'],
            key=lambda x: x['discount_percent'],
            reverse=True
        )
        
        for rule in rules:
            if rule['discount_percent'] <= current_discount_percent:
                continue
            
            items_needed = max(0, rule['min_items'] - total_items)
            
            # Check category requirements
            if 'categories' in rule:
                required_categories = set(rule['categories'])
                missing_categories = required_categories - categories
                if missing_categories:
                    return {
                        'items_needed': items_needed,
                        'discount_percent': rule['discount_percent'],
                        'label': rule.get('label', ''),
                        'missing_categories': list(missing_categories)
                    }
            
            if items_needed > 0:
                return {
                    'items_needed': items_needed,
                    'discount_percent': rule['discount_percent'],
                    'label': rule.get('label', ''),
                    'missing_categories': []
                }
        
        return None  # Already at highest tier
