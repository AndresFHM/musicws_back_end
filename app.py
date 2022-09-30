from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

from flask_bcrypt import Bcrypt
from flask_login import login_user, current_user, logout_user, login_required
import os


app = Flask(__name__)

# @app.route('/')
# def hello():
#     return "Hello you again"

bcrypt = Bcrypt(app)

SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY


basedir = os.path.abspath(os.path.dirname(__file__)) #telling flask where sqlite must be located




app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.sqlite')  #(directory, databasename)
db = SQLAlchemy(app)  #instatiate database object
ma = Marshmallow(app) #instantiate marshmallow object



class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100), unique=False)

    def __init__(self, username, password):
        self.username = username
        self.password = password

class UserSchema(ma.Schema):
    class Meta:
        fields = ('username', 'password')

user_schema = UserSchema()
users_schema = UserSchema(many=True)

#Endpoint to create a new user
@app.route('/user', methods=["POST"])
def add_user():
    username = request.json['username']
    password = request.json['password']

    new_user = User(username, password)
    
    #communicate with database
    db.session.add(new_user)
    db.session.commit()  #opening new connection and saving data

    user = User.query.get(new_user.id)

    return user_schema.jsonify(user)

# Endpoint to query all guides
@app.route("/users", methods=["GET"])
def get_users():
    all_users = User.query.all()
    result = users_schema.dump(all_users)
    return jsonify(result)

#Endpoint for querying a single user
@app.route("/user/<id>", methods=["GET"])
def get_user(id):
    user = User.query.get(id)
    return user_schema.jsonify(user)    

#Endpoint for updating a user
@app.route("/user/<id>", methods=["PUT"])
def user_update(id):
    user = User.query.get(id)
    username = request.json['username']
    password = request.json['password']

    user.username = username
    user.password = password
    
    db.session.commit()
    return user_schema.jsonify(user)

#Endpoint for deleting
@app.route("/user/<id>", methods=["DELETE"])
def user_delete(id):
    user = User.query.get(id)
    db.session.delete(user)
    db.session.commit()
    
    return "User was successfully deleted"


if __name__ == '__main__':
    app.run(debug=True)