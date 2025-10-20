from models.Product import ProductItem
from utils import read_data, write_data
import streamlit as st
class Transaction:
    def __init__(self, transaction_id, date=None):
        self.transaction_id = transaction_id
        self.date = date
        self.cart_items = {}  # Dictionary: {product_id: {'product': ProductItem, 'quantity': int}}
        self.promo_code = None

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
        """Calculate the total price of all items in cart after applying promo code discount"""
        subtotal = 0
        for item_data in self.cart_items.values():
            product = item_data['product']
            quantity = item_data['quantity']
            subtotal += product.price * quantity
        
        # Apply promo code discount if available
        if self.promo_code:
            discount_percent = self.promo_code['discount_percent']
            discount_amount = subtotal * (discount_percent / 100)
            return subtotal - discount_amount
        
        return subtotal

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
                        'quantity': item_data['quantity']
                    }
                    for item_data in self.cart_items.values()
                ],
                'promo_code': self.promo_code,
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
        """Empty the entire cart"""
        self.cart_items = {}

    def __repr__(self):
        return f"Transaction(id={self.transaction_id}, items={len(self.cart_items)}, total=${self.getTotal():.2f})"
