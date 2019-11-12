#!/usr/bin/python3
import requests
import json

URL = "#removed for security"
TOKEN="#removed for security"
DATA={'default_repository_permission' : 'none', 'members_can_create_repositories' : bool('false'), 'members_allowed_repository_creation_type' : 'none'}
#DATA={'email' : '#removed for security'}
projectName = raw_input("Type in the name of the organization: ")

#Do the stuff
PatchStuff=requests.patch(URL + str(projectName), headers={"Authorization" : TOKEN}, data=json.dumps(DATA))

if PatchStuff.status_code != 200:
    print("Yikes. Failure.")
    print("Error Code:")
    print(PatchStuff.status_code)
    jsonPretty = json.dumps(PatchStuff.json(), indent=4)
    print("Error Data:")
    print(jsonPretty)
else:
    print("Success!")
    jsonPretty = json.dumps(PatchStuff.json(), indent=4)
    print(jsonPretty)