# import sys
# import os
# sys.path.append(os.path.abspath("."))

from util.database import db
from util.serializer import ma
from datetime import datetime
from marshmallow import  fields, INCLUDE ,validates, ValidationError, post_load
from models.sellModel import SellSchema


STATUS =  ['CREATED', 'APPROVED', 'REJECT', 'PREPARED', 'WAITING', 'DELIVERED' ]

class OrderModel(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    createdDate = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20))
    restaurant_id = db.Column(db.Integer,  db.ForeignKey(
        'restaurant.id'), nullable=False)
    client_id = db.Column(
        db.Integer,  db.ForeignKey('user.id'), nullable=False)
    sells = db.relationship('SellModel', backref='order',
                            cascade='all, delete-orphan')
    
    
    
class OrderSchema(ma.Schema):
    class Meta:
        model = OrderModel
        unknown =  INCLUDE
        # ordered = True
        
    id =  fields.Number(dump_only= True)
    createdDate =  fields.DateTime(dump_only=True)
    status =  fields.String(dump_default= None, load_default=None)
    client_id = fields.Number(dump_default= None, load_default=None) 
    restaurant_id =  fields.Number(dump_default= None, load_default=None)
    sells  =  fields.Nested(SellSchema( exclude=("order_id", ), many=True))   
    
    
    @validates('status')
    def status_validation(self, value): 
        if value not in STATUS:
            raise ValidationError(f"{value} status is not in {STATUS}")
        
    @post_load
    def getOrderModel(self, data ,  many, **kwargs):
        return OrderModel(**data)    
    

class OrderStatus: 
    CREATED = 'CREATED'
    APPROVED = 'APPROVED'
    REJECT = 'REJECT'
    PREPARED = 'PREPARED'
    WAITING = 'WAITING'
    DELIVERED = 'DELIVERED'
    
    