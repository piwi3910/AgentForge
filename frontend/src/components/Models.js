import React, { useState, useEffect } from 'react';
import axios from 'axios';

/**
 * Models component allows users to manage API keys and models for different providers.
 *
 * @returns {JSX.Element} The rendered Models component.
 */
function Models() {
  const [apiKeys, setApiKeys] = useState([]);
  const [providers] = useState(['OpenAI', 'Anthropic', 'OpenRouter', 'Ollama']);
  const [selectedProvider, setSelectedProvider] = useState('OpenAI');
  const [apiKey, setApiKey] = useState('');
  const [endpoint, setEndpoint] = useState('');
  const [availableModels, setAvailableModels] = useState([]);
  const [enabledModels, setEnabledModels] = useState([]);
  const [selectedModel, setSelectedModel] = useState('');

  useEffect(() => {
    fetchApiKeys();
    fetchEnabledModels();
  }, []);

  /**
   * Fetches the API keys associated with the user.
   */
  const fetchApiKeys = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get('/models/api-keys', {
        headers: { Authorization: `Bearer ${token}` },
      });
      setApiKeys(response.data.api_keys);
    } catch (error) {
      console.error('Error fetching API keys:', error);
    }
  };

  /**
   * Fetches the models enabled by the user.
   */
  const fetchEnabledModels = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get('/models/enabled-models', {
        headers: { Authorization: `Bearer ${token}` },
      });
      setEnabledModels(response.data.enabled_models);
    } catch (error) {
      console.error('Error fetching enabled models:', error);
    }
  };

  /**
   * Handles adding a new API key for a selected provider.
   */
  const handleAddApiKey = async () => {
    try {
      const token = localStorage.getItem('token');
      await axios.post(
        '/models/api-keys',
        {
          provider: selectedProvider,
          api_key: apiKey,
          endpoint: endpoint || undefined,
        },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      alert(`API key for ${selectedProvider} added successfully.`);
      setApiKey('');
      setEndpoint('');
      fetchApiKeys();
    } catch (error) {
      console.error('Error adding API key:', error);
      alert('Failed to add API key: ' + error.response.data.message);
    }
  };

  /**
   * Handles retrieving available models from the selected provider.
   */
  const handleGetModels = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`/models/available-models/${selectedProvider}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setAvailableModels(response.data.models);
    } catch (error) {
      console.error('Error fetching available models:', error);
      alert('Failed to retrieve models: ' + error.response.data.message);
    }
  };

  /**
   * Handles enabling a selected model.
   *
   * @param {string} modelName - The name of the model to enable.
   */
  const handleEnableModel = async (modelName) => {
    try {
      const token = localStorage.getItem('token');
      await axios.post(
        '/models/enabled-models',
        {
          provider: selectedProvider,
          model_name: modelName,
        },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      alert(`Model ${modelName} enabled for ${selectedProvider}.`);
      fetchEnabledModels();
    } catch (error) {
      console.error('Error enabling model:', error);
      alert('Failed to enable model: ' + error.response.data.message);
    }
  };

  /**
   * Handles disabling a selected model.
   *
   * @param {string} modelName - The name of the model to disable.
   */
  const handleDisableModel = async (modelName) => {
    try {
      const token = localStorage.getItem('token');
      await axios.delete('/models/enabled-models', {
        data: {
          provider: selectedProvider,
          model_name: modelName,
        },
        headers: { Authorization: `Bearer ${token}` },
      });
      alert(`Model ${modelName} disabled for ${selectedProvider}.`);
      fetchEnabledModels();
    } catch (error) {
      console.error('Error disabling model:', error);
      alert('Failed to disable model: ' + error.response.data.message);
    }
  };

  return (
    <div>
      <h2>Models Management</h2>
      <div>
        <h3>Add API Key</h3>
        <label>Provider:</label>
        <select
          value={selectedProvider}
          onChange={(event) => setSelectedProvider(event.target.value)}
        >
          {providers.map((providerItem) => (
            <option key={providerItem} value={providerItem}>
              {providerItem}
            </option>
          ))}
        </select>
        <div>
          <label>API Key:</label>
          <input
            type="text"
            value={apiKey}
            onChange={(event) => setApiKey(event.target.value)}
            required
          />
        </div>
        <div>
          <label>Custom Endpoint (Optional):</label>
          <input
            type="text"
            value={endpoint}
            onChange={(event) => setEndpoint(event.target.value)}
          />
        </div>
        <button onClick={handleAddApiKey}>Add API Key</button>
      </div>
      <div>
        <h3>Available Models</h3>
        <button onClick={handleGetModels}>Get Available Models</button>
        {availableModels.length > 0 && (
          <ul>
            {availableModels.map((model) => (
              <li key={model}>
                {model}{' '}
                <button onClick={() => handleEnableModel(model)}>Enable</button>
              </li>
            ))}
          </ul>
        )}
      </div>
      <div>
        <h3>Enabled Models</h3>
        {enabledModels.length > 0 ? (
          <ul>
            {enabledModels.map((model) => (
              <li key={model.id}>
                {model.provider} - {model.model_name}{' '}
                <button onClick={() => handleDisableModel(model.model_name)}>
                  Disable
                </button>
              </li>
            ))}
          </ul>
        ) : (
          <p>No models enabled.</p>
        )}
      </div>
    </div>
  );
}

export default Models;
