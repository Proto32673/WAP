from flask_wtf import FlaskForm
from sqlalchemy import Integer
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, EmailField
from wtforms.fields.numeric import IntegerField
from wtforms.validators import DataRequired


class RegisterForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Пароль еще раз', validators=[DataRequired()])
    name = StringField('Ник', validators=[DataRequired()])
    age = IntegerField('Возраст', validators=[DataRequired()])
    submit = SubmitField('Submit')