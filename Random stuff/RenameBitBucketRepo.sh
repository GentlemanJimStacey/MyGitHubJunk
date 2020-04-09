#!/bin/bash
AUTH='Authorization: Basic YOURKEY'
curl -s -X PUT -H "${AUTH}" -H "Content-Type: application/json" https://api.bitbucket.org/2.0/repositories/YOURORGANIZATION/YOURREPO -d '{"name": "YOUR NEW REPO NAME"}'