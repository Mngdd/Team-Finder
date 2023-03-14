from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, BooleanField, SubmitField, StringField, IntegerField, TextAreaField, \
    SelectMultipleField
from wtforms.validators import DataRequired


class RegisterForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password_again = PasswordField('Repeat password', validators=[DataRequired()])
    nickname = StringField('Nickname', validators=[DataRequired()])
    github_profile = StringField('Github profile', validators=[DataRequired()])
    submit = SubmitField('Register')


class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Log in')


class ProjectForm(FlaskForm):
    title = StringField('Project title', validators=[DataRequired()])
    description = TextAreaField('Project description', validators=[DataRequired()])
    collaborators = IntegerField('Number of collaborators', validators=[DataRequired()])
    tags = SelectMultipleField('Tags')
    submit = SubmitField('Add project')
