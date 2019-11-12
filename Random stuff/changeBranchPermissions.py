#!/usr/bin/env python3

import requests
import base64
import getpass
import sys
import json
import datetime
from os.path import join

#curl -H "Authorization: Basic #removedForSecurity#" YOUR-URL

un = input("Input your BitBucket username: ")
pw = getpass.getpass("Input your BitBucket password: ")
data = (str(un) + ":" + str(pw))
urlSafeEncodedBytes = base64.urlsafe_b64encode(data.encode("utf-8"))
base64Key = "Basic " + urlSafeEncodedBytes.decode('utf-8')
TIMESTAMP = '{:%Y-%m-%d-%H%M%S}'.format(datetime.datetime.now())
baseURL = 'YOUR URL'

def getURL(baseURL, key):
    headers = {
        'Authorization': key,
    }

    try:
        response = requests.get(baseURL, headers=headers)
        if response:
            return response
        return None
    except:
        print("Something happened while trying to get the JSON data in the 'getURL' function!... Check out the traceback:")
        print(sys.exc_info()[0])
        raise

def getURLJson(baseURL, key):
    response = getURL(baseURL, key)
    if response:
        return response.json()
    return None
    
def getRepoSlugs(baseURL, key):
    repoSlugs = []  
    try:
        response = getURLJson(baseURL, key)
        if response:
            print("Grabbing repo names...")
            values = response['values'] 
            while 'next' in response:
                response = getURLJson(response['next'], key)
                if 'next' not in response:
                    break
                elif response['next']: 
                    values = values + response['values']
                else: 
                    print(":O something else happened!")
            for i in values:
                repoSlugs.append(i['slug'])
        return repoSlugs
    except:
        print("Something happened while trying to get the JSON data in the 'getURLJson' funtion... Check out the traceback:")
        print(sys.exc_info()[0])
        raise


def checkForPresentPermissions(URL, key):
    headers = {
        'Authorization': key,
    }
    response = requests.get(URL, headers=headers)
    jsonResponse = response.json()
    if 'error' in jsonResponse:
        isPresent = "Error"
    else:
        values = jsonResponse['values']
        isPresent = False
        for i in values:
            if i['kind'] == "require_approvals_to_merge" or i['kind'] == "push":
                isPresent = True
    return isPresent


def outputTable(header, repoSlugs):
    report = str()
    report += '## ' + header + '(' + str(len(repoSlugs)) + ')\n\n'
    report += '|Repo Name|\n'
    report += '|---|\n'
    for name in repoSlugs:
        report += '|' + name + '|\n'
    return report


def addPermissions(baseURL, repoSlugs, key, applyChanges = True):
    #headers = {
    #'Content-Type': 'application/json',
    #'Authorization' : key
    #}
    #
    #raw_data1 = {
    #    "kind": "require_approvals_to_merge",
    #    "users": [],
    #    "pattern": "",
    #    "value": 2,
    #    "branch_match_kind": "branching_model",
    #    "groups": [],
    #    "branch_type": "development",
    #    "type": "branchrestriction"
    #}
    #raw_data2 = {
    #    "kind": "push",
    #    "users": [],
    #    "pattern": "",
    #    "branch_match_kind": "branching_model",
    #    "groups": [],
    #    "branch_type": "development",
    #    "type": "branchrestriction"
    #}     
    #jsonData1 = json.dumps(raw_data1)
    #jsonData2 = json.dumps(raw_data2)
    

    report = str()
    noChanges = list()
    failedToChange = list()
    unknownStatus = list()
    changes = list()

    report += '# BitBucket Branch Permissions\n\n'
    report += '**Timestamp: **' + TIMESTAMP + '\n\n'
    report += '*All repos found using:*' + '\n\n'
    report += '*YOUR URL*' + '\n\n'
    print("Attempting to POST changes to BitBucket repos...")
    
    for name in repoSlugs:
        newURL = baseURL + name + "/branch-restrictions"
        isPresent = checkForPresentPermissions(newURL, key)
        if isPresent == "Error":
            print("\n" + "ERROR: " + name + "\n")
            unknownStatus.append(name)
        elif isPresent:
            print("Rules already present: " + name)
            noChanges.append(name)
        else:
            try:
                if applyChanges:
                    print("Applying changes to " + name)
                    #response1 = requests.post(newURL, headers=headers, data=jsonData1)
                    #response2 = requests.post(newURL, headers=headers, data=jsonData2)
                    #if response1.status_code is not 201 and response2.status_code is not 201:
                    #    print("ERROR: Failed to POST! HTTP Error: " + str(response1.status_code))
                    #    failedToChange.append(name)
                    #else:
                    changes.append(name)
                    #    print("Added permissions to " + name + "!")
                else:
                    print(name + "will need changes. Adding to report...")
                    changes.append(name)
            except:
                print("Something happened while trying to add changes to repo: " + name + ". Check out the traceback:")
                failedToChange.append(name)
                print(sys.exc_info()[0])
                raise
    
    if len(failedToChange) > 0:
        report += outputTable("Failed To Change Permissions", failedToChange)
    if len(unknownStatus) > 0:
        report += outputTable("Unknown Repo Issues", unknownStatus)
    if len(changes) > 0:
        report += outputTable("Needs Permission Changes", changes)
    if len(noChanges) > 0:
        report += outputTable("No Need For Permission Changes", noChanges)
    return report

if __name__ == "__main__":  
    import argparse

    description = ("""Generates a report of BitBucket branches that have permissions to merge to master without a PR,
    and those that don't, with the flag option of fixing the ones that don't.""")
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("-a", "--applyChanges", action='store_true', default=False, 
                        help="generate the full report of active and inactive users")
    args = parser.parse_args()

    repoSlugs = getRepoSlugs(baseURL, base64Key)
    report = addPermissions(baseURL, repoSlugs, base64Key, args.applyChanges)

    filePath = ('bitbucket-branch-permissions-' + TIMESTAMP + '.md')
    try:
        with open(filePath, 'w') as reportFile:
            reportFile.write(report)
    except:
        print("Failed to open file: " + filePath)
        exit(1)