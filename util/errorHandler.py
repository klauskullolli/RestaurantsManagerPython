from marshmallow import ValidationError
from util.application import  logger
from datetime import datetime
import jwt 

from  util.response import  response_with

strtimeFomrat = "%d/%m/%y %H:%M:%S"

def notFoundHandler(mess): 
    resp ={
            'message': mess,
            'time' :datetime.now().strftime(strtimeFomrat)
        }
    logger.error('%s', mess)
    return response_with(data = resp, status=404) 

def badRequestHandler(message): 
    resp = {
        'message': message, 
        'time' :datetime.now().strftime(strtimeFomrat)
    } 
    logger.error('%s', message)
    return response_with(data=resp, status=400) 


def notAuthorizedHandler(message:'Not authorized request'):
    resp = {
        'message': message, 
        'time' :datetime.now().strftime(strtimeFomrat)
    } 
    logger.error('%s', message)
    return response_with(data=resp, status=401)  

def notAuthenticatedHandler(message):
    resp = {
        'message': message, 
        'time' :datetime.now().strftime(strtimeFomrat)
    } 
    logger.error('%s', message)
    return response_with(data=resp, status=403)    

def exceptionHandler(e):
    if isinstance(e,ValidationError): 
            res = {
                'message':f'{e.messages}',
                'error' : e.__str__(),
                'type': type(e).__name__ ,
                'time' :datetime.now().strftime(strtimeFomrat)
            }
            logger.error('%s', e.__str__())
            return response_with(data = res, status =400)
        
    elif isinstance(e, jwt.InvalidTokenError): 
        return notAuthenticatedHandler('Invalid Token')
    
    elif  isinstance(e, jwt.ExpiredSignatureError) : 
        return notAuthenticatedHandler('Expired Token')
    
    else: 

        logger.error('%s', e.__str__())
        res = {
            'message':'Unexpected Error',
            'error' : e.__str__(),
            'time' :datetime.now().strftime(strtimeFomrat)
        }
        return response_with(data = res, status =500)