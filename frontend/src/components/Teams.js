import React, { useState, useEffect } from 'react';
import axios from 'axios';

/**
 * Teams component allows users to manage teams by creating new teams,
 * adding agents, and selecting models for agents.
 *
 * @returns {JSX.Element} The rendered Teams component.
 */
function Teams() {
  const [teams, setTeams] = useState([]);
  const [teamName, setTeamName] = useState('');
  const [teamFunction, setTeamFunction] = useState('');
  const [enabledModels, setEnabledModels] = useState([]);
  const [projectManagerModelId, setProjectManagerModelId] = useState('');
  const [selectedTeamId, setSelectedTeamId] = useState(null);
  const [agents, setAgents] = useState([]);
  const [agentName, setAgentName] = useState('');
  const [agentRole, setAgentRole] = useState('');
  const [agentModelId, setAgentModelId] = useState('');

  useEffect(() => {
    fetchTeams();
    fetchEnabledModels();
  }, []);

  /**
   * Fetches all teams associated with the user.
   */
  const fetchTeams = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get('/teams', {
        headers: { Authorization: `Bearer ${token}` },
      });
      setTeams(response.data.teams);
    } catch (error) {
      console.error('Error fetching teams:', error);
    }
  };

  /**
   * Fetches all enabled models for the user.
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
   * Handles the creation of a new team with a project manager.
   */
  const handleCreateTeam = async () => {
    try {
      const token = localStorage.getItem('token');
      await axios.post(
        '/teams',
        {
          name: teamName,
          function: teamFunction,
          project_manager_model_id: projectManagerModelId,
        },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      alert('Team created successfully.');
      setTeamName('');
      setTeamFunction('');
      setProjectManagerModelId('');
      fetchTeams();
    } catch (error) {
      console.error('Error creating team:', error);
      alert('Failed to create team: ' + error.response.data.message);
    }
  };

  /**
   * Selects a team and fetches its agents.
   *
   * @param {number} teamId - The ID of the selected team.
   */
  const handleSelectTeam = (teamId) => {
    setSelectedTeamId(teamId);
    fetchAgents(teamId);
  };

  /**
   * Fetches all agents for a specific team.
   *
   * @param {number} teamId - The ID of the team.
   */
  const fetchAgents = async (teamId) => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`/teams/${teamId}/agents`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setAgents(response.data.agents);
    } catch (error) {
      console.error('Error fetching agents:', error);
    }
  };

  /**
   * Handles adding a new agent to the selected team.
   */
  const handleAddAgent = async () => {
    try {
      const token = localStorage.getItem('token');
      await axios.post(
        `/teams/${selectedTeamId}/agents`,
        {
          name: agentName,
          role: agentRole,
          model_id: agentModelId,
        },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      alert('Agent added successfully.');
      setAgentName('');
      setAgentRole('');
      setAgentModelId('');
      fetchAgents(selectedTeamId);
    } catch (error) {
      console.error('Error adding agent:', error);
      alert('Failed to add agent: ' + error.response.data.message);
    }
  };

  return (
    <div>
      <h2>Teams Management</h2>
      <div>
        <h3>Create Team</h3>
        <div>
          <label>Team Name:</label>
          <input
            type="text"
            value={teamName}
            onChange={(event) => setTeamName(event.target.value)}
            required
          />
        </div>
        <div>
          <label>Team Function:</label>
          <input
            type="text"
            value={teamFunction}
            onChange={(event) => setTeamFunction(event.target.value)}
          />
        </div>
        <div>
          <label>Select Project Manager Model:</label>
          <select
            value={projectManagerModelId}
            onChange={(event) => setProjectManagerModelId(event.target.value)}
          >
            <option value="">Select a model</option>
            {enabledModels.map((model) => (
              <option key={model.id} value={model.id}>
                {model.provider} - {model.model_name}
              </option>
            ))}
          </select>
        </div>
        <button onClick={handleCreateTeam}>Create Team</button>
      </div>
      <div>
        <h3>Existing Teams</h3>
        <ul>
          {teams.map((team) => (
            <li key={team.id}>
              {team.name} - {team.function}
              <button onClick={() => handleSelectTeam(team.id)}>
                Manage Team
              </button>
            </li>
          ))}
        </ul>
      </div>
      {selectedTeamId && (
        <div>
          <h3>Manage Agents for Selected Team</h3>
          <div>
            <h4>Add Agent</h4>
            <div>
              <label>Agent Name:</label>
              <input
                type="text"
                value={agentName}
                onChange={(event) => setAgentName(event.target.value)}
                required
              />
            </div>
            <div>
              <label>Agent Role:</label>
              <input
                type="text"
                value={agentRole}
                onChange={(event) => setAgentRole(event.target.value)}
              />
            </div>
            <div>
              <label>Select Agent Model:</label>
              <select
                value={agentModelId}
                onChange={(event) => setAgentModelId(event.target.value)}
              >
                <option value="">Select a model</option>
                {enabledModels.map((model) => (
                  <option key={model.id} value={model.id}>
                    {model.provider} - {model.model_name}
                  </option>
                ))}
              </select>
            </div>
            <button onClick={handleAddAgent}>Add Agent</button>
          </div>
          <div>
            <h4>Agents in Team</h4>
            <ul>
              {agents.map((agent) => (
                <li key={agent.id}>
                  {agent.name} - {agent.role} -{' '}
                  {agent.is_project_manager ? 'Project Manager' : 'Agent'}
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </div>
  );
}

export default Teams;
