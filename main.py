from flask import Flask, redirect, render_template, jsonify, session
from flask_login import logout_user, login_required, login_user, current_user, LoginManager
from forms.LoginForm import LoginForm
from forms.Users import RegisterForm
from data.User import User
from data.distance import lonlat_distance
from data import db_session
import requests
from flask_restful import Api
from data.Game import Location

db_session.global_init("db/geo.db")


photo_url = '/static/images/main_1.jpg'


app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)

api = Api(app)
api.add_resource(Location, '/api/location')


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.get(User,user_id)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()

        print(f"DEBUG: Пытаемся войти под {form.email.data}")
        if user:
            check = user.check_password(form.password.data)
            print(f"DEBUG: Пользователь найден. Пароль верный: {check}")
            if check:
                login_user(user, remember=form.remember_me.data)
                return redirect("/")
        else:
            print("DEBUG: Пользователь не найден в базе")

        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(name=form.name.data, email=form.email.data, age=form.age.data)
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/')
def main():
    return render_template('entrance.html', photo_url=photo_url)


@app.context_processor
def inject_user():
    return dict(current_user=current_user)


@app.route('/stats')
@login_required
def stats():
    return render_template('stats.html')


@app.route('/game')
def game():
    return render_template('panorama.html')


@app.route('/hub')
@login_required
def game_wf():
    return render_template('hub.html')


if __name__ == '__main__':
    app.run(debug=True)