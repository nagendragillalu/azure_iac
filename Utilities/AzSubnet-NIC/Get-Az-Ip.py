from azure.identity import InteractiveBrowserCredential
from azure.mgmt.network import NetworkManagementClient
from netaddr import IPNetwork, IPAddress
import argparse


# Azure authentication details
subscription_id = 'ac351f40-7fd1-4017-b05c-af8d13a0c13a'

# Function to authenticate with Azure and get Azure management client
def get_azure_client():
    credential = InteractiveBrowserCredential()
    client = NetworkManagementClient(credential, subscription_id)
    return client

# Function to get the subnet that contains the specified IP address
def get_subnet_by_ip(client, ip_address):
    vnets_all = client.virtual_networks.list_all()
    for vnet in vnets_all:
        for subnet in vnet.subnets:
            if IPAddress(ip_address) in IPNetwork(subnet.address_prefix):
                return subnet

    return None


# Get NIC using the given IP address, returns none if no NIC is used
def get_nic_in_use(client,subnet,ip_address):
    nics = client.network_interfaces.list_all() 
    for nic in nics:
        if nic.ip_configurations and nic.ip_configurations[0].subnet and nic.ip_configurations[0].subnet.id == subnet.id and nic.ip_configurations[0].private_ip_address == ip_address:
            return nic
    return None

def main():
    parser = argparse.ArgumentParser(description='Azure CLI Tool to get IP subnet details and any attched NIC')
    parser.add_argument('ip_address', help='IP address')
    args = parser.parse_args()

    client = get_azure_client()
    subnet = get_subnet_by_ip(client, args.ip_address)
    print(f"Subnet name:\t{subnet.name}")
    print(f"IPv4 Addr Prefix:\t{subnet.address_prefix}")
    print(f"Subnet ID:\t{subnet.id}")

    resource_nic = get_nic_in_use(client,subnet,args.ip_address)
    if resource_nic:
        print(f"NIC name:\t{resource_nic.name}")
        print(f"NIC ID:\t{resource_nic.id}")
    else:
        print('No NICs or resources are currently using this subnet.')

if __name__ == '__main__':
    main()
