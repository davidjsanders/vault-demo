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
    required=True,
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
_wrapped = args.wrapped_token
_server = args.server
_port = args.port
_auth_file = args.auth_file

# Check if a wrapped token has been passed as a parameter
if _wrapped is not None and not isinstance(_wrapped, str):
    raise TypeError('Wrapped token is not the correct type (str)!')

# Check if a server name has been passed as a parameter
if _server is not None:
    _success = False
    if not isinstance(_server, str):
        raise ValueError(
            'Server, if provided, must be a string. '+
            '{0} is not a string.'.format(_server)
        )
#    if _server[0:7].lower() != "http://":
#        _server = 'http://'+_server
#        Logger.log('Server set to {0}'.format(_server))

# Check if a port number has been passed as a parameter
if _port is not None:
    _success = False
    try:
        _port = int(_port)
        _success = True
    except:
        _success = False

    if not _success:
        raise ValueError(
            'Port number, if provided, must be an integer. '+
            '{0} is not an int'.format(_port)
        )

    if _port < 1:
        raise ValueError('Port number, if provided, must be greater than zero or None.')

# Check if an auth file has been passed and that it exists
if _auth_file is not None:
    if not isinstance(_auth_file, str):
        raise ValueError('Auth file, if provided, must be a filename (i.e. a string).')
    _auth_file_handle = None
    _success = False
    try:
        _auth_file_handle = open(_auth_file, 'r')
        _success = True
    except:
        _success = False

    if not _success:
        raise FileNotFoundError(
            '{0} was not found - is the spelling correct?'.format(_auth_file)
        )
    t_auth = json.load(_auth_file_handle)
    _auth_file_handle.close()

    _wrapped = t_auth.get('wrapped-token', None)
    if _wrapped is None:
        raise ValueError(
            'Authentication file did not contain a wrap token. ' +
            'Key MUST be "wrapped-token":{value}'
        )

vault = VaultServer(name=_server, port=_port)

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
