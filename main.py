import os.path as op
from datetime import datetime as dt
from flask import Flask, render_template, url_for, redirect, request
from flask_admin.contrib.sqla import ModelView
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin, form
from flask import session as login_session
from flask_login import LoginManager, login_user, logout_user, login_required
from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required
from flask_bcrypt import Bcrypt
from flask import Flask, url_for
from flask_sqlalchemy import SQLAlchemy
from flask import jsonify

from sqlalchemy.event import listens_for
from markupsafe import Markup

from flask_admin import Admin, form
from flask_admin.form import rules
from flask_admin.contrib import sqla, rediscli
from sqlalchemy.orm import relationship
import os
from flask import Flask, flash, request, redirect, url_for
from sqlalchemy.exc import IntegrityError
import requests
import json
from sqlalchemy.ext.hybrid import hybrid_property
from typing import Union, Type

admin = Admin()
app = Flask(__name__, static_folder='static')

# see http://bootswatch.com/3/ for available swatches
app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
login_manager = LoginManager(app)
bcrypt = Bcrypt(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:\\Users\\Bongeka.Mpofu\\DB Browser for SQLite\\weather.db'

app.config['SECRET_KEY'] = 'this is a secret key '
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
login_manager.init_app(app)
admin.init_app(app)

UPLOAD_FOLDER = 'static'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# sign up at https://api.weatherapi.com and get the api key
API = "06ccb275663d4297982145820241902"
# include air quality index
aqi = "yes"


class Role(db.Model):
    __tablename__ = "role"
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80))
    users = db.relationship("User", back_populates="role", lazy="dynamic")
    def __repr__(self):
        return f'<Role {self.name}>'


class User(db.Model, UserMixin):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    firstname = db.Column(db.String(20), nullable=False)
    lastname = db.Column(db.String(20), nullable=False)
    gender = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    password_hash: str = db.Column(db.String(80), nullable=False)
    agreed_terms = db.Column(db.String(80), nullable=False)
    reg_datetime = db.Column(db.DateTime, default=dt.now)
    path = db.Column(db.String(80))
    role_code = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=False)
    role = db.relationship("Role", back_populates="users")  # 2nd backpopulates method #relationship with role table

    health_assess = db.relationship("Health", back_populates="user", lazy="dynamic")#relationship with health table

    @hybrid_property
    #def password(self) -> str | None:
    def password(self) -> Union[str,None]:
    #def password(self)    Union[str, None]
        return self.password_hash

    # when a new User.password value is set, this function will be called instead
    @password.setter
    def password(self, password: str) -> None:
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def __repr__(self):
        return f'<User {self.username}>'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Health(db.Model):
    __tablename__ = "health"
    hid = db.Column(db.Integer, primary_key=True)
    weight = db.Column(db.Numeric(10, 2), nullable=False)
    height = db.Column(db.Numeric(10, 2), nullable=False)
    bmi = db.Column(db.Numeric(10, 2), )
    calories = db.Column(db.Numeric(10, 2))
    assess_date = db.Column(db.DateTime, default=dt.now)
    userid = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship("User", back_populates="health_assess")  # 2nd backpopulates method

class Weather(db.Model):
    __tablename__ = "weather"
    wid = db.Column(db.Integer, primary_key=True)
    current_temp = db.Column(db.Numeric(10, 2), nullable=False)
    current_pressure = db.Column(db.Numeric(10, 2), nullable=False)
    current_humidity = db.Column(db.Numeric(10, 2), nullable=False)
    current_airindex = db.Column(db.Numeric(10, 2), nullable=False)
    weather_description = db.Column(db.String(80), nullable=False)
    date_taken = db.Column(db.DateTime, default=dt.now)
    cities = relationship("City", back_populates="weather")


def __unicode__(self):
    return f'<Weather {self.wid}>'


class City(db.Model):
    __tablename__ = 'city'
    city_id = db.Column(db.Integer, primary_key=True)
    city_name = db.Column(db.String(20), nullable=False)
    longitude = db.Column(db.Numeric(10, 2), nullable=False)
    latitude = db.Column(db.Numeric(10, 2), nullable=False)
    # adding the foreign key
    wid = db.Column(db.Integer, db.ForeignKey('weather.wid'), nullable=False)
    weather = relationship("Weather", back_populates="cities")  # 2nd backpopulates method

    # def __repr__(self):


def __unicode__(self):  # new line
    return f'<City'
    f'tem {self.city_name}>'

class RoleView(ModelView):
    form_columns = ["name"]
    column_list = ["name"]


class UserView(ModelView):
    form_columns = ["username", "firstname", "lastname", "gender", "password", "email", "agreed_terms", "reg_datetime", "role"]
    column_list = ["username", "firstname", "lastname", "gender", "password", "email", "agreed_terms", "reg_datetime", "role"]



admin.add_view(RoleView(Role, db.session))

admin.add_view(UserView(User, db.session))



@app.route('/')
@app.route('/home')
def option():
    return render_template('home.html')
'''
@app.errorhandler(IntegrityError)
def handle_integrity_error(e):
    db.session.rollback()
    return jsonify({"error": "username or email already exists"}), 400

@app.errorhandler(Exception)
def handle_generic_error(e):
    db.session.rollback()
    return jsonify({"error": str(e)}), 500
'''
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password_hash = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password_hash, password_hash):
            login_session['username'] = username
            print(login_session['username'])
            login_user(user)
            if "username" in login_session:
                return redirect(url_for('welcome'))
        else:
                return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        gender = request.form['gender']
        print(gender)
        email = request.form['email']
        password_hash = request.form['password']
        agreed_terms = request.form.get('terms')
        path = "avator.jpg"
        role_code = 2
        role_code = int(role_code)

        hashed_password = bcrypt.generate_password_hash(
            password_hash).decode('utf-8')
        try:
            new_user = User(username=username, firstname=firstname, lastname=lastname, email=email, gender=gender,
                            password_hash=hashed_password, agreed_terms=agreed_terms, path=path, role_code=role_code)
            db.session.add(new_user)
        except IntegrityError:
            db.session.rollback()

        else:
            db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/welcome')
def welcome():
    if "username" in login_session:
        username = login_session['username']

        return render_template('welcome.html')
    else:
        return redirect(url_for('login'))


@app.route('/forecast', methods=['GET', 'POST'])
def forecast():
    city_name = ""
    region = ""
    country = ""
    localtime = ""
    current_temperature = ""
    current_wind = ""
    current_humidity = ""
    air_quality = ""
    weather_description = ""
    risk = ""
    general = ""

    if request.method == 'POST':
        city_name = request.form.get('city_name')

        url = f"http://api.weatherapi.com/v1/current.json?key={API}&q={city_name}&aqi={aqi}"
        result = requests.get(url)  # Will call the website and fetch information
        # successful response code is 200
        print(result)
        # data is more readable with json module
        wdata = json.loads(result.text)
        print(wdata)

        city_name = wdata["location"]["name"]

        region = wdata["location"]["region"]
        country = wdata["location"]["country"]
        tz_id = wdata["location"]["tz_id"]
        localtime = wdata["location"]["localtime"]

        # Current vars
        current_temperature = wdata["current"]["temp_c"]
        wind_kph = wdata["current"]["wind_kph"]
        current_wind = wdata["current"]["wind_degree"]
        wind_dir = wdata["current"]["wind_dir"]
        precip_mm = wdata["current"]["precip_mm"]
        current_humidity = wdata["current"]["humidity"]
        cloud = wdata["current"]["cloud"]
        uv = wdata["current"]["uv"]
        gust_kph = wdata["current"]["gust_kph"]
        weather_description = wdata["current"]["condition"]["text"]
        air_quality = wdata["current"]["air_quality"]["gb-defra-index"]

        if int(air_quality) >= 10:
            risk = "Index is Very High, At-risk individuals*, Adults and children with lung problems, adults with heart problems, and older people, should avoid strenuous physical activity. People with asthma may find they need to use their reliever inhaler more often"
            general = "Index is Very High, General population, Reduce physical exertion, particularly outdoors, especially if you experience symptoms such as cough or sore throat"
        elif int(air_quality) >= 7:
            risk = "Index is High, At-risk individuals*, Adults and children with lung problems, and adults with heart problems, should reduce strenuous physical exertion, particularly outdoors, and particularly if they experience symptoms. People with asthma may find they need to use their reliever inhaler more often. Older people should also reduce physical exertion"
            general = "Index is High, General population, Anyone experiencing discomfort such as sore eyes, cough or sore throat should consider reducing activity, particularly outdoors"
        elif air_quality >= 4:
            risk = "Index is Moderate, At-risk individuals*, Adults and children with lung problems, and adults with heart problems, who experience symptoms, should consider reducing strenuous physical activity, particularly outdoors"
            general = "Index is Moderate, General population, Enjoy your usual outdoor activities"
        elif air_quality <= 3:
            risk = "Index is Low, At-risk individuals*, Enjoy your usual outdoor activities"
            general = "Index is Low, General population, Enjoy your usual outdoor activities"

    return render_template("forecast.html", city_name=city_name, region=region, country=country, localtime=localtime,
                           current_temperature=current_temperature, current_wind=current_wind,
                           current_humidity=current_humidity, air_quality=air_quality,
                           weather_description=weather_description, risk=risk, general=general)


@app.route('/bmi', methods=['get', 'post'])
#@app.route('/bmi')
def bmi():
    if "username" in login_session:
        print(login_session['username'])
        name = login_session['username']
        user = User.query.filter_by(username=name).first()
        email = user.email
        userid = user.id
        if request.method == 'POST':
            height = float(request.form['height'])
            weight = float(request.form['weight'])
            #bmi = float(request.form.get('bmi'))
            bmi = float(weight/(height*height))
            calories = float(request.form['calories'])
            print("user is is", userid)
            new_health = Health(height=height, weight=weight, bmi=bmi, calories=calories, userid=userid)
            db.session.add(new_health)
            db.session.commit()
    return render_template("bmi.html")


@app.route('/update', methods=['GET', 'POST'])
def update():
    if request.method == 'POST':
        try:
            username = request.form['username']
            user = User.query.filter_by(username=username).first()
            user.lastname = request.form['lastname']
            user.email = request.form['email']
            password = request.form['password']
            hashed_password = bcrypt.generate_password_hash(
                password).decode('utf-8')
            user.password = hashed_password
        except IntegrityError:
            db.session.rollback()
            raise ValidationError('That email is taken. Please choose a different one.')
        else:
            db.session.commit()
    return render_template("update.html")


@app.route('/terms/')
def terms():
    return render_template('terms.html')

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if "username" in login_session:
        print(login_session['username'])
        name = login_session['username']
        user = User.query.filter_by(username=name).first()
        email = user.email
        if request.method == 'POST':
            if 'file1' not in request.files:
                return 'there is no file1 in form!'
            file1 = request.files['file1']
            path1 = os.path.join(app.config['UPLOAD_FOLDER'], file1.filename)
            file1.save(path1)
            user.path = path1
            db.session.commit()
    return render_template('profile.html', name = name, email=email)


@app.route('/gdpr/')
def gdpr():
    return render_template('gdpr.html')


@app.route('/cookies/')
def cookies():
    return render_template('cookies.html')


@app.route('/js/')
def js():
    return render_template('js.html')


@app.route('/rating/')
def rating():
    return render_template('rating.html')


@app.route('/privacy/')
def privacy():
    return render_template('privacy.html')


@app.route('/logout')
def logout():
    del login_session['username']
    logout_user()
    return redirect(url_for('login'))


if __name__ == "__main__":
    app_dir = op.realpath(os.path.dirname(__file__))
    with app.app_context():
        db.create_all()
    app.run(debug=True)