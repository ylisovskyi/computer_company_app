from . import app, db

from flask import Response, request, render_template, redirect, url_for
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from models import *

from sqlalchemy import func
from sqlalchemy.orm import aliased

# config
app.config.update(
    DEBUG=True,
    SECRET_KEY='secret_xxx'
)

# flask-login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@app.route('/')
@login_required
def home():
    if not current_user:
        return redirect(url_for('login'))

    elif current_user.role in ('admin', 'manager'):
        return redirect(url_for('users_page'))

    elif current_user.role in ('client', 'employee'):
        return redirect(url_for('orders_page'))


@app.route('/assign-order/')
@login_required
def assign_order_page():
    order_id = request.args.get('order-id')
    employee_id = request.args.get('employee')
    db.session.query(Order).filter(Order.order_id == order_id).update(
        {Order.employee_id: employee_id},
        synchronize_session=False
    )
    db.session.commit()
    return redirect(url_for('orders_page'))


@app.route('/edit-order/', methods=['GET', 'POST'])
@login_required
def edit_order_page():
    if request.method == 'POST':
        client_id = request.form.get('client')
        employee = request.form['employee']
        parts = request.form['parts']
        price = sum(db.session.query(Part.price).filter(Part.part_id in parts))
        order_id = request.form.get('order_id')
        db.session.query(PartsProvision).filter(PartsProvision.order_id == order_id).delete(synchronize_session=False)
        provision_start_id = db.session.query(func.count(PartsProvision.provision_id)) + 1
        for part_id in parts:
            db.session.add(PartsProvision(
                provision_id=provision_start_id,
                order_id=order_id,
                part_id=part_id
            ))
            provision_start_id += 1
        db.session.query(Order).filter(Order.order_id == order_id).update({
            Order.employee_id: employee,
            client_id: client_id,
            price: price,
        }, synchronize_session=False)
        db.session.commit()
        return redirect(url_for('orders_page'))

    order_id = request.args.get('order-id')
    order_info = db.session.query(Order).filter(Order.order_id == order_id).first()
    orders = db.session.query(Order).all()
    return render_template(
        'edit_order.html',
        role=current_user.role,
        username=current_user.username,
        order=order_info
    )


@app.route('/orders/', methods=['GET', 'POST'])
@login_required
def orders_page():
    if request.method == 'POST':
        client_id = request.form.get('client')
        employee = request.form['employee']
        order_date = request.form['order_date']
        date_id = db.session.query(func.count(OrderDate.date_id)).first()[0] + 1
        date = OrderDate(date_id=date_id, order_date=order_date)
        db.session.add(date)
        args = dict(request.form)
        parts = [int(part) for part in args['parts']]
        price = sum(int(part[0]) for part in db.session.query(Part.price).filter(Part.part_id in parts).all())
        order_id = db.session.query(func.count(Order.order_id)).first()[0] + 2
        order = Order(
            order_id=order_id,
            client_id=client_id,
            status_id=1,
            employee_id=employee,
            price=price,
            date_id=date.date_id
        )
        db.session.add(order)
        provision_start_id = db.session.query(func.count(PartsProvision.provision_id)).first()[0] + 1
        for part_id in parts:
            part_provision = PartsProvision(
                provision_id=provision_start_id,
                order_id=order.order_id,
                part_id=part_id
            )
            db.session.add(part_provision)
            provision_start_id += 1
        db.session.commit()
        return redirect(url_for('orders_page'))

    employees = db.session.query(Employee.employee_id, PersonalInfo.person_name).join(
        PersonalInfo, Employee.personal_info_id == PersonalInfo.personal_info_id
    ).filter(Employee.role_id > 1).all()
    client = aliased(PersonalInfo)
    emp = aliased(PersonalInfo)
    orders = db.session.query(
        Order.order_id, OrderStatu.status_name, client.person_name, emp.person_name, OrderDate.order_date
    ).join(
        OrderStatu, Order.status_id == OrderStatu.status_id
    ).join(
        Client, Order.client_id == Client.client_id
    ).join(
        client, Client.personal_info_id == client.personal_info_id
    ).join(
        Employee, Order.employee_id == Employee.employee_id
    ).join(
        emp, Employee.personal_info_id == emp.personal_info_id
    ).join(
        OrderDate, Order.date_id == OrderDate.date_id
    ).order_by(Order.order_id).all()
    parts = []
    for order in orders:
        parts.append(db.session.query(Part.part_name).join(
            PartsProvision, Part.part_id == PartsProvision.part_id
        ).join(
            Order, order.order_id == PartsProvision.order_id
        ).distinct())

    orders = zip(orders, parts)
    return render_template(
        'orders.html',
        orders=orders,
        current_user=current_user.username,
        username=current_user.username,
        role=current_user.role,
        employees=employees,
        title='Orders',
    )


@app.route('/cancel-order/')
@login_required
def cancel_order():
    order_id = request.args.get('order-id')
    db.session.query(Order).filter(Order.order_id == order_id).update({Order.status_id: 5}, synchronize_session=False)
    db.session.commit()
    return redirect(url_for('users_page'))


@app.route('/add_order/')
@login_required
def add_order_page():
    parts = db.session.query(Part.part_id, Part.part_name).order_by(Part.part_id).all()
    clients = db.session.query(Client.client_id, PersonalInfo.person_name).join(
        PersonalInfo, Client.personal_info_id == PersonalInfo.personal_info_id
    ).all()
    employees = db.session.query(Employee.employee_id, PersonalInfo.person_name).join(
        PersonalInfo, Employee.personal_info_id == PersonalInfo.personal_info_id
    ).filter(Employee.role_id > 1).all()
    return render_template(
        'add_order.html',
        title='Add order',
        role=current_user.role,
        username=current_user.username,
        parts=parts,
        clients=clients,
        employees=employees
    )


@app.route('/users/')
@login_required
def users_page():
    users = User.query
    return render_template(
        'users_table.html',
        users=users,
        role=current_user.role,
        username=current_user.username,
        title='Users'
    )


@app.route('/remove-user/')
@login_required
def remove_user():
    user_id = request.args.get('user-id')
    db.session.query(User).filter(User.user_id == user_id).delete(synchronize_session=False)
    db.session.commit()
    return redirect(url_for('users_page'))


@app.route("/register/", methods=["GET", "POST"])
def register_user():
    if request.method == 'POST':
        name = request.form['name']
        lastname = request.form['lastname']
        email = request.form['email']
        phone = request.form['number']
        username = request.form['username']
        password = request.form['pass']
        rep_pass = request.form['reppass']
        role = request.form['role']
        _user = User.query.filter_by(username=username).first()
        if _user:
            return 'Such user already exists'

        elif password != rep_pass:
            return 'Passwords do not match'

        elif '@' not in email:
            return 'E-mail is not valid'

        else:
            emp_id = None
            pi_l = len(PersonalInfo.query.all()) + 3
            personal_info = PersonalInfo(
                personal_info_id=pi_l,
                person_name=name,
                person_surname=lastname,
                phone_number=phone,
                email=email
            )
            db.session.add(personal_info)
            db.session.commit()
            if role == 'employee':
                role_id = EmployeeRole.query.filter_by(role_name=role).first().role_id
                e_l = len(Employee.query.all()) + 1
                employee = Employee(
                    employee_id=e_l,
                    company_id=1,
                    role_id=role_id,
                    personal_info_id=personal_info.personal_info_id
                )
                emp_id = employee.employee_id
                db.session.add(employee)
                db.session.commit()

            elif role == 'client':
                c_l = len(Client.query.all()) + 1
                client = Client(
                    client_id=c_l,
                    personal_info_id=personal_info.personal_info_id
                )
                db.session.add(client)
                db.session.commit()

            _user = User(
                username=username,
                password=password,
                employee=emp_id,
                role=role
            )
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
            if user.role in ('admin', 'manager'):
                return redirect(url_for('users_page'))

            elif user.role in ('client', 'employee'):
                return redirect(url_for('orders_page'))

        return 'No such user'

    return render_template('login.html')


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.errorhandler(401)
def page_not_found(e):
    return Response('<p>Login failed</p>')


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


if __name__ == '__main__':
    app.run()
