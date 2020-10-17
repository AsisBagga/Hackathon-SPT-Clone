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
def get_spt(config):
    server_profile_name = "spt_minimal"
    oneview_client = OneViewClient(config)
    profile_templates = oneview_client.server_profile_templates
    template = oneview_client.server_profile_templates.get_by_name(server_profile_name)
    pprint(template.data)
    return template

def home(request):
    form  = ConfigForm()
    if request.method == "POST":
        form = ConfigForm(request.POST)
        if form.is_valid():
            temp = form.save(commit=False)
            get_spt_details(temp)
    return render(request, 'home.html', {'form':form})

def get_spt_details(form):
    print("form => ",form.ov_name, " and ",form.ip)
    config = {
        "ip": form.ip,
        "credentials": {
            "userName": form.user_name,
            "password": form.password,
        },
        "api_version": form.api_version
    }
    print("\n",config)
    #det = get_spt(config)
    return True# {'spt_det': det.data})
