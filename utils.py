import logging
from models import APIKey, EnabledModel, Agent
from flask_jwt_extended import get_jwt_identity

logger = logging.getLogger(__name__)

def get_user_api_key(provider, user_id):
    """
    Retrieve the API key for a given provider and user.

    Args:
        provider (str): The name of the provider.
        user_id (int): The ID of the user.

    Returns:
        APIKey or None: The APIKey object if found, else None.
    """
    return APIKey.query.filter_by(user_id=user_id, provider=provider).first()

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
    else:
        logger.error(f"Provider '{provider}' is not supported.")
        return None

def generate_agent_response(agent, user_message):
    """
    Generate a response from an agent using the associated model.

    Args:
        agent (Agent): The agent generating the response.
        user_message (str): The message to respond to.

    Returns:
        str: The agent's response.
    """
    enabled_model = EnabledModel.query.filter_by(id=agent.enabled_model_id).first()
    api_key_entry = get_user_api_key(enabled_model.provider, agent.team.user_id)
    if not api_key_entry:
        logger.error(f"API key for provider '{enabled_model.provider}' not found for agent ID: {agent.id}")
        return "Unable to generate response due to missing API key."

    provider = enabled_model.provider.lower()
    model_name = enabled_model.model_name
    api_key = api_key_entry.api_key
    endpoint = api_key_entry.endpoint

    if provider == 'openai':
        try:
            import openai
            openai.api_key = api_key
            if endpoint:
                openai.api_base = endpoint
            response = openai.Completion.create(
                engine=model_name,
                prompt=user_message,
                max_tokens=150
            )
            agent_response = response.choices[0].text.strip()
            logger.info(f"Agent ID '{agent.id}' generated a response using OpenAI model '{model_name}'")
            return agent_response
        except Exception as exc:
            logger.error(f"Agent ID '{agent.id}' failed to generate response: {exc}")
            return f"Error generating response: {exc}"
    else:
        logger.error(f"Provider '{provider}' is not supported for agent ID: {agent.id}")
        return "Provider not supported."

def process_project_manager_message(user, team, user_message):
    """
    Process the user's message with the project manager and delegate tasks to agents.

    Args:
        user (User): The user sending the message.
        team (Team): The team the message is directed to.
        user_message (str): The message content from the user.

    Returns:
        str: The response from the project manager after delegating tasks.
    """
    pm_agent = Agent.query.filter_by(id=team.project_manager_id).first()
    if not pm_agent:
        logger.error(f"Project manager not found for team ID '{team.id}'")
        return "Project manager not found."

    pm_response = generate_agent_response(pm_agent, user_message)

    agents = Agent.query.filter_by(team_id=team.id).all()
    responses = []
    for agent in agents:
        if not agent.is_project_manager:
            agent_response = generate_agent_response(agent, user_message)
            responses.append(f"{agent.name}: {agent_response}")

    full_response = f"{pm_response}\n\nDelegated tasks to your team:\n" + "\n".join(responses)
    logger.info(f"Processed message for team ID '{team.id}' by user: {user.email}")
    return full_response
