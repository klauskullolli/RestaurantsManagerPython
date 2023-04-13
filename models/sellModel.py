# import sys
# import os
# sys.path.append(os.path.abspath("."))
from util.database import db
from util.serializer import ma
from marshmallow import fields, INCLUDE, post_load

class SellModel(db.Model):
    __tablename__ = 'sell'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    amount = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200))
    order_id = db.Column(db.Integer, db.ForeignKey(
        'orders.id'),  nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey(
        'product.id'), nullable=False)
    
    
class SellSchema(ma.Schema):
    class Meta:
        model =  SellModel
        unknown = INCLUDE
        # ordered =  True 
    
    id =  fields.Number(dump_only = True)
    amount = fields.Number(dump_default=None , load_default=None)
    price = fields.Decimal(dump_default=None , load_default=None)
    description =  fields.String(required=False, dump_default=None, load_default=None)
    order_id =  fields.Number(dump_default=None , load_default=None)
    product_id = fields.Number(dump_default=None, load_default=None)

    @post_load()
    def getSellModel(self, data , many , **kwargs): 
        return SellModel(**data)
        