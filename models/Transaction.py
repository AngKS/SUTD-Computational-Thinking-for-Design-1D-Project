class Transaction:
    def __init__(self, transaction_id, date=None):
        self.transaction_id = transaction_id
        self.date = date
        self.cart_items = {}  # Dictionary: {product_id: {'product': ProductItem, 'quantity': int}}

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

    def getSubtotal(self, product_id):
        """Get the subtotal for a specific product"""
        if product_id in self.cart_items:
            item = self.cart_items[product_id]
            return item['product'].price * item['quantity']
        return 0

    def getTotal(self):
        """Calculate the total price of all items in cart"""
        total = 0
        for item_data in self.cart_items.values():
            product = item_data['product']
            quantity = item_data['quantity']
            total += product.price * quantity
        return total

    def getItemCount(self):
        """Get total number of items in cart"""
        return sum(item['quantity'] for item in self.cart_items.values())

    def isEmpty(self):
        """Check if cart is empty"""
        return len(self.cart_items) == 0

    def clearCart(self):
        """Empty the entire cart"""
        self.cart_items = {}

    def __repr__(self):
        return f"Transaction(id={self.transaction_id}, items={len(self.cart_items)}, total=${self.getTotal():.2f})"
