import sys
import os

from util.application import app  
from config.config import ProductionConfig, initDatabaseRoles 
from util.database import db 
from util.serializer import ma
from marshmallow import  fields
from models.orderModel import OrderModel
from models.menuModel import MenuModel
from models.productMenu import ProductModel
from models.restaurantModel import RestaurantModel
from  models.sellModel import  SellModel
from models.userModel import  UserModel
from models.roleModel import  Role , ROLES
from controller.userController import user_controller
from controller.restaurantController import restaurant_controller
from controller.productController import  product_controller
from controller.menuController import menu_controller
from controller.orderController import order_controller
from util.security import generateSecretKey

# app = Flask(__name__) 



app.config.from_object(ProductionConfig)
app.config['SECRET_KEY'] = generateSecretKey(32)
app.config['REFRESH_SECRET_KEY'] = generateSecretKey(32)
app.config['INVALID_TOKEN'] = True

logger  =  app.logger

db.init_app(app)
ma.init_app(app)



with app.app_context(): 
    db.create_all()
    try:
        if initDatabaseRoles(): 
            for role in ROLES :
                roleDb = Role(name = role)
                db.session.add(roleDb)
        db.session.commit()
    except  Exception as e : 
        app.logger.info('Roles already exist')     

app.register_blueprint(user_controller, url_prefix='/user')
app.register_blueprint(restaurant_controller, url_prefix='/restaurant')
app.register_blueprint(product_controller, url_prefix='/product')
app.register_blueprint(menu_controller, url_prefix='/menu')
app.register_blueprint(order_controller, url_prefix='/order')

from controller.loginController import  login

if __name__ == '__main__':
   
   app.run(port=5000, debug=True)
   pass