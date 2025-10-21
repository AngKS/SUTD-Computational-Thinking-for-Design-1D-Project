from models.Product import ProductItem
from utils import read_data, write_data
import streamlit as st
from datetime import datetime as dt
class Transaction:
    def __init__(self, transaction_id, date=None):
        self.transaction_id = transaction_id
        self.date = date
        self.cart_items = {}  # Dictionary: {product_id: {'product': ProductItem, 'quantity': int}}
        self.promo_code = None
        self.bundle_discount = 0  # Bundle discount percentage
        self.bundle_discount_label = ""  # Label for bundle discount

    @staticmethod
    def create_new_transaction():
        """Factory method to create a new transaction instance with auto-generated ID and timestamp"""
        return Transaction(
            transaction_id=f"TXN{dt.now().strftime('%Y%m%d%H%M%S')}",
            date=dt.now().strftime("%Y-%m-%d %H:%M:%S")
        )

    def addItem(self, product, quantity=1):
        """Add a product to the cart or increase its quantity with stock validation"""
        # Calculate how many are currently in cart
        current_quantity_in_cart = self.cart_items[product.id]['quantity'] if product.id in self.cart_items else 0

        # Calculate total quantity after adding
        new_total_quantity = current_quantity_in_cart + quantity

        # Check if the new total exceeds available stock
        if new_total_quantity > product.quantity:
            # Return False to indicate failure, and the available amount
            available_to_add = product.quantity - current_quantity_in_cart
            return False, available_to_add

        # Stock is available, proceed with adding
        if product.id in self.cart_items:
            # Product already in cart, increase quantity
            self.cart_items[product.id]['quantity'] += quantity
        else:
            # New product, add to cart
            self.cart_items[product.id] = {
                'product': product,
                'quantity': quantity
            }
        return True, quantity

    def removeItem(self, product_id, quantity=1):
        """Remove a product from cart or decrease its quantity"""
        if product_id in self.cart_items:
            self.cart_items[product_id]['quantity'] -= quantity

            # If quantity reaches 0, remove from cart
            if self.cart_items[product_id]['quantity'] <= 0:
                del self.cart_items[product_id]
            return True
        return False

    def removeItemCompletely(self, product_id):
        """Remove an item completely from the cart"""
        if product_id in self.cart_items:
            del self.cart_items[product_id]
            return True
        return False

    def getItemQuantity(self, product_id):
        """Get the quantity of a specific item in cart"""
        if product_id in self.cart_items:
            return self.cart_items[product_id]['quantity']
        return 0
    
    def calculatePromoDiscount(self, subtotal: float) -> float:
        """Calculate the discount amount based on the applied promo code"""
        if self.promo_code:
            discount_percent = self.promo_code['discount_percent']
            discount_amount = subtotal * (discount_percent / 100)
            return discount_amount
        return 0
    
    def calculateBundleDiscount(self, subtotal: float = None) -> float:
        """Calculate bundle discount amount based on cart composition"""
        if self.bundle_discount > 0:
            if subtotal is None:
                subtotal = self.getSubTotal()
            return subtotal * (self.bundle_discount / 100)
        return 0
    
    def updateBundleDiscount(self):
        """Update bundle discount based on current cart composition"""
        try:
            from services.pricing_engine import PricingEngine
            engine = PricingEngine()
            bundle_info = engine.calculate_bundle_discount(self.cart_items)
            self.bundle_discount = bundle_info['discount_percent']
            self.bundle_discount_label = bundle_info['label']
        except Exception as e:
            print(f"Error calculating bundle discount: {e}")
            self.bundle_discount = 0
            self.bundle_discount_label = ""
    
    def getTotalSavings(self) -> float:
        """Calculate total amount saved from all discounts"""
        subtotal = self.getSubTotal()
        promo_savings = self.calculatePromoDiscount(subtotal)
        bundle_savings = self.calculateBundleDiscount(subtotal)
        return promo_savings + bundle_savings

    def applyPromoCode(self, code: str):
        """Apply a promo code to the transaction"""
        try:
            promo_data = read_data('promocodes.json')
            # The JSON structure has a "codes" array with promo code objects
            if 'codes' in promo_data:
                for promo in promo_data['codes']:
                    if promo['code'] == code:
                        self.promo_code = {
                            'code': code,
                            'discount_percent': promo['discount_percent']
                        }
                        return True
            return False
        except Exception as e:
            print(f"Error applying promo code: {e}")
            return False



    def getProductSubtotal(self, product_id):
        """Get the subtotal for a specific product"""
        if product_id in self.cart_items:
            item = self.cart_items[product_id]
            return item['product'].price * item['quantity']
        return 0

    def getSubTotal(self):
        """Calculate the subtotal price of all items in cart before applying promo code"""
        subtotal = 0
        for item_data in self.cart_items.values():
            product = item_data['product']
            quantity = item_data['quantity']
            subtotal += product.price * quantity
        return subtotal

    def getTotal(self):
        """Calculate the total price of all items in cart after applying all discounts"""
        subtotal = 0
        for item_data in self.cart_items.values():
            product = item_data['product']
            quantity = item_data['quantity']
            subtotal += product.price * quantity
        
        # Apply promo code discount if available
        total = subtotal
        if self.promo_code:
            discount_percent = self.promo_code['discount_percent']
            discount_amount = subtotal * (discount_percent / 100)
            total -= discount_amount
        
        # Apply bundle discount if available
        if self.bundle_discount > 0:
            bundle_discount_amount = subtotal * (self.bundle_discount / 100)
            total -= bundle_discount_amount
        
        return total

    def getItemCount(self):
        """Get total number of items in cart"""
        return sum(item['quantity'] for item in self.cart_items.values())

    def isEmpty(self):
        """Check if cart is empty"""
        return len(self.cart_items) == 0

    def save_transaction(self, file_path='transactions.json'):
        """Save the transaction details to a JSON file"""
        try:
            data = read_data(file_path)
            if 'transactions' not in data:
                data['transactions'] = []

            customer_data = {
                "email": st.session_state.get('billing_email', ''),
                "name": st.session_state.get('billing_name', ''),
                "address": st.session_state.get('billing_address', ''),
                "country": st.session_state.get('billing_country', '')
            }
            
            # Prepare transaction data for saving
            transaction_record = {
                'transaction_id': self.transaction_id,
                'date': self.date if self.date else '',
                'customer': customer_data,
                'items': [
                    {
                        'product_id': item_data['product'].id,
                        'name': item_data['product'].name,
                        'price': item_data['product'].price,
                        'base_price': item_data['product'].base_price,
                        'quantity': item_data['quantity']
                    }
                    for item_data in self.cart_items.values()
                ],
                'promo_code': self.promo_code,
                'bundle_discount': self.bundle_discount,
                'bundle_discount_label': self.bundle_discount_label,
                'subtotal': self.getSubTotal(),
                'total_savings': self.getTotalSavings(),
                'total_amount': self.getTotal()
            }
            data['transactions'].append(transaction_record)
            
            # Write the data and check if it succeeded
            if write_data(file_path, data):
                return True
            else:
                print(f"Failed to write transaction data to {file_path}")
                return False
        except Exception as e:
            print(f"Error saving transaction: {e}")
            import traceback
            traceback.print_exc()
            return False

    def clearCart(self):
        """Empty the entire cart and clear billing info."""
        self.cart_items = {}
        self.promo_code = None
        self.bundle_discount = 0
        self.bundle_discount_label = ""
        # clear billing info from session state
        st.session_state['billing_email'] = ''
        st.session_state['billing_name'] = ''
        st.session_state['billing_address'] = ''
        st.session_state['billing_country'] = ''


    def __repr__(self):
        return f"Transaction(id={self.transaction_id}, items={len(self.cart_items)}, total=${self.getTotal():.2f})"
