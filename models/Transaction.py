
class Transaction:

    def __init__(self, transaction_id, amount, date, description):
        self.transaction_id = transaction_id
        self.amount = amount
        self.date = date
        self.products = []

    def addItem(self, product):
        pass

    def removeItem(self, product):
        pass


    def getTotal(self):
        pass


    def __repr__(self):
        return f"Transaction({self.transaction_id}, {self.amount}, {self.date}, {self.description})"