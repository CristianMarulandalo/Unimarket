import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="123456",
        database="tienda_flask",
        port=3306,
        auth_plugin='mysql_native_password'
    )