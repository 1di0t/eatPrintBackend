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



class Image(db.Model):
    __tablename__ = 'image_tb'
    
    image_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post_tb.post_id'),nullable=False)
    url = db.Column(db.String(255), nullable=False)

    post = db.relationship('Post', back_populates='images')
    

class Post(db.Model):
    __tablename__ = 'post_tb'
    
    post_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_num = db.Column(db.Integer, db.ForeignKey('user_tb.user_num'))
    content = db.Column(db.Text,nullable=True)
    location = db.Column(Geography(geometry_type='POINT', srid=4326),nullable=True)
    

    user = db.relationship('User', back_populates='posts')

class Hashtag(db.Model):
    __tablename__ = 'hashtag_tb'
    
    tag_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tag_name = db.Column(db.String(50), nullable=False, unique=True)
    


posthashtag_table = db.Table('post_hashtag_tb',
    db.Column('post_id', db.ForeignKey('post_tb.post_id'), primary_key=True),
    db.Column('tag_id',  db.ForeignKey('hashtag_tb.tag_id'), primary_key=True)
)
# class PostHashtag(db.Model):
#     __tablename__ = 'post_hashtag_tb'
    
#     post_id = db.Column(db.Integer, db.ForeignKey('post_tb.post_id'), primary_key=True)
#     tag_id = db.Column(db.Integer, db.ForeignKey('hashtag_tb.tag_id'), primary_key=True)

#     post = db.relationship('Post', back_populates='hashtags')
#     hashtag = db.relationship('Hashtag', back_populates='posts')

