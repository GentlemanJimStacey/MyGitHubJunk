#!/bin/bash

usageFunction(){
  echo "Usage: ./doStuff.bash option"
  echo "        Option: Is it a leader? y, or n"
  echo ""
  echo "Example: ./doStuffDockerSwarm.bash n"
}

doStuffFunction(){
  read -p "What cluster? i.e. 1, 2, 3: " clusterVar
  echo "Adding salt pillar key and environment..."
  salt-call grains.append pillar_access_key #removed for security purposes
  salt-call grains.append pillar_env #removed for security purposes
  echo "Switching salt environment.conf from base to prd..."
  envVar="environment: prd"
  echo ${envVar} > /etc/salt/minion.d/environment.conf

  echo "Starting Docker service..."
  service docker start
  echo "Highstating..."
  salt-call state.highstate
}

if [[ ${1} == "-h" ]] || [[ ${1} ==  "--help" ]]; then
  usageFunction
  exit 1
elif [[ ${1} == "" ]]; then
  echo "You need to specify parameters..."
  usageFunction
  exit 1
else
  doStuffFunction
fi

###########################
#Below runs only on master#
###########################

leaderNodeFunction(){
  echo "Making directory..."
  mkdir /etc/#removed for security
  echo "Making yaml file..."
  touch /etc/#removed for security
  echo "All done. Make sure the node joined the cluster. If not, go back and fix that."
}

if [[ ${1} == "y" ]]; then
  leaderNodeFunction
elif [[ ${1} == "n" ]]; then
  echo "All done. Make sure the node joined the cluster. If not, go back and fix that."
fi

directory="/etc/#removed for security"
cat > ${directory} <<'EOF'
"version: "3"
services:
  #removed for security:
    image: #removed for security:0.1.0
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_USER=#removed for security
      - POSTGRES_DB=#removed for security

  #removed for securitygateway:
    image: #removed for security
    restart: always
    ports:
      - "80:8000"
      - "8001:8001"
      - "443:8443"
      - "8444:8444"
    environment:
      - #removed for security_DATABASE=postgres
      - #removed for security_PG_HOST=#removed for securitydatabase
      - #removed for security_PROXY_ACCESS_LOG=/dev/stdout
      - #removed for security_ADMIN_ACCESS_LOG=/dev/stdout
      - #removed for security_PROXY_ERROR_LOG=/dev/stderr
      - #removed for security_ADMIN_ERROR_LOG=/dev/stderr
      - #removed for security_ADMIN_LISTEN=0.0.0.0:8001
      - #removed for security_ADMIN_LISTEN_SSL=0.0.0.0:8444"
EOF
exit 0
