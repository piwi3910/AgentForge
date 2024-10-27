import React, { useState, useEffect, useContext } from 'react';
import axios from 'axios';
import { AuthContext } from '../context/AuthContext';
import { toast } from 'react-toastify';

/**
 * Profile component allows users to view and update their profile information.
 *
 * @returns {JSX.Element} The rendered Profile component.
 */
function Profile() {
  const { isAuthenticated } = useContext(AuthContext);
  const [email, setEmail] = useState('');
  const [oldPassword, setOldPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');

  useEffect(() => {
    if (isAuthenticated) {
      fetchUserProfile();
    }
  }, [isAuthenticated]);

  /**
   * Fetches the user's profile information.
   */
  const fetchUserProfile = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get('/auth/profile', {
        headers: { Authorization: `Bearer ${token}` },
      });
      setEmail(response.data.email);
    } catch (error) {
      console.error('Error fetching user profile:', error);
    }
  };

  /**
   * Handles updating the user's password.
   */
  const handleUpdatePassword = async () => {
    try {
      const token = localStorage.getItem('token');
      await axios.put(
        '/auth/modify-password',
        { old_password: oldPassword, new_password: newPassword },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      toast.success('Password updated successfully.');
      setOldPassword('');
      setNewPassword('');
    } catch (error) {
      console.error('Error updating password:', error);
      toast.error('Failed to update password: ' + error.response.data.message);
    }
  };

  return (
    <div>
      <h2>User Profile</h2>
      <div>
        <label>Email:</label>
        <input type="email" value={email} readOnly />
      </div>
      <div>
        <h3>Change Password</h3>
        <div>
          <label>Old Password:</label>
          <input
            type="password"
            value={oldPassword}
            onChange={(event) => setOldPassword(event.target.value)}
          />
        </div>
        <div>
          <label>New Password:</label>
          <input
            type="password"
            value={newPassword}
            onChange={(event) => setNewPassword(event.target.value)}
          />
        </div>
        <button onClick={handleUpdatePassword}>Update Password</button>
      </div>
    </div>
  );
}

export default Profile;
