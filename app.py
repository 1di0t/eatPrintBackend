from flask import Flask, jsonify, request
import os
import boto3
from flask_sqlalchemy import SQLAlchemy#SQLAlchemy SQL Toolkit libary
from flask_migrate import Migrate
from flask_cors import CORS


from botocore.exceptions import ClientError

from werkzeug.security import generate_password_hash, check_password_hash#hashing password library

from models import db, User


app = Flask(__name__)

#DynamoDB configurations
dynamodb = boto3.resource('dynamodb', region_name='ap-northeast-2')
table_name = 'eatprint-posts'#table name in dynamodb already created
table = dynamodb.Table(table_name)


# MySQL configurations
db_user = os.getenv("DB_USER")
db_pass = os.getenv("DB_PASS")
db_name = os.getenv("DB_NAME")
db_host = os.getenv("DB_HOST")
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{db_user}:{db_pass}@{db_host}/{db_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate = Migrate(app, db)


#MySQL
#===========================================================================================
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    userid = data['userid']
    userpw = generate_password_hash(data['userpw'], method='pbkdf2:sha256')
    #get the user data from the request for check it exists or not
    existing_user = User.query.filter_by(userid=userid).first()
    #check duplicate user id
    if existing_user:
        return jsonify({'message': 'User ID already exists'}), 409
    #create new user
    new_user = User(userid=userid, userpw=userpw)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User registered successfully'}), 201
    

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    userid = data['userid']
    userpw = data['userpw']
    #check user id exists
    user = User.query.filter_by(userid=userid).first()
    #if user id does not exist
    if user is None:
        return jsonify({'message': 'User ID does not exist'}), 404
    #check password when user id exists
    if not check_password_hash(user.userpw, userpw):
        return jsonify({'message': 'Incorrect password'}), 401
    
    return jsonify({'id': user.id, 'message': 'Login successful'}), 200


#dynamoDB
@app.route('/upload', methods=['POST'])
def upload_item():
    data = request.json
    usernum = data.get('usernum')
    text = data.get('text')
    image_data = data.get('image')  # base64로 인코딩된 이미지 데이터

    if not all([usernum, text]):
        return jsonify({'error': 'Missing usernum, text'}), 400

    try:
        # 이미지를 S3에 저장하는 로직 추가 가능
        table.put_item(
            Item={
                'usernum': usernum,
                'text': text,
                'image': image_data  # 이미지를 base64 인코딩된 문자열로 저장
            }
        )
        return jsonify({'message': 'Item created successfully'}), 201
    except ClientError as e:
        return jsonify({'error': str(e)}), 500

@app.route('/items', methods=['GET'])
def get_items():
    try:
        response = table.scan()
        items = response.get('Items', [])
        return jsonify(items)
    except ClientError as e:
        return jsonify({'error': str(e)}), 500

@app.route('/item', methods=['POST'])
def create_item():
    item = request.json
    try:
        table.put_item(Item=item)
        return jsonify({'message': 'Item created successfully'}), 201
    except ClientError as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

