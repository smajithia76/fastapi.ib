import requests

class OrderManager:
#     angelClient
#     instrument - buy - order details
#                        order number
#                - sell - order details
#                        order number
    
    def __init__(self, openOrders, durl):
        self.ordersMap = {}
        self.parentToChildMap = {}
        self.discordURL = durl
        for order in openOrders:
            self.ordersMap[order.orderId] = order
            # if order.parentId != 0:
            #     self.parentToChildMap[order.parentId] = [self.parentToChildMap[order.parentId].append(order.orderId)]

    def tell(self, orderStatus):
        if len(self.ordersMap) > 0:
            order = self.ordersMap[orderStatus.orderId]
            if orderStatus.status == "Filled":
                self.sendDiscordMsg("{} order for {} is filled at avgFillPrice of {} for {} qty".format(order.action, order.instrument, orderStatus.avgFillPrice, orderStatus.filled))
            if orderStatus.status == "Cancelled":
                self.sendDiscordMsg("{} order for {} is cancelled".format(order.action, order.instrument))

    def sendDiscordMsg(self, msg):
        payload = {"content": msg}
        response = requests.post(self.discordURL, json=payload)
        print(response.text)

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

        