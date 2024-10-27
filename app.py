"""
AgentForge Backend Application

This module defines the Flask application, API endpoints, and associated logic
for the AgentForge application. It includes user authentication, model management,
team management, and chat functionalities.
"""

import os
import logging
from datetime import datetime

from flask import Flask, request
from flask_restx import Api, Resource, fields
from flask_jwt_extended import (
    JWTManager, create_access_token, jwt_required, get_jwt_identity
)
from models import db, User, APIKey, EnabledModel, Team, Agent, ChatMessage

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask application
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///agentforge.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Load JWT secret key from environment variable
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'default-secret-key')

# Initialize extensions
db.init_app(app)
jwt = JWTManager(app)

# Initialize API
api = Api(app, title='AgentForge API', description='APIs for AgentForge application')

# Namespaces
user_namespace = api.namespace('users', description='User operations')
models_namespace = api.namespace('models', description='Model management')
teams_namespace = api.namespace('teams', description='Team management')
chat_namespace = api.namespace('chat', description='Chat operations')

# Models for Swagger documentation
user_model = user_namespace.model('User', {
    'email': fields.String(required=True, description='User email'),
    'password': fields.String(required=True, description='User password'),
})

password_model = user_namespace.model('PasswordModify', {
    'old_password': fields.String(required=True, description='Old password'),
    'new_password': fields.String(required=True, description='New password'),
})

reset_request_model = user_namespace.model('PasswordResetRequest', {
    'email': fields.String(required=True, description='User email'),
})

reset_model = user_namespace.model('PasswordReset', {
    'email': fields.String(required=True, description='User email'),
    'new_password': fields.String(required=True, description='New password'),
})

api_key_model = models_namespace.model('APIKey', {
    'provider': fields.String(required=True, description='Provider name'),
    'api_key': fields.String(required=True, description='API key'),
    'endpoint': fields.String(description='Custom API endpoint (optional)'),
})

enabled_model_model = models_namespace.model('EnabledModel', {
    'provider': fields.String(required=True, description='Provider name'),
    'model_name': fields.String(required=True, description='Model name'),
})

team_model = teams_namespace.model('Team', {
    'name': fields.String(required=True, description='Team name'),
    'function': fields.String(description='Team function'),
    'project_manager_model_id': fields.Integer(required=True, description='EnabledModel ID for project manager'),
})

agent_model = teams_namespace.model('Agent', {
    'name': fields.String(required=True, description='Agent name'),
    'role': fields.String(description='Agent role'),
    'model_id': fields.Integer(required=True, description='EnabledModel ID for agent'),
})

chat_message_model = chat_namespace.model('ChatMessage', {
    'message': fields.String(required=True, description='Chat message'),
})

# User Endpoints
@user_namespace.route('/register')
class UserRegister(Resource):
    """User Registration Endpoint."""

    @user_namespace.expect(user_model)
    def post(self):
        """Register a new user."""
        data = api.payload
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

@user_namespace.route('/login')
class UserLogin(Resource):
    """User Login Endpoint."""

    @user_namespace.expect(user_model)
    def post(self):
        """Authenticate and log in a user."""
        data = api.payload
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

@user_namespace.route('/modify-password')
class PasswordModify(Resource):
    """Password Modification Endpoint."""

    @jwt_required()
    @user_namespace.expect(password_model)
    def put(self):
        """Modify the password of the current user."""
        current_user_email = get_jwt_identity()
        user = User.query.filter_by(email=current_user_email).first()
        data = api.payload
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

@user_namespace.route('/reset-password-request')
class PasswordResetRequest(Resource):
    """Password Reset Request Endpoint."""

    @user_namespace.expect(reset_request_model)
    def post(self):
        """Request a password reset."""
        data = api.payload
        email = data.get('email')

        user = User.query.filter_by(email=email).first()
        if user:
            # TODO: Implement sending a password reset email or token
            logger.info(f"Password reset requested for email: {email}")
            return {'message': 'Password reset instructions sent to your email'}, 200
        else:
            logger.warning(f"Password reset requested for non-existent email: {email}")
            return {'message': 'Email not found'}, 404

@user_namespace.route('/reset-password')
class PasswordReset(Resource):
    """Password Reset Endpoint."""

    @user_namespace.expect(reset_model)
    def post(self):
        """Reset the password using a reset token."""
        data = api.payload
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

# Helper Functions
def test_api_key(provider, api_key_value, endpoint=None):
    """
    Test the validity of the provided API key with the given provider.

    Args:
        provider (str): The name of the provider (e.g., 'openai').
        api_key_value (str): The API key to test.
        endpoint (str, optional): Custom API endpoint.

    Returns:
        bool: True if the API key is valid, False otherwise.
    """
    provider = provider.lower()
    if provider == 'openai':
        try:
            import openai
            openai.api_key = api_key_value
            if endpoint:
                openai.api_base = endpoint
            openai.Engine.list()
            logger.info(f"OpenAI API key valid for provider: {provider}")
            return True
        except Exception as exc:
            logger.error(f"OpenAI API key test failed: {exc}")
            return False
    elif provider == 'anthropic':
        # TODO: Implement Anthropic API key testing
        logger.warning("Anthropic API key testing not implemented.")
        return False
    elif provider == 'openrouter':
        # TODO: Implement OpenRouter API key testing
        logger.warning("OpenRouter API key testing not implemented.")
        return False
    elif provider == 'ollama':
        # TODO: Implement Ollama API key testing
        logger.warning("Ollama API key testing not implemented.")
        return False
    else:
        logger.error(f"Provider '{provider}' is not supported.")
        return False

def get_available_models(provider, api_key_value, endpoint=None):
    """
    Retrieve available models from the provider.

    Args:
        provider (str): The name of the provider (e.g., 'openai').
        api_key_value (str): The API key to use.
        endpoint (str, optional): Custom API endpoint.

    Returns:
        list: A list of model names available from the provider.
    """
    provider = provider.lower()
    if provider == 'openai':
        try:
            import openai
            openai.api_key = api_key_value
            if endpoint:
                openai.api_base = endpoint
            models = openai.Model.list()
            model_names = [model.id for model in models['data']]
            logger.info(f"Retrieved models from OpenAI for provider: {provider}")
            return model_names
        except Exception as exc:
            logger.error(f"Failed to retrieve OpenAI models: {exc}")
            return None
    elif provider == 'anthropic':
        # TODO: Implement Anthropic model retrieval
        logger.warning("Anthropic model retrieval not implemented.")
        return []
    elif provider == 'openrouter':
        # TODO: Implement OpenRouter model retrieval
        logger.warning("OpenRouter model retrieval not implemented.")
        return []
    elif provider == 'ollama':
        # TODO: Implement Ollama model retrieval
        logger.warning("Ollama model retrieval not implemented.")
        return []
    else:
        logger.error(f"Provider '{provider}' is not supported.")
        return None

# Models Management Endpoints
@models_namespace.route('/api-keys')
class APIKeyManagement(Resource):
    """API Key Management Endpoint."""

    @jwt_required()
    def get(self):
        """Get all API keys for the current user."""
        current_user_email = get_jwt_identity()
        user = User.query.filter_by(email=current_user_email).first()
        api_keys = APIKey.query.filter_by(user_id=user.id).all()

        result = [{'provider': key.provider, 'endpoint': key.endpoint} for key in api_keys]
        logger.info(f"Retrieved API keys for user: {current_user_email}")
        return {'api_keys': result}, 200

    @jwt_required()
    @models_namespace.expect(api_key_model)
    def post(self):
        """Add or update an API key for a provider."""
        data = api.payload
        provider = data.get('provider')
        api_key_value = data.get('api_key')
        endpoint = data.get('endpoint')
        current_user_email = get_jwt_identity()
        user = User.query.filter_by(email=current_user_email).first()

        # Test the API key
        is_valid = test_api_key(provider, api_key_value, endpoint)
        if not is_valid:
            logger.error(f"Invalid API key for provider '{provider}' by user: {current_user_email}")
            return {'message': f'Invalid API key for provider {provider}'}, 400

        # Save or update the API key
        api_key_entry = APIKey.query.filter_by(user_id=user.id, provider=provider).first()
        if api_key_entry:
            api_key_entry.api_key = api_key_value
            api_key_entry.endpoint = endpoint
            logger.info(f"Updated API key for provider '{provider}' by user: {current_user_email}")
        else:
            api_key_entry = APIKey(
                provider=provider,
                api_key=api_key_value,
                endpoint=endpoint,
                user_id=user.id
            )
            db.session.add(api_key_entry)
            logger.info(f"Added new API key for provider '{provider}' by user: {current_user_email}")

        db.session.commit()
        return {'message': f'API key for provider {provider} saved successfully'}, 201

@models_namespace.route('/available-models/<string:provider>')
class AvailableModels(Resource):
    """Available Models Endpoint."""

    @jwt_required()
    def get(self, provider):
        """Get available models from a provider."""
        current_user_email = get_jwt_identity()
        user = User.query.filter_by(email=current_user_email).first()
        api_key_entry = APIKey.query.filter_by(user_id=user.id, provider=provider).first()

        if not api_key_entry:
            logger.error(f"API key for provider '{provider}' not found for user: {current_user_email}")
            return {'message': f'API key for provider {provider} not found'}, 404

        models = get_available_models(provider, api_key_entry.api_key, api_key_entry.endpoint)
        if models is None:
            logger.error(f"Failed to retrieve models for provider '{provider}' for user: {current_user_email}")
            return {'message': f'Failed to retrieve models for provider {provider}'}, 400

        logger.info(f"Models retrieved for provider '{provider}' by user: {current_user_email}")
        return {'models': models}, 200

@models_namespace.route('/enabled-models')
class EnabledModels(Resource):
    """Enabled Models Endpoint."""

    @jwt_required()
    def get(self):
        """Get enabled models for the current user."""
        current_user_email = get_jwt_identity()
        user = User.query.filter_by(email=current_user_email).first()
        enabled_models = EnabledModel.query.filter_by(user_id=user.id).all()

        result = [{
            'provider': model.provider,
            'model_name': model.model_name,
            'id': model.id
        } for model in enabled_models]

        logger.info(f"Retrieved enabled models for user: {current_user_email}")
        return {'enabled_models': result}, 200

    @jwt_required()
    @models_namespace.expect(enabled_model_model)
    def post(self):
        """Enable a model for use."""
        data = api.payload
        provider = data.get('provider')
        model_name = data.get('model_name')
        current_user_email = get_jwt_identity()
        user = User.query.filter_by(email=current_user_email).first()

        # Check if model is available
        api_key_entry = APIKey.query.filter_by(user_id=user.id, provider=provider).first()
        if not api_key_entry:
            logger.error(f"API key for provider '{provider}' not found for user: {current_user_email}")
            return {'message': f'API key for provider {provider} not found'}, 404

        available_models = get_available_models(provider, api_key_entry.api_key, api_key_entry.endpoint)
        if not available_models or model_name not in available_models:
            logger.error(f"Model '{model_name}' not available for provider '{provider}'")
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
            logger.info(f"Enabled model '{model_name}' for provider '{provider}' by user: {current_user_email}")
        else:
            logger.info(f"Model '{model_name}' already enabled for provider '{provider}' by user: {current_user_email}")

        return {'message': f'Model {model_name} enabled for provider {provider}'}, 201

    @jwt_required()
    @models_namespace.expect(enabled_model_model)
    def delete(self):
        """Disable a model."""
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
            logger.info(f"Disabled model '{model_name}' for provider '{provider}' by user: {current_user_email}")
            return {'message': f'Model {model_name} disabled for provider {provider}'}, 200
        else:
            logger.warning(f"Attempted to disable non-existent model '{model_name}' for provider '{provider}'")
            return {'message': f'Model {model_name} not found in enabled models'}, 404

# Team Management Endpoints
@teams_namespace.route('')
class TeamList(Resource):
    """Team List Endpoint."""

    @jwt_required()
    def get(self):
        """Get all teams for the current user."""
        current_user_email = get_jwt_identity()
        user = User.query.filter_by(email=current_user_email).first()
        teams = Team.query.filter_by(user_id=user.id).all()

        result = [{'id': team.id, 'name': team.name, 'function': team.function} for team in teams]
        logger.info(f"Retrieved teams for user: {current_user_email}")
        return {'teams': result}, 200

    @jwt_required()
    @teams_namespace.expect(team_model)
    def post(self):
        """Create a new team with a project manager."""
        data = api.payload
        name = data.get('name')
        function = data.get('function')
        pm_model_id = data.get('project_manager_model_id')
        current_user_email = get_jwt_identity()
        user = User.query.filter_by(email=current_user_email).first()

        # Check if enabled model exists
        enabled_model = EnabledModel.query.filter_by(id=pm_model_id, user_id=user.id).first()
        if not enabled_model:
            logger.error(f"Enabled model ID '{pm_model_id}' not found for user: {current_user_email}")
            return {'message': 'Enabled model not found'}, 404

        # Create team
        team = Team(name=name, function=function, user_id=user.id)
        db.session.add(team)
        db.session.commit()

        # Create project manager agent
        project_manager = Agent(
            name='Project Manager',
            role='Project Manager',
            enabled_model_id=pm_model_id,
            team_id=team.id,
            is_project_manager=True
        )
        db.session.add(project_manager)
        db.session.commit()

        # Update team with project manager ID
        team.project_manager_id = project_manager.id
        db.session.commit()

        logger.info(f"Team '{name}' created by user: {current_user_email}")
        return {'message': 'Team created successfully', 'team_id': team.id}, 201

@teams_namespace.route('/<int:team_id>/agents')
class AgentList(Resource):
    """Agent List Endpoint."""

    @jwt_required()
    def get(self, team_id):
        """Get all agents for a team."""
        current_user_email = get_jwt_identity()
        user = User.query.filter_by(email=current_user_email).first()
        team = Team.query.filter_by(id=team_id, user_id=user.id).first()

        if not team:
            logger.error(f"Team ID '{team_id}' not found for user: {current_user_email}")
            return {'message': 'Team not found'}, 404

        agents = Agent.query.filter_by(team_id=team.id).all()
        result = [{
            'id': agent.id,
            'name': agent.name,
            'role': agent.role,
            'enabled_model_id': agent.enabled_model_id,
            'is_project_manager': agent.is_project_manager
        } for agent in agents]

        logger.info(f"Retrieved agents for team ID '{team_id}' by user: {current_user_email}")
        return {'agents': result}, 200

    @jwt_required()
    @teams_namespace.expect(agent_model)
    def post(self, team_id):
        """Add an agent to a team."""
        data = api.payload
        name = data.get('name')
        role = data.get('role')
        model_id = data.get('model_id')
        current_user_email = get_jwt_identity()

        user = User.query.filter_by(email=current_user_email).first()
        team = Team.query.filter_by(id=team_id, user_id=user.id).first()
        if not team:
            logger.error(f"Team ID '{team_id}' not found for user: {current_user_email}")
            return {'message': 'Team not found'}, 404

        enabled_model = EnabledModel.query.filter_by(id=model_id, user_id=user.id).first()
        if not enabled_model:
            logger.error(f"Enabled model ID '{model_id}' not found for user: {current_user_email}")
            return {'message': 'Enabled model not found'}, 404

        agent = Agent(
            name=name,
            role=role,
            enabled_model_id=model_id,
            team_id=team.id
        )
        db.session.add(agent)
        db.session.commit()

        logger.info(f"Agent '{name}' added to team ID '{team_id}' by user: {current_user_email}")
        return {'message': 'Agent added successfully', 'agent_id': agent.id}, 201

# Chat Endpoints
@chat_namespace.route('/<int:team_id>/messages')
class ChatMessages(Resource):
    """Chat Messages Endpoint."""

    @jwt_required()
    def get(self, team_id):
        """Get chat history for a team."""
        current_user_email = get_jwt_identity()
        user = User.query.filter_by(email=current_user_email).first()
        team = Team.query.filter_by(id=team_id, user_id=user.id).first()

        if not team:
            logger.error(f"Chat requested for non-existent team ID '{team_id}' by user: {current_user_email}")
            return {'message': 'Team not found'}, 404

        messages = ChatMessage.query.filter_by(team_id=team.id).order_by(ChatMessage.timestamp).all()
        result = [{
            'id': msg.id,
            'sender_type': msg.sender_type,
            'sender_id': msg.sender_id,
            'message': msg.message,
            'timestamp': msg.timestamp.isoformat()
        } for msg in messages]

        logger.info(f"Chat history retrieved for team ID '{team_id}' by user: {current_user_email}")
        return {'messages': result}, 200

    @jwt_required()
    @chat_namespace.expect(chat_message_model)
    def post(self, team_id):
        """Send a message to the project manager."""
        current_user_email = get_jwt_identity()
        user = User.query.filter_by(email=current_user_email).first()
        data = api.payload
        message_content = data.get('message')

        team = Team.query.filter_by(id=team_id, user_id=user.id).first()
        if not team:
            logger.error(f"Message sent to non-existent team ID '{team_id}' by user: {current_user_email}")
            return {'message': 'Team not found'}, 404

        # Save user message
        user_message = ChatMessage(
            sender_type='user',
            sender_id=user.id,
            message=message_content,
            user_id=user.id,
            team_id=team.id
        )
        db.session.add(user_message)
        db.session.commit()

        # Process message with project manager
        response = process_project_manager_message(user, team, message_content)

        # Save project manager response
        pm_agent = Agent.query.filter_by(id=team.project_manager_id).first()
        pm_message = ChatMessage(
            sender_type='project_manager',
            sender_id=pm_agent.id,
            message=response,
            user_id=user.id,
            team_id=team.id,
            agent_id=pm_agent.id
        )
        db.session.add(pm_message)
        db.session.commit()

        logger.info(f"Message sent to project manager for team ID '{team_id}' by user: {current_user_email}")
        return {'message': 'Message sent to project manager', 'response': response}, 200

def process_project_manager_message(user, team, user_message):
    """
    Simulate project manager processing and delegation to agents.

    Args:
        user (User): The user sending the message.
        team (Team): The team the message is directed to.
        user_message (str): The message content from the user.

    Returns:
        str: The response from the project manager after delegating tasks.
    """
    # Simulate delegation to agents and aggregate responses
    agents = Agent.query.filter_by(team_id=team.id).all()
    responses = []
    for agent in agents:
        if not agent.is_project_manager:
            agent_response = simulate_agent_response(agent, user_message)
            responses.append(f"{agent.name}: {agent_response}")

    # Compile project manager response
    pm_response = "I have delegated your request to the team:\n" + "\n".join(responses)
    logger.info(f"Project manager processed message for team ID '{team.id}'")
    return pm_response

def simulate_agent_response(agent, user_message):
    """
    Simulate an agent's response based on their role.

    Args:
        agent (Agent): The agent processing the message.
        user_message (str): The message content to process.

    Returns:
        str: The agent's response.
    """
    # Placeholder for agent processing logic
    return f"Processed '{user_message}' as part of my role '{agent.role}'."

# Application Entry Point
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=False)
