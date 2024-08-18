import logging
import os
import boto3
from flask import Flask, jsonify, request

from flask_migrate import Migrate
from sqlalchemy import insert
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

from models import db, Users, Post, Image, Hashtag, posthashtag_table


app = Flask(__name__)

#DB connection=======================================================
db_user = os.getenv("DB_USER")
db_pass = os.getenv("DB_PASS")
db_name = os.getenv("DB_NAME")
db_host = os.getenv("DB_HOST")
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql+psycopg2://{db_user}:{db_pass}@{db_host}:5432/{db_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate = Migrate(app, db)

#S3 connection=======================================================
S3_BUCKET = os.getenv('BUCKET_NAME')
S3_REGION = os.getenv('REGION_NAME')
S3_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY_ID')
S3_SECRET_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')

s3 = boto3.client(
    's3',
    region_name=S3_REGION,
    aws_access_key_id=S3_ACCESS_KEY,
    aws_secret_access_key=S3_SECRET_KEY,
)
#uploading section======================================================= 미완이여
@app.route('/upload', methods=['POST'])
def upload_image():
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No \'image\' in the request'}), 400

        file = request.files['image']
        
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
    except:
        return jsonify({'error': e}), 400

    filename = secure_filename(file.filename)

    try:
        s3.upload_fileobj(
            file,
            S3_BUCKET,
            filename,
            ExtraArgs={"ACL": "public-read", "ContentType": file.content_type}#public to private?
        )
    except Exception as e:
        app.logger.error(f"Error occurred: {str(e)}")
        return jsonify({'error': str(e)}), 500

    # 업로드된 파일의 URL 생성
    file_url = f"https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com/{filename}"

    return jsonify({'image_url': file_url}), 201

# posting section=======================================================
@app.route('/post', methods=['POST'])
def post():
    data = request.get_json()
    user_num = data['user_num']
    content = data['content']
    location = data['location']#nullable
    imageUrls = data['imageUrls']
    hashtags = data['hashtags']#nullable

    #convert location to WKT
    if location:
        location_wkt = f'POINT({location["longitude"]} {location["latitude"]})'
    else:
        location_wkt = None 

    new_post = Post(user_num=user_num, content=content, location=location_wkt)
    db.session.add(new_post)
    db.session.commit()
    
    for imageUrl in imageUrls:
        new_image = Image(post_id=new_post.post_id, url=imageUrl)
        db.session.add(new_image)
    db.session.commit()
#================================================================================================
    for tag in hashtags:
        existing_tag = Hashtag.query.filter_by(tag_name=tag).first()#check if tag exists
        if not existing_tag:#if tag does not exist, create new tag
            new_tag = Hashtag(tag_name=tag)
            db.session.add(new_tag)
            db.session.commit()
            existing_tag = new_tag

        stmt = insert(posthashtag_table).values(post_id=new_post.post_id, tag_id=existing_tag.tag_id)
        db.session.execute(stmt)
    db.session.commit()

    return jsonify({'message': 'Post created successfully'}), 201

# User Registration and Login
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
    
    return jsonify({'user_num': user.user_num, 'message': 'Login successful'}), 200




if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    app.run(debug=True)

