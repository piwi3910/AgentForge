"""
AgentForge Backend Application

This module defines the Flask application and registers API namespaces for the
AgentForge application. It includes user authentication, model management,
team management, and chat functionalities.
"""

import os
import logging
from flask import Flask
from flask_restx import Api
from flask_jwt_extended import JWTManager
from models import db
from auth_routes import auth_namespace
from model_routes import models_namespace
from team_routes import teams_namespace
from chat_routes import chat_namespace

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

# Register namespaces
api.add_namespace(auth_namespace, path='/auth')
api.add_namespace(models_namespace, path='/models')
api.add_namespace(teams_namespace, path='/teams')
api.add_namespace(chat_namespace, path='/chat')

# Application Entry Point
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=False)
