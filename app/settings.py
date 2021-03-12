""" Application settings module """
from decouple import config


# ############################ GENERAL SETTINGS ###############################
LOG_FILE = './log/app.log'
NAME_TPL = config('NAME_TPL')
JOB_TPL = config('JOB_TPL')
# ############################ OKTA SETTINGS ##################################
# Password for created Okta users
OKTA_USER_PASS = config('OKTA_USER_PASS')

# Okta group ID in which new user should be added
OKTA_USER_GROUP = config('OKTA_USER_GROUP', '')

# Okta API token
OKTA_API_TOKEN = config('OKTA_API_TOKEN')

# Okta API endpoint to create users
OKTA_API_URL = config('OKTA_API_URL')

# Headers rewuired by Okta API
OKTA_HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Authorization": "SSWS " + OKTA_API_TOKEN
}

# ############################# GMAIL SETTINGS ################################
# Your corporate Gmail domain, e.g. company.com
GMAIL_DOMAIN = config('GMAIL_DOMAIN')

# gmail service account's credentials file from Google Dev Console
GMAIL_CREDENTIALS = config('GMAIL_CREDENTIALS')

# Gsuite group if user needs to be added in it
GMAIL_GROUP = config('GMAIL_GROUP', '')

# Organisation can have subfolders. If no then leave '/'
GMAIL_ORG_UNIT_PATH = config('GMAIL_ORG_UNIT_PATH')

# Gmail temp password for new users
GMAIL_USER_PASS = config('GMAIL_USER_PASS')

# ################################ AD SETTINGS ################################
# Active Directory domain name
AD_DOMAIN = config('AD_DOMAIN')

# Active Directory server
AD_SERVER = 'ldap://' + config('AD_DOMAIN')

# Active Directory service user with appropriate rights to create users
AD_ADMIN_USER = config('AD_ADMIN_USER')

# Active Directory service user password
AD_ADMIN_PASS = config('AD_ADMIN_PASS')

# Active Directory temporary password for new users
AD_USER_PASS = config('AD_USER_PASS')

# Connection string fot AD user, e.g. admin@office.local
AD_BIND_DN = AD_ADMIN_USER + '@' + AD_DOMAIN

# Active Directory distinguished name for group in which user should be added
AD_GROUP_DN = config('AD_GROUP_DN')

# Simple AD group name
if AD_GROUP_DN:
    AD_GROUP_NAME = AD_GROUP_DN.split('CN=')[1].replace(',', '')
else:
    AD_GROUP_NAME = False

# Distinguished name for new user, e.g 'OU=Sales,DC=office,DC=local'
AD_USER_DN = config('AD_USER_DN')
