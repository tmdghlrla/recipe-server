from flask import request
from flask_jwt_extended import create_access_token
from flask_restful import Resource
from mysql_connection import get_connection
from mysql.connector import Error

from email_validator import validate_email, EmailNotValidError

from utils import hash_password

class UserRegisterResource(Resource) :
    def post(self) :
        # 1.  클라이언트가 보낸 데이터를 받는다.
        data = request.get_json()

        # 2. 이메일 주소형식이 올바른지 확인한다.
        try :
            validate_email(data['email'])
        except EmailNotValidError as e :
            print(e)
            return {"error" : str(e)}, 400
        
        # 3. 비밀번호 길이가 유효한지 체크한다. 비번은 4자리 이상 14자리 이하라고 한다면 체크한다.
        if len(data['password']) < 4 or len(data['password']) > 14 :
            return {'error' : '비밀번호 길이가 올바르지 않습니다.'}, 400
        
        # 4. 비밀번호를 암호화 한다.
        password = hash_password(data['password'])
        print(password)

        # 5. DB의 user 테이블에 저장
        try :
            connection = get_connection()

            query = '''insert into user
                        (username, email, password)
                        values
                        (%s, %s, %s);'''
            
            record = (data['username'], data['email'], password)

            cursor = connection.cursor()
            cursor.execute(query, record)

            connection.commit()

            ### 테이블에 방금 insert 한 데이터의 아이디를 가져오는 방법

            user_id = cursor.lastrowid

            cursor.close()
            connection.close()
            
        except Error as e:
            print(e)
            cursor.close()
            connection.close()

            return {"error" : str(e)}, 500
        
        # 6. user 테이블의 id로 JWT 토큰을 만들어야 한다.
        access_token = create_access_token(user_id)

        # 7. 토큰을 클라이언트에게 준다. response
        return {"result" : "success", "access_token" : access_token}, 200