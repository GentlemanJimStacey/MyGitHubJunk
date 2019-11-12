#!/usr/bin/env python3

from os.path import join
import json
import csv
from users import get_user
import datetime

atlassianLookupLocation = join("data","atlassian-lookup.csv")
cwdJira = join('services','jira-users.json')
TIMESTAMP = '{:%Y-%m-%d-%H%M%S}'.format(datetime.datetime.now())

def getJiraUsers():
    with open(cwdJira) as f:
        data = json.load(f)
    return data['users']

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

def combineUsernameAndEmail(jiraMembers, atlassianEmails):
    listOfAtlassianNames = []
    displaynameAndEmail = [] 
    for row in atlassianEmails:
        listOfAtlassianNames.append(row)
    for i in jiraMembers:
        displayName = jiraMembers[i]['displayName']
        userName = jiraMembers[i]['name']
        if displayName in listOfAtlassianNames or userName in listOfAtlassianNames:
            displaynameAndEmail.append( (displayName, atlassianEmails[displayName]) )
    return displaynameAndEmail

def validateUsers(domainSpecificValues, totalNumUsers, fullReport):
    report = str()
    departed = dict()
    present = dict()

    for name, email in domainSpecificValues:
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
    report += '# Jira User Validation\n\n'
    report += 'timestamp: ' + TIMESTAMP + '\n\n'
    report += str(numUsers) + ' of ' + str(totalNumUsers) + ' users on account\n\n'

    if len(departed) > 0:
        report += outputTable('Invalid Users', departed)
    else:
        report += '**no departed users found**\n\n'
    if fullReport:
        if len(present) > 0:
            report += outputTable('Present Users', present)
        else:
            report += '**no present users found**\n\n'
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

def getCountry(displaynameAndEmail, fullReport = True):
    usNameAndEmail = []
    chinaNameAndEmail = []
    usReport = str()
    chinaReport = str()
    for name, email in displaynameAndEmail:
        if "cn" not in email.lower() and "hk" not in email.lower():
            usNameAndEmail.append((name, email))
        if "cn" in email.lower() or "hk" in email.lower():
            chinaNameAndEmail.append((name, email))
    totalUsers = len(displaynameAndEmail)
    usReport += validateUsers(usNameAndEmail, totalUsers, fullReport)
    chinaReport += validateUsers(chinaNameAndEmail, totalUsers, fullReport)
    return usReport, chinaReport

def writeToFile(report):
    #for i in report:
    filePathChina = join('reports','china-jira-validation-report-' + TIMESTAMP + '.md')
    filePathUS = join('reports','us-jira-validation-report-' + TIMESTAMP + '.md')
    try:
        with open(filePathUS, 'w') as USReportFile:
            USReportFile.write(report[0])
        with open(filePathChina, 'w') as chinaReportFile:
            chinaReportFile.write(report[1])
    except:
        print("Failed to open file. Directory 'reports' may not exist, or you may not have permissions." )
        exit(1)

if __name__ == "__main__":  
    # Run in script directory
    from os.path import dirname, abspath
    from os import chdir
    chdir(dirname(abspath(__file__)))

    import argparse

    description = """Validate a Jira user against the atlassian-lookup.csv and Azure Active Directory"""
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("-f", "--full", action='store_true', default=False,
                        help="generate the full report of active and inactive users")
    args = parser.parse_args()

    members = getJiraUsers()
    atlassianEmails = getAtlassianUsernameAndEmail()
    displaynameAndEmail = combineUsernameAndEmail(members,atlassianEmails)
    report = getCountry(displaynameAndEmail, args.full)
    writeToFile(report)