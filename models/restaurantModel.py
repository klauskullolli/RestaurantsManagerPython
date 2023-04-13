from util.database import db
from util.serializer import ma
from marshmallow import fields, INCLUDE, validates , ValidationError, post_load
from models.orderModel import OrderSchema
from models.menuModel import  MenuSchema
from models.productMenu import  ProductSchema 
class RestaurantModel(db.Model):
    __tablename__ = 'restaurant'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200))
    rate = db.Column(db.Integer)
    
    manager_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    manager = db.relationship("UserModel", back_populates ='restaurant', lazy=True, uselist=False)
    
    orders = db.relationship(
        'OrderModel', backref='restaurant', lazy=True, cascade='all, delete-orphan')
    menus = db.relationship(
        'MenuModel', backref='restaurant',  cascade='all, delete-orphan')
    products  = db.relationship('ProductModel',  backref='restaurant', cascade='all, delete-orphan')




class RestaurnatSchema(ma.Schema):
    class Meta: 
        model  =  RestaurantModel
        unknown = INCLUDE
        # ordered = True
        
    id = fields.Number(dump_only= True)
    name =  fields.String()
    address  = fields.String(dump_default=None, load_default=None)
    rate =  fields.Number()
    manager_id = fields.Number(dump_default=None, load_default=None)
    orders =  fields.Nested(OrderSchema(many=True, exclude=('restaurant_id',)))
    menus  =  fields.Nested(MenuSchema(exclude=('restaurant_id',), many=True))
    products = fields.Nested(ProductSchema(exclude={'sells', 'restaurant_id',}, many=True))
    
    
    @validates('rate')
    def rate_validation(self,  value): 
        if not (value>=0 and value<=10): 
            raise ValidationError(f'Rate: {value} should be between 0-10')
    
    @post_load
    def getRestaurantModel(self, data ,  many, **kwargs): 
        return RestaurantModel(**data) 