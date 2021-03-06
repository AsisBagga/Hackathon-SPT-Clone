from django.shortcuts import render

# Form Imports
from .forms import ConfigForm, SptForm
from .models import Config, Spt

# Imports for OV-Python SDK
from pprint import pprint
from hpeOneView.oneview_client import OneViewClient
from hpeOneView.exceptions import HPEOneViewException

# Import Json Library
import simplejson as json

# Import Shortcuts
from django.shortcuts import get_object_or_404

# Story line
'''
1. system request the 1st Ov Config details 
2. once successfully connected ask for the SPT name that it wants to clone 
3. after getting all the details of the request SPT, system will show all the details, it will ask for confirmation to clone the network as well, 
a. if user select yes, then it will clone the network while creating SPT 
b. if user select no, then it will ignore the network
4. system will request for 2nd OV Config details
5. creates the SPT as completion. 
'''

def get_spt(oneview_client, config):
    server_profile_name = config.source_SPT_name
    profile_templates = oneview_client.server_profile_templates
    template = oneview_client.server_profile_templates.get_by_name(server_profile_name)
    x, y  = server_hardware_type(oneview_client, template.data['serverHardwareTypeUri'])
    return template.data, x, y  


def server_hardware_type(oneview_client, uri):
    hardware_types = oneview_client.server_hardware_types
    source_hardware_type_by_uri = hardware_types.get_by_uri(uri)
    source_capabilities_list = []
    for i in source_hardware_type_by_uri.data['adapters']:
        for j in i['capabilities']:
            source_capabilities_list.append(j)
    source_server_hardware_model = source_hardware_type_by_uri.data['model']
    return source_server_hardware_model, source_capabilities_list


def home(request):
    form  = ConfigForm()
    if request.method == "POST":
        form = ConfigForm(request.POST)
        if form.is_valid():
            temp = form.save(commit=False)
            # get instance of the source OneView
            oneview_client = client_connect(temp)
            if oneview_client:
                spt_data, source_server_hardware_model, source_capabilities_list = get_spt(oneview_client, temp)
                # spt_data = {'type': 'ServerProfileTemplateV8', 'uri': '/rest/server-profile-templates/38ba61e4-8448-48fb-b5f5-99b9d75184a7', 'name': 'spt_minimal', 'description': '', 'serverProfileDescription': '', 'serverHardwareTypeUri': '/rest/server-hardware-types/8E1C12F6-8B04-4F7B-A9B5-80A7FC621D4E', 'enclosureGroupUri': '/rest/enclosure-groups/d8f1f41e-6bc1-4842-932b-b526ce4f7321', 'affinity': 'Bay', 'hideUnusedFlexNics': True, 'macType': 'Virtual', 'wwnType': 'Virtual', 'serialNumberType': 'Virtual', 'iscsiInitiatorNameType': 'AutoGenerated', 'osDeploymentSettings': None, 'firmware': {'complianceControl': 'Unchecked', 'manageFirmware': False, 'forceInstallFirmware': False}, 'connectionSettings': {'complianceControl': 'CheckedMinimum', 'manageConnections': True, 'connections': []}, 'bootMode': {'complianceControl': 'Checked', 'manageMode': True, 'mode': 'UEFIOptimized', 'pxeBootPolicy': 'Auto', 'secureBoot': 'Unmanaged'}, 'boot': {'complianceControl': 'Checked', 'manageBoot': True, 'order': ['HardDisk']}, 'bios': {'complianceControl': 'Unchecked', 'manageBios': False, 'overriddenSettings': []}, 'managementProcessor': {'complianceControl': 'Unchecked', 'manageMp': False, 'mpSettings': []}, 'localStorage': {'complianceControl': 'Unchecked', 'sasLogicalJBODs': [], 'controllers': []}, 'sanStorage': {'complianceControl': 'Unchecked', 'manageSanStorage': False, 'sanSystemCredentials': [], 'volumeAttachments': []}, 'category': 'server-profile-templates', 'created': '2020-10-16T09:53:25.684Z', 'modified': '2020-10-16T09:53:25.692Z', 'status': 'OK', 'state': None, 'scopesUri': '/rest/scopes/resources/rest/server-profile-templates/38ba61e4-8448-48fb-b5f5-99b9d75184a7', 'eTag': '1602842005692/1', 'refreshState': 'NotRefreshing'}
                destination_form =  ConfigForm()
                temp.save()
                temp_data = {'spt_data': spt_data, 'source_server_hardware_model': source_server_hardware_model,'source_capabilities_list': source_capabilities_list}
                json_data = json.dumps(temp_data)
                SPT_DB = Spt(spt_data = json_data, ov_name = temp)
                SPT_DB.save()
                jsonDec = json.decoder.JSONDecoder()
                SPT_data = jsonDec.decode(SPT_DB.spt_data)
                return render(request, 'home.html', { 'form':form,  'SPT': SPT_data, 'SPT_query':SPT_DB })
            else:
                # if connection fails
                return render(request, 'home.html', {'no_connection_response':f'OneView {temp.ip} is not reachable'})
    return render(request, 'home.html', {'form':form})

def client_connect(form):
    config = {
        "ip": form.ip,
        "credentials": {
            "userName": form.user_name,
            "password": form.password,
        },
        "api_version": form.api_version
    }
    oneview_client = OneViewClient(config)
   # oneview_client = True
    if oneview_client:
        return oneview_client #True
    return False

def destination_home(request, pk):
    SPT_DB = get_object_or_404(Spt, pk=pk)
    form  = ConfigForm()
    if request.method == "POST":
        form = ConfigForm(request.POST)
        if form.is_valid():
            temp = form.save(commit=False)
            # get instance of the source OneView
            oneview_client = client_connect(temp)
            if oneview_client:
                # Initializing resources
                profile_templates = oneview_client.server_profile_templates
                hardware_types = oneview_client.server_hardware_types
                enclosure_groups = oneview_client.enclosure_groups
                # Fetching Enclosure Group
                enclosure_group = enclosure_groups.get_by_name("EG")
                # Creating Json payload for cloning SP to destination OV
                template_data = dict()
                jsonDec = json.decoder.JSONDecoder()
                SPT_data = jsonDec.decode(SPT_DB.spt_data)
                pprint(SPT_data)
                template_data['bios'] = SPT_data['spt_data']['bios']
                template_data['boot'] = SPT_data['spt_data']['boot']
                template_data['bootMode'] = SPT_data['spt_data']['bootMode']
                template_data['name'] = SPT_data['spt_data']['name']
                # Extracting hardware types from destination OV
                destination_hardware_types_all = hardware_types.get_all()
                server_hardware_type_uri = find_hardware_type(destination_hardware_types_all, SPT_data['source_server_hardware_model'], SPT_data['source_capabilities_list'])
                if server_hardware_type_uri:
                    template_data['serverHardwareTypeUri'] =  server_hardware_type_uri
                    # EG needs to be customizable, leaving aside for now
                    template_data['enclosureGroupUri'] = enclosure_group.data['uri']
                    template = profile_templates.create(template_data)
                    return render(request, 'dest_home.html', {'msg': 'Sever Profile Template Cloned Successfully', 'template': template.data})
                else:
                    return render(request, 'dest_home.html', {'msg': 'Cloning Failed', 'template_fail': template})
            else:
                # if connection fails
                return render(request, 'home.html', {'no_connection_response':f'OneView {temp.ip} is not reachable'})
    return render(request, 'dest_home.html', {'form':form})

#checks if minimum requirement is fullfilled or not
def compare(destination_capabilities_list, source_capabilities_list):
    for i in source_capabilities_list:
        if i in destination_capabilities_list:
            continue
        else:
            destination_capabilities_list = []
            return False
    return True

# returns either the destination server hardware type uri which fulfils min requirements or False
def find_hardware_type(destination_hardware_types_all, source_server_hardware_model, source_capabilities_list):
    for dest_hardware_type in destination_hardware_types_all:
        # Checks if destination model and source model matches
        destination_capabilities_list = []
        if dest_hardware_type['model'] == source_server_hardware_model:
            # Fetching capabilities for this model
            for adapter in dest_hardware_type['adapters']:
                # Creating destination capability list for all adapter in this model
                for capability in adapter['capabilities']:
                    destination_capabilities_list.append(capability)
            #checks if minimum requirement is fullfilled or not
            result = compare(destination_capabilities_list, source_capabilities_list)
            print(result)
            if result:
                return dest_hardware_type['uri']
    return False
