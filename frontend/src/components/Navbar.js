import React from 'react';
import { Link } from 'react-router-dom';

/**
 * Navbar component provides navigation links to different parts of the application.
 *
 * @returns {JSX.Element} The rendered Navbar component.
 */
function Navbar() {
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

  return (
    <nav style={navStyle}>
      <Link to="/" style={linkStyle}>Home</Link>
      <Link to="/models" style={linkStyle}>Models</Link>
      <Link to="/teams" style={linkStyle}>Teams</Link>
      <Link to="/chat" style={linkStyle}>Chat</Link>
      <Link to="/login" style={linkStyle}>Login</Link>
      <Link to="/register" style={linkStyle}>Register</Link>
    </nav>
  );
}

export default Navbar;
