class Reserve:
    def __init__(self, amount, order_number):
        self.amount = amount
        self.orderNumber = order_number
        self.type = "order"
        self.ActionType = "auto"
        self.balance = "consume"
