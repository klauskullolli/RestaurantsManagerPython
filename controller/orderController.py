from flask import Blueprint , request 
from util.database import db
from util.response import  response_with
from util.errorHandler import  exceptionHandler, badRequestHandler, notFoundHandler
from models.orderModel import  OrderModel, OrderSchema , OrderStatus
from  models.menuModel import  MenuModel
from  models.productMenu import  ProductModel
from models.userModel import UserModel
from models.roleModel import  Role, ROLE
from datetime import datetime, timezone
from models.sellModel import SellModel
from  service.orderService import  isActive
from sqlalchemy import  text
from util.security import authenticated, getCurrentLoggedUser
from models.roleModel import ROLE

order_controller  = Blueprint('order', __name__)
serializer  = OrderSchema()
serializers = OrderSchema(many=True)
session =  db.session



@order_controller.route('/', methods=['GET'])
@authenticated(roles=[ROLE.CLIENT , ROLE.MANAGER])
def getOrders(): 
    try:
        orders =  OrderModel.query.all()
        if not orders: 
            return response_with(data=[])
        return response_with(data=serializers.dump(orders)) 
    except Exception as e:
        return exceptionHandler(e)
    
    
@order_controller.route('/<id>' , methods=['GET'])
@authenticated(roles=[ROLE.CLIENT , ROLE.MANAGER])
def getOrderById(id: int):
    try:
        order  = OrderModel.query.filter_by(id=id).first()
        if not order:
            return notFoundHandler(f'Order with id: {id} does not exist') 
        return response_with(data = serializer.dump(order))
    except  Exception as e :
        return exceptionHandler(e)
    
    
@order_controller.route('/menu/<menuId>/product', methods=['POST']) 
@authenticated(roles=[ROLE.CLIENT])
def createOrder(menuId:int): 
    try:
        menu =  MenuModel.query.filter_by(id=menuId).first()
        if not menu: 
            return notFoundHandler(f'Menu with id: {menuId} does not exist')
        product_id = request.args.get('product_id')
        amount = request.args.get('amount')
        client_id =  request.args.get('client_id')
        
        if not client_id: 
            return badRequestHandler('client_id request param is missing')
        
        user  =  UserModel.query.join(Role, UserModel.roles).filter(UserModel.id == client_id  , Role.name == ROLE.CLIENT).first()
        
        if not user: 
            return notFoundHandler(f'Client with id: {client_id} does not exist')        
        
        if not product_id: 
            return badRequestHandler('product_id request param is missing')
        if not amount:  
            amount = 1  
        amount = int(amount)
        
        product = ProductModel.query.filter_by(id=product_id,  restaurant_id= menu.restaurant_id).first()
        
        if not product: 
            return notFoundHandler(f'product with id: {product_id} does not exist or is not in same restaurant as menu')
        
        isInMenu = session.execute(text(f'select * from product_menu where product_id= {product_id} and menu_id = {menuId} LIMIT 1')).first()
        
        if  not isInMenu: 
            return badRequestHandler(f'Porduct with id: {product_id} does exist in menu')
        
        if not isActive(menu.startTime, menu.endTime):   
            return badRequestHandler(f'Menu with id: {menuId} is not active now')
        
        order =  OrderModel()
        sell =  SellModel()
        
        if amount > product.amount: 
            amount = product.amount 
        
        product.amount -= amount 
        
        price = amount * product.price
        
        desc =  request.get_json().get('description')
        
        if desc: 
            sell.description = desc
    
        sell.amount = amount 
        sell.price  =price  
        sell.product_id = product_id
        
        order.restaurant_id = menu.restaurant_id
        order.client_id = user.id
        order.status = OrderStatus.CREATED
        order.sells.append(sell)
        
                
        session.add(product)
        session.add(order)
        
        session.commit()
        session.refresh(order)
        
        return response_with(data=serializer.dump(order), code=201)
        
    except Exception as e:
        session.rollback()
        return exceptionHandler(e)
    

@order_controller.route('/<id>/menu/<menuId>/product' , methods=['POST'])   
@authenticated(roles=[ROLE.CLIENT]) 
def addProductToOrder(id: int , menuId:int):
    try:
        order  =  OrderModel.query.filter_by(id=id).first()
        if not order :
            return notFoundHandler(f'Order with id: {id} does not exist')
        
        menu =  MenuModel.query.filter_by(id=menuId, restaurant_id = order.restaurant_id).first()
        if not menu :
            return notFoundHandler(f'Menu with id: {menuId} does not exist in this restaurant')
        
        if not isActive(menu.startTime, menu.endTime):   
            return badRequestHandler(f'Menu with id: {menuId} is not active now')
        
        
        product_id = request.args.get('product_id')
        amount = request.args.get('amount') 
        
        if not product_id: 
            return badRequestHandler('product_id request param is missing')
        if not amount:  
            amount = 1   
        amount = int(amount)
        
        product = ProductModel.query.filter_by(id=product_id,  restaurant_id= menu.restaurant_id).first()
        
        if not product: 
            return notFoundHandler(f'product with id: {product_id} does not exist or is not in same restaurant as menu')
        
        isInMenu = session.execute(text(f'select * from product_menu where product_id= {product_id} and menu_id = {menuId} LIMIT 1')).first()
        
        if  not isInMenu: 
            return badRequestHandler(f'Porduct with id: {product_id} does exist in menu')
        
        if product.amount == 0 :
            return badRequestHandler(f'Product with id: {product_id} has finished') 
        
        if amount > product.amount: 
            amount = product.amount 
            
        sell  = SellModel.query.filter_by(product_id = product_id , order_id = id).first() 
        
        
        desc = None
        
        if request.args.get('Content-Type') == 'application/json' : 
            desc =  request.get_json().get('description')
            
        
        if sell:
            diff =  sell.amount  -  amount 
            sell.amount  = amount 
            sell.price  =  product.price * amount
            
            if desc: sell.description = desc
            
            product.amount += diff
            session.add(sell)
               
        else : 
            sell =  SellModel()
            if desc: sell.description = desc
            sell.amount = amount 
            sell.price  = product.price * amount  
            sell.product_id = product_id
            
            product.amount -=amount 
            
            order.sells.append(sell)
            
            session.add(order)
        
        session.add(product)
        session.commit()
        session.refresh(order)
        
        return response_with(data=serializer.dump(order))    
    except Exception as e: 
        session.rollback()
        return exceptionHandler(e)
    


@order_controller.route('/<id>/product/<productId>', methods=['DELETE'])
@authenticated(roles=[ROLE.CLIENT])
def removeProductFromOrder(id:int,productId:int):
    try:
        order  =  OrderModel.query.filter_by(id=id).first()
        if not order :
            return notFoundHandler(f'Order with id: {id} does not exist') 
            
        sell = SellModel.query.filter_by(product_id=productId, order_id=id).first()
        
        if not sell : 
            return notFoundHandler(f'Product with id: {productId} does not exist in order with id: {id}')
        
        session.delete(sell)
        session.commit()
        session.refresh(order)
        return response_with(data=serializer.dump(order))
    except Exception as e: 
        return exceptionHandler(e)
    
    
@order_controller.route('/<id>', methods=['PUT']) 
@authenticated(roles=[ROLE.MANAGER])   
def updateStatus(id:int):
    try: 
        order  =  OrderModel.query.filter_by(id=id).first()
        if not order :
            return notFoundHandler(f'Order with id: {id} does not exist') 
        
        status  = str(request.args.get('status'))
        if not status: 
            return badRequestHandler('status param is missing')
        
        status = status.upper() 
        serializer.status_validation(status)
        
        order.status = status
        session.add(order) 
        session.commit()
        session.refresh(order)
        
        return response_with(data=serializer.dump(order))
        
    except Exception as e : 
        session.rollback()
        return exceptionHandler(e)