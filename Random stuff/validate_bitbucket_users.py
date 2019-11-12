#!/usr/bin/env python3

from os.path import join
import json
import csv
from users import get_user
import datetime

atlassianLookupLocation = join("data","atlassian-lookup.csv")
cwdBitBucket = join('services','bitbucket_data.json')
TIMESTAMP = '{:%Y-%m-%d-%H%M%S}'.format(datetime.datetime.now())

def getBitBucketMembers():
    with open(cwdBitBucket) as f:
        data = json.load(f)
    return data['members']

def getAtlassianUsernameAndEmail():
    values = csv.reader(open(atlassianLookupLocation, 'r'))
    atlassianUsernameAndEmail = {}
    firstLine = True
    for row in values:
        if firstLine:
            firstLine = False
            continue
        atlassianUsernameAndEmail.update({row[1] : row[2]})
    return atlassianUsernameAndEmail

def combineUsernameAndEmail(members, email_lookup):
    # with open(cwdStored, 'w', newline='') as f:
    listOfAtlassianNames = []
    displaynameAndEmail = [] 
    for row in email_lookup:
        listOfAtlassianNames.append(row)
    for i in members:
        if i['display_name'] in listOfAtlassianNames:
            displaynameAndEmail.append( (i['display_name'], email_lookup[i['display_name']]) )
    return displaynameAndEmail
    
def validateUsers(displaynameAndEmail, fullReport = True):
    report = str()
    departed = dict()
    present = dict()

    for name, email in displaynameAndEmail:
        try:
            result = get_user(email)
            if not result or 'accountEnabled' not in result: 
                departed[email]={'name':name, 'email':email, 'status':'Unknown'}
            elif result['accountEnabled']:
                result.update({'status':'Active'})
                present[email]=result
            else: 
                result.update({'status':'Departed'})
                departed[email]=result
        except:
            print("There was a problem. Search for me in the code, and find out what's wrong. :)")
            result.update({'status':'Departed'})
            departed[email]=result
    numUsers = len(present) + len(departed)
    report += '# BitBucket User Validation\n\n'
    report += 'timestamp: ' + TIMESTAMP + '\n\n'
    report += str(numUsers) + ' of 100 users on account\n\n'
    
    if fullReport:
        if len(present) > 0:
            report += outputTable('Present Users', present)
        else:
            report += '**no present users found**\n\n'
    if len(departed) > 0:
        report += outputTable('Invalid Users', departed)
    else:
        report += '**no departed users found**\n\n'
    return report


def outputTable(header, records):
    report = str()
    report += '## ' + header + '(' + str(len(records)) + ')\n\n'
    report += '|Name|Email Address|Status|\n'
    report += '|---|---|---|\n'
    for record in records.values():
        report += '|' + record['name'] + ' | ' + record['email'] + ' | ' + record['status'] + '|\n'
        #report += '\n'
    return report


if __name__ == "__main__":  
    # Run in script directory
    from os.path import dirname, abspath
    from os import chdir
    chdir(dirname(abspath(__file__)))

    import argparse

    description = """Validate a BitBucket user against the atlassian-lookup.csv and Azure Active Directory"""
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("-f", "--full", action='store_true', default=False)
    args = parser.parse_args()

    
    members = getBitBucketMembers()
    email_lookup = getAtlassianUsernameAndEmail()
    displaynameAndEmail = combineUsernameAndEmail(members, email_lookup)
    report = validateUsers(displaynameAndEmail, args.full)

    filePath = join('reports', 'bitbucket-validation-report-' + TIMESTAMP + '.md')
    try:
        with open(filePath, 'w') as reportFile:
            reportFile.write(report)
    except:
        print("Failed to open file: " + filePath)
        exit(1)
        