#!/bin/bash
source ./env
export $(cut -d= -f1 env) # export env variables
docker build -f Dockerfile.nginx --rm -t adgo .
docker run -d --rm --name adgo_app \
           --env-file env \
           -v $(pwd)/app/log/:/app/log \
           -v $(pwd)/$GMAIL_CREDENTIALS:/app/$GMAIL_CREDENTIALS \
           -p $IP_BIND:80:80 adgo
