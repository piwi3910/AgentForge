"""
Models for AgentForge Application

This module defines the SQLAlchemy models for the AgentForge application, including
User, APIKey, EnabledModel, Team, Agent, and ChatMessage.
"""

from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    """
    Model representing a user in the system.

    Attributes:
        id (int): Primary key.
        email (str): Unique email address of the user.
        password_hash (str): Hashed password.
        api_keys (list of APIKey): API keys associated with the user.
        enabled_models (list of EnabledModel): Models enabled by the user.
        teams (list of Team): Teams created by the user.
        chats (list of ChatMessage): Chat messages associated with the user.
    """
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    api_keys = db.relationship('APIKey', backref='user', lazy=True)
    enabled_models = db.relationship('EnabledModel', backref='user', lazy=True)
    teams = db.relationship('Team', backref='user', lazy=True)
    chats = db.relationship('ChatMessage', backref='user', lazy=True)

    def set_password(self, password):
        """Set the user's password hash."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check the user's password."""
        return check_password_hash(self.password_hash, password)

class APIKey(db.Model):
    """
    Model representing an API key associated with a user.

    Attributes:
        id (int): Primary key.
        provider (str): Name of the API provider.
        api_key (str): The API key value.
        endpoint (str): Custom API endpoint (optional).
        user_id (int): Foreign key referencing the user.
    """
    __tablename__ = 'api_keys'

    id = db.Column(db.Integer, primary_key=True)
    provider = db.Column(db.String(50), nullable=False)
    api_key = db.Column(db.String(256), nullable=False)
    endpoint = db.Column(db.String(256), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

class EnabledModel(db.Model):
    """
    Model representing a model enabled by the user for use.

    Attributes:
        id (int): Primary key.
        provider (str): Name of the API provider.
        model_name (str): Name of the enabled model.
        user_id (int): Foreign key referencing the user.
    """
    __tablename__ = 'enabled_models'

    id = db.Column(db.Integer, primary_key=True)
    provider = db.Column(db.String(50), nullable=False)
    model_name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

class Team(db.Model):
    """
    Model representing a team created by a user.

    Attributes:
        id (int): Primary key.
        name (str): Name of the team.
        function (str): Function or purpose of the team.
        project_manager_id (int): Foreign key referencing the project manager agent.
        user_id (int): Foreign key referencing the user who created the team.
        agents (list of Agent): Agents associated with the team.
        chats (list of ChatMessage): Chat messages associated with the team.
    """
    __tablename__ = 'teams'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    function = db.Column(db.String(255), nullable=True)
    project_manager_id = db.Column(db.Integer, db.ForeignKey('agents.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    agents = db.relationship('Agent', backref='team', lazy=True)
    chats = db.relationship('ChatMessage', backref='team', lazy=True)

class Agent(db.Model):
    """
    Model representing an agent within a team.

    Attributes:
        id (int): Primary key.
        name (str): Name of the agent.
        role (str): Role or function of the agent.
        enabled_model_id (int): Foreign key referencing the enabled model.
        team_id (int): Foreign key referencing the team.
        is_project_manager (bool): Indicates if the agent is the project manager.
        chats (list of ChatMessage): Chat messages associated with the agent.
    """
    __tablename__ = 'agents'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(100), nullable=True)
    enabled_model_id = db.Column(db.Integer, db.ForeignKey('enabled_models.id'), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    is_project_manager = db.Column(db.Boolean, default=False, nullable=False)

    chats = db.relationship('ChatMessage', backref='agent', lazy=True)

class ChatMessage(db.Model):
    """
    Model representing a message in a chat between the user and agents.

    Attributes:
        id (int): Primary key.
        sender_type (str): Type of the sender ('user', 'project_manager', 'agent').
        sender_id (int): ID of the sender (User ID or Agent ID).
        message (str): The message content.
        timestamp (datetime): Time when the message was sent.
        user_id (int): Foreign key referencing the user.
        team_id (int): Foreign key referencing the team.
        agent_id (int): Foreign key referencing the agent (nullable).
    """
    __tablename__ = 'chat_messages'

    id = db.Column(db.Integer, primary_key=True)
    sender_type = db.Column(db.String(50), nullable=False)
    sender_id = db.Column(db.Integer, nullable=False)
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    agent_id = db.Column(db.Integer, db.ForeignKey('agents.id'), nullable=True)
