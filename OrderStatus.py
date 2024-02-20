# -*- coding: utf-8 -*-
"""
Created on Thu Feb  9 17:44:37 2023

@author: smajithia
"""

class OrderStatus:
    
    def __init__(self, orderId, 
                  status,
                  filled, 
                  remaining, 
                  avgFillPrice, 
                  permId, 
                  parentId, 
                  lastFillPrice,
                  clientId,	
                  whyHeld, 
                  mktCapPrice):
        
            self.orderId = orderId 
            self.status = status
            self.filled = filled
            self.remaining = remaining 
            self.avgFillPrice = avgFillPrice 
            self.permId = permId 
            self.parentId = parentId 
            self.lastFillPrice = lastFillPrice
            self.clientId = clientId	
            self.whyHeld = whyHeld 
            self.mktCapPrice = mktCapPrice
            
    def __str__(self):
          return "orderId: {}, status:{}, filled: {}, avgFillPrice: {}, permId: {}".format(self.orderId, self.status, self.filled, self.avgFillPrice, self.permId)            