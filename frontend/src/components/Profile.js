import React, { useState, useEffect, useContext } from 'react';
import axios from 'axios';
import { AuthContext } from '../context/AuthContext';
import { toast } from 'react-toastify';
import TextField from '@mui/material/TextField';
import Button from '@mui/material/Button';
import Container from '@mui/material/Container';
import Typography from '@mui/material/Typography';

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
    <Container maxWidth="sm">
      <Typography variant="h4" component="h1" gutterBottom>
        User Profile
      </Typography>
      <TextField
        label="Email"
        type="email"
        fullWidth
        margin="normal"
        value={email}
        InputProps={{
          readOnly: true,
        }}
      />
      <Typography variant="h6" component="h2" gutterBottom>
        Change Password
      </Typography>
      <TextField
        label="Old Password"
        type="password"
        fullWidth
        margin="normal"
        value={oldPassword}
        onChange={(event) => setOldPassword(event.target.value)}
      />
      <TextField
        label="New Password"
        type="password"
        fullWidth
        margin="normal"
        value={newPassword}
        onChange={(event) => setNewPassword(event.target.value)}
      />
      <Button variant="contained" color="primary" onClick={handleUpdatePassword} fullWidth>
        Update Password
      </Button>
    </Container>
  );
}

export default Profile;
