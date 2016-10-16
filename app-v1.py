import json, hvac, requests.exceptions, argparse
from packages.VaultServer import VaultServer
from packages.Logger import Logger

wrapped = None
auth = None
vault = None

parser = argparse.ArgumentParser(description='Process optional tokens')
parser.add_argument(
    '--wrapped-token',
    dest='wrapped_token',
    default=None,
    help='Pass the Vault wrapped authentication token via the command line.'
)
parser.add_argument(
    '--auth-file',
    dest='auth_file',
    default=None,
    help='Pass the filename of a JSON file containing authentication tokens (wrapped or unwrapped).'
)
parser.add_argument(
    '--server',
    dest='server',
    default=None,
    help='Pass the Vault server name (or FQDN).'
)
parser.add_argument(
    '--port',
    dest='port',
    default=8200,
    help='Pass the Vault server port number (default 8200)'
)
args = parser.parse_args()
wrapped = args.wrapped_token
server = args.server
port = args.port


try:
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
            'Token {0} returns permission denied!'.format(
                vault.accessor if vault.accessor is not None else 'is null, so'
            ),
        security_related=True
    )
