from flask import Flask, make_response, jsonify
from flask_migrate import Migrate
from models import db, User
from flask_restful import Resource, Api, reqparse
from passlib.hash import pbkdf2_sha256
import datetime
import jwt

app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:cinnamonuser@192.168.0.108:5432/postgres"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
migrate = Migrate(app, db)


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


class Login(Resource):
    def post(self):
        args = login_args.parse_args()
        username = args['username']
        password = args['password']
        user = User.query.filter_by(username=username).first()
        if user:
            if user.check_password(password):
                token = jwt.encode({'user': user.username, 'exp': datetime.datetime.utcnow(
                ) + datetime.timedelta(minutes=30)}, "hello")
                return customResponseHelper("Successfully logged in!", 200, {"token": token}), 200
            else:
                return customResponseHelper("Invalid password.", 401), 401
        else:
            return customResponseHelper("No user with the given email.", 404), 404


class Logout(Resource):
    def delete(self):
        return customResponseHelper("Successfully logged out!", 200), 200


class Users(Resource):
    def get(self):
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
            return customResponseHelper("A user with this email is already present.", 409), 409

        user = User(username=username)
        user.set_password(password)
        # Login user
        db.session.add(user)
        db.session.commit()
        return {}, 201


class SingleUser(Resource):
    def get(self, username):
        return {}


api.add_resource(Users, '/users')
api.add_resource(SingleUser, '/users/<int:username>')
api.add_resource(Login, '/login')
api.add_resource(Logout, '/logout')


if __name__ == '__main__':
    app.run(debug=True)
