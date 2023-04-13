from util.database import db
from util.serializer import  ma
from marshmallow import fields, INCLUDE, validates , ValidationError, post_load
from models.sellModel import SellSchema
from models.menuModel import product_menu 


BELONGING = ['SALADS', 'SOUPS', 'MAIN', 'DESERTS', 'DRINKS']

class ProductModel(db.Model):
    __tablename__ = 'product'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    belonging = db.Column(db.String(20), nullable=False)
    description = db.Column(db.String(200))
    sells =  db.relationship('SellModel', backref='product', lazy=True)
    restaurant_id =  db.Column(db.Integer, db.ForeignKey('restaurant.id'), nullable = False) 
    menus =  db.relationship('MenuModel', secondary=product_menu, lazy='subquery', back_populates='products')  


class  ProductSchema(ma.Schema): 
    class Meta:
        model = ProductModel
        unknown = INCLUDE
        # ordered =  True
        
    id = fields.Number(dump_only=True)
    name = fields.String(required=True)
    price = fields.Decimal()
    amount =  fields.Number()
    belonging  =  fields.String()
    description = fields.String(required = False, dump_default=None, load_default=None)
    sells =  fields.Nested(SellSchema( exclude=("order_id", "product_id",), many=True))
    restaurant_id =  fields.Number(required = False, dump_default=None, load_default=None)
    
    
    @validates('belonging')
    def validate_belonging(self, value): 
        if value not in BELONGING:
            raise  ValidationError(f'{value} belonging is not one of {BELONGING}') 
    
    @post_load() 
    def getProductModel(self, data ,  many, **kwargs):
        return ProductModel(**data)       
    
class Belonging():
    SALADS = 'SALADS'
    SOUPS = 'SOUPS'
    MAIN = 'MAIN'
    DESERTS = 'DESERTS'
    DRINKS = 'DRINKS'

