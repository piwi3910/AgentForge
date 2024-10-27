from flask import Flask, request
from flask_restx import Api, Resource, fields
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from models import db, User, APIKey, EnabledModel

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///agentforge.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'your-secret-key'  # Replace with a strong secret key

db.init_app(app)
jwt = JWTManager(app)

api = Api(app, title='AgentForge API', description='APIs for AgentForge application')

# Namespaces
user_ns = api.namespace('users', description='User operations')
models_ns = api.namespace('models', description='Model management')

# User models for Swagger documentation
user_model = user_ns.model('User', {
    'email': fields.String(required=True, description='User email'),
    'password': fields.String(required=True, description='User password'),
})

password_model = user_ns.model('PasswordModify', {
    'old_password': fields.String(required=True, description='Old password'),
    'new_password': fields.String(required=True, description='New password'),
})

reset_request_model = user_ns.model('PasswordResetRequest', {
    'email': fields.String(required=True, description='User email'),
})

reset_model = user_ns.model('PasswordReset', {
    'email': fields.String(required=True, description='User email'),
    'new_password': fields.String(required=True, description='New password'),
})

# APIKey model for Swagger documentation
api_key_model = models_ns.model('APIKey', {
    'provider': fields.String(required=True, description='Provider name'),
    'api_key': fields.String(required=True, description='API key'),
    'endpoint': fields.String(description='Custom API endpoint (optional)'),
})

# EnabledModel model for Swagger documentation
enabled_model_model = models_ns.model('EnabledModel', {
    'provider': fields.String(required=True, description='Provider name'),
    'model_name': fields.String(required=True, description='Model name'),
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

# Function to test API key validity (stub implementations)
def test_api_key(provider, api_key_value, endpoint=None):
    # Implement logic to test the API key with the provider
    # Return True if valid, False otherwise
    # Example for OpenAI:
    if provider.lower() == 'openai':
        import openai
        openai.api_key = api_key_value
        if endpoint:
            openai.api_base = endpoint
        try:
            openai.Engine.list()
            return True
        except Exception:
            return False
    # Similar logic for other providers...
    return False

# Function to retrieve available models (stub implementations)
def get_available_models(provider, api_key_value, endpoint=None):
    # Implement logic to get available models from the provider
    # Return a list of model names
    # Example for OpenAI:
    if provider.lower() == 'openai':
        import openai
        openai.api_key = api_key_value
        if endpoint:
            openai.api_base = endpoint
        try:
            models = openai.Model.list()
            model_names = [model.id for model in models['data']]
            return model_names
        except Exception:
            return None
    # Similar logic for other providers...
    return None

# Models management endpoints
@models_ns.route('/api-keys')
class APIKeyManagement(Resource):
    @jwt_required()
    def get(self):
        """Get all API keys for the current user"""
        current_user_email = get_jwt_identity()
        user = User.query.filter_by(email=current_user_email).first()
        api_keys = APIKey.query.filter_by(user_id=user.id).all()
        result = []
        for key in api_keys:
            result.append({
                'provider': key.provider,
                'endpoint': key.endpoint
            })
        return {'api_keys': result}, 200

    @jwt_required()
    @models_ns.expect(api_key_model)
    def post(self):
        """Add or update an API key for a provider"""
        data = api.payload
        provider = data.get('provider')
        api_key_value = data.get('api_key')
        endpoint = data.get('endpoint')
        current_user_email = get_jwt_identity()
        user = User.query.filter_by(email=current_user_email).first()
        # Test the API key
        is_valid = test_api_key(provider, api_key_value, endpoint)
        if not is_valid:
            return {'message': f'Invalid API key for provider {provider}'}, 400
        # Save or update the API key
        api_key_entry = APIKey.query.filter_by(user_id=user.id, provider=provider).first()
        if api_key_entry:
            api_key_entry.api_key = api_key_value
            api_key_entry.endpoint = endpoint
        else:
            api_key_entry = APIKey(
                provider=provider,
                api_key=api_key_value,
                endpoint=endpoint,
                user_id=user.id
            )
            db.session.add(api_key_entry)
        db.session.commit()
        return {'message': f'API key for provider {provider} saved successfully'}, 201

@models_ns.route('/available-models/<string:provider>')
class AvailableModels(Resource):
    @jwt_required()
    def get(self, provider):
        """Get available models from a provider"""
        current_user_email = get_jwt_identity()
        user = User.query.filter_by(email=current_user_email).first()
        api_key_entry = APIKey.query.filter_by(user_id=user.id, provider=provider).first()
        if not api_key_entry:
            return {'message': f'API key for provider {provider} not found'}, 404
        models = get_available_models(provider, api_key_entry.api_key, api_key_entry.endpoint)
        if models is None:
            return {'message': f'Failed to retrieve models for provider {provider}'}, 400
        return {'models': models}, 200

@models_ns.route('/enabled-models')
class EnabledModels(Resource):
    @jwt_required()
    def get(self):
        """Get enabled models for the current user"""
        current_user_email = get_jwt_identity()
        user = User.query.filter_by(email=current_user_email).first()
        enabled_models = EnabledModel.query.filter_by(user_id=user.id).all()
        result = []
        for model in enabled_models:
            result.append({
                'provider': model.provider,
                'model_name': model.model_name
            })
        return {'enabled_models': result}, 200

    @jwt_required()
    @models_ns.expect(enabled_model_model)
    def post(self):
        """Enable a model for use"""
        data = api.payload
        provider = data.get('provider')
        model_name = data.get('model_name')
        current_user_email = get_jwt_identity()
        user = User.query.filter_by(email=current_user_email).first()
        # Check if model is available
        api_key_entry = APIKey.query.filter_by(user_id=user.id, provider=provider).first()
        if not api_key_entry:
            return {'message': f'API key for provider {provider} not found'}, 404
        available_models = get_available_models(provider, api_key_entry.api_key, api_key_entry.endpoint)
        if not available_models or model_name not in available_models:
            return {'message': f'Model {model_name} not available for provider {provider}'}, 400
        # Enable the model
        enabled_model = EnabledModel.query.filter_by(
            user_id=user.id,
            provider=provider,
            model_name=model_name
        ).first()
        if not enabled_model:
            enabled_model = EnabledModel(
                provider=provider,
                model_name=model_name,
                user_id=user.id
            )
            db.session.add(enabled_model)
            db.session.commit()
        return {'message': f'Model {model_name} enabled for provider {provider}'}, 201

    @jwt_required()
    @models_ns.expect(enabled_model_model)
    def delete(self):
        """Disable a model"""
        data = api.payload
        provider = data.get('provider')
        model_name = data.get('model_name')
        current_user_email = get_jwt_identity()
        user = User.query.filter_by(email=current_user_email).first()
        enabled_model = EnabledModel.query.filter_by(
            user_id=user.id,
            provider=provider,
            model_name=model_name
        ).first()
        if enabled_model:
            db.session.delete(enabled_model)
            db.session.commit()
            return {'message': f'Model {model_name} disabled for provider {provider}'}, 200
        else:
            return {'message': f'Model {model_name} not found in enabled models'}, 404

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
