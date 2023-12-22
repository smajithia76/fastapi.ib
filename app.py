import asyncio
import uvicorn
from fastapi import FastAPI
import ib_insync 
import nest_asyncio
from pydantic import BaseModel
import time

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

app = FastAPI()
ib = ib_insync.IB()
ib.connect('localhost', 7497, clientId=3)

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
    

if __name__ == '__main__':
    uvicorn.run(app)