import React, { useState, useEffect } from 'react';
import axios from 'axios';

/**
 * Chat component allows users to chat with the project manager of a selected team.
 *
 * @returns {JSX.Element} The rendered Chat component.
 */
function Chat() {
  const [teams, setTeams] = useState([]);
  const [selectedTeamId, setSelectedTeamId] = useState('');
  const [messages, setMessages] = useState([]);
  const [messageContent, setMessageContent] = useState('');

  // Fetch teams on component mount
  useEffect(() => {
    fetchTeams();
  }, []);

  /**
   * Fetches the list of teams associated with the user.
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
   * Fetches chat messages for a selected team.
   *
   * @param {string} teamId - The ID of the selected team.
   */
  const fetchMessages = async (teamId) => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`/chat/${teamId}/messages`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setMessages(response.data.messages);
    } catch (error) {
      console.error('Error fetching messages:', error);
    }
  };

  /**
   * Handles team selection and fetches messages for the selected team.
   *
   * @param {string} teamId - The ID of the selected team.
   */
  const handleSelectTeam = (teamId) => {
    setSelectedTeamId(teamId);
    fetchMessages(teamId);
  };

  /**
   * Handles sending a message to the project manager.
   */
  const handleSendMessage = async () => {
    if (!messageContent) return;
    try {
      const token = localStorage.getItem('token');
      await axios.post(
        `/chat/${selectedTeamId}/messages`,
        { message: messageContent },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setMessageContent('');
      fetchMessages(selectedTeamId);
    } catch (error) {
      console.error('Error sending message:', error);
      alert('Failed to send message: ' + error.response.data.message);
    }
  };

  return (
    <div>
      <h2>Chat with Project Manager</h2>
      <div>
        <label>Select Team:</label>
        <select
          value={selectedTeamId}
          onChange={(event) => handleSelectTeam(event.target.value)}
        >
          <option value="">Select a team</option>
          {teams.map((team) => (
            <option key={team.id} value={team.id}>
              {team.name}
            </option>
          ))}
        </select>
      </div>
      {selectedTeamId && (
        <div>
          <div
            style={{
              border: '1px solid #ccc',
              padding: '10px',
              height: '300px',
              overflowY: 'scroll',
              margin: '10px 0',
            }}
          >
            {messages.map((msg) => (
              <div key={msg.id}>
                <strong>{msg.sender_type}</strong>: {msg.message}
              </div>
            ))}
          </div>
          <div>
            <input
              type="text"
              value={messageContent}
              onChange={(event) => setMessageContent(event.target.value)}
              placeholder="Type your message"
            />
            <button onClick={handleSendMessage}>Send</button>
          </div>
        </div>
      )}
    </div>
  );
}

export default Chat;
