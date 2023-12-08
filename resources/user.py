import datetime
from flask import request
from flask_jwt_extended import create_access_token, get_jwt, get_jwt_identity, jwt_required
from flask_restful import Resource
from mysql_connection import get_connection
from mysql.connector import Error

from email_validator import validate_email, EmailNotValidError

from utils import check_password, hash_password

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
class UserLoginResource(Resource) :
    def post(self) :
        # 1. 클라이언트로부터 데이터 받아온다.
        data = request.get_json()

        # 2. 유저 테이블에서, 이 이메일주소로 데이터를 가져온다.

        try :
            connection = get_connection()
            query = '''select *
                    from user
                    where email= %s;'''
            record = (data['email'],)

            cursor = connection.cursor(dictionary=True)
            cursor.execute(query,record)
            result_list = cursor.fetchall()                 # 리스트 형태로 가져옴

            print([result_list])

            cursor.close()
            connection.close()

        except Error as e:
            print(e)
            cursor.close()
            connection.close()

            return {"error" : str(e)}, 500
        
        # 회원강입을 안한경우, 리스트에 데이터가 없다.
        if len(result_list) == 0 :
            return {"error" : "가입 정보가 없습니다."}, 400
        
        # 회원은 맞으니 비밀번호가 맞는지 체크한다.
        # 로그인한 사람이 막 입력한 비번 : data['password']
        # 회원가입할 때 입력했던, 암호화된 비번 :  DB에 있다.
        # result_list 에 들어있고 이 리스트의 첫번째 데이터에 들어있다.

        check = check_password(data['password'], result_list[0]['password'])
        if check == False :
            return {"error" : "비밀번호가 맞지 않습니다."}, 406
        
        # JWT 토큰을 만들어서 클라이언트에게 응답한다.
        access_token = create_access_token(result_list[0]['id'],expires_delta=datetime.timedelta(minutes= 200))            # 파라미터로 유저아이디를 받음

        return {"result" : "success", "access_token" : access_token}, 200
jwt_blocklist = set()
class UserLogoutResource(Resource) :
    @jwt_required()
    def delete(self) :
        jti = get_jwt()['jti']          # 토큰안에 있는 jti 정보
        print()
        print(jti)
        print()
        jwt_blocklist.add(jti)

        return {"result" : "success"}, 200