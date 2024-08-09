from flask_sqlalchemy import SQLAlchemy

from geoalchemy2 import Geography



db = SQLAlchemy()

class Users(db.Model):
    __tablename__ = 'user_tb'

    user_num = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.String(100), unique=True, nullable=False)
    user_pw = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    nick_name = db.Column(db.String(100), nullable=False)

    posts = db.relationship('Post', back_populates='user')


class Post(db.Model):
    __tablename__ = 'post_tb'
    
    post_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_num = db.Column(db.Integer, db.ForeignKey('user_tb.user_num'))
    image = db.Column(db.Text)
    content = db.Column(db.Text)
    location = db.Column(Geography(geometry_type='POINT', srid=4326))
    
    user = db.relationship('Users', back_populates='posts')
    hashtags = db.relationship('Hashtag', secondary='post_hashtag_tb', back_populates='posts')

class Hashtag(db.Model):
    __tablename__ = 'hashtag_tb'
    
    tag_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tag_name = db.Column(db.String(50), nullable=False, unique=True)
    
    posts = db.relationship('Post', secondary='post_hashtag_tb', back_populates='hashtags')

class PostHashtag(db.Model):
    __tablename__ = 'post_hashtag_tb'
    
    post_id = db.Column(db.Integer, db.ForeignKey('post_tb.post_id'), primary_key=True)
    tag_id = db.Column(db.Integer, db.ForeignKey('hashtag_tb.tag_id'), primary_key=True)
