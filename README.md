# ADGO - Active Directory, Gmail, Okta user creation tool

Create users in all systems in 1 click.

## Purpose

This project has 3 purposes:
1. practical - it can help to decrease time of users creation.
2. demo - from this project you can see what skills have author.
3. educational - author learn technologies through the development.

## System requirements

RAM: 256Mb

Soft: docker, docker-compose

## Install

1. Clone this repo.
2. Go to root dir of repo.
3. Copy ***env.sample*** to ***env*** and specify in it all settings:
```
IP_BIND - ip address on wich ADGO app will be listen for connections if app runs via ***docker run*** commnad. Default=127.0.0.1
NAME_TPL - search word for name of user.
JOB_TPL - search word for jobtitle of user.
OKTA_API_URL - okta api url for user creation, something like https://YOUR-COMPANY.okta.com/api/v1/users?activate=true&nextLogin=changePassword
OKTA_API_TOKEN - okta api token. You need to get it in okta admin panel.
OKTA_USER_GROUP - group ID in which okta user will be added. Can be blank.
OKTA_USER_PASS - temp password for okta user. After user login okta ask to change it.
GMAIL_DOMAIN - your gmail organization domain, something like company.com
GMAIL_CREDENTIALS - json file with gmail creds.You need to get it in google admin panel.https://support.google.com/cloud/answer/6158849?hl=en
GMAIL_GROUP - group name in which gmail user will be added. Can be blank.
GMAIL_ORG_UNIT_PATH - organization path in Gsuite admin. Default / it means the root organization.
GMAIL_USER_PASS - password for created gmail user.
AD_DOMAIN - Active Directory domain name, for example office.local.
AD_ADMIN_USER - Active Directory user which have permissions to create users.
AD_ADMIN_PASS - password for Active Directory user which have permissions to create users.
AD_USER_PASS - temp password for created users.
AD_GROUP_DN - Active Directory distinguished name for group in which user should be added. For example: CN=SimpleUsers,CN=Groups,OU=Sales,DC=office,DC=local
AD_USER_DN - Distinguished name for new user. For example CN=Users,OU=Sales,DC=office,DC=local
```

Get ***credentials.json*** file from Google Developer console and place it in directory where ***env*** file is stored.

3. Run ***start.sh*** script. It'll build docker image and then will run it.
To stop ADGO app run ***stop.sh*** script from root directory.

Also it can be runned by ***docker-compose up -d***. In that case application will be consisted from 2 containers.


## Before start using
When you run app first you need to get creds form gmail. For this you need to click on Gmail button and then go to logs(something like this ```docker logs adgo_app```) of app and find link similar like this:
```
Please visit this URL to authorize this application: https://accounts.google.com/o/oauth2/auth?response_type=code&client_id=128622456843-kaiii0f2v1k8blkabo3p91h6286qr9k9.apps.googleusercontent.com&redirect_uri=http%3A%2F%2Flocalhost%3A50969%2F&scope=https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fadmin.directory.user+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fadmin.directory.group&state=8tpEPGvuAGSP8F3hj7vx5MgqIMISgf&access_type=offline
```
You should go to this link and authorize app to create users.
Then you'll be redirected to link similar like this:

```
http://localhost:50969/?state=8tpEPGvuAGSP8F3hj7vx5MgqIMISgf&code=4/0AY0e-g76bpFUJyhDaMWz4GdoBrZuTPLX8dydLyE_JFwLrWwIahFW2212ADDiXwxFsX5p6w&scope=https://www.googleapis.com/auth
/admin.directory.user%20https://www.googleapis.com/auth/admin.directory.group
```
Copy this link and go to shell.

Go inside container with app:
```
docker exec -it adgo_app sh

```
Install curl and go to link which you copy on previous step
```
apk add curl

curl 'http://localhost:50969/?state=8tpEPGvuAGSP8F3hj7vx5MgqIMISgf&code=4/0AY0e-g76bpFUJyhDaMWz4GdoBrZuTPLX8dydLyE_JFwLrWwIahFW2212ADDiXwxFsX5p6w&scope=https://www.googleapis.com/auth
/admin.directory.user%20https://www.googleapis.com/auth/admin.directory.group'

```

After this you'll see message:
```
The authentication flow has completed. You may close this window
```

After this gmail api lib generate file ```token.pickle``` and save it in conatiner in /app directory, and app will be able to create gmail users.


## Usage
To create users you should copy info about users from your data source and paste in form ***Input data***.

Allowed data formats are:

```
name - Name1 Lastname1
jobtitle - Support Manager
name - Name2 Lastname2
jobtitle - Office Manager
```
or
```
name: Name1 Lastname1
jobtitle: Support Manager
name: Name2 Lastname2
jobtitle: Office Manager
```
Where ***name*** and ***jobtitle*** were got from settings NAME_TPL=name JOB_TPL=jobtitle.

You can use another search words for ***name*** and ***jobtitle***.

For example if settings will be ***NAME_TPL=fullname*** and ***JOB_TPL=job_position*** then you can pass in ***Input data:*** this data:

```
fullname - Name1 Lastname1
job_position - Support Manager
fullname - Name2 Lastname2
job_position - Office Manager
```
or
```
fullname: Name1 Lastname1
job_position: Support Manager
fullname: Name2 Lastname2
job_position: Office Manager
```


To check data before creation you should press button ***Check data*** and ADGO app show you in textarea ***Output*** wich users can be created, for example:
```
You can create these users:

Email: name1.lastname1@company.com    AD: n.lastname1
Email: name2.lastname2@company.com    AD: n.lastname2
```
As you can see format of created users is ***name1.lastname1@company.com***  for Gmail accounts and ***n.lastname1*** for Active Directory accounts.

To create users click on corresponding button.

To show history of added users click to button ***History***.

## Customization
If you need another format of account names or you have another format of input data you can change it in function ***users_list_gen*** in ***utils.py***
