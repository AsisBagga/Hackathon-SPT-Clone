from django.shortcuts import render

# Form Imports
from .forms import ConfigForm, SptForm

# Imports for OV-Python SDK
from pprint import pprint
from hpeOneView.oneview_client import OneViewClient
from hpeOneView.exceptions import HPEOneViewException

# Story line
'''
1. system request the 1st Ov Config details 
2. once successfully connected ask for the SPT name that it wants to clone 
3. after getting all the details of the request SPT, system will show all the details and request for confirmation. 
    User can either select for removal or leave confirm the status. 
4. system will request for 2nd OV Config details
5. creates the SPT as completion. 
'''
def get_spt(oneview_client, config):
    server_profile_name = config.source_SPT_name
    profile_templates = oneview_client.server_profile_templates
    template = oneview_client.server_profile_templates.get_by_name(server_profile_name)
    return template             

def home(request):
    form  = ConfigForm()
    if request.method == "POST":
        form = ConfigForm(request.POST)
        if form.is_valid():
            temp = form.save(commit=False)
            # get instance of the source OneView
            oneview_client = client_connect(temp)
            if oneview_client:
                #spt_data = get_spt(oneview_client, temp)
                spt_data = {'type': 'ServerProfileTemplateV8', 'uri': '/rest/server-profile-templates/38ba61e4-8448-48fb-b5f5-99b9d75184a7', 'name': 'spt_minimal', 'description': '', 'serverProfileDescription': '', 'serverHardwareTypeUri': '/rest/server-hardware-types/8E1C12F6-8B04-4F7B-A9B5-80A7FC621D4E', 'enclosureGroupUri': '/rest/enclosure-groups/d8f1f41e-6bc1-4842-932b-b526ce4f7321', 'affinity': 'Bay', 'hideUnusedFlexNics': True, 'macType': 'Virtual', 'wwnType': 'Virtual', 'serialNumberType': 'Virtual', 'iscsiInitiatorNameType': 'AutoGenerated', 'osDeploymentSettings': None, 'firmware': {'complianceControl': 'Unchecked', 'manageFirmware': False, 'forceInstallFirmware': False}, 'connectionSettings': {'complianceControl': 'CheckedMinimum', 'manageConnections': True, 'connections': []}, 'bootMode': {'complianceControl': 'Checked', 'manageMode': True, 'mode': 'UEFIOptimized', 'pxeBootPolicy': 'Auto', 'secureBoot': 'Unmanaged'}, 'boot': {'complianceControl': 'Checked', 'manageBoot': True, 'order': ['HardDisk']}, 'bios': {'complianceControl': 'Unchecked', 'manageBios': False, 'overriddenSettings': []}, 'managementProcessor': {'complianceControl': 'Unchecked', 'manageMp': False, 'mpSettings': []}, 'localStorage': {'complianceControl': 'Unchecked', 'sasLogicalJBODs': [], 'controllers': []}, 'sanStorage': {'complianceControl': 'Unchecked', 'manageSanStorage': False, 'sanSystemCredentials': [], 'volumeAttachments': []}, 'category': 'server-profile-templates', 'created': '2020-10-16T09:53:25.684Z', 'modified': '2020-10-16T09:53:25.692Z', 'status': 'OK', 'state': None, 'scopesUri': '/rest/scopes/resources/rest/server-profile-templates/38ba61e4-8448-48fb-b5f5-99b9d75184a7', 'eTag': '1602842005692/1', 'refreshState': 'NotRefreshing'}
                #print(spt_data.data)
                return render(request, 'home.html', {'spt_data':spt_data, 'form':form})
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
    #oneview_client = OneViewClient(config)
    oneview_client = True
    if oneview_client:
        return True #oneview_client
    return False
