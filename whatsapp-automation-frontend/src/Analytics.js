import React, { useEffect, useState } from 'react';
import './Analytics.css';

const Analytics = () => {
  const [analytics, setAnalytics] = useState(null);

  useEffect(() => {
    fetch('/automation/analytics/')
      .then((response) => response.json())
      .then((data) => setAnalytics(data))
      .catch((error) => console.error('Error fetching analytics:', error));
  }, []);

  if (!analytics) {
    return <div>Loading analytics...</div>;
  }

  return (
    <div className="analytics">
      <h2>Analytics Dashboard</h2>
      <ul>
        <li>Total Contacts: {analytics.total_contacts}</li>
        <li>Total Messages Sent: {analytics.total_messages}</li>
        <li>Response Rate: {analytics.response_rate}%</li>
      </ul>
    </div>
  );
};

export default Analytics;