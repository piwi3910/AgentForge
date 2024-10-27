from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    api_keys = db.relationship('APIKey', backref='user', lazy=True)
    enabled_models = db.relationship('EnabledModel', backref='user', lazy=True)
    teams = db.relationship('Team', backref='user', lazy=True)
    chats = db.relationship('ChatMessage', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class APIKey(db.Model):
    __tablename__ = 'api_keys'
    id = db.Column(db.Integer, primary_key=True)
    provider = db.Column(db.String(50), nullable=False)
    api_key = db.Column(db.String(256), nullable=False)
    endpoint = db.Column(db.String(256), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

class EnabledModel(db.Model):
    __tablename__ = 'enabled_models'
    id = db.Column(db.Integer, primary_key=True)
    provider = db.Column(db.String(50), nullable=False)
    model_name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

class Team(db.Model):
    __tablename__ = 'teams'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    function = db.Column(db.String(255), nullable=True)
    project_manager_id = db.Column(db.Integer, db.ForeignKey('agents.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    agents = db.relationship('Agent', backref='team', lazy=True)
    chats = db.relationship('ChatMessage', backref='team', lazy=True)

class Agent(db.Model):
    __tablename__ = 'agents'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(100), nullable=True)
    enabled_model_id = db.Column(db.Integer, db.ForeignKey('enabled_models.id'), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    is_project_manager = db.Column(db.Boolean, default=False)
    chats = db.relationship('ChatMessage', backref='agent', lazy=True)

class ChatMessage(db.Model):
    __tablename__ = 'chat_messages'
    id = db.Column(db.Integer, primary_key=True)
    sender_type = db.Column(db.String(50), nullable=False)  # 'user', 'project_manager', 'agent'
    sender_id = db.Column(db.Integer, nullable=False)        # ID of the sender (User ID or Agent ID)
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    agent_id = db.Column(db.Integer, db.ForeignKey('agents.id'), nullable=True)
