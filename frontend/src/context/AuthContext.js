import React, { createContext, useState, useEffect } from 'react';

export const AuthContext = createContext();

/**
 * AuthProvider component provides authentication context to child components.
 *
 * @param {Object} props - The props passed to the component.
 * @returns {JSX.Element} The rendered AuthProvider component.
 */
export function AuthProvider({ children }) {
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    // Check if token exists in local storage to set authentication status
    const token = localStorage.getItem('token');
    setIsAuthenticated(!!token);
  }, []);

  return (
    <AuthContext.Provider value={{ isAuthenticated, setIsAuthenticated }}>
      {children}
    </AuthContext.Provider>
  );
}
