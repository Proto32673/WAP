from flask_wtf import FlaskForm
from sqlalchemy import Integer
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, EmailField
from wtforms.fields.numeric import IntegerField
from wtforms.validators import DataRequired
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import SubmitField


class RegisterForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Пароль еще раз', validators=[DataRequired()])
    name = StringField('Ник', validators=[DataRequired()])
    age = IntegerField('Возраст', validators=[DataRequired()])
    submit = SubmitField('Submit')

class AvatarForm(FlaskForm):
    avatar = FileField('Выберите фото (JPG или PNG)', validators=[
        FileAllowed(['jpg', 'png', 'jpeg'], 'Только изображения!')
    ])
    submit = SubmitField('Сохранить')