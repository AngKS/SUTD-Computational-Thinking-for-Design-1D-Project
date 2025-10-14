from models.Product import ProductItem
class Transaction:
    def __init__(self, transaction_id, totalamount, date, description):
        self.transaction_id = transaction_id
        self.totalamount = totalamount
        self.date = date
        self.products = []

    def addItem(self, item: ProductItem):
        self.products.append(item)
        
        

    def removeItem(self, product):
        self.products.remove(product)
    

    def getTotal(self):
        total_with_tax= self.totalamount*0.09
        discount=1
        if discountcode==code:
            discount=0.2
        discounted_total= total_with_tax - (total_with_tax*discount)
        return discounted_total

    def __repr__(self):
        return f"Transaction({self.transaction_id}, {self.amount}, {self.date}, {self.description})"