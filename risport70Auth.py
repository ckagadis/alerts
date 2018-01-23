from suds.xsd.doctor import Import
from suds.xsd.doctor import ImportDoctor
from suds.client import Client
import ssl

cmserver = 'X.X.X.X'
cmport = '8443'
wsdl = 'https://cmserver:8443/realtimeservice/services/RisPort?wsdl'
location = 'https://' + cmserver + ':' + cmport + '/realtimeservice/services/RisPort'
username = 'usernameString'
password = 'passwordString'
tns = 'http://schemas.cisco.com/ast/soap/'
imp = Import('http://schemas.xmlsoap.org/soap/encoding/', 'http://schemas.xmlsoap.org/soap/encoding/')
imp.filter.add(tns)

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    # Legacy Python that doesn't verify HTTPS certificates by default
    pass
else:
    # Handle target environment that doesn't support HTTPS verification
    ssl._create_default_https_context = _create_unverified_https_context
