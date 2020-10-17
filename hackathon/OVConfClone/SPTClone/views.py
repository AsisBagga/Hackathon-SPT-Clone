from django.shortcuts import render

# Imports for OV-Python SDK
from pprint import pprint
from hpeOneView.oneview_client import OneViewClient
from hpeOneView.exceptions import HPEOneViewException


# config for OV client 
#config = {
#    "ip": "10.1.19.142",
#    "credentials": {
#        "userName": "Administrator",
#        "password": "asis.local"
#    },
#    "api_version": 2000
#}

# Try load config from a file (if there is a config file)
#config = try_load_from_file(config)

#oneview_client = OneViewClient(config)
#fc_networks = oneview_client.fc_networks

# Get all, with defaults
#print("\nGet all fc-networks")
#fc_nets = fc_networks.get_all()
#pprint(fc_nets)

def get_spt(config):
    server_profile_name = "spt_minimal"
    oneview_client = OneViewClient(config)
    profile_templates = oneview_client.server_profile_templates
    template = oneview_client.server_profile_templates.get_by_name(server_profile_name)
    pprint(template.data)
    return template

def home(request):
    return render(request, 'home.html')

def get_spt_details(request):
    config = {
        "ip": "10.1.19.142",
        "credentials": {
            "userName": "Administrator",
            "password": "asis.local"
        },
        "api_version": 2000
    }
    det = get_spt(config)
    return render(request, 'home.html', {'spt_det': det.data})
