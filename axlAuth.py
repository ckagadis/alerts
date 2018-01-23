from __future__ import print_function
import ssl
import time
from suds.xsd.doctor import Import, ImportDoctor
import requests
import urllib3
import os
from suds.client import Client

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
requests.packages.urllib3.disable_warnings()

path = os.path.dirname(os.path.abspath(__file__))
username = 'usernameString'
password = 'passwordString'
wsdl = 'file:' + path + '/schema/current/AXLAPI.wsdl'
url = 'https://ipAddress:8443/axl/'
tns = 'http://schemas.cisco.com/ast/soap/'
imp = Import('http://schemas.xmlsoap.org/soap/encoding/','http://schemas.xmlsoap.org/soap/encoding/')
imp.filter.add(tns)
requests.get(url, verify=False,auth=(username,password))
client = Client(wsdl,location=url,faults=False,plugins=[ImportDoctor(imp)],username=username,password=password)

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    # Legacy Python that doesn't verify HTTPS certificates by default
    pass
else:
    # Handle target environment that doesn't support HTTPS verification
    ssl._create_default_https_context = _create_unverified_https_context
