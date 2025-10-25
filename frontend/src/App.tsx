import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import './App.css';
import Dashboard from './pages/Dashboard';
import MarketDetail from './pages/MarketDetail';
import IdeaExplorer from './pages/IdeaExplorer';
import AgentConsole from './pages/AgentConsole';

const queryClient = new QueryClient();

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <div className="App">
          <nav className="navbar">
            <div className="nav-container">
              <Link to="/" className="nav-logo">
                AI Safety Prediction Market
              </Link>
              <ul className="nav-menu">
                <li className="nav-item">
                  <Link to="/" className="nav-link">Dashboard</Link>
                </li>
                <li className="nav-item">
                  <Link to="/ideas" className="nav-link">Ideas</Link>
                </li>
                <li className="nav-item">
                  <Link to="/agents" className="nav-link">Agents</Link>
                </li>
              </ul>
            </div>
          </nav>

          <main className="main-content">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/markets/:id" element={<MarketDetail />} />
              <Route path="/ideas" element={<IdeaExplorer />} />
              <Route path="/agents" element={<AgentConsole />} />
            </Routes>
          </main>
        </div>
      </Router>
    </QueryClientProvider>
  );
}

export default App;
