import React from 'react';
import { Link } from 'react-router-dom';
import { Button } from '@mui/material';

const Dashboard = () => {
  return (
    <div className="container">
      <div className="content">
        <h1>Choose a Device</h1>
        <Link to="/device-config/3725">
          <Button variant="contained" sx={{ mr: 2, mb: 2 }}>
            Cisco 3725 Switch
          </Button>
        </Link>
        <Link to="/device-config/2600">
          <Button variant="contained" sx={{ mr: 2, mb: 2 }}>
            Cisco 2600 Routers
          </Button>
        </Link>
      </div>
    </div>
  );
};

export default Dashboard;
