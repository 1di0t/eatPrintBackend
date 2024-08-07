from flask_sqlalchemy import SQLAlchemy

from geoalchemy2 import Geography, Geometry



db = SQLAlchemy()

class Users(db.Model):
    __tablename__ = 'USERS_TB'

    user_num = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.String(100), unique=True, nullable=False)
    user_pw = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    nick_name = db.Column(db.String(100), nullable=False)

    posts = db.relationship('Post', back_populates='USERS_TB')


class Post(db.Model):
    __tablename__ = 'POST_TB'
    
    post_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_num = db.Column(db.Integer, db.ForeignKey('USERS_TB.user_num'))
    content = db.Column(db.Text)
    location = db.Column(Geography(geometry_type='POINT', srid=4326))
    
    user = db.relationship('Users', back_populates='POST_TB')

class Hashtag(db.Model):
    __tablename__ = 'HASHTAG_TB'
    
    tag_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tag_name = db.Column(db.String(50), nullable=False, unique=True)
    
    posts = db.relationship('Post', secondary='POST_HASHTAG_TB', back_populates='hashtags')

class PostHashtag(db.Model):
    __tablename__ = 'POST_HASHTAG_TB'
    
    post_id = db.Column(db.Integer, db.ForeignKey('POST_TB.post_id'), primary_key=True)
    tag_id = db.Column(db.Integer, db.ForeignKey('HASHTAG_TB.tag_id'), primary_key=True)