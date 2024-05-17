#!/usr/bin/env python
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from typing import Optional
from flask_login import UserMixin
from hashlib import md5
from time import time
import jwt
import sqlalchemy as sa
import sqlalchemy.orm as orm
from app import app, db, login

followers = sa.Table(
    'followers',
    db.metadata,
    sa.Column('follower_id', sa.Integer, sa.ForeignKey('user.id'),
              primary_key=True),
    sa.Column('followed_id', sa.Integer, sa.ForeignKey('user.id'),
              primary_key=True)
)

class User(UserMixin, db.Model):
    id: orm.Mapped[int] = orm.mapped_column(primary_key=True)
    username: orm.Mapped[str] = orm.mapped_column(sa.String(64), index=True,
                                                  unique=True)
    email: orm.Mapped[str] = orm.mapped_column(sa.String(120), index=True,
                                               unique=True)
    password_hash: orm.Mapped[Optional[str]] = orm.mapped_column(sa.String(256))
    about_me: orm.Mapped[Optional[str]] = orm.mapped_column(sa.String(140))
    last_seen: orm.Mapped[Optional[datetime]] = orm.mapped_column(
        default=lambda: datetime.now(timezone.utc))
    posts: orm.WriteOnlyMapped['Post'] = orm.relationship(
        back_populates='author')
    following: orm.WriteOnlyMapped['User'] = orm.relationship(
        secondary=followers, primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        back_populates='followers')
    followers: orm.WriteOnlyMapped['User'] = orm.relationship(
        secondary=followers, primaryjoin=(followers.c.followed_id == id),
        secondaryjoin=(followers.c.follower_id == id),
        back_populates='following')

    def __repr__(self) -> str:
        return f'<User {self.username}>'
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return db.session.get(User, id)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return f'https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}'

    def follow(self, user):
        if not self.is_following(user):
            self.following.add(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.following.remove(user)

    def is_following(self, user):
        query = self.following.select().where(User.id == user.id)
        return db.session.scalar(query) is not None

    def followers_count(self):
        query = sa.select(sa.func.count()).select_from(
            self.followers.select().subquery())
        return db.session.scalar(query)

    def following_count(self):
        query = sa.select(sa.func.count()).select_from(
            self.following.select().subquery())
        return db.session.scalar(query)

    def following_posts(self):
        Author = orm.aliased(User)
        Follower = orm.aliased(User)
        return (
            sa.select(Post)
            .join(Post.author.of_type(Author))
            .join(Author.followers.of_type(Follower), isouter=True)
            .where(sa.or_(
                Follower.id == self.id,
                Author.id == self.id))
            .group_by(Post)
            .order_by(Post.timestamp.desc())
        )

class Post(db.Model):
    id: orm.Mapped[int] = orm.mapped_column(primary_key=True)
    body: orm.Mapped[int] = orm.mapped_column(sa.String(140))
    timestamp: orm.Mapped[datetime] = orm.mapped_column(index=True,
                                                        default=lambda:
                                                            datetime.now(
                                                                timezone.utc))
    user_id: orm.Mapped[int] = orm.mapped_column(sa.ForeignKey(User.id),
                                                 index=True)
    author: orm.Mapped[User] = orm.relationship(back_populates='posts')
    language: orm.Mapped[Optional[str]] = orm.mapped_column(sa.String(50))

    def __repr__(self) -> str:
        return f'<Post {self.body}>'

@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))
