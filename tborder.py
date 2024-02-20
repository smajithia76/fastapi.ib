class TBOrder:

    def __init__(self, 
                 orderId,
                 parentId, 
                 instrument,
                 orderType, 
                 action,
                 quantity, 
                 limitPrice, 
                 takeProfitPrice, 
                 stopLossPrice):
        
        self.orderId = orderId
        self.instrument = instrument
        self.orderType = orderType
        self.action = action
        self.quantity = quantity
        self.limitPrice = limitPrice
        self.takeProfitPrice = takeProfitPrice
        self.stopLossPrice = stopLossPrice
        self.parentId = parentId

    def __str__(self) -> str:
        return "orderId: {}\ninstrument: {}\norderType: {}\naction: {}\nquantity: {}\nlimitPrice:{}\ntakeProfitPrice:{}\nstopLossPrice:{}".format(self.orderId, self.instrument, self.orderType, self.action, self.quantity, self.limitPrice, self.takeProfitPrice, self.stopLossPrice)