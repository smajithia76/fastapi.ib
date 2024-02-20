

class OrderManager:
#     angelClient
#     instrument - buy - order details
#                        order number
#                - sell - order details
#                        order number
    
    def __init__(self, openOrders):
        self.ordersMap = {}
        self.parentToChildMap = {}
        for order in openOrders:
            self.ordersMap[order.orderId] = order
            # if order.parentId != 0:
            #     self.parentToChildMap[order.parentId] = [self.parentToChildMap[order.parentId].append(order.orderId)]

    def tell(self, orderStatus):
        print(">>>>>>>>>>>>>>>>>>>>>>>")
        if len(self.ordersMap) > 0:
            order = self.ordersMap[orderStatus.orderId]
            if orderStatus.status == "Filled":
                print("{} order for {} is filled at avgFillPrice of {} for {} qty".format(order.action, order.instrument, orderStatus.avgFillPrice, orderStatus.filled))
            if orderStatus.status == "Cancelled":
                print("{} order for {} is cancelled".format(order.action, order.instrument))

        print("<<<<<<<<<<<<<<<<<<<<<<<")

    def addOrders(self, orders):
        
        parent = {}
        takeProfit = {}
        stopLoss = {}

        for order in orders:
            self.ordersMap[order.orderId] = order

            if order.orderType == "PARENT":
                parent = order
            if order.orderType == "TAKE_PROFIT":
                takeProfit = order
            if order.orderType == "STOP_LOSS":
                stopLoss = order
        

        self.parentToChildMap[parent.orderId] = [takeProfit.orderId, stopLoss.orderId]

        