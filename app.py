from flask import Flask, jsonify, request
import os
import boto3
from botocore.exceptions import ClientError
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash


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

db = SQLAlchemy(app)
migrate = Migrate(app, db)


#MySQL
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.String(255), unique=True, nullable=False)
    userpw = db.Column(db.String(255), nullable=False)
    
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    userid = data['userid']
    userpw = generate_password_hash(data['userpw'], method='pbkdf2:sha256')
    print(f"{userid}\n{userpw}")
    new_user = User(userid=userid, userpw=userpw)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User registered successfully'}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    userid = data['userid']
    userpw = data['userpw']
    
    user = User.query.filter_by(userid=userid).first()
    
    if user and check_password_hash(user.userpw, userpw):
        return jsonify({'id': user.id, 'message': 'Login successful'}), 200
    return jsonify({'message': 'Invalid credentials'}), 401


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

