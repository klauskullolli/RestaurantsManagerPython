from flask import Blueprint, make_response, jsonify ,request
from  models.userModel import  UserModel, UserSchema 
from util.errorHandler import  exceptionHandler, notFoundHandler, notAuthorizedHandler
from util.response import response_with
from util.database import db
from models.roleModel import Role, ROLE
from util.security import  authenticated , getCurrentLoggedUser


user_controller = Blueprint("user", __name__)

serializer = UserSchema()
serializers = UserSchema(many=True)
session  =  db.session


@user_controller.route('/', methods=['GET']) 
@authenticated(roles=[ROLE.ADMIN , ROLE.SUPERUSER]) 
def getAllUsers():
    try: 
        loggedUser  = getCurrentLoggedUser()
        roles = [role.name for role in loggedUser.roles]
        data = None
        if ROLE.isSuperUser(roles): 
            data =  UserModel.query.all()
        else: 
            data =  UserModel.query.join(Role , UserModel.roles).filter(Role.name !=ROLE.SUPERUSER)
        if not data: 
            return response_with(data=[])
        result =  serializers.dump(data)
        return response_with(data=result)
    except Exception as e : 
        return exceptionHandler(e)



@user_controller.route('/<id>', methods=['GET']) 
@authenticated(roles=['ALL']) 
def getUserById(id):
    try: 
        user  =  UserModel.query.filter_by(id=id).first()
        loggedUser =  getCurrentLoggedUser()
        loggedUserRoles =   [role.name for role in loggedUser.roles]
        
        if not user : 
            return notFoundHandler(f'User with id: {id} does not exist')
        
        roles  =  [role.name for role in user.roles]
        
        if ROLE.isAdmin(loggedUserRoles) or ROLE.isSuperUser(loggedUserRoles): 
            return response_with(data=serializer.dump(user))
        else: 
            if ROLE.haveSimilarRole(loggedUserRoles, roles):
                return response_with(data=serializer.dump(user))
                
            else:
                return  notAuthorizedHandler(f'Use with id: {loggedUser.id} is not authorzied for this request')
    except Exception as e:
        return exceptionHandler(e)


      
@user_controller.route('/<role>', methods=['POST'])
@authenticated(roles=[ROLE.ADMIN , ROLE.SUPERUSER])  
def addUser(role:str): 
    try:
        role  = role.upper()
        roleDb = Role.query.filter_by(name= role).first()
        loggedUser  =  getLoggedUser()
        if not roleDb: 
            return notFoundHandler(f'Role : {role} does not exist')
        
        if role == ROLE.ADMIN and ROLE.isAdmin(loggedUser.roles): 
            return notAuthorizedHandler()
        
        user = serializer.load(request.get_json())
        user.roles.append(roleDb)
        session.add(user)
        session.commit()
        session.refresh(user)
        return response_with(data=serializer.dump(user))
    except Exception as e:
        return exceptionHandler(e)
    
      
@user_controller.route('/<id>', methods= ['DELETE'])
@authenticated(roles=[ROLE.ADMIN , ROLE.SUPERUSER])   
def deleteUserById(id:int):
    try:
        user = UserModel.query.filter_by(id=id).first()
        loggedUser  =  getLoggedUser()
        if not user: 
            return notFoundHandler(f'User with id: {id} does not exist')
        
        if (ROLE.isAdmin(user.roles) or ROLE.isSuperUser(user.roles)) and ROLE.isAdmin(loggedUser.roles): 
            return notAuthorizedHandler()
        
        session.delete(user)
        session.commit()
        
        res = {
            'message': f'User with id:{id} deleted succesfully'
        }
        
        return response_with(data=res)
    
    except Exception as e:
        return exceptionHandler(e) 
    
    
     
@user_controller.route('/<id>', methods= ['PUT'])
@authenticated(roles=['ALL']) 
def updateUserById(id): 
    try:
        user = UserModel.query.filter_by(id=id).first()
        loggedUser = getLoggedUser()
        if not user: 
            return notFoundHandler(f'User with id: {id} does not exist')
        
        loggedRoles =  [role.name for role in loggedUser.roles]
        roles  = [role.name for role  in user.roles]
        
        if (ROLE.isClient(loggedRoles) or ROLE.isManager(loggedRoles)) and loggedUser.id != user.id :
            return notAuthorizedHandler() 
        
        if(ROLE.isAdmin(roles) and ROLE.isAdmin(loggedRoles)) and  loggedUser.id != user.id:
            return notAuthorizedHandler()       
        
        if(ROLE.isSuperUser(roles) and ROLE.isAdmin(loggedRoles)):
            return notAuthorizedHandler()
        
        req  = request.get_json() 
        
        if req.get('name'): user.name =  req['name']
        if req.get('surname'): user.surname =  req['surname']
        if req.get('email'): user.email =  req['email']
        if req.get('phone'): user.phone =  req['phone']
        if req.get('username'): user.username =  req['username']
        if req.get('password'): user.password =  req['password']
        
        session.add(user)
        session.commit()
        
        return response_with(data=serializer.dump(user))
    
    except Exception as e:
        return exceptionHandler(e)  
    
    
   
@user_controller.route('username/<username>', methods=['GET'])
@authenticated(roles=[ROLE.ADMIN , ROLE.SUPERUSER]) 
def getUserByUsername(username: str):
    try:
        user =  UserModel.query.filter_by(username=username).first()
        loggedUser  =  getCurrentLoggedUser()
        loggedRoles = [role.name for role in loggedUser.roles]
        
        if not user: 
            return notFoundHandler(f'User with username: {username} does not exist')
        roles = [role.name for role in user.roles]
        
        if ROLE.isSuperUser(roles) and ROLE.isAdmin(loggedRoles): 
            return notAuthorizedHandler()
        
        return response_with(data=serializer.dump(user))
    except Exception as e: 
        return exceptionHandler(e)