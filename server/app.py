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


signup_post_args = reqparse.RequestParser()
signup_post_args.add_argument(
    "email", type=str, help="Email is required", required=True)
signup_post_args.add_argument(
    "username", type=str, help="Username is required", required=True)
signup_post_args.add_argument(
    "password", type=str, help="Password is required", required=True)

login_args = reqparse.RequestParser()

login_args.add_argument(
    "email", type=str, help="Email is required", required=True)
login_args.add_argument(
    "password", type=str, help="Password is required", required=True)


class Login(Resource):
    def post(self):
        args = login_args.parse_args()
        email = args['email']
        password = args['password']
        user = User.query.filter_by(email=email).first()
        if user:
            if user.check_password(password):
                token = jwt.encode({'user': user.username, 'exp': datetime.datetime.utcnow(
                ) + datetime.timedelta(minutes=30)}, "hello")
                print(token)
                return jsonify({"token": token})
            else:
                pass
                return make_response("Invalid password", 401)
        else:
            pass
            return make_response("No user with the given email", 404)


class Logout(Resource):
    def get(self):
        return make_response("Successfully logged out!", 200)


class SignUp(Resource):
    def post(self):
        try:
            args = signup_post_args.parse_args()
            email = args['email']
            username = args['username']
            password = args['password']

            if User.query.filter_by(email=email).first():
                return {"message": "A user with this email is already present."}, 409

            user = User(email=email, username=username)
            user.set_password(password)
            # Login user
            db.session.add(user)
            db.session.commit()
            return {}, 201
        except:
            print('error')


api.add_resource(SignUp, '/signup')
api.add_resource(Login, '/login')
api.add_resource(Logout, '/logout')


if __name__ == '__main__':
    app.run(debug=True)
