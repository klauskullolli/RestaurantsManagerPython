from util.database import db
from util.errorHandler import  exceptionHandler,  notFoundHandler
from  flask import  Blueprint, request 
from models.restaurantModel import  RestaurantModel, RestaurnatSchema 
from util.response import response_with 
from util.security import authenticated, getCurrentLoggedUser
from models.roleModel import ROLE

restaurant_controller  = Blueprint('restaurant', __name__)

session =  db.session 
serializer =  RestaurnatSchema()
serializers = RestaurnatSchema(many = True)

@restaurant_controller.route('/', methods=['GET'])
@authenticated(roles=['ALL'])
def getRestaurants():
    try:
        restaurants  = RestaurantModel.query.all()
        if not restaurants: 
            return  response_with(data=[]) 
        return response_with(data = serializers.dump(restaurants))
    except  Exception as e:
        return exceptionHandler(e)


@restaurant_controller.route('/<id>',  methods=['GET'])
@authenticated(roles=['ALL'])
def getRestaurantById(id: int):
    try:
        restaurant  = RestaurantModel.query.filter_by(id=id).first()
        if not restaurant :
            return notFoundHandler(f'Restaurant with id: {id} does not exist')
        return response_with(data=serializer.dump(restaurant))
    except Exception as e:
        return exceptionHandler(e)
    

@restaurant_controller.route('/<id>',  methods=['DELETE'])
@authenticated(roles=[ROLE.ADMIN , ROLE.SUPERUSER])
def deleteRestaurantById(id:int):
    try:
        restaurant  = RestaurantModel.query.filter_by(id=id).first()
        if not restaurant :
            return notFoundHandler(f'Restaurant with id: {id} does not exist')
        session.delete(restaurant)
         
        res = {
            'message': f'Restaurant with id:{id} deleted succesfully'
        }
        
        return response_with(data=res)
    except Exception as e:
        return exceptionHandler(e) 
    
    
@restaurant_controller.route('/', methods=['POST'])
@authenticated(roles=[ROLE.ADMIN , ROLE.SUPERUSER])
def createRestaurant(): 
    try:
        restaurant =  serializer.load(request.get_json())
        session.add(restaurant)
        session.commit()
        
        session.refresh(restaurant)
        
        return response_with(data=serializer.dump(restaurant), code=201)
    except Exception as e:
        
        return exceptionHandler(e)
        
        
@restaurant_controller.route('/<id>', methods=['PUT'])
@authenticated(roles=[ROLE.ADMIN , ROLE.SUPERUSER])
def updateRestaurant(id:int):
    try:
        restaurant  = RestaurantModel.query.filter_by(id=id).first()
        if not restaurant :
            return notFoundHandler(f'Restaurant with id: {id} does not exist')
        
        body  =  request.get_json()
        if body.get('name'): restaurant.name = body['name']
        if body.get('address'): restaurant.address = body['address']
        if body.get('rate'): 
            serializer.rate_validation(body['rate'])
            restaurant.rate = body['rate']
        
        session.add(restaurant)
        session.commit()
        session.refresh(restaurant)
      
        return response_with(data=serializer.dump(restaurant))
    except Exception as e:
        return exceptionHandler(e) 
