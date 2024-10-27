from flask import Flask, request
from flask_restx import Api, Resource, fields
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from models import db, User

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///agentforge.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'your-secret-key'  # Replace with a strong secret key

db.init_app(app)
jwt = JWTManager(app)

api = Api(app, title='AgentForge API', description='APIs for AgentForge application')

user_ns = api.namespace('users', description='User operations')

# User model for Swagger documentation
user_model = user_ns.model('User', {
    'email': fields.String(required=True, description='User email'),
    'password': fields.String(required=True, description='User password'),
})

# Password modification model
password_model = user_ns.model('PasswordModify', {
    'old_password': fields.String(required=True, description='Old password'),
    'new_password': fields.String(required=True, description='New password'),
})

# Password reset request model
reset_request_model = user_ns.model('PasswordResetRequest', {
    'email': fields.String(required=True, description='User email'),
})

# Password reset model
reset_model = user_ns.model('PasswordReset', {
    'email': fields.String(required=True, description='User email'),
    'new_password': fields.String(required=True, description='New password'),
})

# User registration endpoint
@user_ns.route('/register')
class UserRegister(Resource):
    @user_ns.expect(user_model)
    def post(self):
        data = api.payload
        email = data.get('email')
        password = data.get('password')
        if User.query.filter_by(email=email).first():
            return {'message': 'User already exists'}, 400
        new_user = User(email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        return {'message': 'User registered successfully'}, 201

# User login endpoint
@user_ns.route('/login')
class UserLogin(Resource):
    @user_ns.expect(user_model)
    def post(self):
        data = api.payload
        email = data.get('email')
        password = data.get('password')
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            access_token = create_access_token(identity=user.email)
            return {'message': 'Login successful', 'access_token': access_token}, 200
        else:
            return {'message': 'Invalid credentials'}, 401

# Password modification endpoint
@user_ns.route('/modify-password')
class PasswordModify(Resource):
    @jwt_required()
    @user_ns.expect(password_model)
    def put(self):
        current_user_email = get_jwt_identity()
        user = User.query.filter_by(email=current_user_email).first()
        data = api.payload
        old_password = data.get('old_password')
        new_password = data.get('new_password')
        if user and user.check_password(old_password):
            user.set_password(new_password)
            db.session.commit()
            return {'message': 'Password updated successfully'}, 200
        else:
            return {'message': 'Invalid old password'}, 400

# Password reset request endpoint
@user_ns.route('/reset-password-request')
class PasswordResetRequest(Resource):
    @user_ns.expect(reset_request_model)
    def post(self):
        data = api.payload
        email = data.get('email')
        user = User.query.filter_by(email=email).first()
        if user:
            # Here, implement sending a password reset email or token
            return {'message': 'Password reset instructions sent to your email'}, 200
        else:
            return {'message': 'Email not found'}, 404

# Password reset endpoint
@user_ns.route('/reset-password')
class PasswordReset(Resource):
    @user_ns.expect(reset_model)
    def post(self):
        data = api.payload
        email = data.get('email')
        new_password = data.get('new_password')
        user = User.query.filter_by(email=email).first()
        if user:
            user.set_password(new_password)
            db.session.commit()
            return {'message': 'Password has been reset successfully'}, 200
        else:
            return {'message': 'Invalid email'}, 400

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
