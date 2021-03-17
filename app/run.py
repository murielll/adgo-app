# -*- coding: utf-8 -*-
""" This is main flask app module """
import os
import json
import pickle
import ldap
from ldap import modlist
from requests import post
from flask import Flask, request, render_template
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import settings
from utils import users_list_gen, write_to_log, get_err_msg


app = Flask(__name__)


@app.route('/', methods=['GET'])
def index():
    """ View for / route """
    return render_template('index.html')


@app.route('/check', methods=['POST'])
def check_info():
    """ View for checking if input data is correct """
    data = request.get_data()
    users = users_list_gen(data)

    if users:
        return 'You can create these users:\n\n' + '\n'\
               .join([
                'Email: ' + user['email'] + '    '
                'AD: ' + user['adName'] for user in users])
    return 'No users to create!'


@app.route('/log', methods=['GET'])
def hist_log():
    """ View for show log """
    if not os.path.exists(settings.LOG_FILE):
        with open(settings.LOG_FILE, 'w'):
            pass
    with open(settings.LOG_FILE) as log:
        log_data = log.read()
        if '--' not in log_data:  # check if log has a historical data
            return 'No historical data!'
        return log_data


@app.route('/okta', methods=['POST'])
def okta():
    """ View for user creation in Okta """
    result = list()
    data = request.get_data()
    users = users_list_gen(data)

    if not users:
        return 'No users to create!'

    for user in users:
        okta_user = {
            "profile": {
                "firstName": user["firstName"],
                "lastName": user["lastName"],
                "email": user["email"],
                "login": user["email"]
            },
            "credentials": {
                "password": {"value": settings.OKTA_USER_PASS}
            },
        }
        if settings.OKTA_USER_GROUP:
            okta_user.update({"groupIds": [settings.OKTA_USER_GROUP, ]})

        okta_req = post(settings.OKTA_API_URL,
                        headers=settings.OKTA_HEADERS,
                        data=json.dumps(okta_user))

        if okta_req.status_code != 200:
            result.append('%s: %s' % (user['email'],
                          okta_req.json()['errorCauses'][0]['errorSummary']))

        else:
            result.append(
              '%s: user succefully created.' % user['email']
            )
            write_to_log(user['email'], 'OKTA')
    return '\n'.join(result)


@app.route('/gmail', methods=['POST'])
def gmail():
    """ View for user creation in Gmail """
    result = list()
    data = request.get_data()
    users = users_list_gen(data)

    if not users:
        return 'No users to create!'

    scopes = ['https://www.googleapis.com/auth/admin.directory.user',
              'https://www.googleapis.com/auth/admin.directory.group']
    creds = None

    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                settings.GMAIL_CREDENTIALS, scopes)
            creds = flow.run_local_server(port=0)

        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('admin', 'directory_v1', credentials=creds)

    for user in users:
        gmail_user = {'primaryEmail': user['email'],
                      'name': {
                        'givenName': user['firstName'],
                        'familyName': user['lastName']
                      },
                      'orgUnitPath': settings.GMAIL_ORG_UNIT_PATH,
                      'password': settings.GMAIL_USER_PASS}

        member = {'email': user['email']}
        # add user
        try:
            service.users().insert(body=gmail_user).execute()
            result.append('%s: user succefully created.' % user['email'])
            write_to_log(user['email'], 'GMAIL')
        except HttpError as err:
            msg = json.loads(err.content.decode())['error']['message']
            result.append('%s: Failed to create user. Error message: %s'
                          % (user['email'], msg))
            return '\n'.join(result)
        # add user to group
        if settings.GMAIL_GROUP:
            try:
                service.members().insert(groupKey=settings.GMAIL_GROUP,
                                         body=member).execute()
                result.append(
                  '%s: User succefully added to group %s.'
                  % (user['email'], settings.GMAIL_GROUP)
                )
            except HttpError as err:
                msg = json.loads(err.content.decode())['error']['message']
                result.append(
                    '%s: Failed to add user to group %s. Error message: %s.'
                    % (user['email'], settings.GMAIL_GROUP, msg)
                )

    return '\n'.join(result)


@app.route('/ad', methods=['POST'])
def active_directory():
    """
    View for user creation in Active Directory

    Useful info about python ldap lib
    http://marcitland.blogspot.com/2011/02/python-active-directory-linux.html

    """

    result = list()
    data = request.get_data()
    users = users_list_gen(data)

    if not users:
        return 'No users to create!'

    ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)

    ad_srv = ldap.initialize(settings.AD_SERVER)

    ad_srv.set_option(ldap.OPT_REFERRALS, 0)
    ad_srv.set_option(ldap.OPT_PROTOCOL_VERSION, 3)
    ad_srv.set_option(ldap.OPT_X_TLS, ldap.OPT_X_TLS_DEMAND)
    ad_srv.set_option(ldap.OPT_X_TLS_DEMAND, True)
    ad_srv.set_option(ldap.OPT_DEBUG_LEVEL, 255)

    try:
        ad_srv.start_tls_s()
    except ldap.LDAPError as err:
        msg = get_err_msg(err)
        result.append(
            'Failed to connect to LDAP server! Error message: %s.'
            % msg
        )
        return '\n'.join(result)

    ad_srv.simple_bind_s(settings.AD_BIND_DN, settings.AD_ADMIN_PASS)

    for user in users:

        user_dn = 'CN=' + user['fullName'] + ',' + settings.AD_USER_DN

        user_attrs = {}
        user_attrs['objectClass'] = [b'top',
                                     b'person',
                                     b'organizationalPerson',
                                     b'user']
        user_attrs['cn'] = str.encode(user['fullName'])
        user_attrs['userPrincipalName'] = str.encode(user['adName'] + '@' +
                                                     settings.AD_DOMAIN)
        user_attrs['sAMAccountName'] = str.encode(user['adName'])
        user_attrs['givenName'] = str.encode(user['firstName'])
        user_attrs['sn'] = str.encode(user['lastName'])
        user_attrs['displayName'] = str.encode(user['fullName'])
        user_attrs['description'] = str.encode(user['jobtitle'])
        user_attrs['userAccountControl'] = b'514'  # user is disabled

        # add user
        user_ldif = modlist.addModlist(user_attrs)
        try:
            ad_srv.add_s(user_dn, user_ldif)
            result.append('%s: User succefully created.' % user['adName'])
            write_to_log(user['email'], 'AD')
        except ldap.LDAPError as err:
            msg = get_err_msg(err)
            result.append(
                '%s: Failed to create user! Error message: %s'
                % (user['adName'], msg))
            return '\n'.join(result)

        # change pass
        unicode_pass = '\"' + settings.AD_USER_PASS + '\"'
        password_value = unicode_pass.encode('utf-16-le')
        add_pass = [(ldap.MOD_REPLACE, 'unicodePwd', [password_value])]
        try:
            ad_srv.modify_s(user_dn, add_pass)
            result.append(
              '%s: Password has changed succefully.' % user['adName']
            )
        except ldap.LDAPError as err:
            msg = get_err_msg(err)
            result.append(
                '%s: Failed to change password! Error message: %s.'
                % (user['adName'], msg)
            )
            return '\n'.join(result)

        # enable user
        mod_acct = [(ldap.MOD_REPLACE, 'userAccountControl', b'512')]
        try:
            ad_srv.modify_s(user_dn, mod_acct)
            result.append(
              '%s: user enabled succefully' % user['adName']
            )
        except ldap.LDAPError as err:
            msg = get_err_msg(err)
            result.append(
                '%s: Failed to enable user! Error message: %s.'
                % (user['adName'], msg)
            )
            return '\n'.join(result)
        if settings.AD_GROUP_NAME:
            # add to group
            add_member = [(ldap.MOD_ADD, 'member', str.encode(user_dn))]

            try:
                ad_srv.modify_s(settings.AD_GROUP_DN, add_member)
                result.append(
                  '%s: User succefully added to group %s.'
                  % (user['adName'], settings.AD_GROUP_NAME)
                )
            except ldap.LDAPError as err:
                msg = get_err_msg(err)
                result.append(
                    '%s: Failed to add user to group %s! Error message: %s.'
                    % (user['adName'], settings.AD_GROUP_NAME, msg)
                )

    # Disconnect from AD server
    ad_srv.unbind_s()

    return '\n'.join(result)
