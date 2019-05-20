import os

from flask import Flask, Response, request, render_template, redirect, url_for
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user

from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)


project_dir = os.path.dirname(os.path.abspath(__file__))
database_file = "sqlite:///{}".format(os.path.join(project_dir, "computer_company.db"))
app.config["SQLALCHEMY_DATABASE_URI"] = database_file
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True

db = SQLAlchemy(app)

# config
app.config.update(
    DEBUG=True,
    SECRET_KEY='secret_xxx'
)

# flask-login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


class User(UserMixin, db.Model):

    __tablename__ = 'user'

    user_id = db.Column(
        db.Integer,
        unique=True,
        nullable=False,
        primary_key=True,
        autoincrement=True
    )
    username = db.Column(db.String(25), unique=True, nullable=False)
    password = db.Column(db.String(64), nullable=False)


# some protected url
@app.route('/')
@login_required
def home():
    return Response("Hello World!")


@app.route('/admin/')
def admin_page():
    return render_template('admin.html')


@app.route("/register/", methods=["GET", "POST"])
def register_user():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['pass']
        _user = User.query.filter_by(username=username).first()
        if _user:
            return 'Such user already exists'

        else:
            _user = User(username=username, password=password)
            print _user.username
            db.session.add(_user)
            db.session.commit()

        return redirect(url_for('login'))

    return render_template('register.html')


@app.route("/login/", methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user is not None and user.password == password:
            return render_template('admin.html')

        return 'No such user'

    return render_template('login.html')


# somewhere to logout
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return Response('<p>Logged out</p>')


# handle login failed
@app.errorhandler(401)
def page_not_found(e):
    return Response('<p>Login failed</p>')


# callback to reload the user object
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


if __name__ == '__main__':
    app.run()
