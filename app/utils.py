# -*- coding: utf-8 -*-
""" Some service functions for ADGO app """
import os
import json
import datetime
from settings import LOG_FILE, GMAIL_DOMAIN, NAME_TPL, JOB_TPL


def users_list_gen(data):
    """ Parse input text. Generates users list. """

    users = list()
    data = data.decode('utf-8')
    for line in data.splitlines():
        if line.startswith(NAME_TPL):
            # name can contain "-" character, therefore replaced only one "-"
            name = line.replace(NAME_TPL, '', 1)\
                       .replace('-', '', 1)\
                       .replace(':', '')\
                       .strip()
            first_name = name.split()[0].strip()
            last_name = name.split()[1].strip()

            email = (first_name.lower() + '.' + last_name.lower() + '@' +
                     GMAIL_DOMAIN)

            user = {
                "firstName": first_name,
                "lastName": last_name,
                "fullName": last_name + ' ' + first_name,
                "adName": first_name[0].lower() + '.' + last_name.lower(),
                "email": email
            }
            continue

        if line.startswith(JOB_TPL):
            jobtitle = line.replace(JOB_TPL, '', 1)\
                           .replace('-', '')\
                           .replace(':', '')\
                           .strip()
            user.update({"jobtitle": jobtitle})
            users.append(user)
    return users


def write_to_log(email, event):
    """ Writes events to log file """

    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'w'):
            pass

    with open(LOG_FILE, 'a+') as log_file:
        record = email + ', ' + event
        if record not in log_file.read():
            today = datetime.date.today().strftime('%d-%m-%Y')
            log_str = '[' + today + '] -- ' + record + '\n'
            log_file.write(log_str)


def get_err_msg(err):
    """ Get error message from LDAP lib Exception message """
    err = err.__str__() \
             .replace("\'", "\"") \
             .replace('\"\\n', '') \
             .replace('\\n\\t\"', '')
    msg = json.loads(err)['desc']
    return msg
