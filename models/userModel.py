# import sys
# import os
# sys.path.append(os.path.abspath("."))

from util.database import db
from util.serializer import ma
from marshmallow import  fields, INCLUDE, post_load, validates, ValidationError, post_dump
from models.orderModel import OrderSchema
from models.restaurantModel import RestaurnatSchema
from models.roleModel import  role_user, RoleSchema


class UserModel(db.Model):
    __tablename__ = 'user'
    extend_existing=True
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(20))
    surname = db.Column(db.String(20))
    email = db.Column(db.String(20))
    phone = db.Column(db.String(12))
    username = db.Column(db.String(20), nullable=False, index= True,  unique = True)
    password = db.Column(db.String(20), nullable=False)
    roles =  db.relationship('Role', secondary=role_user, lazy='subquery', back_populates ='users') 
    restaurant = db.relationship('RestaurantModel',back_populates ='manager', uselist=False)    
    orders = db.relationship(
        'OrderModel', backref='client', cascade='all, delete-orphan')


class UserSchema(ma.Schema):
    class Meta:
        model  = UserModel
        unknown = INCLUDE
        # ordered = True
    
    
    id = fields.Number(dump_only=True)
    name =  fields.String(dump_default=None , load_default=None)
    surname =  fields.String(dump_default=None , load_default=None)
    email =  fields.String(dump_default=None , load_default=None)
    phone = fields.String(dump_default=None , load_default=None)
    username =  fields.String()
    password = fields.String()
    roles  = fields.Nested(RoleSchema(many=True, exclude=('id',)))
    restaurant = fields.Nested(RestaurnatSchema(exclude=("manager_id", "orders",'products', 'menus' )))  
    orders = fields.Nested(OrderSchema(many=True), exclude=('client_id',))
    
    
    # @validates('role')
    # def role_validation(self, value):
    #     if value not in ROLES  :
    #         raise ValidationError(f'Role: {value} is not in {ROLES}')
    
    # @post_dump()
    # def setUserModel(self, data, many, **kwargs):
    #     roles  = data['roles']
    #     roles  = [role['name'] for role in roles ]
    #     data['roles'] = roles
    #     return data 
    
    @post_load()
    def getUserModel(self, data, many, **kwargs):
        return  UserModel(**data)
    
        


# class Role():
#     SUPERUSER = 'SUPERUSER'
#     ADMIN = 'ADMIN'
#     RESTAURANT_MANAGER = 'RESTAURANT_MANAGER'
#     CLIENT = 'CLIENT'
