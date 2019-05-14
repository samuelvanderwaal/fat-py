from . import session
from .exceptions import MissingRequiredParameter


class Fat:
    def __init__(self, url):
        self._api = BaseApi(url)
        self._daemon = Daemon(api=self._api)
        self._rpc = Rpc(api=self._api)

    @property
    def daemon(self):
        return self._daemon

    @property
    def rpc(self):
        return self._rpc


class BaseApi:
    def __init__(self, url):
        self.url = url

    def call(self, method, params=None):
        payload = {"jsonrpc": "2.0", "method": method,
                   "params": params, "id": 1}

        response = session.post(self.url, json=payload)
        return response.json()


class Rpc:
    def __init__(self, api: BaseApi):
        self.api = api

    @staticmethod
    def check_id_params(chain_id, token_id, issuer_id):
        if chain_id:
            return {"chainid": chain_id}
        elif token_id and issuer_id:
            return {"tokenid": token_id, "issuerid": issuer_id}
        else:
            raise MissingRequiredParameter("Requires either chain_id or token_id AND issuer_id.")

    def get_issuance(self, chain_id=None, token_id=None, issuer_id=None):
        params = Rpc.check_id_params(chain_id, token_id, issuer_id)
        return self.api.call(method="get-issuance", params=params)

    def get_transaction(self, entry_hash, chain_id=None, token_id=None, issuer_id=None):
        params = Rpc.check_id_params(chain_id, token_id, issuer_id)
        params["entryhash"] = entry_hash
        return self.api.call(method="get-transaction", params=params)

    def get_transactions(self, addresses, chain_id=None, token_id=None, issuer_id=None):
        params = Rpc.check_id_params(chain_id, token_id, issuer_id)
        params["addresses"] = addresses

        return self.api.call(method="get-transactions", params=params)

    def get_balance(self, address, chain_id=None, token_id=None, issuer_id=None):
        params = Rpc.check_id_params(chain_id, token_id, issuer_id)
        params["address"] = address
        return self.api.call(method="get-balance", params=params)


class Daemon:
    def __init__(self, api: BaseApi):
        self.api = api

    def get_tokens(self):
        return self.api.call(method="get-daemon-tokens")

    def get_properties(self):
        return self.api.call(method="get-daemon-properties")

    def get_sync_status(self):
        return self.api.call(method="get-sync-status")
