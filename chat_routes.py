from flask_restx import Namespace, Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Team, Agent, ChatMessage
from utils import process_project_manager_message
import logging

logger = logging.getLogger(__name__)

chat_namespace = Namespace('chat', description='Chat operations')

chat_message_model = chat_namespace.model('ChatMessage', {
    'message': fields.String(required=True, description='Chat message'),
})

@chat_namespace.route('/<int:team_id>/messages')
class ChatMessages(Resource):
    @jwt_required()
    def get(self, team_id):
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
        current_user_email = get_jwt_identity()
        user = User.query.filter_by(email=current_user_email).first()
        data = chat_namespace.payload
        message_content = data.get('message')

        team = Team.query.filter_by(id=team_id, user_id=user.id).first()
        if not team:
            logger.error(f"Message sent to non-existent team ID '{team_id}' by user: {current_user_email}")
            return {'message': 'Team not found'}, 404

        user_message = ChatMessage(
            sender_type='user',
            sender_id=user.id,
            message=message_content,
            user_id=user.id,
            team_id=team.id
        )
        db.session.add(user_message)
        db.session.commit()

        response = process_project_manager_message(user, team, message_content)

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
