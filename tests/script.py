from marshmallow import Schema ,fields, post_load,  INCLUDE

from datetime import datetime
import json 
from flask import  Flask, Blueprint,  make_response,  jsonify, request, abort 
from flask_sqlalchemy import  SQLAlchemy 
from flask_marshmallow import  Marshmallow 
from marshmallow import  post_load, ValidationError
from config.config  import ProductionConfig



app =  Flask(__name__) 

db = SQLAlchemy()
ma =  Marshmallow()

app.config.from_object(ProductionConfig)

strtimeFomrat = "%d/%m/%y %H:%M:%S"


product_course = db.Table('person_course',
                        db.Column('person_id', db.Integer, db.ForeignKey(
                            'person.id'), primary_key=True),
                        db.Column('course_id', db.Integer, db.ForeignKey(
                            'course.id',), primary_key=True)
                        )


class Person(db.Model):
    __tablename__ = 'person'
    id =  db.Column(db.Integer ,primary_key=True,  autoincrement=True)
    username = db.Column(db.String(20))
    password  = db.Column(db.String(20))
    age  = db.Column(db.Integer)
    book =  db.relationship('Book',backref='person', uselist=False, cascade='all, delete-orphan')        
    courses = db.relationship('Course', secondary=product_course, lazy='subquery', back_populates='persons')   
    
class Book(db.Model): 
    __tablename__ = 'book'
    id = db.Column(db.Integer ,primary_key=True,  autoincrement=True)
    name =  db.Column(db.String(30))
    person_id = db.Column(db.Integer, db.ForeignKey('person.id'), nullable= False, unique=True)
   
   
class Course(db.Model):
    __tablename__ = 'course'
    id = db.Column(db.Integer ,primary_key=True,  autoincrement=True) 
    name  = db.Column(db.String(30))
    studentNumber =  db.Column(db.Integer, default=0)
    persons = db.relationship('Person', secondary=product_course, lazy='subquery', back_populates='courses')   
    
class BookSchema(ma.Schema): 
    class Meta:
        model =  Book 
        unknown = INCLUDE
        ordered = True
    id =  fields.Number(dump_only=True)
    name = fields.String()
    person_id = fields.Number(required=False, dump_default=None,  load_default=None)
    
    @post_load
    def getBook(self, data ,  many, **kwargs):
        return Book(**data)
        
     
class PersonSchema(ma.Schema):
    
    class Meta:
        model = Person
        unknown = INCLUDE
        ordered =  True 
        
    id = fields.Number(dump_only=True)
    username =  fields.String() 
    password =  fields.String()
    age  =  fields.Int(required=False, dump_default=None,  load_default=None)
    book =  fields.Nested(BookSchema(exclude=('person_id',)))
    courses = fields.Nested('CourseSchema', exclude=('students',), many=True)
    
    @post_load
    def getPerson(self, data ,  many, **kwargs):
        return Person(**data)
        

class CourseSchema(ma.Schema):  
    class Meta: 
        model = Course
        unknown = INCLUDE
        ordered = True 
        
    id = fields.Number(dump_only=True)  
    name  =  fields.String(required=True) 
    studentNumber = fields.Number() 
    students =  fields.Nested(PersonSchema(exclude=("book",'courses',), many=True))  
    
db.init_app(app)
ma.init_app(app)

session =  db.session
# with open('database.db', 'w') as file: 
#     pass 

with app.app_context(): 
    db.create_all()

person_controller  =  Blueprint('person', __name__)
book_controller = Blueprint('book', __name__)

def exceptionHandler(e):
    if isinstance(e,ValidationError): 
            return make_response(jsonify(e.messages), 400)
    else: 
        app.logger.error('%s', e.__str__())
        res = {
            'message':'Unexpected Error',
            'error' : e.__str__(),
            'time' :datetime.now().strftime(strtimeFomrat)
        }
        return make_response(jsonify(res), 500)
    

def notFoundHandler(mess): 
    resp ={
            'message': mess,
            'time' :datetime.now().strftime(strtimeFomrat)
        }
    return make_response(jsonify(resp), 404) 

def badRequestHandler(message): 
    resp = {
        'message': message, 
        'time' :datetime.now().strftime(strtimeFomrat)
    } 
    
    return make_response(jsonify(resp), 400) 

    
@person_controller.route('/', methods=['GET'])
def getAllPeople(): 
    try: 
        serilizer = PersonSchema(many=True)
        data   = Person.query.all()
        
        if not data: 
            return make_response(jsonify([]), 200)
        
        result = serilizer.dump(data)
        
        return make_response(jsonify(result), 200)
    except Exception as e :
        return exceptionHandler(e) 


@person_controller.route('/', methods=['POST'])
def add_Person():
    try:
        data =  request.get_json()
        serializer =  PersonSchema()
        person = serializer.load(data)
        db.session.add(person)
        db.session.commit()
        db.session.refresh(person)
        
        return make_response(jsonify(serializer.dump(person)), 200)
    except Exception as e : 
        if isinstance(e,ValidationError): 
            return make_response(jsonify(e.messages), 400)
        else: 
            app.logger.error('%s', e.__str__())
            res = {
                'message':'Unexpected Error'
            }
            return make_response(jsonify(res), 500)


    
    
@person_controller.route("/<id>", methods=['GET'])
def getPersonById(id): 
    try : 
        serializer =  PersonSchema()
        user  =  Person.query.filter_by(id=id).first()
        if not user: 
            resp ={
                'message': f'Person not found with id:{id}'
            }
            return make_response(jsonify(resp), 404)
        else: 
            return make_response(jsonify(serializer.dump(user)), 200)
    except Exception as e : 
        if isinstance(e,ValidationError): 
            return make_response(jsonify(e.messages), 400)
        else: 
            app.logger.error('%s', e.__str__())
            res = {
                'message':'Unexpected Error'
            }
            return make_response(jsonify(res), 500)
 
@person_controller.route('/<id>', methods=['PUT']) 
def updateUser(id): 
    try: 
        serializer = PersonSchema()
        newUser = serializer.load(request.get_json()) 
        person = Person.query.filter_by(id=id).first()
        if not person:
            resp ={
                'message': f'Person not found with id:{id}'
            }
            return make_response(jsonify(resp), 404) 
        newUser.id =  id
        person =  newUser
        session.commit()
        
        return make_response(jsonify(serializer.dump(person)), 200)
                  
    except Exception as e : 
        if isinstance(e,ValidationError): 
            return make_response(jsonify(e.messages), 400)
        else: 
            app.logger.error('%s', e.__str__())
            res = {
                'message':'Unexpected Error'
            }
            return make_response(jsonify(res), 500)
        
@person_controller.route('/<id>',  methods=['DELETE'])
def deletePerson(id): 
    try: 
        serializer = PersonSchema()
        person = Person.query.filter_by(id=id).first()
        if not person:
            resp ={
                'message': f'Person not found with id:{id}'
            }
            return make_response(jsonify(resp), 404) 

        session.delete(person)
        session.commit()
        
        res = {
            'message': f'Persion with id:{id} deleted succesfully'
        }
        return make_response(jsonify(res), 200)
            
    except Exception as e: 
        return exceptionHandler(e)
    

@book_controller.route("/", methods= ['GET'])
def getBooks():
    try:
        serializer  = BookSchema(many=True)
        books = Book.query.all()
        if not books: 
            return make_response(jsonify([]), 200)
        result =  serializer.dump(books)
        return make_response(jsonify(result), 200)
            
    except Exception as e :
        return exceptionHandler(e)
    

@book_controller.route('/<id>', methods = ['GET'])
def getBookById(id): 
    try: 
        serializer =  BookSchema()
        book =  Book.query.filter_by(id=id).first()
        if not book:
            return notFoundHandler(f'Book with id: {id} does not exist') 
        return make_response(jsonify(serializer.dump(book)))     
    
    except Exception as e:
        return exceptionHandler(e)
                 
@book_controller.route('/', methods = ['POST'])
def  createBook(): 
    try:
        personId  =  request.args.get('personId')
        if not personId: 
            return badRequestHandler('Person id is missing. Add personId param with person id.')
        
        person =  Person.query.filter_by(id=personId).first()
        
        if not person: 
            return notFoundHandler(f'Person with id: {personId} does not exist')
        
        serializer = BookSchema()
        newBook =  serializer.load(request.get_json())
        newBook.person_id =personId
        person.book = newBook
        session.add(newBook)
        session.commit() 
        session.refresh(newBook)
        return make_response(jsonify(serializer.dump(newBook)))
        
    except Exception as e: 
        return exceptionHandler(e)
    
    

      
  


app.register_blueprint(person_controller, url_prefix='/person')
app.register_blueprint(book_controller, url_prefix='/book')
    
if __name__ =="__main__":
    app.run(port=500, debug=True)
    