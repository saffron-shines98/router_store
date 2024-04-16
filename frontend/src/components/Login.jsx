import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { TextField, Button, Typography } from "@mui/material";

const Login = () => {
  const [ipAddress, setIpAddress] = useState("");
  const [password, setPassword] = useState("");
  const [userName, setUserName] = useState("");
  const [hostName, setHostName] = useState("");
  const [bannerMsg, setBannerMsg] = useState("");
  const [errors, setErrors] = useState({});
  const navigate = useNavigate();

  const validateForm = () => {
    let errors = {};
    let isValid = true;

    // Validate IP Address
    if (!ipAddress) {
      errors.ipAddress = "IP Address is required";
      isValid = false;
    }

    // Validate Username
    if (!userName) {
      errors.userName = "Username is required";
      isValid = false;
    }

    // Validate Password
    if (!password) {
      errors.password = "Password is required";
      isValid = false;
    }

    // Validate Hostname
    if (!hostName) {
      errors.hostName = "Hostname is required";
      isValid = false;
    }

    // Validate Banner Message
    if (!bannerMsg) {
      errors.bannerMsg = "Banner Message is required";
      isValid = false;
    }

    setErrors(errors);
    return isValid;
  };

  const handleLogin = () => {
    if (validateForm()) {
      // Perform login logic, for simplicity let's just redirect to dashboard
      let data = {
        ip: ipAddress,
        password: password,
        user_name: userName,
        host_name: hostName,
        banner_msg: bannerMsg
      }
      localStorage.setItem('systemInfo', JSON.stringify(data));
      navigate("/dashboard");
    }
  };

  return (
    <div className="container">
      <div className="content">
        <Typography variant="h4" gutterBottom>
          NetMorph - SDN Config Pro
        </Typography>
        <TextField
          label="IP Address"
          value={ipAddress}
          onChange={(e) => setIpAddress(e.target.value)}
          fullWidth
          margin="normal"
          error={errors.ipAddress ? true : false}
          helperText={errors.ipAddress}
        />
        <TextField
          label="User Name"
          value={userName}
          onChange={(e) => setUserName(e.target.value)}
          fullWidth
          margin="normal"
          error={errors.userName ? true : false}
          helperText={errors.userName}
        />
        <TextField
          label="Password"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          fullWidth
          margin="normal"
          error={errors.password ? true : false}
          helperText={errors.password}
        />
        <TextField
          label="Hostname"
          type="text"
          value={hostName}
          onChange={(e) => setHostName(e.target.value)}
          fullWidth
          margin="normal"
          error={errors.hostName ? true : false}
          helperText={errors.hostName}
        />
        <TextField
          label="Banner Message"
          type="text"
          value={bannerMsg}
          onChange={(e) => setBannerMsg(e.target.value)}
          fullWidth
          margin="normal"
          error={errors.hostName ? true : false}
          helperText={errors.bannerMsg}
        />
        <Button variant="contained" onClick={handleLogin}>
          Connect
        </Button>
      </div>
    </div>
  );
};

export default Login;
