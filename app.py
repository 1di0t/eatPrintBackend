from flask import Flask, jsonify, request
import os
import boto3
from flask_sqlalchemy import SQLAlchemy#SQLAlchemy SQL Toolkit libary
from flask_migrate import Migrate
from flask_cors import CORS


from werkzeug.security import generate_password_hash, check_password_hash#hashing password library

from models import db, Users


app = Flask(__name__)

db_user = os.getenv("DB_USER")
db_pass = os.getenv("DB_PASS")
db_name = os.getenv("DB_NAME")
db_host = os.getenv("DB_HOST")
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql+psycopg2://{db_user}:{db_pass}@{db_host}:5432/{db_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
migrate = Migrate(app, db)
#Posting section
# @app.route('/post', methods=['POST'])
# def post():

#User Registration and Login
#===========================================================================================
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    userid = data['userid']
    userpw = generate_password_hash(data['userpw'], method='pbkdf2:sha256')
    name = data['name'] 
    nick_name = data['nickname']
    #get the user data from the request for check it exists or not
    existing_user = Users.query.filter_by(user_id=userid).first()
    #check duplicate user id
    if existing_user:
        return jsonify({'message': 'User ID already exists'}), 409
    #create new user
    new_user = Users(user_id=userid, user_pw=userpw,name=name,nick_name=nick_name)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User registered successfully'}), 201
    

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    userid = data['userid']
    userpw = data['userpw']
    #check user id exists
    user = Users.query.filter_by(user_id=userid).first()
    #if user id does not exist
    if user is None:
        return jsonify({'message': 'User ID does not exist'}), 404
    #check password when user id exists
    if not check_password_hash(user.user_pw, userpw):
        return jsonify({'message': 'Incorrect password'}), 401
    
    return jsonify({'id': user.user_num, 'message': 'Login successful'}), 200




if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
    app.run(debug=True)

