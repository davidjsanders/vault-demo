import hvac
import logging
from packages.Logger import Logger


class VaultServer:
    vault_information = {
        "name": None,
        "location": None,
        "service": None,
        "protocol": None,
        "port": None,
        "token": None
    }
    _client = None
    _token = None
    _accessor = None
    _wrapped_token = None

    def __init__(
        self,
        name=None,
        location=None,
        service=None,
        protocol="http",
        port=8200
    ):
        if name is None \
            or (port is None or not isinstance(port, int) or port < 1024)\
            or protocol is None:
                raise ValueError('Vault instantiation is badly formed.')

        self.vault_information["name"] = name
        self.vault_information["location"] = location
        self.vault_information["service"] = service
        self.vault_information["protocol"] = protocol
        self.vault_information["port"] = port
        try:
            self.client = hvac.Client(url=self.fqdn)
        except Exception:
            raise

    @property
    def fqdn(self, short=True):
        return_string = "{0}://{1}:{2}".format(
            self.vault_information["protocol"],
            self.vault_information["name"],
            self.vault_information["port"]
        ) if short else "{0}://{1}.{2}.{3}:{4}".format(
            self.vault_information["protocol"],
            self.vault_information["name"],
            self.vault_information["location"],
            self.vault_information["service"],
            self.vault_information["port"]
        )
        return return_string

    @property
    def accessor(self):
        return self._accessor

    @property
    def token(self):
        return self.vault_information["token"]

    @token.setter
    def token(self, v):
        self.vault_information["token"] = v

    @property
    def client(self):
        return self._client

    @client.setter
    def client(self, new_value=None):
        if new_value is not None and not isinstance(new_value, hvac.Client):
            _error_text = 'The client must be an instance of hvac.Client.'
            logging.error('ERROR: VaultServer.py: @client.setter: {0}'.format(_error_text))
            raise TypeError(_error_text)
        self._client = new_value

    def read_kv_secret(self, secret=None):
        if secret is None:
            _error_text = 'Secret name must be provided.'
            logging.error('ERROR: VaultServer.py: read_kv_secret: {0}'.format(_error_text))
            raise ValueError(_error_text)

        try:
            secret_kv = self.client.read(path="secret/{0}".format(secret))
            if not isinstance(secret_kv, dict):
                _error_text = 'Unable to read secret "{0}".'.format(str(secret))
                logging.error('ERROR: VaultServer.py: read_kv_secret: {0}'.format(_error_text))
                raise ValueError(_error_text)
            secret_data = secret_kv.get('data', None)
            secret_value = secret_data.get('value', None)
            if secret_value is not None:
                return secret_value
            else:
                _error_text = 'Secret {0} is not defined.'.format(secret)
                logging.error('ERROR: VaultServer.py: read_kv_secret: {0}'.format(_error_text))
                raise ValueError(_error_text)
        except hvac.exceptions.Forbidden as f:
            _error_text = '** SECURITY LOG ** Forbidden. Permission Denied!'
            logging.error(_error_text)
            raise

    def authenticate(self, token=None, wrapped_token=None):
        if token is None and wrapped_token is None:
            raise TypeError('Either a token or wrapped token must be provided.')

        if token is not None:
            _auth = {"client_token":token}
        else:
            temp_unwrap = None
            try:
                temp_unwrap = self.client.unwrap('{0}'.format(wrapped_token))
            except hvac.exceptions.Forbidden as f:
                _error_text = '** SECURITY LOG ** ' + \
                              'Unable to unwrap Token!! Token: {0}. Error: {1}.'.format(wrapped_token, str(f))
                logging.error(_error_text)
                raise

            if temp_unwrap is None:
                raise TypeError('Unwrap unsuccessful. The authentication failed.')

            _auth = temp_unwrap.get('auth', None)

        _token = _auth.get('client_token', None)
        self._accessor = _auth.get('accessor', None)
        if _auth is None or _token is None:
            _error_text = 'The unwrapped value is not an authentication token.'
            logging.error(_error_text)
            # Logger.log(temp_unwrap, security_related=True)
            raise ValueError(_error_text)

        try:
            self.client = hvac.Client(url=self.fqdn, token=_token)
        except Exception:
            raise
