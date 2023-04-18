import  random 
import string
from  flask import request  
from util.errorHandler import exceptionHandler, notAuthorizedHandler, notAuthenticatedHandler
import jwt 
from util.application import  app
from models.userModel import UserModel 
import asyncio


def generateSecretKey(nr:int): 
    return ''.join(random.choice(string.printable) for _ in range(nr))


def authenticated(roles: list):
    def inner(func): 
        async def wrapper_async(*args, **kwargs): 
            try: 
                token  =  request.headers['Authorization']
                if not token :
                    return notAuthenticatedHandler('Token is missing in Authorization header')
                token =  token.replace('Bearer: ', '')
                
                if app.config['INVALID_TOKEN']: 
                    return notAuthenticatedHandler('Invalid Token')
                
                payload = jwt.decode(token, app.config['SECRET_KEY'] , algorithms='HS256')
                
                authorized =  False 
                
                for  role in roles: 
                    if role in ['All' , 'all' , 'ALL'] :
                        authorized = True
                    if role in payload['roles']: 
                        authorized =  True
                        break 
                    
                if not authorized:  
                    return notAuthorizedHandler('Unauthorized Request')
                                 
                return func(*args, **kwargs)
            except Exception as e : 
                return exceptionHandler(e)
            
        def wrapper_sync(*args, **kwargs): 
            try: 
                token  =  request.headers['Authorization']
                if not token :
                    return notAuthenticatedHandler('Token is missing in Authorization header')
                token =  token.replace('Bearer: ', '')
                
                if app.config['INVALID_TOKEN']: 
                    return notAuthenticatedHandler('Invalid Token')
                
                payload = jwt.decode(token, app.config['SECRET_KEY'] , algorithms='HS256')
                
                authorized =  False 
                
                for  role in roles: 
                    if role in ['All' , 'all' , 'ALL'] :
                        authorized = True
                    if role in payload['roles']: 
                        authorized =  True
                        break 
                    
                if not authorized:  
                    return notAuthorizedHandler('Unauthorized Request')
                                 
                return func(*args, **kwargs)
            except Exception as e : 
                return exceptionHandler(e)
            
       
        if asyncio.iscoroutinefunction(func):
            wrapper_async.__name__ = func.__name__
            return wrapper_async
            
        wrapper_sync.__name__ = func.__name__
        return wrapper_sync
    
    return inner 


def getCurrentLoggedUser():
    token = request.headers['Authorization'] 
    if not token : 
        raise Exception('Token is missing in request')
    token =  token.replace('Bearer: ', '')
    
    payload = jwt.decode(token, app.config['SECRET_KEY'] , algorithms='HS256')
    
    user =  UserModel.query.filter_by(username=payload['username'], password = payload['password']).first()
    if not user : 
        raise Exception('User does not exist')
    return  user 
    