#!/usr/bin/python

import requests
import json
import getpass
import traceback
import sys
import os

def securityCenterLogin():
	un=raw_input("Please input your SecurityCenter username:")
	pw=getpass.getpass("Please enter you SecurityCenter password:")
	sessionRelease = bool("false")
	tokenUrl = "#removed for security"
	data={'username' : un, 
	      'password' : pw,
	      'sessionRelease' : sessionRelease}

	print ("Logging in...")
	try:
		s = requests.session()
		response = s.post(tokenUrl, data=json.dumps(data))	
		if response.status_code is not 200:
			print ("ERROR: Failed to log in! HTTP Error: " + str(response.status_code))
		else:
			print ("Login successful!")
	except: 
		print ("Lol, some crazy !@#$ happened while trying to log in. Check out the traceback:")
		print(sys.exc_info()[0])
		raise

	loginData = response.json()
	loginToken = loginData['response']['token']
	cookieJar = response.cookies
	sessionID = cookieJar.get('TNS_SESSIONID')
	return loginToken, sessionID

def getSCAssets(token, sessionid):	
	try:	
		
		jsonFileName = ("jsonFile.txt")
		if os.path.exists(jsonFileName):
			print ("Removing previous JSON file: " + jsonFileName + "!")
			removePrevious = os.remove(jsonFileName)
		
		print ("Trying to fetch assets...")
		assetUrl = "#removed for security"
		sessionIDFormatted = "TNS_SESSIONID=" + sessionid
		headersPayload = {'X-SecurityCenter' : str(token),
				  'Cookie' : sessionIDFormatted}
		#queryData = '{"type" : "vuln"}'
		response = requests.get(assetUrl, headers=headersPayload)
	
		jsonFile = open(jsonFileName, "w")
		jsonResponse = response.json()
		jsonPretty = json.dumps(jsonResponse, indent=4)
		jsonFile.write(jsonPretty)
		print ("JSON data stored in " + jsonFileName + "!")

	#	if response.status_code is not 200:
	#		print ("ERROR: Failed to fetch asset list! HTTP Error code: " + str(response.status_code))
	#		jsonResponse = response.json()
	#		specificResponse = jsonResponse['error_msg']
	#		print ("ERROR MESSAGE: " + specificResponse)
	except :
		print ("Lol, some crazy !@#$ happened while trying to fetch assets. Check out the traceback:")
		print(sys.exc_info()[0])
		raise

returnValue = securityCenterLogin()
loginToken = returnValue[0]
sessionID = returnValue[1]
getSCAssets(loginToken, sessionID)
