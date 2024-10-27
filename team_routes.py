from flask_restx import Namespace, Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Team, Agent, EnabledModel
import logging

logger = logging.getLogger(__name__)

teams_namespace = Namespace('teams', description='Team management')

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

@teams_namespace.route('')
class TeamList(Resource):
    @jwt_required()
    def get(self):
        current_user_email = get_jwt_identity()
        user = User.query.filter_by(email=current_user_email).first()
        teams = Team.query.filter_by(user_id=user.id).all()

        result = [{'id': team.id, 'name': team.name, 'function': team.function} for team in teams]
        logger.info(f"Retrieved teams for user: {current_user_email}")
        return {'teams': result}, 200

    @jwt_required()
    @teams_namespace.expect(team_model)
    def post(self):
        data = teams_namespace.payload
        name = data.get('name')
        function = data.get('function')
        pm_model_id = data.get('project_manager_model_id')
        current_user_email = get_jwt_identity()
        user = User.query.filter_by(email=current_user_email).first()

        enabled_model = EnabledModel.query.filter_by(id=pm_model_id, user_id=user.id).first()
        if not enabled_model:
            logger.error(f"Enabled model ID '{pm_model_id}' not found for user: {current_user_email}")
            return {'message': 'Enabled model not found'}, 404

        team = Team(name=name, function=function, user_id=user.id)
        db.session.add(team)
        db.session.commit()

        project_manager = Agent(
            name='Project Manager',
            role='Project Manager',
            enabled_model_id=pm_model_id,
            team_id=team.id,
            is_project_manager=True
        )
        db.session.add(project_manager)
        db.session.commit()

        team.project_manager_id = project_manager.id
        db.session.commit()

        logger.info(f"Team '{name}' created by user: {current_user_email}")
        return {'message': 'Team created successfully', 'team_id': team.id}, 201

@teams_namespace.route('/<int:team_id>/agents')
class AgentList(Resource):
    @jwt_required()
    def get(self, team_id):
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
        data = teams_namespace.payload
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
