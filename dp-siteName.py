from __future__ import print_function
from axlAuth import *
from risport70Auth import *
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import ipaddress
import smtplib

devicePool = 'DP-SITENAME' # Enter the name of the device pool being queried.
resp = client.service.executeSQLQuery("""select * from devicepool where devicepool.name = '%s'""" % (devicePool)) # Perfoms query for phones in the specified devicePool variable, filters for devices that start with "SEP".
devicePoolDetail = resp[1]['return']['row'] # Pulls the output from the sql query and prepares it for pulling specific details.
devicePoolPKID = devicePoolDetail[0].pkid # Pulls the PKID of the device pool, needed for the following SQL statement.
devicePoolName = devicePoolDetail[0].name # Stores the cosmetic name of the device pool.  Handy for troubleshooting.
rangeStart = 0 # Used to pull groups of 1000 devices (needed because of AXLAPI throttling).
rangeEnd = 999 # Used to pull groups of 1000 devices (needed because of AXLAPI throttling).
count = 1 # Used for counting listed devices in the IF statement.
totalCountOfDevices = client.service.executeSQLQuery("""select count(*) from device where fkdevicepool='%s' and device.name MATCHES 'SEP*'""" % (devicePoolPKID)) # Number needed to determine how many total devices starting with SEP exist in a given device pool.
totalCountOfDevicesIntTest = totalCountOfDevices[1]['return']['row'] # Iterate through the output of totalCountOfDevices.
totalCountOfDevicesInt = totalCountOfDevicesIntTest[0].count # Yield the number of devices.  This is used in the WHILE statement to determine if the loop should continue relative to the COUNT value.

while count < int(totalCountOfDevicesInt): # Determines how many times the loop should run based on how many total devices are found in count
    resp2 = client.service.executeSQLQuery("""select * from (select skip %s first 1000 * from device where fkdevicepool='%s' and device.name MATCHES 'SEP*' order by pkid asc)""" % (rangeStart, devicePoolPKID)) # Ask the device table for all devices that belong to the devicepool PKID, determined with devicePoolPID, and filter for devices whose names start with "SEP" (phones).  Pull the results in groups of 1000 because of AXLAPI throttling.

    rangeStart += 1000
    rangeEnd += 1000
    phoneDetail = resp2[1]['return']['row'] # Pulls the output from the sql query and prepares it for pulling data.
    phoneDetailLength = len(phoneDetail) # Determines how many items are found in the query.  This is needed for the while loop below.

    #print(phoneDetail)

    x = 0 # Our starting point for the while loop, this will incremenet until it reaches the value of phoneDetailLength.
    while x < phoneDetailLength: # Execute loop until we reach the end of the items in the device pool.
        phoneDetailName = phoneDetail[x].name
        if phoneDetailName.startswith('SEP'): # Check if the item starts with SEP (a phone).  We're only pulling phones in this script.
            phoneDetailName = phoneDetail[x].name
            phoneDetailPKID = phoneDetail[x].pkid
            phoneDetailDescription = phoneDetail[x].description

            # We use the fkcallingsearchspace value from our device information in phoneDetail to get the PKID of the device calling search space.  A device may not have a calling search space (like a Syn-Apps VIP device).  We use an IF statement to determine if a value for phoneDetail[x].fkcallingsearchspace is returned.  If yes, then use it to get the name of the device's calling search space in phoneDetailDeviceCallingSearchSpaceQuery.  If not, then set the variable "phoneDetailDeviceCallingSearchSpaceQuery[1]['return']['row'][0].name = None".

            if phoneDetail[x].fkcallingsearchspace != "":
                phoneDetailDeviceCallingSearchSpaceQuery = client.service.executeSQLQuery("""select * from callingsearchspace where callingsearchspace.pkid = '%s'""" % (phoneDetail[x].fkcallingsearchspace))

                # This IF structure determines if the string pulled from our device pool matches a string pulled from our device's calling search space.  If it doesn't, it will set a variable that will be called upon during the email notification piece.

                #if (devicePool[2]+devicePool[3]+devicePool[4]+devicePool[5]) == (phoneDetailDeviceCallingSearchSpaceQuery[1]['return']['row'][0].name[3]+phoneDetailDeviceCallingSearchSpaceQuery[1]['return']['row'][0].name[4]+phoneDetailDeviceCallingSearchSpaceQuery[1]['return']['row'][0].name[5]+phoneDetailDeviceCallingSearchSpaceQuery[1]['return']['row'][0].name[6]):
                #    pass
                #else:
                #    phoneCallingSearchSpaceMessage = "Phone Device Calling Search Space is incorrect."

            else:
                phoneDetailDeviceCallingSearchSpaceQuery[1]['return']['row'][0].name = None

            # We authenticate to the Risport70 service and request information based on the phoneDetailName variable.
            clientRisport70 = Client(wsdl,location=location, username=username, password=password, plugins=[ImportDoctor(imp)])
            resultRisport70 = clientRisport70.service.SelectCmDevice('',{'SelectBy':'Name', 'Status':'Registered', 'Class':'Phone','SelectItems':{'SelectItem':{'Item':phoneDetailName}}})
            #print(resultRisport70)
            print("Phone PKID " + str(count) +   " = " + phoneDetailPKID)
            print("Phone Name " + str(count) +   " = " + phoneDetailName)
            print("Phone Description " + str(count) +   " = " + phoneDetailDescription)
            if phoneDetailDeviceCallingSearchSpaceQuery[1]['return']['row'][0].name != None:
                print("Phone Device Calling Search Space " + str(count) + " = " + phoneDetailDeviceCallingSearchSpaceQuery[1]['return']['row'][0].name) # Print the device's calling search space.
            else:
                #phoneDetailDeviceCallingSearchSpaceQuery = "None"
                print("Phone Device Calling Search Space = " + str(phoneDetailDeviceCallingSearchSpaceQuery[1]['return']['row'][0].name))

            # We iterate through the resultRisport70 outout for this pass to yield the phone's IP address.  Phones that are not registered will not have an IP, so this IF statment evaluates whether they are registed.  If they are, print the IP address.  If they're not, then print "No Registered".
            if resultRisport70['SelectCmDeviceResult']['CmNodes'] != None:
                for node in resultRisport70['SelectCmDeviceResult']['CmNodes']:
                    for device in node['CmDevices']:
                        print("Phone IP Address " + str(count) +   " = " + device['IpAddress'] + "\n")
                        if ipaddress.ip_address(device['IpAddress']) in ipaddress.ip_network(u'X.X.X.X/24'): # Determine if an IP address is in the acceptable range.

                            # This IF statement verified whether a CSS has been configured on the device at all.  If it does, we can take the value and assugn it to the phoneDetailDeviceCallingSearchSpaceQuery variable for further evaluation.  If a device CSS has not been assigned, we're going to hard code a value of None to phoneDetailDeviceCallingSearchSpaceQueryString.
                            if phoneDetailDeviceCallingSearchSpaceQuery[1]['return']['row'][0].name != None:
                                phoneDetailDeviceCallingSearchSpaceQueryString = phoneDetailDeviceCallingSearchSpaceQuery[1]['return']['row'][0].name[3]+phoneDetailDeviceCallingSearchSpaceQuery[1]['return']['row'][0].name[4]+phoneDetailDeviceCallingSearchSpaceQuery[1]['return']['row'][0].name[5]+phoneDetailDeviceCallingSearchSpaceQuery[1]['return']['row'][0].name[6]
                            else:
                                phoneDetailDeviceCallingSearchSpaceQueryString = None

                            if devicePool[2]+devicePool[3]+devicePool[4]+devicePool[5] == phoneDetailDeviceCallingSearchSpaceQueryString:
                                pass
                            else:
                                if (phoneDetailDescription != "addAnExceptionHereIfNeeded"):
                                    phoneCallingSearchSpaceMessage = "Phone Device Calling Search Space is incorrect."
                                    fromaddr = "sender@address.com"
                                    toaddr = "receiver@address.com"
                                    msg = MIMEMultipart()
                                    msg['From'] = fromaddr
                                    msg['To'] = toaddr
                                    msg['Subject'] = "Telecom Alert - Incorrectly configured phone \"" + phoneDetailDescription + "\" (" +  phoneDetailName + ") at " + device['IpAddress'] + ".  Please correct."
                                    body = "Incorrect calling search space for phone " + phoneDetailName + ".  Phone is in the " + devicePool + " device pool, the device calling search space has been set to " + str(phoneDetailDeviceCallingSearchSpaceQueryString) + "."
                                    msg.attach(MIMEText(body, 'plain'))
                                    server = smtplib.SMTP('mail.domain.com', 25)
                                    server.ehlo()
                                    text = msg.as_string()
                                    server.sendmail(fromaddr, toaddr, text)
                        else:
                            fromaddr = "sender@address.com"
                            toaddr = "receiver@address.com"
                            msg = MIMEMultipart()
                            msg['From'] = fromaddr
                            msg['To'] = toaddr
                            msg['Subject'] = "Telecom Alert - Incorrectly configured phone \"" + phoneDetailDescription + "\" (" +  phoneDetailName + ") at " + device['IpAddress'] + ".  Please correct."
                            body = "Incorrect Device Pool for phone " + phoneDetailName + ".  Please verify that the device pool assignment and calling search space are correct for the phone's subnet."
                            msg.attach(MIMEText(body, 'plain'))
                            server = smtplib.SMTP('mail.domain.com', 25)
                            server.ehlo()
                            text = msg.as_string()
                            server.sendmail(fromaddr, toaddr, text)

            else:
                print("Phone IP Address " + str(count) +   " =  Not Registered \n")
            count += 1
        x += 1
