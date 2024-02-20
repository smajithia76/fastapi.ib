# -*- coding: utf-8 -*-
"""
Created on Tue Dec 13 19:59:57 2022

@author: smajithia
"""

# Import libraries
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.order import Order
from OrderStatus import OrderStatus
from tborder import TBOrder

import pandas as pd
import threading
import time

class IBClient(EWrapper, EClient): 
    #TODO make use of historical data end to handle waiting for data elegantly
    def __init__(self): 
        EClient.__init__(self, self) 
        self.data = {}
        self.__event = threading.Event()
        self.__listener = None
        self.__openOrdersEnd = False
        self.__openOrders = []
        
    def registerOrderListener(self, listener):
        self.__listener = listener
        
    def historicalData(self, reqId, bar):
        #print(f'Time: {bar.date}, Open: {bar.open}, Close: {bar.close}')
        if reqId not in self.data:
            self.data[reqId] = [{"Date":bar.date,"Open":bar.open,"High":bar.high,"Low":bar.low,"Close":bar.close,"Volume":bar.volume}]
        else:
            self.data[reqId].append({"Date":bar.date,"Open":bar.open,"High":bar.high,"Low":bar.low,"Close":bar.close,"Volume":bar.volume})

    def historicalDataEnd(self, reqId, start, end):
        super().historicalDataEnd(reqId, start, end)
        #print("HistoricalDataEnd. ReqId:", reqId, "from", start, "to", end)
        self.__event.set()

    def nextValidId(self, orderId):
        super().nextValidId(orderId)
        self.nextValidOrderId = orderId
        print("NextValidId:", orderId)

    def openOrder(self, orderId, contract, order, orderState):
        self.__openOrdersEnd = False
        tbOrder = TBOrder(orderId = orderId, 
                 parentId = order.parentId,
                 instrument = contract.symbol,
                 orderType = order.orderType, 
                 action = order.action,
                 quantity = order.totalQuantity, 
                 limitPrice = order.lmtPrice, 
                 takeProfitPrice = order.lmtPrice, 
                 stopLossPrice = order.lmtPrice)
        self.__openOrders.append(tbOrder)
        print("Inside openOrder")

    def openOrderEnd(self):
        self.__openOrdersEnd = True
        print("Inside openOrderEnd")

    def reqOpenOrders(self):
        self.reqAllOpenOrders()
        while not self.__openOrdersEnd:
            for order in self.__openOrders:
                print(order)

        return self.__openOrders

    def orderStatus(self, orderId,	status, filled,	remaining, avgFillPrice, permId, parentId, lastFillPrice, clientId,	whyHeld, mktCapPrice ):
        
        # dictionary = {"orderId": orderId, 
        #               "status": status,
        #               "filled": filled, 
        #               "remaining": remaining, 
        #               "avgFillPrice": avgFillPrice, 
        #               "permId": permId, 
        #               "parentId": parentId, 
        #               "lastFillPrice": lastFillPrice,
        #               "clientId": clientId,	
        #               "whyHeld": whyHeld, 
        #               "mktCapPrice": mktCapPrice}
        
        #print(dictionary)        
        
        order_status = OrderStatus(orderId,
                            status, 
                            filled,	
                            remaining, 
                            avgFillPrice, 
                            permId, 
                            parentId, 
                            lastFillPrice, 
                            clientId, 
                            whyHeld, 
                            mktCapPrice)
        if self.__listener != None:
            self.__listener.tell(order_status)
        else:
            print("Listener is missing")

    def __getLimitOrder(self, direction, quantity, limit_price):
        #print("Inside __getMarketOrder")
        order = Order()
        order.action = direction
        order.orderType = "LMT"
        order.totalQuantity = quantity
        order.eTradeOnly = False
        order.firmQuoteOnly = False
        order.lmtPrice = limit_price
        #print(order)
        return order

    def __getMarketOrder(self, direction, quantity):
        #print("Inside __getMarketOrder")
        order = Order()
        order.action = direction
        order.orderType = "MKT"
        order.totalQuantity = quantity
        order.eTradeOnly = False
        order.firmQuoteOnly = False
        #print(order)
        return order
    
    def __getTrailingStopLimitOrder(self, direction, quantity, trailStopPrice, lmtPriceOffset, trailingAmount):
        order = Order()
        order.action = direction
        order.orderType = "TRAIL LIMIT"
        order.totalQuantity = quantity
        order.trailStopPrice = trailStopPrice
        order.lmtPriceOffset = lmtPriceOffset
        order.auxPrice = trailingAmount    
        order.eTradeOnly = False
        order.firmQuoteOnly = False
        return order
        
    def __getStopLossLimitOrder(self, direction, quantity, stopPrice, limitPrice):
        #print("Inside __getStopLossLimitOrder")
        order = Order()
        order.action = direction
        order.orderType = "STP LMT"
        order.auxPrice = stopPrice
        order.lmtPrice = limitPrice
        order.totalQuantity = quantity
        order.eTradeOnly = False
        order.firmQuoteOnly = False
        #print(order)
        return order

    def __getContract(self, 
                      symbol,
                      sec_type="STK",
                      currency="INR",
                      exchange="NSE", 
                      contract_month=''):
        
        contract = Contract()
        if sec_type == "OPT":
            contract.localSymbol = symbol
        else:
            contract.symbol = symbol
        contract.secType = sec_type
        contract.currency = currency
        contract.exchange = exchange
        
        if sec_type == "FUT":
            contract.lastTradeDateOrContractMonth = contract_month

        return contract 
    
    def __histData(self, req_num, contract, endDateTime, duration, candle_size):
        """extracts historical data"""
        #print("Fetching data for %s" % (contract.symbol))
        self.reqHistoricalData(reqId=req_num, 
                              contract=contract,
                              endDateTime=endDateTime,
                              durationStr=duration,
                              barSizeSetting=candle_size,
                              whatToShow='TRADES',
                              useRTH=1,
                              formatDate=1,
                              keepUpToDate=0,
                              chartOptions=[])	 # EClient function to request contract details        
    
    def getHistoricalData(self, 
                          req_num,
                          duration, 
                          candle_size, 
                          symbol,
                          endDateTime='',
                          sec_type="STK",
                          currency="INR",
                          exchange="NSE",
                          contract_month=''):
        
        contract = self.__getContract(symbol, 
                                      sec_type, 
                                      currency, 
                                      exchange, 
                                      contract_month)
        self.__event.clear()
        self.__histData(req_num, contract, endDateTime, duration, candle_size)
        self.__event.wait()  
        return self.data[req_num]
    
    def placeMarketOrder(self, symbol, sec_type, currency, exchange, action, quantity, contract_month=''):
        contract = self.__getContract(symbol, 
                                      sec_type, 
                                      currency, 
                                      exchange, 
                                      contract_month)

        order = self.__getMarketOrder(action, quantity)
        self.placeOrder(self.nextValidOrderId, contract, order)
        retVal = self.nextValidOrderId
        self.reqIds(-1)
        return retVal
        
    def placeStopLossLimitOrder(self, symbol, sec_type, currency, exchange, action, quantity, stop_price, limit_price, contract_month=''):
        #print("Inside placeStopLossLimitOrder")
        #print("stop_price: {}".format(stop_price))
        #print("limit_price: {}".format(limit_price))
        contract = self.__getContract(symbol, 
                                      sec_type, 
                                      currency, 
                                      exchange, 
                                      contract_month)
        
        self.placeOrder(self.nextValidOrderId, contract, self.__getStopLossLimitOrder(action, quantity, stop_price, limit_price))
        retVal = self.nextValidOrderId
        self.reqIds(-1)
        return retVal
    
    def updateStopLossLimitOrder(self, order_id, symbol, sec_type, currency, exchange, action, quantity, stop_price, limit_price, contract_month=''):
        contract = self.__getContract(symbol, 
                                      sec_type, 
                                      currency, 
                                      exchange, 
                                      contract_month)
        
        self.placeOrder(order_id, contract, self.__getStopLossLimitOrder(action, quantity, stop_price, limit_price))
        return order_id
    
    def placeTrailingStopLimitOrder(self, symbol, sec_type, currency, exchange, action, quantity, contract_month=''):
        contract = self.__getContract(symbol, 
                                      sec_type, 
                                      currency, 
                                      exchange, 
                                      contract_month)
        
        self.placeOrder(self.nextValidOrderId, contract, self.__getMarketOrder(action, quantity))
        retVal = self.nextValidOrderId
        self.reqIds(-1)
        return retVal
    
    def placeBracketOrder(self, parent_order_id, symbol, sec_type, currency, exchange, action, quantity, limit_price, take_profit, stop_loss, contract_month=''):
        contract = self.__getContract(symbol, 
                                      sec_type, 
                                      currency, 
                                      exchange, 
                                      contract_month)
        
        parent = self.__getLimitOrder(action, quantity, limit_price)
        take_profit_order = self.__getLimitOrder("SELL" if action == "BUY" else "BUY", quantity, take_profit)
        stop_loss_order = self.__getStopLossLimitOrder("SELL" if action == "BUY" else "BUY", quantity, stop_loss, stop_loss)

        parent.transmit = False

        parent.orderId = self.nextValidOrderId

        take_profit_order.transmit = False
        take_profit_order.parentId = parent.orderId
        take_profit_order.orderId = parent.orderId+1

        stop_loss_order.transmit = True
        stop_loss_order.parentId = parent.orderId
        stop_loss_order.orderId = parent.orderId+2

        parentTBOrder = TBOrder(parent.orderId, parent.parentId, symbol, "PARENT", parent.action, parent.totalQuantity, parent.lmtPrice, 0.0, 0.0)
        tpTBOrder = TBOrder(take_profit_order.orderId, take_profit_order.parentId, symbol, "TAKE_PROFIT", take_profit_order.action, take_profit_order.totalQuantity, 0.0, take_profit_order.lmtPrice, 0.0)
        slTBOrder = TBOrder(stop_loss_order.orderId, stop_loss_order.parentId, symbol, "STOP_LOSS", stop_loss_order.action, stop_loss_order.totalQuantity, 0.0, 0.0, stop_loss_order.lmtPrice)

        self.placeOrder(parent.orderId, contract, parent)
        self.placeOrder(take_profit_order.orderId, contract, take_profit_order)
#        print("Sending orders for " + contract.symbol)
        self.placeOrder(stop_loss_order.orderId, contract, stop_loss_order)
        self.reqIds(-1)
        return [parentTBOrder, tpTBOrder, slTBOrder]

class IBDataSource:
    #TODO Implement graceful exit of daemon thread and connection close
    def __init__(self, host='127.0.0.1', port=7497, clientId=1):
        self.__ibClient = IBClient()
        self.__ibClient.connect(host=host, port=port, clientId=clientId)
        con_thread = threading.Thread(target=self.client_handler, daemon=True)
        con_thread.start()
        time.sleep(3)
        self.__reqId = 1

    
    def getHistoricalDataFrame(self, 
                               req_num, 
                               duration, 
                               candle_size, 
                               symbol,
                               endDateTime='',
                               sec_type="STK",
                               currency="INR",
                               exchange="NSE",
                               contract_month=''):
        
        data = self.__ibClient.getHistoricalData(self.__reqId, 
                                                 duration, 
                                                 candle_size, 
                                                 symbol,
                                                 endDateTime,
                                                 sec_type,
                                                 currency,
                                                 exchange,
                                                 contract_month)
        self.__reqId = self.__reqId + 1
        df = pd.DataFrame(data)
        df.set_index(pd.DatetimeIndex(df["Date"]),inplace=True)
        return df

    def placeMarketOrder(self, symbol, sec_type, currency, exchange, action, quantity, contract_month=''):
        print("Inside IBDataSource::placeMarketOrder")
        return self.__ibClient.placeMarketOrder(symbol, 
                                         sec_type, 
                                         currency, 
                                         exchange, 
                                         action, 
                                         quantity, 
                                         contract_month)
        
    def placeStopLossLimitOrder(self, symbol, sec_type, currency, exchange, action, quantity, stop_price, limit_price, contract_month=''):
        return self.__ibClient.placeStopLossLimitOrder(symbol, 
                                                sec_type, 
                                                currency, 
                                                exchange, 
                                                action, 
                                                quantity, 
                                                stop_price, 
                                                limit_price, 
                                                contract_month)        

    def updateStopLossLimitOrder(self, order_id, symbol, sec_type, currency, exchange, action, quantity, stop_price, limit_price, contract_month=''):
        return self.__ibClient.updateStopLossLimitOrder(order_id, symbol, 
                                                sec_type, 
                                                currency, 
                                                exchange, 
                                                action, 
                                                quantity, 
                                                stop_price, 
                                                limit_price, 
                                                contract_month)

    def placeTrailingStopLimitOrder(self, symbol, sec_type, currency, exchange, action, quantity, contract_month=''):
        return self.__ibClient.placeTrailingStopLimitOrder(symbol, 
                                                    sec_type, 
                                                    currency, 
                                                    exchange, 
                                                    action, 
                                                    quantity, 
                                                    contract_month)
    
    def placeBracketOrder(self, parent_order_id, symbol, sec_type, currency, exchange, action, quantity, limit_price, take_profit, stop_loss, contract_month=''):
        return self.__ibClient.placeBracketOrder(parent_order_id,
                                                 symbol, 
                                                    sec_type, 
                                                    currency, 
                                                    exchange, 
                                                    action, 
                                                    quantity,
                                                    limit_price,
                                                    take_profit,
                                                    stop_loss, 
                                                    contract_month)
    
    def reqOpenOrders(self):
        return self.__ibClient.reqOpenOrders()

    
    def cancelAllOrders(self):
        self.__ibClient.reqGlobalCancel()

    def registerOrderListener(self, listener):
        self.__ibClient.registerOrderListener(listener)

    def client_handler(self):
        self.__ibClient.run()
        
    def cleanup(self):
        self.__ibClient.disconnect()
