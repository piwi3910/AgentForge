import React, { useContext } from 'react';
import { Navigate } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';

/**
 * PrivateRoute component that protects routes from unauthenticated access.
 *
 * @param {Object} props - The props passed to the component.
 * @returns {JSX.Element} The rendered component or a redirect.
 */
function PrivateRoute({ children }) {
  const { isAuthenticated } = useContext(AuthContext);

  return isAuthenticated ? children : <Navigate to="/login" replace />;
}

export default PrivateRoute;
