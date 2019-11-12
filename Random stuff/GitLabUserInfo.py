import requests
import json
import sys
import getpass

#V1.0
#Author: Andrew Hill, 08/13/2018

# Function to retrieve json data from GitLab
def gitLabRetrieve():
	userID = raw_input("Please enter a user ID (You should be able to find this in the tool... I think?): ")
	privateToken = getpass.getpass("Now enter your GitLab private token: ")
        print("Getting JSON response from GitLab repos...")
        #Try Catch's are my best friend. I hope they're yours too. Because when all the things break on their end, nothing actually breaks.
        try:
                #Get a response from GitLabs API using the GET request, and providing your log in information in the header.
                response = requests.get('#removed for security' + userID, headers={"PRIVATE-TOKEN" : str(privateToken)})
                #Check the response code of your request. If it's not 200... it's not what we want.
                if response.status_code is not 200:
                        print("ERROR: Failed to retrieve data! HTTP Error: " + str(response.status_code))
                #Check if the response is... essentially... null. If it is, there are is no user with that ID.
                elif response.json() == []:
                        print("That user doesn't seem to exist!")
                #Otherwise, everything is awesome.
                else:
                        print("Retrieved!")
			print("")
                        garbageJson = response.json()
			prettyJson = json.dumps(garbageJson, indent=4)
			print(prettyJson)
			return response
        except:
                #Everything is not awesome. Something else occured.
                print("Lol, some crazy !@#$ happened while trying to either get the JSON data, or upload the new visibility level.. Check out the traceback:")
                print(sys.exc_info()[0])
                raise

gitLabRetrieve()
