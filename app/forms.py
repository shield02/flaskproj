#!/usr/bin/env python
from flask_wtf import FlaskForm
from flask_wtf.form import _Auto
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Length
from app import db
from app.models import User
import sqlalchemy as sa


class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    about_me = TextAreaField('About Me', validators=[Length(min=0, max=140)])
    submit = SubmitField('Submit')

    def __init__(self, original_username, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = db.session.scalar(sa.select(User).where(
                User.username == self.username.data))
            if user is not None:
                raise ValidationError('Please use a different username.')
