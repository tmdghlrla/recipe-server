import mysql.connector

# 파이썬으로 MySQL에 접속할 수 있는 함수.

def get_connection() :
    connection = mysql.connector.connect(
        host = 'yhdb.cxlwxw3zxakh.ap-northeast-2.rds.amazonaws.com',
        database = 'recipe_db',
        user='recipe_db_user',
        password='0611'
    )
    return connection