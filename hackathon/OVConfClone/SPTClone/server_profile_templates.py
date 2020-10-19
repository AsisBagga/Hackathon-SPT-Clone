# -*- coding: utf-8 -*-
###
# (C) Copyright [2020] Hewlett Packard Enterprise Development LP
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
###

from pprint import pprint
from hpeOneView.oneview_client import OneViewClient
from config_loader import try_load_from_file

config_Ov1 = {
    "ip": "10.1.19.142",
    "credentials": {
        "userName": "Administrator",
        "password": "asis.local"
    },
    "api_version": 2000
}
config_Ov2 = {
    "ip": "10.1.19.63",
    "credentials": {
        "userName": "Administrator",
        "password": "admin123"
    },
    "api_version": 2000
}

# Try load config from a file (if there is a config file)
#config = try_load_from_file(config)
oneview_client = OneViewClient(config_Ov1)
#oneview_client2 = OneViewClient(config_Ov2)
profile_templates = oneview_client.server_profile_templates
#profile_templates2 = oneview_client2.server_profile_templates
# Dependency resources
#hardware_types = oneview_client.server_hardware_types
#hardware_types2 = oneview_client2.server_hardware_types
#enclosure_groups2 = oneview_client2.enclosure_groups

# These variables must be defined according with your environment
#enclosure_group_name = "EG"

#hardware_type = hardware_types.get_by_name(hardware_type_name)
#enclosure_group = enclosure_groups2.get_by_name(enclosure_group_name)

print("\nGet a server profile templates by name 'spt_minimal' ")
template = oneview_client.server_profile_templates.get_by_name("SPT-Con")
#pprint(template.data)
#connectionSettings
template_data = dict()
template_data['bios']= template.data['bios']
template_data['boot']= template.data['boot'] 
template_data['bootMode']= template.data['bootMode']
template_data['name']= template.data['name']+"copy"
template_data['serverHardwareTypeUri'] = template.data['serverHardwareTypeUri']
template_data['enclosureGroupUri'] = template.data['enclosureGroupUri']

#template_data['Length-connectionSettings']= len(template.data['connectionSettings']['connections'])
network_list = []
fc_networks=None
ethernet_networks=None
#Fetching all network Uris from source oneview
for i in template.data['connectionSettings']['connections']:
    if 'fc-network' in i['networkUri']:
        # Creating FC Network in Destination OV one by one
        if not fc_networks:
            fc_networks = oneview_client.fc_networks
        net = fc_networks.get_by_uri(i['networkUri']).data
        options = {'fabricType': net['fabricType'], 
                   'autoLoginRedistribution': net['autoLoginRedistribution'], 
                   'linkStabilityTime': net['linkStabilityTime'],
                   'managedSanUri': net['managedSanUri'],
                   'name': net['name']+"copy",
                   'connectionTemplateUri': None 
                  }
        new_fc = fc_networks.create(options)
        # Creating list of all these newly created URIs
        network_list.append(new_fc.data['uri'])
        i['networkUri'] = new_fc.data['uri']
    elif 'ethernet-network' in i['networkUri']:
        if not ethernet_networks:
            ethernet_networks = oneview_client.ethernet_networks
        net = ethernet_networks.get_by_uri(i['networkUri']).data
        # For now we dont have subnet URI
        options = {
                    'description': net['description'],
                    'ethernetNetworkType': net['ethernetNetworkType'],
                    #'ipv6SubnetUri': net['ethernetNetworkType'],
                    'name': net['name']+"copy",
                    'privateNetwork': net['privateNetwork'],
                    'purpose': net['purpose'],
                    'smartLink': net['smartLink'],
                    'type': net['type'],
                    'vlanId': net['vlanId']
                  }
        new_eth = ethernet_networks.create(options)
        network_list.append(new_eth.data['uri'])
        i['networkUri'] = new_eth.data['uri']
pprint(network_list)
template_data['connectionSettings'] = template.data['connectionSettings']
templates = profile_templates.create(template_data)
pprint(templates.data)

'''
# Get all
print("\nGet list of all server profile templates")
all_templates = profile_templates.get_all()
for template in all_templates:
    print('  %s' % template['name'])

# Get Server Profile Template by scope_uris
if oneview_client.api_version >= 600:
    server_profile_templates_by_scope_uris = profile_templates.get_all(
        scope_uris="\"'/rest/scopes/3bb0c754-fd38-45af-be8a-4d4419de06e9'\"")
    if len(server_profile_templates_by_scope_uris) > 0:
        print("Found %d Server profile Templates" % (len(server_profile_templates_by_scope_uris)))
        i = 0
        while i < len(server_profile_templates_by_scope_uris):
            print("Found Server Profile Template by scope_uris: '%s'.\n  uri = '%s'" % (server_profile_templates_by_scope_uris[i]['name'],
                                                                                        server_profile_templates_by_scope_uris[i]['uri']))
            i += 1
        pprint(server_profile_templates_by_scope_uris)
    else:
        print("No Server Profile Template found.")

# Get by property
print("\nGet a list of server profile templates that matches the specified macType")
if all_templates[1]:
    template_mac_type = all_templates[1]["macType"]
    templates = profile_templates.get_by('macType', template_mac_type)
    for template in templates:
        print('  %s' % template['name'])

# Get available networks
print("\nGet available networks")
available_networks = profile_templates.get_available_networks(enclosureGroupUri=enclosure_group.data["uri"],
                                                              serverHardwareTypeUri=hardware_type.data["uri"])
print(available_networks)
'''
'''
# Get SPT by name
print("\nGet a server profile templates by name 'spt_minimal' ")
template = oneview_client.server_profile_templates.get_by_name("spt_minimal")

template_data = dict()
template_data['bios']= template.data['bios']
template_data['boot']= template.data['boot'] 
template_data['bootMode']= template.data['bootMode']
template_data['name']= template.data['name']+"copy"

# Getting Server Hardware Type URI
source_hardware_type_by_uri = hardware_types.get_by_uri(template.data['serverHardwareTypeUri'])
source_capabilities_list = []
for i in source_hardware_type_by_uri.data['adapters']:
    for j in i['capabilities']: 
        source_capabilities_list.append(j)

destination_hardware_types_all = hardware_types2.get_all()
destination_capabilities_list = []

#checks if minimum requirement is fullfilled or not
def compare(destination_capabilities_list):
    for i in source_capabilities_list:
        if i in destination_capabilities_list:
            continue
        else:
            destination_capabilities_list = []
            return False
    return True

def find_hardware_type(destination_hardware_types_all):
    for dest_hardware_type in destination_hardware_types_all:
        # Checks if destination model and source model matches
        destination_capabilities_list = []
        if dest_hardware_type['model'] == source_hardware_type_by_uri.data['model']:
            # Fetching capabilities for this model
            for adapter in dest_hardware_type['adapters']:
                # Creating destination capability list for all adapter in this model
                for capability in adapter['capabilities']:
                    destination_capabilities_list.append(capability)
            #checks if minimum requirement is fullfilled or not
            result = compare(destination_capabilities_list)
            print(result)
            if result:
                return dest_hardware_type['uri']
    return False

server_hardware_type_uri = find_hardware_type(destination_hardware_types_all)
if not server_hardware_type_uri:
    print('No Matching server hardware found.')
template_data['serverHardwareTypeUri'] =  server_hardware_type_uri
template_data['enclosureGroupUri'] = enclosure_group.data['uri']

# Create a server profile template
print("Create a basic connection-less server profile template ")
#basic_template_options = dict(
#    name=server_profile_name,
#    serverHardwareTypeUri=hardware_type.data["uri"],
#    enclosureGroupUri=enclosure_group.data["uri"]
#)
template = profile_templates2.create(template_data)
pprint(template.data)
'''
'''
# Update bootMode from recently created template
print("\nUpdate bootMode from recently created template")
if template:
    template_to_update = template.data.copy()
    template_to_update["bootMode"] = dict(manageMode=True, mode="BIOS")
    template.update(template_to_update)
    pprint(template.data)

# Get new profile
print("\nGet new profile")
if template:
    profile = template.get_new_profile()
    pprint(profile)

if oneview_client.api_version >= 300 and template:
    # Get server profile template transformation
    print("\nGet a server profile template transformation")
    hardware = hardware_types.get_by_name(hardware_type_for_transformation)
    enclosure_group = enclosure_groups.get_by_name(enclosure_group_for_transformation)

    transformation = template.get_transformation(hardware.data["uri"],
                                                 enclosure_group.data["uri"])
    pprint(transformation)

# Delete the created template
print("\nDelete the created template")
if template:
    template.delete()
    print("The template was successfully deleted.")
'''
