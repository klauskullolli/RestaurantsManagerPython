from util.database import db
from util.serializer import ma
from marshmallow import  fields, Schema
from marshmallow import fields, INCLUDE, validates, validates_schema, ValidationError, post_load, pre_dump
import re
from datetime import datetime, timezone


timeFromat = '%H:%M'

product_menu = db.Table('product_menu',
                        db.Column('product_id', db.Integer, db.ForeignKey(
                            'product.id')),
                        db.Column('menu_id', db.Integer, db.ForeignKey(
                            'menu.id'))
                        )


class MenuModel(db.Model):
    __tablename__ = 'menu'
    id =  db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(32), nullable=False)
    startTime = db.Column(db.String(100), nullable=False )
    endTime = db.Column(db.String(100), nullable=False)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurant.id'), nullable=False)
    products =  db.relationship('ProductModel', secondary=product_menu, lazy='subquery', back_populates='menus')    

    __table_args__ = (
        db.CheckConstraint('name IS NOT NULL', name='not_null_name'),
        db.CheckConstraint('startTime IS NOT NULL', name='not_null_startTime'),
        db.CheckConstraint('endTime IS NOT NULL', name='not_null_endTime')
    )



class MenuSchema(ma.Schema):
    class  Meta:
        model = MenuModel 
        unknown = INCLUDE
        # ordered =  True

    id =  fields.Number(dump_only=True)
    name =  fields.String(required=True)
    startTime = fields.String(required=True)
    endTime =  fields.String(required=True)
    restaurant_id = fields.Number(required = False, dump_default = None, load_default = None)
    products = fields.Nested('ProductSchema', exclude=("sells", ), many=True)
    
    
    @post_load
    def getMenuModel(self, data ,  many, **kwargs):
        return MenuModel(**data)
    
    @validates_schema()
    def val_Time(self, data,**kwargs):
     
        if not timeFormatOk(data['startTime']):
            raise ValidationError('StartTime format is not ok')
        if not timeFormatOk(data['endTime']) :
            raise ValidationError('EndTime format is not ok')
        
        startTime =  datetime.strptime(data['startTime'], timeFromat).replace(tzinfo=timezone.utc).timestamp()
        endTime = datetime.strptime(data['endTime'], timeFromat).replace(tzinfo=timezone.utc).timestamp()
            
        if startTime >= endTime : 
            raise  ValidationError('StartTime should be smaller than EndTime')

    
def timeFormatOk(string:type[str])-> bool:
    pattern = '^(\d{1}|[0]{1}[0-9]{1}|[1]{1}[0-9]{1}|[2]{1}[0-3]{1})[:]{1}([0-5]{1}[0-9]{1}|\d{1})$'
    exptress = re.match(pattern=pattern, string=string)
    
    if exptress is None:
        return False
    else:
        return True
    



