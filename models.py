# coding: utf-8
from sqlalchemy import Column, Date, ForeignKey, Index, Integer, LargeBinary, Text, Unicode
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mssql.base import MONEY
from flask_sqlalchemy import SQLAlchemy

from flask_login import UserMixin


db = SQLAlchemy()


class Client(db.Model):
    __tablename__ = 'Client'

    client_id = db.Column(db.Integer, primary_key=True, autoincrement=False)
    personal_info_id = db.Column(db.ForeignKey('PersonalInfo.personal_info_id'), nullable=False)

    personal_info = db.relationship('PersonalInfo', primaryjoin='Client.personal_info_id == PersonalInfo.personal_info_id', backref='clients')


class Company(db.Model):
    __tablename__ = 'Company'

    company_id = db.Column(db.Integer, primary_key=True, autoincrement=False)
    company_name = db.Column(db.Unicode(50), nullable=False)
    company_address = db.Column(db.Unicode(50), nullable=False)
    company_number = db.Column(db.Unicode(50), nullable=False)


class OrderDate(db.Model):
    __tablename__ = 'OrderDate'

    date_id = db.Column(db.Integer, primary_key=True, autoincrement=False)
    order_date = db.Column(db.Date, nullable=False)
    delivery_date = db.Column(db.Date)


class Employee(db.Model):
    __tablename__ = 'Employee'

    employee_id = db.Column(db.Integer, primary_key=True, autoincrement=False)
    company_id = db.Column(db.ForeignKey('Company.company_id'), nullable=False)
    role_id = db.Column(db.ForeignKey('EmployeeRole.role_id'), nullable=False)
    personal_info_id = db.Column(db.ForeignKey('PersonalInfo.personal_info_id'), nullable=False)

    company = db.relationship('Company', primaryjoin='Employee.company_id == Company.company_id', backref='employees')
    personal_info = db.relationship('PersonalInfo', primaryjoin='Employee.personal_info_id == PersonalInfo.personal_info_id', backref='employees')
    role = db.relationship('EmployeeRole', primaryjoin='Employee.role_id == EmployeeRole.role_id', backref='employees')


class EmployeeRole(db.Model):
    __tablename__ = 'EmployeeRole'

    role_id = db.Column(db.Integer, primary_key=True, autoincrement=False)
    role_name = db.Column(db.Unicode(25), nullable=False)
    role_description = db.Column(db.Text(2147483647, 'Ukrainian_CI_AS'))


class OrderStatu(db.Model):
    __tablename__ = 'OrderStatus'

    status_id = db.Column(db.Integer, primary_key=True, autoincrement=False)
    status_name = db.Column(db.Unicode(25), nullable=False)


class Order(db.Model):
    __tablename__ = 'Orders'

    order_id = db.Column(db.Integer, primary_key=True, autoincrement=False)
    client_id = db.Column(db.ForeignKey('Client.client_id'), nullable=False)
    status_id = db.Column(db.ForeignKey('OrderStatus.status_id'), nullable=False)
    employee_id = db.Column(db.ForeignKey('Employee.employee_id'), nullable=False)
    price = db.Column(MONEY, nullable=False)
    date_id = db.Column(db.ForeignKey('Date.date_id'))

    client = db.relationship('Client', primaryjoin='Order.client_id == Client.client_id', backref='orders')
    date = db.relationship('Date', primaryjoin='Order.date_id == Date.date_id', backref='orders')
    employee = db.relationship('Employee', primaryjoin='Order.employee_id == Employee.employee_id', backref='orders')
    status = db.relationship('OrderStatu', primaryjoin='Order.status_id == OrderStatu.status_id', backref='orders')


class Part(db.Model):
    __tablename__ = 'Part'

    part_id = db.Column(db.Integer, primary_key=True, autoincrement=False)
    category_id = db.Column(db.ForeignKey('PartCategory.category_id'), nullable=False)
    producer_id = db.Column(db.ForeignKey('PartProducer.producer_id'), nullable=False)
    part_name = db.Column(db.Unicode(40), nullable=False)
    part_description = db.Column(db.Text(2147483647, 'Ukrainian_CI_AS'))
    price = db.Column(MONEY, nullable=True, default=500)

    category = db.relationship('PartCategory', primaryjoin='Part.category_id == PartCategory.category_id', backref='parts')
    producer = db.relationship('PartProducer', primaryjoin='Part.producer_id == PartProducer.producer_id', backref='parts')


class PartCategory(db.Model):
    __tablename__ = 'PartCategory'

    category_id = db.Column(db.Integer, primary_key=True, autoincrement=False)
    category_name = db.Column(db.Unicode(50), nullable=False)
    category_description = db.Column(db.Text(2147483647, 'Ukrainian_CI_AS'))


class PartProducer(db.Model):
    __tablename__ = 'PartProducer'

    producer_id = db.Column(db.Integer, primary_key=True, autoincrement=False)
    producer_name = db.Column(db.Unicode(50), nullable=False)


class PartsProvision(db.Model):
    __tablename__ = 'PartsProvision'

    provision_id = db.Column(db.Integer, primary_key=True, autoincrement=False)
    order_id = db.Column(db.ForeignKey('Orders.order_id'), nullable=False)
    part_id = db.Column(db.ForeignKey('Part.part_id'), nullable=False)

    order = db.relationship('Order', primaryjoin='PartsProvision.order_id == Order.order_id', backref='parts_provisions')
    part = db.relationship('Part', primaryjoin='PartsProvision.part_id == Part.part_id', backref='parts_provisions')


class PersonalInfo(db.Model):
    __tablename__ = 'PersonalInfo'

    personal_info_id = db.Column(db.Integer, primary_key=True, autoincrement=False)
    person_name = db.Column(db.Unicode(25), nullable=False)
    person_surname = db.Column(db.Unicode(30), nullable=False)
    phone_number = db.Column(db.Unicode(20), nullable=False)
    email = db.Column(db.Unicode(30), nullable=False)


class User(UserMixin, db.Model):
    __tablename__ = 'Users'

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.Unicode(25), nullable=False, unique=True)
    password = db.Column(db.Unicode(64), nullable=False)
    employee = db.Column(db.ForeignKey('Employee.employee_id'), nullable=True)
    role = db.Column(db.Unicode(10), nullable=False)

    def get_id(self):
        return self.user_id


class Sysdiagram(db.Model):
    __tablename__ = 'sysdiagrams'
    __table_args__ = (
        db.Index('UK_principal_name', 'principal_id', 'name'),
    )

    name = db.Column(db.Unicode(128), nullable=False)
    principal_id = db.Column(db.Integer, nullable=False)
    diagram_id = db.Column(db.Integer, primary_key=True)
    version = db.Column(db.Integer)
    definition = db.Column(db.LargeBinary)
