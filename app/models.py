from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from typing import Optional
from flask_login import UserMixin
from hashlib import md5
import sqlalchemy as sa
import sqlalchemy.orm as orm
from app import db, login

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

    def __repr__(self) -> str:
        return f'<User {self.username}>'
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return f'https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}'


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

    def __repr__(self) -> str:
        return f'<Post {self.body}>'

@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))
