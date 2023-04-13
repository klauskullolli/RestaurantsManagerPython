from flask import Blueprint , request 
from util.response import  response_with
from util.errorHandler import exceptionHandler, notFoundHandler, badRequestHandler
from util.database import  db 
from  models.menuModel import  MenuModel , MenuSchema 
from models.restaurantModel import RestaurantModel
from models.productMenu import  ProductModel
from marshmallow import  ValidationError
from sqlalchemy import  text
from util.security import authenticated, getCurrentLoggedUser
from models.roleModel import  ROLE

menu_controller = Blueprint('menu', __name__)
session = db.session 
serializer =  MenuSchema()
serializers = MenuSchema(many=True)




@menu_controller.route('/', methods=['GET'])
@authenticated(roles=[ROLE.SUPERUSER , ROLE.CLIENT, ROLE.MANAGER])
def getMenus():
    try:
        menus =  MenuModel.query.all()
        if not menus:
            return response_with(data=[])
        return response_with(data=serializers.dump(menus)) 
    except  Exception as e: 
        return exceptionHandler(e)

  
@menu_controller.route('/<id>',  methods=['GET'])
@authenticated(roles=[ROLE.SUPERUSER , ROLE.CLIENT, ROLE.MANAGER])
def getMenuById(id:int):
    try:
        menu = MenuModel.query.filter_by(id=id).first()
        if not menu :
            return notFoundHandler(f'Menu with id: {id} does not exist')
        return response_with(data=serializer.dump(menu))
    except Exception as e:
        return exceptionHandler(e) 


@menu_controller.route('product/<id>', methods=['POST'])
@authenticated(roles=[ROLE.MANAGER])
def addMenu(id:int): 
    try:
        restaurant_id =  request.args.get('restaurant_id')
        if not restaurant_id : 
            return badRequestHandler(f'restaurant_id request param is missing')
        
        restaurant = RestaurantModel.query.filter_by(id=restaurant_id).first()
        if not restaurant:
            return notFoundHandler(f'Restaurant with id: {restaurant_id} does not exist')
        
        
        product  = ProductModel.query.filter_by(restaurant_id=restaurant_id, id=id).first()
        
        if not product: 
            return notFoundHandler(f'Product with id: {id} does not exist or is not in this restaurant')
        
        menu = serializer.load(request.get_json())
        
        menu.restaurant_id = restaurant_id 
        menu.products.append(product)
        restaurant.menus.append(menu)
        
        session.add(menu)
        session.commit()
        session.refresh(menu)
        
        return response_with(data = serializer.dump(menu), code=201)
        
    except Exception as e: 
        session.rollback()
        return exceptionHandler(e) 
    
  
@menu_controller.route('/<id>',  methods=['DELETE'])
@authenticated(roles=[ROLE.MANAGER])  
def deleteMenu(id: int):
    try:
        menu = MenuModel.query.filter_by(id=id).first()
        if not menu :
            return notFoundHandler(f'Menu with id: {id} does not exist')

        session.delete(menu)
        session.commit()
        res = {
            'message': f'Menu with id:{id} deleted succesfully'
        }
        return response_with(data=res)
            
    except Exception as e : 
        session.rollback()
        return exceptionHandler(e)




@menu_controller.route('/<id>' , methods=['PUT'])
@authenticated(roles=[ROLE.MANAGER])  
def updateMenu(id: int): 
    try:
        menu = MenuModel.query.filter_by(id=id).first()
        if not menu :
            return notFoundHandler(f'Menu with id: {id} does not exist')
        data =  request.get_json()
        if data.get('name'): menu.name = data['name']
        if data.get('startTime'): menu.startTime = data['startTime']
        if data.get('endTime'): menu.endTime = data['endTime']
    
        data['startTime']  = menu.startTime
        data['endTime'] = menu.endTime

        serializer.val_Time(data)
        
        session.add(menu)
        session.commit()
        session.refresh(menu)
        
        return response_with(data=serializer.dump(menu))
        
    except Exception as e: 
        session.rollback()
        return exceptionHandler(e)

 
@menu_controller.route('/<id>/product/<productId>' , methods=['POST'])
@authenticated(roles=[ROLE.MANAGER])   
def addProductToMenu(id:int , productId:int): 
    try:
        menu = MenuModel.query.filter_by(id=id).first()
        if not menu :
            return notFoundHandler(f'Menu with id: {id} does not exist')
        
        product = ProductModel.query.filter_by(id=productId , restaurant_id = menu.restaurant_id).first()
        
        if not product:
            return notFoundHandler(f'Product with id: {id} does not exist or is not in this restaurant')
        
        isInMenu = session.execute(text(f'select * from product_menu where product_id= {productId} and menu_id = {id} LIMIT 1')).first()        
      
        if isInMenu: 
            return badRequestHandler(f'Porduct with id: {productId} already exist in menu')
        
        menu.products.append(product)
        
        session.add(menu)
        session.commit()
        session.refresh(menu)
        
        return response_with(data=serializer.dump(menu))
    except Exception as e: 
        session.rollback()
        return exceptionHandler(e)
   
    

@menu_controller.route('/<id>/product/<productId>' , methods=['DELETE'])
@authenticated(roles=[ROLE.MANAGER])  
def delteteProductFrom(id:int , productId:int): 
    try: 
        menu = MenuModel.query.filter_by(id=id).first()
        if not menu :
            return notFoundHandler(f'Menu with id: {id} does not exist') 
        
        product = ProductModel.query.filter_by(id=productId , restaurant_id = menu.restaurant_id).first()
        
        if not product:
            return notFoundHandler(f'Product with id: {id} does not exist or is not in this restaurant')
        
        isInMenu = session.execute(text(f'select * from product_menu where product_id= {productId} and menu_id = {id} LIMIT 1')).first()
        
        if  not isInMenu: 
            return badRequestHandler(f'Porduct with id: {productId} does exist in menu')
        
        menu.products.remove(product)
        
        session.add(menu)
        session.commit()
        session.refresh(menu)
        
        return response_with(data = serializer.dump(menu))
        
    except Exception as e : 
        session.rollback()
        return exceptionHandler(e)