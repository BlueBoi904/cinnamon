# from flask_restful import Resource, Api
from flask import Flask, render_template, request
from flask_migrate import Migrate
from models import db, UserModel
from flask_restful import Resource, Api, reqparse

app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:cinnamonuser@192.168.0.108:5432/postgres"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
migrate = Migrate(app, db)


login_post_args = reqparse.RequestParser()
login_post_args.add_argument(
    "email", type=str, help="Email is required", required=True)
login_post_args.add_argument(
    "username", type=str, help="Username is required", required=True)
login_post_args.add_argument(
    "password", type=str, help="Password is required", required=True)


class Login(Resource):
    def post(self):
        try:
            args = login_post_args.parse_args()
            email = args['email']
            username = args['username']
            password = args['password']

            if UserModel.query.filter_by(email=email).first():
                # userExists = UserModel.query.filter_by(email=email).first()
                return {"message": "A user with this email is already present."}, 409

            user = UserModel(email=email, username=username)
            user.set_password(password)
            # user.check_password(password)
            db.session.add(user)
            db.session.commit()
            return {}, 201
        except:
            print('error')


api.add_resource(Login, '/login')


if __name__ == '__main__':
    app.run(debug=True)
