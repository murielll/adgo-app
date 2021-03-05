# -*- coding: utf-8 -*-
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
            firstName = name.split()[0].strip()
            lastName = name.split()[1].strip()

            email = (firstName.lower() + '.' + lastName.lower() + '@' +
                     GMAIL_DOMAIN)

            user = {
                "firstName": firstName,
                "lastName": lastName,
                "fullName": lastName + ' ' + firstName,
                "adName": firstName[0].lower() + '.' + lastName.lower(),
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
    with open(LOG_FILE, 'a+') as f:
        record = email + ', ' + event
        if record not in f.read():
            today = datetime.date.today().strftime('%d-%m-%Y')
            log_str = '[' + today + '] -- ' + record + '\n'
            f.write(log_str)


def get_err_msg(err):
    err = err.__str__() \
             .replace("\'", "\"") \
             .replace('\"\\n', '') \
             .replace('\\n\\t\"', '')
    msg = json.loads(err)['desc']
    return msg
