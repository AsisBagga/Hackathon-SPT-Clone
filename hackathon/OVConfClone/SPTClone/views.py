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
                spt_data = get_spt(oneview_client, temp)
                print(spt_data.data)
                return render(request, 'home.html', {'spt_data':spt_data.data, 'form':form})
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
    if oneview_client:
        return oneview_client
    return False
