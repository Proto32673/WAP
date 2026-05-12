from flask_socketio import SocketIO, emit, join_room
import datetime
from flask import Flask, redirect, render_template, jsonify, request
from flask_login import logout_user, login_required, login_user, current_user, LoginManager
from sqlalchemy import true
from forms.LoginForm import LoginForm
from forms.Users import RegisterForm
from data.User import User
from data import db_session
from sqlalchemy import desc
from flask_restful import Api
from data.Game import Location
from data.Score import Score
from data.Room import Room
import math
from data.Score import Score
import os
from forms.Users import AvatarForm

import random
import string

db_session.global_init("db/geo.db")

photo_url = '/static/images/main_1.jpg'

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key1'
socketio = SocketIO(app)

login_manager = LoginManager()
login_manager.init_app(app)

api = Api(app)
api.add_resource(Location, '/api/location')


@app.route('/profile/edit_avatar', methods=['GET', 'POST'])
@login_required
def edit_avatar():
    form = AvatarForm()
    if form.validate_on_submit():
        file = form.avatar.data
        if file:
            ext = file.filename.split('.')[-1]
            filename = f"avatar_{current_user.id}.{ext}"
            path = os.path.join('static/img/avatars', filename)
            os.makedirs('static/img/avatars', exist_ok=True)
            file.save(path)
            db_sess = db_session.create_session()
            user = db_sess.query(User).get(current_user.id)
            user.avatar = filename
            db_sess.commit()
            return redirect('/profile')

    return render_template('avatar.html', title='Смена аватара', form=form)


@app.context_processor
def inject_user():
    db_sess = db_session.create_session()

    # Получаем топ игроков по максимальному счету
    try:
        leaders = db_sess.query(User.name, Score.max_score, Score.user_id, User.avatar) \
            .join(Score, User.id == Score.user_id) \
            .order_by(desc(Score.max_score)).limit(20).all()
    except Exception as e:
        print(f"Ошибка получения лидеров: {e}")
        leaders = []

    db_sess.close()

    return dict(current_user=current_user, leaders=leaders)


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
    score = 10000 * math.exp(-distance_km / alpha)
    return min(10000, max(0, round(score)))

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


@app.route('/profile')
@login_required
def profile():
    db_sess = db_session.create_session()
    score_record = db_sess.query(Score).filter(Score.user_id == current_user.id).first()
    max_score = score_record.max_score if score_record else 0
    db_sess.close()
    return render_template('profile.html', max_score=max_score)


@app.route('/game')
def game():
    return render_template('panorama.html')


@app.route('/game_m')
def game_m():
    code_url = request.args.get('code')
    db_sess = db_session.create_session()
    room = db_sess.query(Room).filter(Room.code == code_url).first()
    r_code = room.code
    is_creator = (room.id_creator == current_user.id)
    db_sess.close()
    return render_template('panorama.html', code=r_code, c_id=is_creator)


@app.route('/hub')
@login_required
def hub():
    code_url = request.args.get('code')
    db_sess = db_session.create_session()
    if code_url:
        room = db_sess.query(Room).filter(Room.code == code_url).first()
        if room:
            r_code = room.code
            is_creator = (room.id_creator == current_user.id)
            db_sess.close()
            return render_template('hub.html', code=r_code, c_id=is_creator)
        db_sess.close()
        return redirect('/')
    a_c = string.ascii_letters + string.digits
    while True:
        c = "".join(random.choices(a_c, k=4))
        if not db_sess.query(Room).filter(Room.code == c).first():
            break
    room = Room()
    room.code = c
    room.id_creator = current_user.id
    room.updated_at = datetime.datetime.now(datetime.timezone.utc)
    db_sess.add(room)
    db_sess.commit()
    db_sess.close()
    return redirect(f'/hub?code={c}')


@app.route('/results')
def results():
    code = request.args.get('code')
    return render_template('results_multiplayer.html', code=code)


@socketio.on('join_to_room')
def join_to_room(data):
    code = data.get('code')
    db_sess = db_session.create_session()
    room = db_sess.query(Room).filter(Room.code == code).first()
    if room:
        emit('join_success', {'code': code})
    else:
        emit('join_error', {'msg': 'Комната не найдена!'})


@socketio.on('game_m')
def game_m(data):
    code = data.get('code')
    db_sess = db_session.create_session()
    room = db_sess.query(Room).filter(Room.code == code).first()
    if room.id_creator == current_user.id:
        emit('game_success', {'code': code}, to=code)
    db_sess.close()


room_l = {}


@socketio.on('player_move')
def player_move(data):
    room = data.get('room')
    if room:
        room_l[room] = data
        emit('update', data, to=room, include_self=False)


@socketio.on('join')
def on_join(data):
    room = data['room']
    join_room(room)
    if room in room_l:
        emit('update', room_l[room], to=request.sid)


@app.route('/map')
def map_ans():
    code = request.args.get('code')
    return render_template('map.html', code=code)


room_ans = {}


@socketio.on('submit_answer')
def answer(data):
    room_code = data.get('room')
    user_id = current_user.id
    if room_code not in room_ans:
        room_ans[room_code] = {}
    try:
        u_lat = float(data.get('lat'))
        u_lng = float(data.get('lng'))
        c_lat = float(data.get('correctLat'))
        c_lng = float(data.get('correctLng'))
    except (TypeError, ValueError):
        return
    dist = calculate_distance(u_lat, u_lng, c_lat, c_lng)
    score = calculate_score(dist)
    if current_user.is_authenticated:
        update_user_score(user_id, score)
    room_ans[room_code][user_id] = {
        'name': current_user.name,
        'score': score,
        'dist': dist,
        'lat': u_lat,
        'lng': u_lng
    }
    emit('player_answered_notice', {'name': current_user.name}, to=room_code, include_self=False)
    if len(room_ans[room_code]) >= 2:
        results_data = {
            'results': room_ans[room_code],
            'correctLat': c_lat,
            'correctLng': c_lng
        }
        emit('all_finished', results_data, to=room_code)
        room_ans[room_code] = {}


@app.route('/ans')
def ans():
    user_lat = request.args.get('userLat', type=float)
    user_lng = request.args.get('userLng', type=float)
    correct_lat = request.args.get('correctLat', type=float)
    correct_lng = request.args.get('correctLng', type=float)
    location_name = request.args.get('name', 'Неизвестное место')

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
                           location_name=location_name)


if __name__ == '__main__':
    socketio.run(app, debug=True, allow_unsafe_werkzeug=true)