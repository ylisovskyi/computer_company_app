from flask import Flask, render_template, redirect, url_for

app = Flask(__name__)


mock_data = [
    {'name': 'Yurii', 'surname': 'Lisovskyi', 'phone_number': '+380964096774'},
    {'name': 'Iryna', 'surname': 'Kutna', 'phone_number': '+380964096774'},
    {'name': 'Danylo', 'surname': 'Skliarov', 'phone_number': '+380964096774'},
    {'name': 'Mayya', 'surname': 'Vu', 'phone_number': '+380964096774'},
    {'name': 'Ihor', 'surname': 'Pankiv', 'phone_number': '+380964096774'},
    {'name': 'Bohdan', 'surname': 'Kaminskyi', 'phone_number': '+380964096774'}
]


@app.route('/')
def main_page():
    return render_template('form.html', context=mock_data)


@app.route('/welcome')
def welcome_page():
    return render_template('form.html', context=mock_data)


if __name__ == '__main__':
    app.run()
