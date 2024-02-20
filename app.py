import asyncio
import uvicorn
from fastapi import FastAPI
import ib_insync 
import nest_asyncio
from pydantic import BaseModel
import time
import IBDataSource
import threading
import json

# package import statement
from SmartApi import SmartConnect #or from SmartApi.smartConnect import SmartConnect
import pyotp
from logzero import logger

from ordermanager import OrderManager

nest_asyncio.apply()
#"{\"symbol\":\"TCS\",\"securityType\":\"STK\",\"currency\":\"INR\",\"exchange\":\"NSE\",\"action\":\"BUY\",\"quantity\":25,\"contractMonth\":\"\",\"id\":0}"

class OrderDetail(BaseModel):
    symbol: str
    securityType: str
    currency: str 
    exchange: str
    quantity: int
    action: str
    contractMonth: str

class LimitOrderDetail(BaseModel):
    symbol: str
    securityType: str
    currency: str 
    exchange: str
    quantity: int
    action: str
    contractMonth: str
    limitPrice: float

class BracketOrderDetail(BaseModel):
    parentOrderId: int
    symbol: str
    securityType: str
    currency: str 
    exchange: str
    quantity: int
    action: str
    orderType: str
    limitPrice: float
    stopLossPrice: float
    takeProfitLimitPrice: float

app = FastAPI()
ib = ib_insync.IB()
ib.connect('localhost', 7497, clientId=3)
ibDataSource = IBDataSource.IBDataSource()
om = OrderManager(ibDataSource.reqOpenOrders())
ibDataSource.registerOrderListener(om)
lock = threading.Lock()


# @app.on_event("startup")
# async def start_tasks():
#     await ib.connectAsync('localhost', 7497, clientId=3)

@app.post("/placeOrder")
async def placeOrder(orderDetail: OrderDetail):
    print(orderDetail)
    contract = ib_insync.Stock(orderDetail.symbol, orderDetail.exchange, orderDetail.currency)
    order = ib_insync.MarketOrder(orderDetail.action, orderDetail.quantity)
    print("Before placeOrder")
    trade = ib.placeOrder(contract, order)
    print("After placeOrder")
    print(trade.log)
    print(trade.orderStatus.status)
    return trade.order

@app.post("/placeLimitOrder")
async def placeLimitOrder(limitOrderDetail: LimitOrderDetail):
    print(limitOrderDetail)
    contract = ib_insync.Stock(limitOrderDetail.symbol, limitOrderDetail.exchange, limitOrderDetail.currency)
    order = ib_insync.LimitOrder(limitOrderDetail.action, limitOrderDetail.quantity, limitOrderDetail.limitPrice)
    print("Before placeLimitOrder")
    trade = ib.placeOrder(contract, order)
    print("After placeLimitOrder")
    print(trade.log)
    print(trade.orderStatus.status)
    return trade.order    

@app.post("/placeBracketOrder")
async def placeBracketOrder(bracketOrderDetail: BracketOrderDetail):
    print(bracketOrderDetail)
    lock.acquire()
    orders = ibDataSource.placeBracketOrder(bracketOrderDetail.parentOrderId,
                                   bracketOrderDetail.symbol, 
                                   bracketOrderDetail.securityType, 
                                   bracketOrderDetail.currency, 
                                   bracketOrderDetail.exchange, 
                                   bracketOrderDetail.action, 
                                    bracketOrderDetail.quantity,
                                    bracketOrderDetail.limitPrice,
                                    bracketOrderDetail.takeProfitLimitPrice,
                                    bracketOrderDetail.stopLossPrice)
    
    for order in orders:
        print("****************")
        print(order)
        print("****************")

    om.addOrders(orders)
    lock.release()

@app.post("/cancelAllOrders")
async def cancelAllOrders():
    ibDataSource.cancelAllOrders()

# @app.get("/getHistoricalData")
# async def getHistoricalData():
#     ib.

if __name__ == '__main__':

    # api_key = ''
    # username = ''
    # pwd = ''
    # token = ''

    # f = open("d://tmp//brokers.json")
    # brokers = json.load(f)

    # for broker in brokers['brokers']:
    #     if broker['name'] == 'angel':
    #         api_key = broker['apikey']
    #         username = broker['clientcode']
    #         pwd = broker['mpin']
    #         token = broker['totp']

    # smartApi = SmartConnect(api_key)
    # try:
    #     totp = pyotp.TOTP(token).now()
    # except Exception as e:
    #     logger.error("Invalid Token: The provided token is not valid.")
    #     raise e

    # correlation_id = "abcde"
    # data = smartApi.generateSession(username, pwd, totp)

    # if data['status'] == False:
    #     logger.error(data)
        
    # else:
    #     # login api call
    #     # logger.info(f"You Credentials: {data}")
    #     authToken = data['data']['jwtToken']
    #     refreshToken = data['data']['refreshToken']
    #     # fetch the feedtoken
    #     feedToken = smartApi.getfeedToken()
    #     # fetch User Profile
    #     res = smartApi.getProfile(refreshToken)
    #     smartApi.generateToken(refreshToken)
    #     res=res['data']['exchanges']
    uvicorn.run(app)