from flask import Flask, Response, redirect, url_for, request, session, abort, render_template
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user

app = Flask(__name__)


mock_data = [
    {'name': 'Yurii', 'surname': 'Lisovskyi', 'phone_number': '+380964096774'},
    {'name': 'Iryna', 'surname': 'Kutna', 'phone_number': '+380964096774'},
    {'name': 'Danylo', 'surname': 'Skliarov', 'phone_number': '+380964096774'},
    {'name': 'Mayya', 'surname': 'Vu', 'phone_number': '+380964096774'},
    {'name': 'Ihor', 'surname': 'Pankiv', 'phone_number': '+380964096774'},
    {'name': 'Bohdan', 'surname': 'Kaminskyi', 'phone_number': '+380964096774'}
]

# config
app.config.update(
    DEBUG=True,
    SECRET_KEY='secret_xxx'
)

# flask-login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


# silly user model
class User(UserMixin):

    def __init__(self, id, username=None, password=None, email=None):
        self.id = id
        self.name = "user" + str(id) if username is None else username
        self.password = self.name + "_secret" if password is None else password
        self.email = email

    def __repr__(self):
        return "%d/%s/%s" % (self.id, self.name, self.password)


# create some users with ids 1 to 20
users = [User(id) for id in range(1, 21)]


# some protected url
@app.route('/')
@login_required
def home():
    return Response("Hello World!")


@app.route("/register_user/", methods=["POST"])
def register_user():
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    id = username[::2]
    user = User(id, username, password, email)
    login_user(user)
    return redirect(request.args.get("next"))


@app.route("/login", methods=["GET"])
def login():
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
def load_user(userid):
    return User(userid)


@app.route('/register/', methods=['GET', 'POST'])
def welcome_page():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        id = username[::2]
        user = User(id, username, password, email)
        login_user(user)
        return redirect(request.args.get("next"))
    else:
        return render_template('register.html')


if __name__ == '__main__':
    app.run()
