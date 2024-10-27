from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, APIKey, EnabledModel
from utils import test_api_key, get_available_models
import logging

logger = logging.getLogger(__name__)

models_namespace = Namespace('models', description='Model management')

api_key_model = models_namespace.model('APIKey', {
    'provider': fields.String(required=True, description='Provider name'),
    'api_key': fields.String(required=True, description='API key'),
    'endpoint': fields.String(description='Custom API endpoint (optional)'),
})

enabled_model_model = models_namespace.model('EnabledModel', {
    'provider': fields.String(required=True, description='Provider name'),
    'model_name': fields.String(required=True, description='Model name'),
})

@models_namespace.route('/api-keys')
class APIKeyManagement(Resource):
    @jwt_required()
    def get(self):
        current_user_email = get_jwt_identity()
        user = User.query.filter_by(email=current_user_email).first()
        api_keys = APIKey.query.filter_by(user_id=user.id).all()

        result = [{'provider': key.provider, 'endpoint': key.endpoint} for key in api_keys]
        logger.info(f"Retrieved API keys for user: {current_user_email}")
        return {'api_keys': result}, 200

    @jwt_required()
    @models_namespace.expect(api_key_model)
    def post(self):
        data = models_namespace.payload
        provider = data.get('provider')
        api_key_value = data.get('api_key')
        endpoint = data.get('endpoint')
        current_user_email = get_jwt_identity()
        user = User.query.filter_by(email=current_user_email).first()

        is_valid = test_api_key(provider, api_key_value, endpoint)
        if not is_valid:
            logger.error(f"Invalid API key for provider '{provider}' by user: {current_user_email}")
            return {'message': f'Invalid API key for provider {provider}'}, 400

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
    @jwt_required()
    def get(self, provider):
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
    @jwt_required()
    def get(self):
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
        data = models_namespace.payload
        provider = data.get('provider')
        model_name = data.get('model_name')
        current_user_email = get_jwt_identity()
        user = User.query.filter_by(email=current_user_email).first()

        api_key_entry = APIKey.query.filter_by(user_id=user.id, provider=provider).first()
        if not api_key_entry:
            logger.error(f"API key for provider '{provider}' not found for user: {current_user_email}")
            return {'message': f'API key for provider {provider} not found'}, 404

        available_models = get_available_models(provider, api_key_entry.api_key, api_key_entry.endpoint)
        if not available_models or model_name not in available_models:
            logger.error(f"Model '{model_name}' not available for provider '{provider}'")
            return {'message': f'Model {model_name} not available for provider {provider}'}, 400

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
        data = models_namespace.payload
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
