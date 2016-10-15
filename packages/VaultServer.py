import hvac
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
    _wrapped_token = None

    def __init__(
        self,
        name=None,
        location="eastus",
        service="cloudapp.azure.com",
        protocol="http",
        port=18200
    ):
        if name is None \
            or location is None\
            or service is None\
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
    def fqdn(self):
        return "{0}://{1}.{2}.{3}:{4}".format(
            self.vault_information["protocol"],
            self.vault_information["name"],
            self.vault_information["location"],
            self.vault_information["service"],
            self.vault_information["port"]
        )

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
            raise TypeError('The client must be an instance of hvac.Client.')
        self._client = new_value

    def read_kv_secret(self, secret=None):
        if secret is None:
            raise ValueError('Secret name must be provided.')

        try:
            secret_kv = self.client.read(path="secret/{0}".format(secret))
            if not isinstance(secret_kv, dict):
                raise ValueError('Unable to read secret "{0}".'.format(str(secret)))
            secret_data = secret_kv.get('data', None)
            secret_value = secret_data.get('value', None)
            if secret_value is not None:
                return secret_value
            else:
                raise ValueError('Secret {0} is not defined.'.format(secret))
        except hvac.exceptions.Forbidden as f:
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
                Logger.log(
                    'Unable to unwrap Token!! Token: {0}. Error: {1}.'.format(wrapped_token, str(f)),
                    security_related=True
                )
                raise

            if temp_unwrap is None:
                raise TypeError('Unwrap unsuccessful. The authentication failed.')

            _auth = temp_unwrap.get('auth', None)

        _token = _auth.get('client_token', None)
        if _auth is None or _token is None:
            Logger.log(temp_unwrap, security_related=True)
            raise ValueError('The unwrapped value is not an authentication token.')

        try:
            self.client = hvac.Client(url=self.fqdn, token=_token)
        except Exception:
            raise
