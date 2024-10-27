from flask_restx import Namespace, Resource
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models import db, User
import logging

logger = logging.getLogger(__name__)

auth_namespace = Namespace('auth', description='Authentication operations')

user_model = auth_namespace.model('User', {
    'email': fields.String(required=True, description='User email'),
    'password': fields.String(required=True, description='User password'),
})

password_model = auth_namespace.model('PasswordModify', {
    'old_password': fields.String(required=True, description='Old password'),
    'new_password': fields.String(required=True, description='New password'),
})

reset_request_model = auth_namespace.model('PasswordResetRequest', {
    'email': fields.String(required=True, description='User email'),
})

reset_model = auth_namespace.model('PasswordReset', {
    'email': fields.String(required=True, description='User email'),
    'new_password': fields.String(required=True, description='New password'),
})

@auth_namespace.route('/register')
class UserRegister(Resource):
    @auth_namespace.expect(user_model)
    def post(self):
        data = auth_namespace.payload
        email = data.get('email')
        password = data.get('password')

        if User.query.filter_by(email=email).first():
            logger.warning(f"Registration attempt with existing email: {email}")
            return {'message': 'User already exists'}, 400

        new_user = User(email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        logger.info(f"New user registered: {email}")
        return {'message': 'User registered successfully'}, 201

@auth_namespace.route('/login')
class UserLogin(Resource):
    @auth_namespace.expect(user_model)
    def post(self):
        data = auth_namespace.payload
        email = data.get('email')
        password = data.get('password')

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            access_token = create_access_token(identity=user.email)
            logger.info(f"User logged in: {email}")
            return {'message': 'Login successful', 'access_token': access_token}, 200
        else:
            logger.warning(f"Failed login attempt for email: {email}")
            return {'message': 'Invalid credentials'}, 401

@auth_namespace.route('/modify-password')
class PasswordModify(Resource):
    @jwt_required()
    @auth_namespace.expect(password_model)
    def put(self):
        current_user_email = get_jwt_identity()
        user = User.query.filter_by(email=current_user_email).first()
        data = auth_namespace.payload
        old_password = data.get('old_password')
        new_password = data.get('new_password')

        if user and user.check_password(old_password):
            user.set_password(new_password)
            db.session.commit()
            logger.info(f"Password updated for user: {current_user_email}")
            return {'message': 'Password updated successfully'}, 200
        else:
            logger.warning(f"Invalid old password for user: {current_user_email}")
            return {'message': 'Invalid old password'}, 400

@auth_namespace.route('/reset-password-request')
class PasswordResetRequest(Resource):
    @auth_namespace.expect(reset_request_model)
    def post(self):
        data = auth_namespace.payload
        email = data.get('email')

        user = User.query.filter_by(email=email).first()
        if user:
            # TODO: Implement sending a password reset email or token
            logger.info(f"Password reset requested for email: {email}")
            return {'message': 'Password reset instructions sent to your email'}, 200
        else:
            logger.warning(f"Password reset requested for non-existent email: {email}")
            return {'message': 'Email not found'}, 404

@auth_namespace.route('/reset-password')
class PasswordReset(Resource):
    @auth_namespace.expect(reset_model)
    def post(self):
        data = auth_namespace.payload
        email = data.get('email')
        new_password = data.get('new_password')

        user = User.query.filter_by(email=email).first()
        if user:
            user.set_password(new_password)
            db.session.commit()
            logger.info(f"Password reset for user: {email}")
            return {'message': 'Password has been reset successfully'}, 200
        else:
            logger.warning(f"Password reset failed for non-existent email: {email}")
            return {'message': 'Invalid email'}, 400
