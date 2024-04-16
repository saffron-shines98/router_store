import React, { useState } from 'react';
import { TextField, Typography } from '@mui/material';

const Form = ({ configType, formData, setFormData }) => {

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prevData) => ({
      ...prevData,
      [name]: value,
    }));
  };

  // Render different input fields based on configType
  const renderInputFields = () => {
    switch (configType) {
      case 'Basic device setting':
        return (
          <>
            <Typography sx={{display: 'flex', alignItems: 'center', fontWeight: 'bold', marginTop: '10px'}}>Basic Configuration:</Typography>
            <TextField
              name="basic_interface"
              label="Interface"
              value={formData.basic_interface}
              onChange={handleChange}
              fullWidth
              margin="normal"
            />
            <TextField
              name="ipAddress"
              label="IP Address"
              value={formData.ipAddress}
              onChange={handleChange}
              fullWidth
              margin="normal"
            />
            <TextField
              name="subnetMask"
              label="Subnet Mask"
              value={formData.subnetMask}
              onChange={handleChange}
              fullWidth
              margin="normal"
            />
          </>
        );
      case 'OSPF':
        return (
          <>
          <Typography sx={{display: 'flex', alignItems: 'center', fontWeight: 'bold', marginTop: '10px'}}>Process Id:</Typography>
            <TextField
              name="process_id"
              label="Process Id"
              value={formData.process_id}
              onChange={handleChange}
              fullWidth
              margin="normal"
            />
            <TextField
              name="network"
              label="Network"
              value={formData.network}
              onChange={handleChange}
              fullWidth
              margin="normal"
            />
            <TextField
              name="area"
              label="Area"
              value={formData.area}
              onChange={handleChange}
              fullWidth
              margin="normal"
            />
          </>
        );
      case 'HSRP':
        return (
          <>
          <Typography sx={{display: 'flex', alignItems: 'center', fontWeight: 'bold', marginTop: '10px'}}>HSRP Configuration:</Typography>
            <TextField
              name="interface"
              label="Interface"
              value={formData.interface}
              onChange={handleChange}
              fullWidth
              margin="normal"
            />
            <TextField
              name="group_id"
              label="Group Id"
              value={formData.group_id}
              onChange={handleChange}
              fullWidth
              margin="normal"
            />
            <TextField
              name="virtual_ip"
              label="Virtual Ip"
              value={formData.virtual_ip}
              onChange={handleChange}
              fullWidth
              margin="normal"
            />
          </>
        );
      case 'VLAN':
        return (
          <>
          <Typography sx={{display: 'flex', alignItems: 'center', fontWeight: 'bold', marginTop: '10px'}}>VLAN Configuration:</Typography>
            <TextField
              name="vlan_id"
              label="Vlan Id"
              value={formData.vlan_id}
              onChange={handleChange}
              fullWidth
              margin="normal"
            />
            <TextField
              name="name"
              label="Name"
              value={formData.name}
              onChange={handleChange}
              fullWidth
              margin="normal"
            />
          </>
        );
      case 'ACL-Access Control List':
        return (
          <>
          <Typography sx={{display: 'flex', alignItems: 'center', fontWeight: 'bold', marginTop: '10px'}}>ACL-Access Control List:</Typography>
            <TextField
              name="acl_number"
              label="Acl Number"
              value={formData.acl_number}
              onChange={handleChange}
              fullWidth
              margin="normal"
            />
            <TextField
              name="direction"
              label="Direction"
              value={formData.direction}
              onChange={handleChange}
              fullWidth
              margin="normal"
            />
            <TextField
              name="acl_rules"
              label="Acl Rules"
              value={formData.acl_rules}
              onChange={handleChange}
              fullWidth
              margin="normal"
            />
          </>
        );
      // Add cases for other configuration types as needed
      default:
        return null;
    }
  };

  return (
    <div className="form-container">
      <div className="content">
        {renderInputFields()}
      </div>
    </div>
  );
};

export default Form;
