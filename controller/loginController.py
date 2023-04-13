from util.application import app 
from util.errorHandler import exceptionHandler, badRequestHandler, notFoundHandler , strtimeFomrat
from flask import request 
from  util.response import response_with
from models.userModel import  UserModel 
from datetime import datetime, timedelta ,timezone
from  config.config import  ProductionConfig
from util.security import  authenticated
import  jwt

@app.route('/login', methods=['POST'])
def login(): 
    try:
        username  =  request.form['username']
        if not username: 
            return badRequestHandler('username form param is missing')
        password = request.form['password']
        if not password: 
            return badRequestHandler('password form param is missing')
        
        user =  UserModel.query.filter_by(username=username, password=password).first()
        if not user:
            return notFoundHandler('Credentials are not correct')
        
        dt = datetime.now(tz=timezone.utc)  + timedelta(seconds=ProductionConfig.TOKEN_EXPIRATION)
        
        roles = [role.name for role in user.roles]
        
        payload = {
            'username': user.username,
            'password': user.password, 
            'roles' : roles, 
            'exp' : dt
        } 
        
        access_token = jwt.encode(payload, app.config['SECRET_KEY'] , algorithm='HS256')
        
        del payload['exp']
        refresh_token = jwt.encode(payload , app.config['REFRESH_SECRET_KEY'], algorithm='HS256')
        
        body = {
            'access_token': access_token , 
            'refresh_token': refresh_token, 
            'time': datetime.now(tz=timezone.utc).strftime(strtimeFomrat) 
        }
        app.config['INVALID_TOKEN']  = False
        return response_with(data=body)
        
    except Exception as e: 
        INVALIDE  = True
        return exceptionHandler(e)
 

@app.route('/access_token/refresh', methods=['POST'])
def refreshAccessToken():
    try:
        refresh_token  = request.form['refresh_token'] 
        if not refresh_token : 
            return badRequestHandler('refresh_token form param is missing')
        payload = jwt.decode(refresh_token , app.config['REFRESH_SECRET_KEY'] , algorithms='HS256' )
        payload['exp']  = dt = datetime.now(tz=timezone.utc)  + timedelta(seconds=ProductionConfig.TOKEN_EXPIRATION)
        
        access_token = jwt.encode(payload, app.config['SECRET_KEY'] , algorithm='HS256')
        
        body = {
            'access_token': access_token , 
            'refresh_token': refresh_token, 
            'time': datetime.now(tz=timezone.utc).strftime(strtimeFomrat) 
        }
        app.config['INVALID_TOKEN'] = False
        return response_with(data=body)
        
    except  Exception as e : 
        return exceptionHandler(e) 


@app.route('/logout', methods=['POST'])  
@authenticated(roles=['ALL'])      
def logout(): 
    try:
        app.config['INVALID_TOKEN'] = False  
    except Exception  as e : 
        return exceptionHandler(e)