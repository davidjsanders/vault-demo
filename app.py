import json, hvac, requests.exceptions, argparse
from packages.VaultServer import VaultServer
from packages.Logger import Logger

wrapped = None
auth = None
vault = None

parser = argparse.ArgumentParser(description='Process optional tokens')
parser.add_argument(
    '--token',
    dest='token',
    default=None,
    help='Pass the Vault authentication token via the command line.'
)
parser.add_argument(
    '--wrapped-token',
    dest='wrapped_token',
    default=None,
    help='Pass the Vault wrapped authentication token via the command line.'
)
args = parser.parse_args()

try:
    if args.token is None:
        if args.wrapped_token is None:
            f = open('authentication_file.json', 'r')
            _auth_dict = json.load(f)
            if 'auth' in _auth_dict:
                auth = _auth_dict['auth']
            elif 'wrapped' in _auth_dict:
                wrapped = _auth_dict['wrapped']
            f.close()
        else:
            wrapped = args.wrapped_token
    else:
        auth = args.token
        wrapped = None
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
    Logger.log(
        'Unable to read secret. '+
            'Token {0} returns permission denied!'.format(vault.accessor),
        security_related=True
    )
