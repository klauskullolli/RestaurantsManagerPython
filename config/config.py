
import os 

basedir =  os.path.abspath(os.getcwd()).replace("/config" , '')

class Config():
    DEBUG = True
    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir ,  'resources/database1.db')
    SQLALCHEMY_ECHO =  True
    TOKEN_EXPIRATION = 1200 
    
    
    
def initDatabaseRoles()-> bool:
    return True

