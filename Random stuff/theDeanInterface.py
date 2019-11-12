#!/usr/bin/python

import requests
import json
import getpass
import sys
import os

#V1.0
#Author: Andrew Hill, DATE

print("This is a script to make changes to a tool.")
fileName = raw_input("First, let's create a name for the file we'll store data in (this is for JSON responses, etc.): ")

#################################################################################################################################################################
######################################                           ALWAYS RUN                                       ###############################################
#################################################################################################################################################################
def deanGetToken():
        un = raw_input("Now, please enter your LDAP username: ")
        pw = getpass.getpass("And now please enter you LDAP password: ")
        headers = {'Content-Type' : 'application/json'}
        data = '{"username" : "'+un+'", "password" : "'+pw+'"}'

        print("Logging you in...")

        #Try Catch's are my best friend. I hope they're yours too. Because when all the things break on their end, nothing actually breaks.
        try:
                #Get a response from the API using the GET request, and providing your log in information in the header.
                response = requests.post('#removed for security', headers=headers, data=data)
                #Check the response code of your request. If it's not 200... it's not what we want.
                if response.status_code is not 200:
                        print("ERROR: Failed to retrieve data! HTTP Error: " + str(response.status_code))
                #Check if the response is... essentially... null. If it is, there are no public projects in the GitLab.
                elif response.json() == 500:
                        print("You have typed in invalid credentials! Try again!")
                #Otherwise, everything is awesome.
                else:
                        print("Log in success!")
        except:
                #Everything is not awesome. Something else occured.
                print("Lol, some crazy !@#$ happened while trying to either get the JSON data, or upload the new visibility level.. Check out the traceback:")
                print(sys.exc_info()[0])
                raise
        responseData = response.json()
        deanToken = responseData['value']
	print(deanToken)
        return deanToken

def deanGetALLUsersInfo(token):
        headers = {'Content-Type': 'application/json',}
        data = '{"token":"'+token+'"}'
        try:
                #Get a response from The Dean API using the GET request.
                response = requests.post('#removed for security', headers=headers, data=data)
                #Check the response code of your request. If it's not 200... it's not what we want.
                if response.status_code is not 200:
                        print("ERROR: Failed to retrieve data! HTTP Error: " + str(response.status_code))
                #Otherwise, everything is awesome.
                else:
                        response = response.json()
                        jsonFile = open(fileName, "w")
                        jsonPretty = json.dumps(response, indent=4)
                        jsonFile.write(jsonPretty)
                        
        except:
                #Everything is not awesome. Something else occured.
                print("Lol, some crazy !@#$ happened while trying to either get the JSON data, or upload the new visibility level.. Check out the traceback:")
                print(sys.exc_info()[0])
                raise
#################################################################################################################################################################
######################################                          RUNS DEPENDING ON INPUT                           ###############################################
#################################################################################################################################################################

def getUserID(userName):
        found = False
        try:
                with open(fileName, "rb") as fileIn:
                        content = json.load(fileIn)
                with open("stringJson.txt", "wb") as fileOut:
                        json.dump(content, fileOut, indent=4)
                for i in content:
                        if userName == i['name']:
                                userID = str(i['id'])
                                print("")
                                print("The user ID of " + userName + " is: " + userID)
                                found = True
                                return userID
                                break
                if found == False:
                        print("")
                        print("That is not a valid name. Try again.")
        except:
                print("Something went wrong. Traceback:")
                print(sys.exc_info())

def deanGetUserInfo(token, userID):
        headers = {'Content-Type': 'application/json',}
        data = '{"token":"'+token+'"}'
        try:
                print("\n Getting user info...")
                #Get a response from The Dean API using the GET request.
                response = requests.post('#removed for security'+userID+'', headers=headers, data=data)
                #Check the response code of your request. If it's not 200... it's not what we want.
                if response.status_code is not 200:
                        print("ERROR: Failed to retrieve data! HTTP Error: " + str(response.status_code))
                #Otherwise, everything is awesome.
                else:
                        print("Here is the info for your user!")
        except:
                #Everything is not awesome. Something else occured.
                print("Lol, some crazy !@#$ happened while trying to either get the JSON data, or upload the new visibility level.. Check out the traceback:")
                print(sys.exc_info()[0])
                raise
        userInfo = response.json()
        userInfoPretty = json.dumps(userInfo, indent=4)
        print(userInfoPretty)

def deanAddUserRole(token, userID, roleName):
        headers = {'Content-Type': 'application/json',}
        data = '{"token" : "'+token+'"}'
        try:
                #Get a response from The Dean API using the GET request.
                response = requests.patch('#removed for security'+userID+'/role/'+roleName, headers=headers, data=data)
                #Check the response code of your request. If it's not 200... it's not what we want.
                if response.status_code is not 200:
                        print("ERROR: Failed to retrieve data! HTTP Error: " + str(response.status_code))
                #Otherwise, everything is awesome.
                else:
                        print("Role Change Success!")
        except:
                #Everything is not awesome. Something else occured.
                print("Lol, some crazy !@#$ happened while trying to either get the JSON data, or upload the new visibility level.. Check out the traceback:")
                print(sys.exc_info()[0])
                raise

#def deanAddUserTeam():

#def deanAddUserHomeTeam():

token = deanGetToken()
deanGetALLUsersInfo(token)
ans = True
while ans:
        print ("""
        MENU:
        1. Get User ID From Users Full Name (i.e. John Smith)
        2. Get Single User Info Using ID
        3. Add User Role Using ID
        4. Exit/Quit
        """)
        ans = raw_input("\nWhat would you like to do? ") 
        if ans == "1": 
                userName = raw_input("Input the users first and last name (i.e. John Smith), or LDAP username. This IS case sensitive: ")
                getUserID(userName)       
        elif ans == "2":
                userID = raw_input("Enter the user ID: ")
                deanGetUserInfo(token, userID)
        elif ans == "3":
                userID = raw_input("Enter the user ID:")
                roleName = raw_input("Enter the role name (i.e. 'THE_DEAN'):")
                deanAddUserRole(token, userID, roleName)
        elif ans == "4":
                if os.path.isfile(fileName):
                        os.remove(fileName)
                if os.path.isfile("stringJson.txt"):
                        os.remove("stringJson.txt")
                print("\n Goodbye!") 
                ans = False
        else:
                print("\n Not a valid choice. Try again.")
