""" Unit tests for app """
import datetime
import pytest
import run
from settings import GMAIL_DOMAIN, NAME_TPL, JOB_TPL, LOG_FILE
from utils import users_list_gen, write_to_log


@pytest.fixture
def client_fixture():
    """ Create a pytest fixture called client() """
    run.app.config['TESTING'] = True
    with run.app.test_client() as client:
        yield client


def test_root_url(client_fixture):
    """Test / url."""

    req = client_fixture.get('/')
    assert b'<title>Create Users in AD Gmail and Okta</title>' in req.data


def test_check_url(client_fixture):
    """Test /check url."""

    user_test = '%s - Name1 Lastname1\n' \
                '%s - Test Manager\n' \
                '%s - Name2 Lastname2\n' \
                '%s - Test Manager\n' % (NAME_TPL, JOB_TPL, NAME_TPL, JOB_TPL)

    email_test_1 = "name1.lastname1@" + GMAIL_DOMAIN
    email_test_2 = "name2.lastname2@" + GMAIL_DOMAIN

    req = client_fixture.post('/check', data=user_test)
    assert email_test_1.encode() in req.data
    assert email_test_2.encode() in req.data


def test_log_url(client_fixture):
    """Test /log url."""

    req = client_fixture.get('/log')
    assert (b'No historical data!' in req.data or
            b'--' in req.data)


def test_users_list_gen_func():
    """Test users_list_gen function from utils"""

    user_test = b'%s - Name1 Lastname1\n' \
                b'%s - Test Manager\n' % (NAME_TPL.encode(), JOB_TPL.encode())
    user_dict_test = {
        "firstName": "Name1",
        "lastName": "Lastname1",
        "fullName": "Lastname1 Name1",
        "adName": "n.lastname1",
        "email": "name1.lastname1@" + GMAIL_DOMAIN,
        "jobtitle": "Test Manager"
    }
    users_list_test = [user_dict_test, ]
    assert users_list_test == users_list_gen(user_test)


def test_write_to_log_func():
    """Test write_to_log function from utils"""
    email = 'test@test.test'
    event = 'TEST'
    today = datetime.date.today().strftime('%d-%m-%Y')
    record = email + ', ' + event
    log_str = '[' + today + '] -- ' + record + '\n'
    write_to_log(email, event)
    with open(LOG_FILE) as log_file:
        assert log_str in log_file.read()

    # clean log from test records
    with open(LOG_FILE, 'r') as log_file:
        lines = log_file.readlines()
    with open(LOG_FILE, 'w') as log_file:
        for line in lines:
            if line != log_str:
                log_file.write(line)
