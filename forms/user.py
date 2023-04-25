from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, BooleanField, SubmitField, StringField, TextAreaField, \
    SelectMultipleField, FileField, widgets
from wtforms.validators import DataRequired


class RegisterForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired()])
    nickname = StringField('Nickname', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password_again = PasswordField('Repeat password', validators=[DataRequired()])
    submit = SubmitField('Register')


class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Log in')


class ProjectForm(FlaskForm):
    title = StringField('Project title', validators=[DataRequired()])
    description = TextAreaField('Project description', validators=[DataRequired()])
    location = StringField('Project location (if applicable)')
    image = FileField('Image')
    remove_image = BooleanField('Remove image')
    tags = SelectMultipleField('Tags', coerce=int)
    additional_tags = StringField('Additional tags')
    submit = SubmitField('Submit')


class MultiCheckboxField(SelectMultipleField):
    """
    A multiple-select, except displays a list of checkboxes.

    Iterating the field will produce subfields, allowing custom rendering of
    the enclosed checkbox fields.
    """
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class FilterForm(FlaskForm):
    tags = MultiCheckboxField('Tags', coerce=int)
    search = StringField('Search')
    show_all = BooleanField('Show all')
    submit = SubmitField('Search')
