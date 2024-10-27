import React, { useContext } from 'react';
import { Link } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';

/**
 * Navbar component provides navigation links based on authentication status.
 *
 * @returns {JSX.Element} The rendered Navbar component.
 */
function Navbar() {
  const { isAuthenticated, setIsAuthenticated } = useContext(AuthContext);

  const navStyle = {
    padding: '10px',
    borderBottom: '1px solid #ccc',
    marginBottom: '20px',
  };

  const linkStyle = {
    marginRight: '15px',
    textDecoration: 'none',
    color: '#333',
  };

  /**
   * Handles user logout by clearing the token and updating authentication status.
   */
  const handleLogout = () => {
    localStorage.removeItem('token');
    setIsAuthenticated(false);
  };

  return (
    <nav style={navStyle}>
      <Link to="/" style={linkStyle}>Home</Link>
      {isAuthenticated ? (
        <>
          <Link to="/models" style={linkStyle}>Models</Link>
          <Link to="/teams" style={linkStyle}>Teams</Link>
          <Link to="/chat" style={linkStyle}>Chat</Link>
          <button onClick={handleLogout} style={linkStyle}>Logout</button>
        </>
      ) : (
        <>
          <Link to="/login" style={linkStyle}>Login</Link>
          <Link to="/register" style={linkStyle}>Register</Link>
        </>
      )}
    </nav>
  );
}

export default Navbar;
