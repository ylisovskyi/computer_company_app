class Config:
    SQLALCHEMY_DATABASE_URI = 'mssql+pyodbc://localhost:1433/Computer_company?driver=ODBC+Driver+13+for+SQL+Server?trusted_connection=yes'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SECRET_KEY = 'you-will-never-guess'


