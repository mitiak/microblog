from datetime import datetime
from hashlib import md5
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import UserMixin
from app import app, db, login
from time import time
import jwt

'''
Note that I am not declaring this table as a model, like I did for the 
users and posts tables. Since this is an auxiliary table that has no data 
other than the foreign keys, I created it without an associated model class.
'''
followers = db.Table('followers', 
            db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
            db.Column('followed_id', db.Integer, db.ForeignKey('user.id')))


class User(UserMixin, db.Model):
    id              = db.Column(db.Integer, primary_key=True)
    username        = db.Column(db.String(64), index=True, unique=True)
    email           = db.Column(db.String(120), index=True, unique=True)
    password_hash   = db.Column(db.String(128))
    about_me        = db.Column(db.String(256))
    last_seen       = db.Column(db.DateTime, default=datetime.utcnow)
    posts           = db.relationship(
        'Post', 
        backref='author', 
        lazy='dynamic')
    followed        = db.relationship(
        # right side entity of the relationship (the left side entity 
        # is the parent class). Since this is a self-referential 
        # relationship, I have to use the same class on both sides.
        'User', 
        # configures the association table that is used for this
        # relationship, which I defined right above this class
        secondary=followers,
        # indicates the condition that links the left side entity (the follower user) 
        # with the association table. The join condition for the left side of the 
        # relationship is the user ID matching the follower_id field of the 
        # association table. The followers.c.follower_id expression references 
        # the follower_id column of the association table.
        primaryjoin=(followers.c.follower_id == id),
        # indicates the condition that links the right side entity (the followed user) 
        # with the association table. This condition is similar to the one for 
        # primaryjoin, with the only difference that now I'm using followed_id, which 
        # is the other foreign key in the association table
        secondaryjoin=(followers.c.followed_id == id),
        # defines how this relationship will be accessed from the right side entity. 
        # From the left side, the relationship is named followed, so from the right 
        # side I am going to use the name followers to represent all the left side 
        # users that are linked to the target user in the right side. The additional 
        # lazy argument indicates the execution mode for this query. A mode of dynamic 
        # sets up the query to not run until specifically requested, which is also 
        # how I set up the posts one-to-many relationship
        backref=db.backref('followers', lazy='dynamic'), 
        # similar to the parameter of the same name in the backref, but this one 
        # applies to the left side query instead of the right side
        lazy='dynamic')    

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        avatar_host = 'https://www.gravatar.com/avatar/'
        avatar_style = 'retro'
        avatar_size = str(size)
        '''
         because the MD5 support in Python works on bytes and not on strings, 
         I encode the string as bytes before passing it on to the hash function
        '''
        avatar_email_md5 = md5(self.email.lower().encode('utf-8')).hexdigest()
        avatar_options = '?d=' + avatar_style + '&s=' + avatar_size
        return avatar_host + avatar_email_md5 + avatar_options

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(followers.c.followed_id==user.id).count() > 0

    def __repr__(self):
        return '<User {}>'.format(self.username)   


    def followed_posts(self):
        '''
        The condition that I used says that the followed_id field of the 
        followers table must be equal to the user_id of the posts table. 
        To perform this merge, the database will take each record from the 
        posts table (the left side of the join) and append any records from 
        the followers table (the right side of the join) that match the condition. 
        If multiple records in followers match the condition, then the post 
        entry will be repeated for each. If for a given post there is no match 
        in followers, then that post record is not part of the join
        '''
        all_followed_posts = Post.query.join(followers, (followers.c.followed_id == Post.user_id))

        '''
        The join operation gave me a list of all the posts that are followed 
        by some user, which is a lot more data that I really want. I'm only 
        interested in a subset of this list, the posts followed by a single user, 
        so I need trim all the entries I don't need, which I can do with a filter() 
        '''
        posts_followed_by_self = all_followed_posts.filter(followers.c.follower_id == self.id)
        
        '''
        create a second query that returns the user's own posts, and then use 
        the "union" operator to combine the two queries into a single one.
        '''
        posts_by_self = Post.query.filter(Post.user_id==self.id) 
        
        '''
        Note how the followed and own queries are combined into one, 
        before the sorting is applied
        '''
        return posts_followed_by_self.union(posts_by_self).order_by(Post.timestamp.desc())


    def get_reset_password_token(self, expires_in=600):
        return jwt.encode({'reset_password': self.id, 'exp': time() + expires_in}, app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))



class Post(db.Model):
    id              = db.Column(db.Integer, primary_key=True)
    body            = db.Column(db.String(140))
    timestamp       = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id         = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post {}>'.format(self.body)


