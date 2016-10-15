import json, hvac, requests.exceptions
from packages.VaultServer import VaultServer
from packages.Logger import Logger

wrapped = None
auth = None
vault = None

try:
    f = open('authentication_file.json', 'r')
    _auth_dict = json.load(f)
    if 'wrapped' in _auth_dict:
        wrapped = _auth_dict['wrapped']
    elif 'auth' in _auth_dict:
        auth = _auth_dict['auth']
    f.close()
except Exception as e:
    Logger.log('Exception! {0}'.format(repr(e)))
    exit(1)

try:
    vault = VaultServer(name="dasander-azure-gen")
except hvac.exceptions.Forbidden:
    exit(1)

try:
    if wrapped is not None:
        vault.authenticate(wrapped_token=wrapped)
    else:
        vault.authenticate(token=auth)
except requests.ConnectionError as ce:
    Logger.log('A connection error occurred; is the vault server information correct?')
    exit(1)
except hvac.exceptions.Forbidden:
    exit(1)
except Exception as e:
    Logger.log('Exception! {0}'.format(repr(e)))
    exit(1)

try:
    foo = vault.read_kv_secret(secret='foo')
    print('foo: {0}'.format(foo))
except ValueError as ve:
    Logger.log(ve)
except hvac.exceptions.Forbidden as f:
    Logger.log('Unable to read secret because permission is denied! Un-authenticated!', security_related=True)
