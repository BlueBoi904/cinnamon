from flask import Flask, jsonify, request
from flask_migrate import Migrate
from models import db, User, WatchList
from flask_restful import Resource, Api, reqparse
import datetime
import jwt
from functools import wraps
from newsapi import NewsApiClient
from flask_marshmallow import Marshmallow

app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:cinnamonuser@192.168.0.108:5432/postgres"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
migrate = Migrate(app, db)
ma = Marshmallow(app)
secretKey = "hello"


class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        include_fk = True


class WatchListSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = WatchList
        include_fk = True


login_args = reqparse.RequestParser()
login_args.add_argument(
    "username", type=str, help="Username is required", required=True)
login_args.add_argument(
    "password", type=str, help="Password is required", required=True)

watchlist_args = reqparse.RequestParser()
watchlist_args.add_argument(
    "name", type=str, help="Name is required", required=True)
watchlist_args.add_argument('watchlist', action='append')


def customResponseHelper(message, status, data={}):
    return {
        "status": status,
        "message": message,
        "data": data
    }


def formatUsers(users):
    output = []
    for user in users:
        watchlist_output = []
        user_data = {}
        user_data['id'] = user.id
        user_data['username'] = user.username
        user_data['password'] = user.password
        user_data['admin'] = user.admin
        user_watchlist = WatchList.query.filter_by(
            user_id=user.id).all()
        if user_watchlist:
            for item in user_watchlist:
                watchlist_item = {
                    "id": item.id,
                    "watchlist": item.watchlist,
                    "name": item.name,
                    "user_id": item.user_id
                }
                watchlist_output.append(watchlist_item)
            user_data['watchlists'] = watchlist_output
        else:
            user_data['watchlists'] = []
        output.append(user_data)
    return output


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
            return customResponseHelper("No user with the given username.", 404), 404


class Users(Resource):
    method_decorators = {'get': [token_required]}

    def get(self, current_user):

        if not current_user.admin:
            return customResponseHelper("Not authorized to perform this function.", 401), 401

        users = User.query.all()

        output = formatUsers(users)

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

        if not user:
            return customResponseHelper("No user found.", 404), 404

        user_data = formatUsers([user])
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


class News(Resource):
    def get(self):
        newsapi = NewsApiClient(api_key='184539ecf77f415eb92acc1dc904d2b4')

        all_articles = newsapi.get_everything(q='bitcoin',
                                              from_param='2021-05-22',
                                              to='2021-06-20',
                                              language='en',
                                              sort_by='relevancy',
                                              page=2)

        return all_articles


class Watchlist(Resource):
    method_decorators = {'get': [token_required],
                         'post': [token_required], }

    def post(self, current_user):
        args = watchlist_args.parse_args()
        name = args['name']
        watchlist = args['watchlist']
        new_watchlist = WatchList(
            watchlist=watchlist, user_id=current_user.id, name=name)
        current_user.watchlists.append(new_watchlist)
        db.session.add_all([current_user, new_watchlist])
        db.session.commit()
        return customResponseHelper("success", 201), 201


api.add_resource(Users, '/users')
api.add_resource(SingleUser, '/users/<string:username>')
api.add_resource(Login, '/login')
api.add_resource(News, '/news')
api.add_resource(Watchlist, '/watchlist')


if __name__ == '__main__':
    app.run(debug=True)
