import requests
import json
import sys

#V1.0
#Author: Andrew Hill, 08/13/2018

# Function to retrieve json data from GitLab
def gitLabRetrieve():
    print("Getting JSON response from GitLab repos...")
    privateToken = raw_input("Please input your private token: ")
	#Try Catch's are my best friend. I hope they're yours too. Because when all the things break on their end, nothing actually breaks.
	try:
		#Get a response from GitLabs API using the GET request, and providing your log in information in the header. 
		response = requests.get('#removed for security', headers={"PRIVATE-TOKEN" : str(privateToken)})	
		#Check the response code of your request. If it's not 200... it's not what we want.
		if response.status_code is not 200:
                        print("ERROR: Failed to retrieve data! HTTP Error: " + str(response.status_code))
		#Check if the response is... essentially... null. If it is, there are no public projects in the GitLab. 
		elif response.json() == []:
			print("There are no public projects left!")
		#Otherwise, everything is awesome.
                else:
			print("Retrieved JSON Data!")
		return response
	except:
		#Everything is not awesome. Something else occured. 
                print("Lol, some crazy !@#$ happened while trying to either get the JSON data, or upload the new visibility level.. Check out the traceback:")
                print(sys.exc_info()[0])
                raise
				
# Function to change the permissions Takes the resulting JSON raw data from the previous function as a parameter. 
def changeGitRepoPermissions(jsonResponse):
        privateToken = raw_input("Please input your private token: ")
	print("Changing public projects to internal...")
	#Takes the JSON data from the previous function and converts it into a proper JSON format. 
	jsonData = jsonResponse.json()
	#Loops through the entries in the JSON list and searches for the project ID, Name, and what the visibility/permission is. 
	for item in jsonData:
		projectID = item['id']
		name = item['name']
		visibility = item['visibility']
		#Sends a PUT request to the server telling it to alter the visibility state to your new one. 
		valueEdit = requests.put('#removed for security' + str(projectID) + '?visibility=internal', headers={"PRIVATE-TOKEN" : str(privateToken)})
		print("Project ID: " + str(projectID) + "; Project Name: " + name + ".")
		
#Runs the stuff. 
jsonResponse = gitLabRetrieve()
changeGitRepoPermissions(jsonResponse)
