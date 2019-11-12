#!/usr/bin/env python
import boto3
import json
import pprint
from os import environ, path

s3Client = boto3.client('s3')
s3Resource = boto3.resource('s3')
pp = pprint.PrettyPrinter(indent=4)
#testfordeleteartifactory

print("If you don't know how to use the script, run the script, then enter help when it prompts you to.")

if "AWS_PROFILE" not in environ:
    print("You don't seem to have the AWS_PROFILE variable defined. Make sure you define it using 'export AWS_PROFILE=profilename' Exiting...")
    print("Also, make sure you've run the gimme-aws-creds command to get temporary credentials. ")
    exit()

def getBucketName():
    bucket_name = raw_input("Enter the name of the bucket: ")
    count = 1
    while s3Resource.Bucket(bucket_name).creation_date is None:
        print("Bucket does not exist! Try again!")
        bucket_name = raw_input("Enter the name of the bucket: ")
        count += 1
        if count == 3:
            print("Stop. Check the name again and rerun the script, you idiot.")
            exit()
    return bucket_name
        
bucket_name = getBucketName()

userOption = raw_input("Enter 'test' to run a test, which will return the key names of all files to restore, or enter 'real' to do it. Or help... if you need help. ")

def testRunDelete(bucket):
    """A function to test files for a deleted marker in S3."""
    paginator = s3Client.get_paginator('list_object_versions')
    pageResponse = paginator.paginate(Bucket=bucket)
    for pageObject in pageResponse:
        count = 0
        if 'DeleteMarkers' in pageObject.keys():
            for item in pageObject['DeleteMarkers']:
                count += 1
            print("Number of S3 Objects to be restored: " + str(count))
        else:
            print("Looks like there aren't any objects to be restored!")
            exit()


def removeDeletedMarkers(bucket):
    """A function to remove the deleted marker which restores the file in S3."""
    paginator = s3Client.get_paginator('list_object_versions')
    pageResponse = paginator.paginate(Bucket=bucket)
    for pageObject in pageResponse:
        count = 0
        if 'DeleteMarkers' in pageObject.keys():
            for item in pageObject['DeleteMarkers']:
                count += 1
                fileobjver = s3Resource.ObjectVersion(bucket, item['Key'], item['VersionId'])
                fileobjver.delete()
                print('Restoring ' + item['Key'] + "...")
            print("S3 Objects restored: " + str(count))
        else:
            print("Looks like there aren't any objects to be restored!")
            exit()

if userOption == "help":
    print("This script needs AWS_PROFILE env variable set, and needs aws credentials through gimme-aws-creds.")
    print("")
    print("There are three options for this script: 'test' and 'real', or 'help'")
    print("Enter 'test' to see which files will be restored. Enter real. to restore the files.")
    print("No caps, no blanks, no numbers, etc. Just 'test' or 'real'. It's not complex. ;)")
elif userOption == "test":
    testRunDelete(bucket_name)
elif userOption == "real":
    removeDeletedMarkers(bucket_name)
elif userOption == "":
    print("You'll want to enter an argument.")
else:
    print("I'm not actually sure what happened, but you've found a way to break things. Good job!")