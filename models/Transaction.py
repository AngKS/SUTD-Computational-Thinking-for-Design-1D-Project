from models.Product import ProductItem

class Transaction:

    def __init__(self, transaction_id, amount, date, description):
        self.transaction_id = transaction_id
        self.amount = amount
        self.date = date
        self.products = []

    def addItem(self, product):
        product = ProductItem(id="001", name="Sample Product", price=9.99, quantity=1, description="A sample product", category="Sample Category")

        pass

    def removeItem(self, product):
        pass


    def getTotal(self):
        pass


    def __repr__(self):
        return f"Transaction({self.transaction_id}, {self.amount}, {self.date}, {self.description})"