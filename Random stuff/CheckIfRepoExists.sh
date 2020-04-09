#!/bin/bash

GitName="YOUR REPO NAME"
AUTH='Authorization: Basic YOURKEY'
GitSCM=`curl -s -X GET -H "${AUTH}" -H "Content-Type: application/json" "https://api.bitbucket.org/2.0/repositories/YOURORG/${GitName}" | jq -r '.'`

if [[ ${GitSCM} = *"error"* ]]; then
    echo "This repo does not exist."
else
    echo "This repo exists."
fi