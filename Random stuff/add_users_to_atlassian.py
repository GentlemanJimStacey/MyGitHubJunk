import json
import os
import csv

cwd = os.getcwd()
cwdBitBucket = cwd + r"\services\bitbucket_data.json"
cwdStored = cwd + r"\storedUsers.csv"
cwdEmails = cwd + r"\data\bitbucket-lookup.csv"
cwdAtlassian = cwd + r"\data\atlassian-lookup.csv"

def getMembers():
    with open(cwdBitBucket) as f:
        data = json.load(f)
        return data['members']

def getMemberEmails(members):
    values = csv.reader(open(cwdEmails, 'r'))
    myValues = {}
    firstLine = True
    for row in values:
        if firstLine:
            firstLine = False
            continue
        myValues.update({row[1] : row[0]})
    return myValues

def storeMembers(members, email_lookup):
    with open(cwdStored, 'w', newline='') as f:
        values = csv.reader(open(cwdAtlassian, 'r'))
        listOfAtlassianNames = []
        for row in values:
            atlassianNames = row[1]
            listOfAtlassianNames.append(atlassianNames)
        account_id = []
        display_name = []
        listOfEmails = []
        email = "UNKNOWN"
        for i in members:
            if i['display_name'] in email_lookup:
                email = email_lookup.get(i['display_name'])
            else:
                email = "UNKNOWN"
            if i['display_name'] in listOfAtlassianNames:
                print(i['display_name'] + " is already present.")
            else:
                listOfEmails.append(email)
                account_id.append(i['account_id'])
                display_name.append(i['display_name'])
        writer = csv.writer(f)
        writer.writerows(zip(account_id, display_name, listOfEmails))
    return account_id, display_name, listOfEmails

def appendToAtlassianLookup(account_id, display_name, emails):
    writer = csv.writer(open(cwdAtlassian, 'a', newline=''))
    writer.writerows(zip(account_id, display_name, emails))

def deleteStoreUsersFile():
    os.remove(cwdStored)
            
if __name__== "__main__":
    members = getMembers()
    email_lookup = getMemberEmails(members)
    account_id, display_name, emails = storeMembers(members, email_lookup)
    appendToAtlassianLookup(account_id, display_name, emails)
    #deleteStoreUsersFile()