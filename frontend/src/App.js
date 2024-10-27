import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Login from './components/Login';
import Register from './components/Register';
import Home from './components/Home';
import Models from './components/Models';
import Teams from './components/Teams';
import Chat from './components/Chat';
import PrivateRoute from './components/PrivateRoute';

/**
 * Main application component that defines routing and includes the Navbar.
 *
 * @returns {JSX.Element} The rendered application.
 */
function App() {
  return (
    <Router>
      <div className="App">
        <Navbar />
        {/* Define your routes here */}
        <Routes>
          <Route path="/" element={<Home />} />
          <Route
            path="/models"
            element={
              <PrivateRoute>
                <Models />
              </PrivateRoute>
            }
          />
          <Route
            path="/teams"
            element={
              <PrivateRoute>
                <Teams />
              </PrivateRoute>
            }
          />
          <Route
            path="/chat"
            element={
              <PrivateRoute>
                <Chat />
              </PrivateRoute>
            }
          />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          {/* Add other routes as needed */}
        </Routes>
      </div>
    </Router>
  );
}

export default App;
