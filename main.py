from flask import Flask, render_template, redirect, url_for

app = Flask(__name__)


@app.route('/')
def main_page():
    return redirect(url_for(welcome_page))


@app.route('/welcome')
def welcome_page():
    return render_template('form.html')


if __name__ == '__main__':
    app.run()
