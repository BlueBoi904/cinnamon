from flask import Flask, jsonify, request
from flask_migrate import Migrate
from models import db, User
from flask_restful import Resource, Api, reqparse
import datetime
import jwt
from functools import wraps

app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:cinnamonuser@192.168.0.108:5432/postgres"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
migrate = Migrate(app, db)

secretKey = "hello"

login_args = reqparse.RequestParser()
login_args.add_argument(
    "username", type=str, help="Username is required", required=True)
login_args.add_argument(
    "password", type=str, help="Password is required", required=True)


def customResponseHelper(message, status, data={}):
    return {
        "status": status,
        "message": message,
        "data": data
    }


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        if not token:
            return customResponseHelper("Token is missing", 401), 401

        try:
            data = jwt.decode(token, secretKey, algorithms=["HS256"])
            current_user = User.query.filter_by(
                username=data['username']).first()
        except Exception as e:
            print(e)
            return customResponseHelper("Token is invalid", 401), 401

        return f(current_user, *args, **kwargs)
    return decorated


class Login(Resource):
    def post(self):
        args = login_args.parse_args()
        username = args['username']
        password = args['password']
        user = User.query.filter_by(username=username).first()
        if user:
            if user.check_password(password):
                token = jwt.encode({'username': user.username, 'exp': datetime.datetime.utcnow(
                ) + datetime.timedelta(minutes=30)}, secretKey)
                return customResponseHelper("Successfully logged in!", 200, {"token": token}), 200
            else:
                return customResponseHelper("Invalid password.", 401), 401
        else:
            return customResponseHelper("No user with the given email.", 404), 404


class Users(Resource):
    method_decorators = {'get': [token_required]}

    def get(self, current_user):

        if not current_user.admin:
            return customResponseHelper("Not authorized to perform this function.", 401), 401

        users = User.query.all()

        output = []

        for user in users:
            user_data = {}
            user_data['username'] = user.username
            user_data['password'] = user.password
            user_data['admin'] = user.admin
            output.append(user_data)

        return customResponseHelper("Success", 200, output)

    def post(self):
        args = login_args.parse_args()
        username = args['username']
        password = args['password']

        if User.query.filter_by(username=username).first():
            return customResponseHelper("This username is already taken.", 409), 409

        user = User(username=username)
        user.set_password(password)
        # Login user
        token = jwt.encode({'username': user.username, 'exp': datetime.datetime.utcnow(
        ) + datetime.timedelta(minutes=30)}, secretKey)
        db.session.add(user)
        db.session.commit()
        return customResponseHelper("success", 201, {"token": token}), 201


class SingleUser(Resource):
    method_decorators = {'get': [token_required],
                         'delete': [token_required], }

    def put(self, username):

        user = User.query.filter_by(username=username).first()

        if not user:
            return customResponseHelper("No user found.", 404), 404

        user.admin = True
        db.session.commit()
        return customResponseHelper("User promoted to admin.", 200), 200

    def get(self, current_user, username):
        if not current_user.admin:
            return customResponseHelper("Not authorized to perform this function.", 401), 401

        user = User.query.filter_by(username=username).first()
        print(user)
        if not user:
            return customResponseHelper("No user found.", 404), 404
        user_data = {}
        user_data['username'] = user.username
        user_data['password'] = user.password
        user_data['admin'] = user.admin
        return customResponseHelper("success", 200, user_data)

    def delete(self, current_user,  username):
        if not current_user.admin:
            return customResponseHelper("Not authorized to perform this function.", 401), 401

        user = User.query.filter_by(username=username).first()
        if not user:
            return customResponseHelper("No user found.", 404), 404
        db.session.delete(user)
        db.session.commit()
        return customResponseHelper("User deleted successfully", 200), 200


api.add_resource(Users, '/users')
api.add_resource(SingleUser, '/users/<string:username>')
api.add_resource(Login, '/login')


if __name__ == '__main__':
    app.run(debug=True)
