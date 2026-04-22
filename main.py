import random
from flask import Flask, redirect, render_template, jsonify
from flask_login import logout_user, login_required, login_user, current_user, LoginManager
from forms.LoginForm import LoginForm
from forms.Users import RegisterForm
from data.User import User
from data.distance import lonlat_distance
from data import db_session
import requests

db_session.global_init("db/geo.db")


app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)
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


photo_url = '/static/images/main_1.jpg'

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

@app.route('/api/get_location')
def get_location():
    cities = [
        {'name': 'Yerevan', 'lat': 40.1772, 'lng': 44.5035},
        {'name': 'Gyumri', 'lat': 40.7858, 'lng': 43.8417},
        {'name': 'Vanadzor', 'lat': 40.8077, 'lng': 44.4948},
        {'name': 'Almaty', 'lat': 43.2389, 'lng': 76.8897},
        {'name': 'Astana', 'lat': 51.1605, 'lng': 71.4277},
        {'name': 'Shymkent', 'lat': 42.3417, 'lng': 69.5901},
        {'name': 'Aktau', 'lat': 43.6480, 'lng': 51.1722},
        {'name': 'Karaganda', 'lat': 49.8019, 'lng': 73.1021},
        {'name': 'Tashkent', 'lat': 41.2995, 'lng': 69.2401},
        {'name': 'Samarkand', 'lat': 39.6270, 'lng': 66.9750},
        {'name': 'Bukhara', 'lat': 39.7680, 'lng': 64.4556},
        {'name': 'Namangan', 'lat': 40.9983, 'lng': 71.6726},
        {'name': 'Istanbul', 'lat': 41.0082, 'lng': 28.9784},
        {'name': 'Ankara', 'lat': 39.9334, 'lng': 32.8597},
        {'name': 'Antalya', 'lat': 36.8841, 'lng': 30.7056},
        {'name': 'Izmir', 'lat': 38.4192, 'lng': 27.1287},
        {'name': 'Trabzon', 'lat': 41.0027, 'lng': 39.7168},
        {'name': 'Moscow', 'lat': 55.7558, 'lng': 37.6173},
        {'name': 'Saint_P', 'lat': 59.9311, 'lng': 30.3609},
        {'name': 'Ekaterinburg', 'lat': 56.8389, 'lng': 60.6057},
        {'name': 'Novosibirsk', 'lat': 55.0084, 'lng': 82.9357},
        {'name': 'Krasnodar', 'lat': 45.0355, 'lng': 38.9747},
        {'name': 'Kazan', 'lat': 55.7887, 'lng': 49.1221},
        {'name': 'Vladivostok', 'lat': 43.1155, 'lng': 131.8855},
        {'name': 'Nizhny_Nov', 'lat': 56.3269, 'lng': 44.0059},
        {'name': 'Kaliningrad', 'lat': 54.7104, 'lng': 20.4522}]
    city = random.choice(cities)
    city['lat'] += random.uniform(-0.3, 0.3)
    city['lng'] += random.uniform(-0.3, 0.3)
    return jsonify({
        'lat': city['lat'],
        'lng': city['lng'],
    })

if __name__ == '__main__':
    app.run(debug=True)