from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, validators, BooleanField
from wtforms.fields import SelectField
from wtforms.validators import  Length, Email, InputRequired


class RegisterForm(FlaskForm):
    username  = StringField   (u'username' , validators=[validators.Length(min=4, max=25, message='Field must be between 4 and 25 characters long.')])
    email     = StringField   (u'email'    , validators=[Email(message='Invalid email address.')])
    firstname = StringField   (u'firstname', validators=[validators.Length(min=2, message='Field must be at least 2 character long.')])
    lastname  = StringField   (u'lastname' , validators=[validators.Length(min=2, message='Field must be at least 2 character long.')])
    password  = PasswordField (u'password' , validators=[Length(min=4, message='Field must be at least 4 character long.'), validators.EqualTo('confirm', message='Passwords must match')])
    confirm   = PasswordField (u'Repeat Password')
    #role = SelectField   (u'role', choices=[(member.value, name) for name, member in UserRole.__members__.items()], validators=[InputRequired()])
    #role = SelectField   (u'role', choices=[(1,"Guest"),(2,"User"), (3,"Admin")]) 
    role      = SelectField   (u'role'     , validate_choice=False)
    submit    = SubmitField   (u'Submit')


class LoginForm(FlaskForm):
	username  = StringField   (u'login' , validators=[validators.Length(min=4, max=25, message='Field must be between 4 and 25 characters long.')])
	password  = PasswordField (u'pwd' , validators=[Length(min=4, message='Field must be at least 4 character long.')])
	remember  = BooleanField  (u'remember me')
	submit    = SubmitField   (u'Submit')
