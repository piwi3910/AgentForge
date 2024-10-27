import React, { useState, useEffect } from 'react';
import axios from 'axios';

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

  const handleSelectTeam = (teamId) => {
    setSelectedTeamId(teamId);
    fetchAgents(teamId);
  };

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

  const handleAddAgent = async () => {
    try {
      const token = localStorage.getItem('token');
      await axios.post(
        `/teams/${selectedTeamId}/agents`,
        {
          name: agentName,
          role: agentRole,
          model_id: agentModelId,
          team_id: selectedTeamId,
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
            onChange={(e) => setTeamName(e.target.value)}
            required
          />
        </div>
        <div>
          <label>Team Function:</label>
          <input
            type="text"
            value={teamFunction}
            onChange={(e) => setTeamFunction(e.target.value)}
          />
        </div>
        <div>
          <label>Select Project Manager Model:</label>
          <select
            value={projectManagerModelId}
            onChange={(e) => setProjectManagerModelId(e.target.value)}
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
                onChange={(e) => setAgentName(e.target.value)}
                required
              />
            </div>
            <div>
              <label>Agent Role:</label>
              <input
                type="text"
                value={agentRole}
                onChange={(e) => setAgentRole(e.target.value)}
              />
            </div>
            <div>
              <label>Select Agent Model:</label>
              <select
                value={agentModelId}
                onChange={(e) => setAgentModelId(e.target.value)}
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
