import os

from flask import Flask, Response, request, render_template, redirect, url_for
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user

from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)


project_dir = os.path.dirname(os.path.abspath(__file__))
database_file = "sqlite:///{}".format(os.path.join(project_dir, "computer_company.db"))
app.config["SQLALCHEMY_DATABASE_URI"] = database_file
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.config['user'] = None

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
    role = db.Column(db.String(10), nullable=False)

    def get_id(self):
        return self.user_id


class Orders(db.Model):

    __tablename__ = 'Orders'

    order_id = db.Column(
        db.Integer,
        unique=True,
        nullable=False,
        primary_key=True,
        autoincrement=True
    )
    client = db.Column(db.String(25), unique=True, nullable=False)
    part = db.Column(db.String(64), nullable=False)
    status = db.Column(db.String(10), nullable=False)


@app.route('/')
@login_required
def home():
    if not app.config['user']:
        return redirect(url_for('login'))

    return Response("Hello World!")


@app.route('/admin/')
@login_required
def admin_page():
    return render_template('admin_main.html')


@app.route('/orders/')
@login_required
def orders_page():
    orders = Orders.query
    client = app.config['user'].username
    return render_template('orders.html', orders=orders, current_user=client)


@app.route("/register/", methods=["GET", "POST"])
def register_user():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['pass']
        role = request.form['role']
        _user = User.query.filter_by(username=username).first()
        if _user:
            return 'Such user already exists'

        else:
            _user = User(username=username, password=password, role=role)
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
            login_user(user)
            app.config['user'] = user
            if user.role == 'admin':
                return render_template('admin_main.html')

            elif user.role == 'client':
                return render_template('client_main.html')

        return 'No such user'

    return render_template('login.html')


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return Response('<p>Logged out</p>')


@app.errorhandler(401)
def page_not_found(e):
    return Response('<p>Login failed</p>')


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


if __name__ == '__main__':
    app.run()
