import hvac


class VaultServer:

    def __init__(
        self,
        name=None,
        location="eastus",
        service="cloudapp.azure.com",
        protocol="http",
        port=18200,
        token=None
    ):
        if name is None:
            raise ValueError('Server name cannot be None.')
        self.name = name
        self.location = location
        self.service = service
        self.protocol = protocol
        self.port = port
        self._token = token

    @property
    def fqdn(self):
        return "{0}://{1}.{2}.{3}:{4}".format(
            self.protocol,
            self.name,
            self.location,
            self.service,
            self.port
        )

    @property
    def token(self):
        return self._token

    @token.setter
    def token(self, v):
        self._token = v


the_vault = VaultServer(
    name="dasander-azure-gen",
    location="eastus",
    service="cloudapp.azure.com",
    protocol="http",
    port=18200
)

print('Vault server is {0}'.format(the_vault.fqdn))
print('Connecting...')
client=hvac.Client(url=the_vault.fqdn)
wrapped="a6570dbd-6cf1-2153-141a-3b86345801c4"
try:
    tok = client.unwrap('{0}'.format(wrapped))['auth']['client_token']
    # print(tok['auth']['client_token'])
    client = hvac.Client(url=the_vault.fqdn, token=tok)

    print('Connected. Validating authorization')
    assert client.is_authenticated()
    print('Authorized')
    foo = client.read(path="secret/foo")
    print('foo: {0}'.format(foo['data']))
except hvac.exceptions.Forbidden:
    print()
    print('**** SECURITY LOG')
    print('     ' +
          'The wrapped token {0} is invalid (likely already used)! '.format(wrapped) +
          'It may have been intercepted.'
          )
    print('**** SECURITY LOG')

