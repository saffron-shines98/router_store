import React, { useState } from "react";
import { useParams } from "react-router-dom";
import {
  Button,
  Dialog,
  DialogContent,
  Slide,
  Typography,
  Checkbox,
  List,
  ListItem,
} from "@mui/material";
import Form from "./Form";
import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import FiberManualRecordIcon from '@mui/icons-material/FiberManualRecord';
import ErrorIcon from "@mui/icons-material/Error";
import axios from "axios";

const DeviceConfig = () => {
  const { deviceId } = useParams();
  const [selectedConfigs, setSelectedConfigs] = useState([]);
  const [showSuccessModal, setShowSuccessModal] = useState(false);
  const [showErrorModal, setShowErrorModal] = useState(false);
  const [submittedData, setSubmittedData] = useState(null);
  const [errors, setErrors] = useState({});
  const [response, setResponse] = useState("");
  const [loading, setLoading] = useState(false); // Add loading state
  const systemInfo = JSON.parse(localStorage.getItem("systemInfo"));
  const [formData, setFormData] = useState({
    // Define initial form data based on configType
    interface: "",
    ipAddress: "",
    subnetMask: "",
    process_id: "",
    network: "",
    area: "",
    group_id: "",
    virtual_ip: "",
    vlan_id: "",
    name: "",
    acl_number: "",
    direction: "",
    acl_rules: "",
    basic_interface: "",
  });

  const handleConfigSelection = (configType) => {
    const updatedConfigs = selectedConfigs.includes(configType)
      ? selectedConfigs.filter(
          (selectedConfig) => selectedConfig !== configType
        )
      : [...selectedConfigs, configType];
    setSelectedConfigs(updatedConfigs);
  };

  const handleCloseSuccessModal = () => {
    setShowSuccessModal(false);
    resetForm();
  };

  const handleCloseErrorModal = () => {
    setShowErrorModal(false);
  };

  const resetForm = () => {
    setErrors({});
  };

  const handleSubmit = async () => {
    setLoading(true); // Set loading state to true when submitting
    // Logic to handle submission of selected configs
    let data = {
      ip: systemInfo?.ip,
      user_name: systemInfo?.user_name,
      password: systemInfo?.password,
      host_name: systemInfo?.host_name,
      banner_msg: systemInfo?.banner_msg,
      config: [
        {
          task: "basic",
          params: {
            interface: formData?.basic_interface,
            ip_address: formData?.ipAddress,
            subnet_mask: formData?.subnetMask,
          },
        },
        {
          task: "configure_ospf",
          params: {
            process_id: formData?.process_id,
            network: formData?.network,
            area: formData?.network,
          },
        },
        {
          task: "configure_hsrp",
          params: {
            interface: formData?.interface,
            group_id: formData?.group_id,
            virtual_ip: formData?.virtual_ip,
          },
        },
        {
          task: "configure_vlan",
          params: { vlan_id: formData?.vlan_id, name: formData?.name },
        },
        {
          task: "configure_acl",
          params: {
            acl_number: formData?.acl_number,
            direction: formData?.direction,
            acl_rules: formData?.acl_rules,
          },
        },
      ],
    };
    try {
      // Send POST request with application/json Content-Type header
      const res = await axios.post(
        `http://localhost:5000/router/config`,
        data,
        {
          headers: {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
          },
        }
      );
      setResponse(res?.data?.d); // Assuming you want to log the response data
      setShowSuccessModal(true);
    } catch (error) {
      console.error("Error occurred while submitting data:", error);
      setShowErrorModal(true);
    } finally {
      setLoading(false); // Set loading state to false after API response
    }
  };

  return (
    <div className="container">
      <div className="content">
        <h2>Device Configuration</h2>
        <p>Select what you want to configure:</p>
        <div style={{ marginBottom: "10px" }}>
          <Checkbox
            checked={selectedConfigs.includes("Basic device setting")}
            onChange={() => handleConfigSelection("Basic device setting")}
          />
          Basic device setting
          {deviceId === "3725" && (
            <>
              <Checkbox
                checked={selectedConfigs.includes("VLAN")}
                onChange={() => handleConfigSelection("VLAN")}
              />
              VLAN
            </>
          )}
          {deviceId === "2600" && (
            <>
              <Checkbox
                checked={selectedConfigs.includes("OSPF")}
                onChange={() => handleConfigSelection("OSPF")}
              />
              OSPF
              <Checkbox
                checked={selectedConfigs.includes("HSRP")}
                onChange={() => handleConfigSelection("HSRP")}
              />
              HSRP
              <Checkbox
                checked={selectedConfigs.includes("ACL-Access Control List")}
                onChange={() =>
                  handleConfigSelection("ACL-Access Control List")
                }
              />
              ACL-Access Control List
            </>
          )}
        </div>

        {/* Render forms for selected configs */}
        {selectedConfigs.map((selectedConfig) => (
          <Form
            key={selectedConfig}
            configType={selectedConfig}
            formData={formData}
            setFormData={setFormData}
          />
        ))}

        <Button
          onClick={handleSubmit}
          disabled={selectedConfigs.length === 0 || loading} // Disable button when loading
          variant="contained"
        >
          {loading ? 'Loading...' : 'Submit'} {/* Show loading text when loading */}
        </Button>

        {/* Success Modal */}
        <Dialog open={showSuccessModal} onClose={handleCloseSuccessModal}>
          <DialogContent>
            <Slide
              direction="down"
              in={showSuccessModal}
              mountOnEnter
              unmountOnExit
            >
              <div style={{ textAlign: "center" }}>
                <CheckCircleIcon sx={{ fontSize: 80, color: "green" }} />
                <Typography variant="h6" gutterBottom>
                  Configuration updated successfully
                </Typography>
                {/* Display submitted data */}
                {response.length &&
                  response.map((item, key) => {
                    return (
                      <List key={key} sx={{paddingTop: 0, paddingBottom: 0}}>
                        <ListItem>
                          <FiberManualRecordIcon style={{ marginRight: "8px" }} />
                          <Typography variant="body2">
                            {item.msg}
                          </Typography>
                        </ListItem>
                      </List>
                    );
                  })}
              </div>
            </Slide>
          </DialogContent>
        </Dialog>
        {/* Error Modal */}
        <Dialog open={showErrorModal} onClose={handleCloseErrorModal}>
          <DialogContent>
            <Slide
              direction="down"
              in={showErrorModal}
              mountOnEnter
              unmountOnExit
            >
              <div style={{ textAlign: "center" }}>
                <ErrorIcon sx={{ fontSize: 80, color: "red" }} />
                <Typography variant="h6" gutterBottom>
                  Something went wrong
                </Typography>
              </div>
            </Slide>
          </DialogContent>
        </Dialog>
      </div>
    </div>
  );
};

export default DeviceConfig;
