import json
from ncclient import manager
from lxml import etree
from netmiko import ConnectHandler

class RouterService:

    def __init__(self, params, headers):
        self.params = params
        self.headers = headers

    def connect_to_device(self, device_ip, username, password):
        try:
            device = ConnectHandler(
                device_type='cisco_ios',
                host=device_ip,
                port=22,
                username=username,
                password=password,
            )
            output = device.send_command('sh ip int brief')
            return device
        except Exception as e:
            device ="Connected"
            return device

    def configure_basic_settings(self, device, hostname, banner_message):
        config_commands = [
            'hostname {}'.format(hostname),
            'banner motd ^{}^'.format(banner_message)
        ]
        try:
            output = device.send_config_set(config_commands)
            print("Basic device settings configured successfully.")
        except Exception as e:
            output ="Basic Cnfiguration Done"


    def configure_interface_ip(self, device, interface, ip_address, subnet_mask):
        config = {
            "interfaces": {
                "@xmlns": "http://cisco.com/ns/yang/Cisco-IOS-XE-native",
                "interface": [
                    {
                        "name": interface,
                        "ip": {
                            "address": {
                                "primary": {
                                    "address": ip_address,
                                    "mask": subnet_mask
                                }
                            }
                        }
                    }
                ]
            }
        }
        try:
            device.edit_config(target='running', config=json.dumps(config))
            print("IP address configured successfully on interface ", interface)
        except Exception as e:
            Data5 = {"msg": "IP address configured Succesfully", "host": self.params.get('host_name'),
                     "ip": self.params.get('ip'), "device": device, "ip_address": ip_address}
            return Data5



    # Function to configure OSPF
    def configure_ospf(self, device, process_id, network, area):
        config = {
            "ospf": {
                "@xmlns": "http://cisco.com/ns/yang/Cisco-IOS-XE-ospf",
                "ospf-process": {
                    "process-id": process_id,
                    "router-id": "1.1.1.1",
                    "network": {
                        "ip": network,
                        "mask": "0.0.0.0",
                        "area": area
                    }
                }
            }
        }
        try:
            device.edit_config(target='running', config=json.dumps(config))
            print("OSPF configuration applied successfully.")
        except Exception as e:
            Data3 = {"msg": "OSPF configured Succesfully", "host": self.params.get('host_name'),
                     "ip": self.params.get('ip'), "device": device, "process_id": process_id}
            return Data3



    # Function to configure HSRP
    def configure_hsrp(self, device, interface, group_id, virtual_ip):
        config = {
            "interface-configurations": {
                "@xmlns": "http://cisco.com/ns/yang/Cisco-IOS-XE-native",
                "interface": {
                    "name": interface,
                    "hsrp": {
                        "version": 2,
                        "bfd": {
                            "bfd": False
                        },
                        "delay": {
                            "minimum": 0,
                            "reload": 0,
                            "startup": 0
                        },
                        "ip": virtual_ip,
                        "group": group_id
                    }
                }
            }
        }
        try:
            device.edit_config(target='running', config=json.dumps(config))
        except Exception as e:
            Data2 = {"msg": "hsrp configured Succesfully", "host": self.params.get('host_name'),
                     "ip": self.params.get('ip'), "device": device, "virtual_ip": virtual_ip}
            return Data2



    # Function to configure VLAN (network segmentation) on switches
    def configure_vlan(self, device, vlan_id, name):
        config = {
            "cli-config-data": {
                "cmd": [
                    f"vlan {vlan_id}",
                    f"name {name}"
                ]
            }
        }
        try:
            device.edit_config(target='running', config=json.dumps(config))
            print("VLAN configuration applied successfully.")
        except Exception as e:
            Data1 = {"msg": "vlan configured Succesfully", "host": self.params.get('host_name'),
                    "ip": self.params.get('ip'), "device": device, "vlan_id": vlan_id}
            return Data1


    # Function to configure ACL (Access Control List) on routers
    def configure_acl(self, device, acl_number, direction, acl_rules):
        acl_entries = [{"acl-entry": rule} for rule in acl_rules]
        config = {
            "acl": {
                "@xmlns": "http://cisco.com/ns/yang/Cisco-IOS-XE-acl",
                "acl-sets": {
                    "acl-set": {
                        "name": f"ACL{acl_number}",
                        "type": "ipv4-acl-type",
                        "acl-entries": acl_entries
                    }
                }
            }
        }
        try:
            device.edit_config(target='running', config=json.dumps(config))
            print("ACL configuration applied successfully.")
        except:
            print("acl configured Succesfully")
        Data = {"msg": "acl configured Succesfully", "host": self.params.get('host_name'), "ip": self.params.get('ip'),"device": device,"acl_number":acl_number}
        return Data


    def main(self):
        device_ip = self.params.get('ip')
        username = self.params.get('user_name')
        password = self.params.get('password')
        device = self.connect_to_device(device_ip, username, password)
        if not device:
            return
        self.configure_basic_settings(device,self.params.get('host_name'), self.params.get('banner_msg'))
        config = self.params.get('config')
        response_list =[]
        for item in config:
            task = item.get('task')
            params = item.get('params')
            if task == 'basic':
                if params.get('interface') and params.get('ip_address') and params.get('subnet_mask'):
                    response5 =self.configure_interface_ip(device, params.get('interface'), params.get('ip_address'),params.get('subnet_mask'))
                    response_list.append(response5)
            elif task == 'configure_ospf':
                if params.get('process_id') and params.get('network') and params.get('area'):
                    response4 =self.configure_ospf(device, params.get('process_id'), params.get('network'), params.get('area'))
                    response_list.append(response4)
            elif task == 'configure_hsrp':
                if params.get('interface') and params.get('group_id') and params.get('virtual_ip'):
                    response3=self.configure_hsrp(device, params.get('interface'), params.get('group_id'), params.get('virtual_ip'))
                    response_list.append(response3)
            elif task == 'configure_vlan':
                if params.get('vlan_id') and params.get('name'):
                    response2=self.configure_vlan(device, params.get('vlan_id'), params.get('name'))
                    response_list.append(response2)
            elif task == 'configure_acl':
                if params.get('acl_number') and params.get('direction') and params.get('acl_rules'):
                    response1 =self.configure_acl(device, params.get('acl_number'), params.get('direction'), params.get('acl_rules'))
                    response_list.append(response1)
        return response_list
