from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import ValidationError, DataRequired, EqualTo, Email, Length
from app.models import User

class LoginForm(FlaskForm):
    username        = StringField('Username', validators=[DataRequired()])
    password        = PasswordField('Password', validators =[DataRequired()])
    remember_me     = BooleanField('Remember Me')
    submit          = SubmitField('Sign In')

class RegisterForm(FlaskForm):
    username        = StringField('Username', validators=[DataRequired(), Length(min=3, max=10)])
    email           = StringField('Email', validators=[DataRequired(), Email()])
    about_me        = TextAreaField('About Me', validators=[Length(min=0, max=256)])
    password        = PasswordField('Password', validators=[DataRequired(), EqualTo('confirm', message="Passwords don't match")])
    confirm         = PasswordField('Confirm Password')
    submit          = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please, use another username')

    def validate_email(self, email):
        email = User.query.filter_by(email=email.data).first()
        if email is not None:
            raise ValidationError('Please, use another email')

class EditProfileForm(FlaskForm):
    username        = StringField('Username', validators=[DataRequired(), Length(min=3, max=10)])
    about_me        = TextAreaField('About Me', validators=[Length(min=0, max=256)])
    submit          = SubmitField('Save')

class PostForm(FlaskForm):
    post = TextAreaField('Say Something', validators=[DataRequired(), Length(min=1, max=140)])
    submit = SubmitField('Submit')