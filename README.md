Author's Note:
--------------
BEFORE USING ANY CODE IN THESE SCRIPTS, READ THROUGH ALL FILES THOROUGHLY, UNDERSTAND WHAT THE SCRIPTS ARE DOING AND TEST THEIR BEHAVIOR IN AN ISOLATED ENVIRONMENT.  RESEARCH ANY POTENTIAL BUGS IN THE VERSION OF THE SOFTWARE YOU ARE USING THESE SCRIPTS WITH AND UNDERSTAND THAT FEATURE SETS OFTEN CHANGE FROM VERSION TO VERSION OF ANY PLATFORM WHICH MAY DEPRECATE CERTAIN PARTS OF THIS CODE.  ANY INDIVIDUAL CHARGED WITH RESPONSIBILITY IN THE MANAGEMENT OF A SYSTEM RUNS THE RISK OF CAUSING SERVICE DISRUPTIONS AND/OR DATA LOSS WHEN THEY MAKE ANY CHANGES AND SHOULD TAKE THIS DUTY SERIOUSLY AND ALWAYS USE CAUTION.  THIS CODE IS PROVIDED WITHOUT ANY WARRANTY WHATSOEVER AND IS INTENDED FOR EDUCATIONAL PURPOSES.  

Cisco Unified Communications Manager Phone Audit Scripts (for Python)
=======================================================
These scripts were written to address certain challenges in managing Cisco phones in a Cisco Unified Communications (CUCM) environment.  

Corporate policies for moving phones (or endpoints) on a corporate network can vary widely from organization to organization.  Some are quite strict; moving a phone from one network to another outside of a formal process can be subject to disciplinary action.  Many, however, are lax.  Cisco's unified communications platform can accommodate any of these situations.

There are substantial challenges in keeping CUCM endpoints organized.  For instance, 911 emergency dialing is often different for each remote site in a corporate network.  If a user moves their endpoint from site A to site B without notifying corporate telecom, this can lead to the incorrect routing of an emergency call.  There are products for CUCM in the market that will automatically adjust phone settings when they are moved, but an organization may choose not to use them because of cost or unmet technical prerequisites.  The Cisco AXL API allows administrators and developers to interface with CUCM to solve problems like these.  

These scripts were written for CUCM networks that are configured for layer 3 to the site (meaning that each site's phones will be on their own unique local subnet - a common practice).  We are also assuming another common practice that each site's phones are in device pools organized by site.  Finally, the naming convention for each site's calling search spaces share similarities with their respective device pools.  So, for example;

Site A's device pool:
  * "DP-SiteA"

Site A's calling search spaces:
  * "CSS-SiteA-LOCAL"
  * "CSS-SiteA-LONGDISTANCE"
  * "CSS-SiteA-INTERNATIONAL"

Here, the common string between the device pool and the respective calling search spaces is "-SiteA".  This kind of consistency in naming is also a fairly common practice as it helps administrators keep track of these settings on a per-site basis.

When the devicePoolQuery file is run, it will query CUCM for all devices in a specified device pool and retrieve the IP address for each phone.  It will verify that each phone is within the first and last host for that subnet as configured in that script.  It then checks the calling search space on the device and its respective line(s) to see if it/they share the same common string as its device pool.  If any misconfiguration is found, the script will use its server's local MTA (this has been tested with Sendmail, but of course any should work) to send a notification email to the specified recipients.  These scripts can be run as a cron job or from a web browser (which will provide a complete inventory of a device pool's phones).

NOTE:  At the time of this writing, Cisco is planning to deprecate the RPC form of soap in its AXL API in CUCM 11.0.  This is why there are two versions of the devicePoolQuery file - each has been written for their respective formats.  For more infomation on Cisco's WSDLs, please visit http://solutionpartnerdashboard.cisco.com/web/sxml-developer/get-wsdl  

Tested on:
----------
* Python 3
* CUCM 10.5
* Cisco AXL Toolkit (specifically, the AXLAPI.wsdl file)
* An application user account on CUCM with the following privileges
  * Standard AXL API access
  * Standard CCM Admin Users
  * Standard CCMADMIN Read Only
  * Standard Serviceability Read Only
