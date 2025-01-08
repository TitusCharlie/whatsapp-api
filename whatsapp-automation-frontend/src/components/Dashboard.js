// src/components/Dashboard.js

import React from 'react';
import { Link } from 'react-router-dom';
import './Dashboard.css';

const Dashboard = () => {
  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <h1>WhatsApp Automation Dashboard</h1>
      </header>
      <nav className="dashboard-nav">
        <ul>
          <li><Link to="/create-contact">Manage Contacts</Link></li>
          <li><Link to="/broadcast">Broadcast Messages</Link></li>
          <li><Link to="/autoresponder">Autoresponder</Link></li>
          <li><Link to="/analytics">Analytics</Link></li>
          <li><Link to="/group-automation">Group Automation</Link></li>
          <li><Link to="/status-scheduler">Status Scheduler</Link></li>
        </ul>
      </nav>
      <main className="dashboard-main">
        <p>Select a feature to get started.</p>
      </main>
    </div>
  );
};

export default Dashboard;