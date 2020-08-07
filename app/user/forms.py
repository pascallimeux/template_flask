from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, validators, PasswordField, BooleanField
from wtforms.fields import SelectField
from wtforms.validators import DataRequired, Length, Email

class UserEditForm(FlaskForm):
    id        = StringField   (u'id')
    username  = StringField   (u'username' , validators=[validators.Length(min=4, max=25, message='Field must be between 4 and 25 characters long.')])
    email     = StringField   (u'email'    , validators=[Email(message='Not a valid email address.')])
    firstname = StringField   (u'firstname', validators=[validators.Length(min=2, message='Field must be at least 2 character long.')])
    lastname  = StringField   (u'lastname' , validators=[validators.Length(min=2, message='Field must be at least 2 character long.')])
    role      = SelectField   (u'role'     , validate_choice=False)
    active    = BooleanField  (u'active')
    submit    = SubmitField   (u'Submit')
    back      = SubmitField   (u'Back')


class UserForm(FlaskForm):
    username  = StringField   (u'username' , validators=[validators.Length(min=4, max=25, message='Field must be between 4 and 25 characters long.')])
    email     = StringField   (u'email'    , validators=[Email(message='Invalid email address.')])
    firstname = StringField   (u'firstname', validators=[validators.Length(min=2, message='Field must be at least 2 character long.')])
    lastname  = StringField   (u'lastname' , validators=[validators.Length(min=2, message='Field must be at least 2 character long.')])
    password  = PasswordField (u'password' , validators=[Length(min=4, message='Field must be at least 4 character long.')])
    #role = SelectField   (u'role', choices=[(member.value, name) for name, member in UserRole.__members__.items()], validators=[InputRequired()])
    #role = SelectField   (u'role', choices=[(1,"Guest"),(2,"User"), (3,"Admin")]) 
    role      = SelectField   (u'role'     , validate_choice=False)
    submit    = SubmitField   (u'Submit')
    back      = SubmitField   (u'Back')