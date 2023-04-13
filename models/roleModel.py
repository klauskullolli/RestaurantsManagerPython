from util.database import  db 
from util.serializer import ma

from marshmallow import  INCLUDE, fields, post_load, post_dump
ROLES = ['SUPERUSER', 'ADMIN' , 'MANAGER', 'CLIENT']


role_user = db.Table('role_user',
                        db.Column('role_id', db.Integer, db.ForeignKey(
                            'role.id'), primary_key=True),
                        db.Column('user_id', db.Integer, db.ForeignKey(
                            'user.id',), primary_key=True)
                        )


class Role(db.Model):
    __tablename__ = 'role'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(20), nullable=False, unique=True, index=True) 
    users =  db.relationship('UserModel', secondary=role_user, lazy='subquery', back_populates='roles')  


class RoleSchema(ma.Schema):
    class Meta:
        model  = Role
        unknown = INCLUDE
        # ordered = True 
        
    id = fields.Number(dump_only=True)
    name =  fields.String()
    
    @post_dump()
    def setRole(self, data,  many, **kwargs):
        return data['name'] 
    
    
    @post_load()
    def getRole(self, data,  many, **kwargs):
        return Role(**data)


class  ROLE: 
    SUPERUSER = 'SUPERUSER'
    ADMIN = 'ADMIN'
    MANAGER = 'MANAGER'
    CLIENT = 'CLIENT'
    

    def isAdmin(roles:list): 
        if isinstance(roles[0], Role):
            roles =  [role.name for role in roles] 
        return ROLE.ADMIN in roles
    
    def isSuperUser(roles: list): 
        if isinstance(roles[0], Role):
            roles =  [role.name for role in roles] 
        return ROLE.SUPERUSER in roles
    
    def isClient(roles: list): 
        if isinstance(roles[0], Role):
            roles =  [role.name for role in roles] 
        return  ROLE.CLIENT in roles 
    
    def  isManager(roles: list): 
        if isinstance(roles[0], Role):
            roles =  [role.name for role in roles] 
        return ROLE.MANAGER in roles
    
    def haveSimilarRole(rolesA: list, rolesB:list)-> bool:
        if isinstance(rolesA[0], Role):
            rolesA =  [role.name for role in rolesA] 
        if isinstance(rolesB[0], Role):
            rolesB =  [role.name for role in rolesB] 
        
        for role in rolesA: 
            if role in rolesB: 
                return True
        return False 