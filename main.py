from flask import Flask, redirect, render_template, jsonify, request
from flask_login import logout_user, login_required, login_user, current_user, LoginManager
from forms.LoginForm import LoginForm
from forms.Users import RegisterForm
from data.User import User
from data import db_session
from flask_restful import Api
from data.Game import Location
from data.Score import Score
import math
import random

db_session.global_init("db/geo.db")

photo_url = '/static/images/main_1.jpg'

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)

api = Api(app)
api.add_resource(Location, '/api/location')

def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))
    return R * c


def calculate_score(distance_km):
    if distance_km <= 0:
        return 10000
    alpha = 3100
    score = 10000 * math.exp(distance_km / alpha)
    return min(10000, round(score))



def update_user_score(user_id, new_score):
    db_sess = db_session.create_session()
    score_record = db_sess.query(Score).filter(Score.user_id == user_id).first()

    if score_record:
        if new_score > score_record.max_score:
            score_record.max_score = new_score
            db_sess.commit()
            return True
    else:
        # Создаем новую запись
        new_score_record = Score(user_id=user_id, max_score=new_score)
        db_sess.add(new_score_record)
        db_sess.commit()
        return True
    return False


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.get(User, user_id)


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

        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html', message="Неправильный логин или пароль", form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация', form=form, message="Пароли не совпадают")

        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация', form=form,
                                   message="Такой пользователь уже есть")

        user = User(name=form.name.data, email=form.email.data, age=form.age.data)
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()

        new_score = Score(user_id=user.id, max_score=0)
        db_sess.add(new_score)
        db_sess.commit()

        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/')
def main():
    return render_template('entrance.html', photo_url=photo_url)


@app.context_processor
def inject_user():
    return dict(current_user=current_user)


from data.Score import Score


@app.route('/stats')
@login_required
def stats():
    db_sess = db_session.create_session()
    # Получаем максимальный счет из таблицы score
    score_record = db_sess.query(Score).filter(Score.user_id == current_user.id).first()
    max_score = score_record.max_score if score_record else 0
    db_sess.close()

    print(f"DEBUG: user_id={current_user.id}, max_score={max_score}")  # Отладка

    return render_template('stats.html', max_score=max_score)


@app.route('/game')
def game():
    return render_template('panorama.html')


@app.route('/map')
def map_ans():
    return render_template('map.html')


@app.route('/ans')
def ans():
    user_lat = request.args.get('userLat', type=float)
    user_lng = request.args.get('userLng', type=float)
    correct_lat = request.args.get('correctLat', type=float)
    correct_lng = request.args.get('correctLng', type=float)
    location_name = request.args.get('name', 'Неизвестное место')
    round_id = request.args.get('roundId', type=int)

    print(f"DEBUG: userLat={user_lat}, userLng={user_lng}")
    print(f"DEBUG: correctLat={correct_lat}, correctLng={correct_lng}")

    distance = calculate_distance(user_lat, user_lng, correct_lat, correct_lng)
    score = calculate_score(distance)

    print(f"DEBUG: distance={distance}, score={score}")

    if current_user.is_authenticated:
        update_user_score(current_user.id, score)

    return render_template('answer.html',
                           user_lat=user_lat,
                           user_lng=user_lng,
                           correct_lat=correct_lat,
                           correct_lng=correct_lng,
                           #distance=distance,
                           #score=score,
                           location_name=location_name)


if __name__ == '__main__':
    app.run(debug=True)