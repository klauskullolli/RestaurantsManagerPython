from util.database import db
from util.errorHandler import exceptionHandler, notFoundHandler, badRequestHandler
from flask import  Blueprint, request 
from util.response import response_with
from models.productMenu import ProductModel, ProductSchema
from models.restaurantModel import RestaurantModel
from util.security import  authenticated, getCurrentLoggedUser
from models.roleModel import  ROLE

product_controller =  Blueprint('product', __name__)
session = db.session
serializer =  ProductSchema()
serializers = ProductSchema(many=True)

@product_controller.route('/' , methods=['GET'])
@authenticated(roles=['ALL'])
def getProducts():
    try:
        products =  ProductModel.query.all()
        if not products:
            return response_with(data=[])
        return response_with(data=serializers.dump(products)) 
    except  Exception as e: 
        return exceptionHandler(e)
    
@product_controller.route('/<id>',  methods=['GET'])
@authenticated(roles=['ALL'])
def getProductById(id:int):
    try:
        product = ProductModel.query.filter_by(id=id).first()
        if not product :
            return notFoundHandler(f'Product with id: {id} does not exist')
        return response_with(data=serializer.dump(product))
    except Exception as e:
        return exceptionHandler(e) 
    

@product_controller.route('/', methods=['POST'])
@authenticated(roles=[ROLE.MANAGER])
def addProduct(): 
    try:
        restaurant_id =  request.args.get('restaurant_id')
        if not restaurant_id:
            return badRequestHandler(f'Restaurant id is missing as restaurant_id param')
        restaurant = RestaurantModel.query.filter_by(id=restaurant_id).first()
        if not restaurant:
            return notFoundHandler(f'Restaurant with id: {restaurant_id} does not exist')
        product = serializer.load(request.get_json())
        product.restaurant_id = restaurant_id
        restaurant.products.append(product) 
        session.add(product)
        session.commit()
        session.refresh(product)
        
        return response_with(data=serializer.dump(product), code=201)    
    except Exception as e:
        return exceptionHandler(e)
    
@product_controller.route('/<id>',  methods=['PUT'])
@authenticated(roles=[ROLE.MANAGER])
def updateProduct(id: int):
    try:
        product = ProductModel.query.filter_by(id=id).first()
        if not product :
            return notFoundHandler(f'Product with id: {id} does not exist')
        
        data =  request.get_json()
        if data.get('name'): product.name = data['name']
        if data.get('price'): product.price = data['price']
        if data.get('amount'): product.amount = data['amount']
        if data.get('belonging'): 
            serializer.validate_belonging(data['belonging'])
            product.belonging = data['belonging']
        if data.get('description'): product.name = data['description']
        
        session.add(product)
        session.commit()
        return response_with(data=serializer.dump(product))
    except  Exception as e:
        return exceptionHandler(e)
    

@product_controller.route('/<id>',  methods=['DELETE'])
@authenticated(roles=[ROLE.MANAGER])
def deleteProduct(id: int):
    try:
        product = ProductModel.query.filter_by(id=id).first()
        if not product :
            return notFoundHandler(f'Product with id: {id} does not exist')
        
    
        session.delete(product)
        session.commit()
        res = {
            'message': f'Product with id:{id} deleted succesfully'
        }
        
        return response_with(data=res)
    except  Exception as e:
        return exceptionHandler(e)