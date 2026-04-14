from flask_mysqldb import MySQL

mysql = MySQL()

def get_db():
    return mysql
