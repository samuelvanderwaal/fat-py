from . import session
from .exceptions import MissingRequiredParameter
from factom import Factomd, FactomWalletd


class Client:
    def __init__(
                self,
                fatd_host: str = "http://localhost:8078/v1",
                factomd_host: str = "http://localhost:8088",
                walletd_host: str = "http://localhost:8089"
                ):
        self._api = BaseApi(fatd_host)
        self._daemon = Daemon(api=self._api)
        self._rpc = Rpc(api=self._api)
        # self._fat0 = Fat0(api=self._api)
        # self._fat1 = Fat1(api=self._api)
        self._factomd = Factomd(host=factomd_host)
        self._walletd = FactomWalletd(host=walletd_host)

    @property
    def daemon(self):
        return self._daemon

    @property
    def rpc(self):
        return self._rpc

    # @property
    # def fat0(self):
    #     return self._fat0
    # @property
    # def fat1(self):
    #     return self.fat1

    def initialize_token(self, supply: int, symbol: str = None, metadata=None):
        pass

    def issue_token(self, inputs: dict, outputs: dict, metadata=None):
        pass

    def send_transaction(self, inputs: dict, outputs: dict, metadata=None):
        pass

    def get_fat0_balance(self, address, chain_id=None, token_id=None, issuer_id=None):
        response = self.rpc.get_balance(address, chain_id, token_id, issuer_id)
        try:
            return response["result"]
        except KeyError:
            return response["error"]

    def get_fat1_balance(self, address, chain_id=None, token_id=None, issuer_id=None):
        response = self.rpc.get_nf_balance(address, chain_id, token_id, issuer_id)
        try:
            return response["result"]
        except KeyError:
            return f"Error: {response['error']}"


class BaseApi:
    def __init__(self, fatd_host):
        self.url = fatd_host

    def call(self, method, params=None):
        payload = {"jsonrpc": "2.0", "method": method,
                   "params": params, "id": 1}

        response = session.post(self.url, json=payload)
        return response.json()


class Fat0:
    def __init__(self, api: BaseApi):
        self.api = api

    @staticmethod
    def check_id_params(chain_id: str, token_id: str, issuer_id: str):
        if chain_id:
            return {"chainid": chain_id}
        elif token_id and issuer_id:
            return {"tokenid": token_id, "issuerid": issuer_id}
        else:
            raise MissingRequiredParameter("Requires either chain_id or token_id AND issuer_id.")


class Fat1:
    def __init__(self, api: BaseApi):
        self.api = api


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

    def get_transactions(self, nf_token_id=None, addresses=None, tofrom=None, entry_hash=None,
                         page=None, limit=None, order=None, chain_id=None, token_id=None,
                         issuer_id=None):
        params = Rpc.check_id_params(chain_id, token_id, issuer_id)
        if nf_token_id:
            params["nftokenid"] = nf_token_id
        if addresses:
            params["addresses"] = addresses
        if tofrom:
            params["tofrom"] = tofrom
        if entry_hash:
            params["entryhash"] = entry_hash
        if page:
            params["page"] = page
        if limit:
            params["limit"] = limit
        if order:
            params["order"] = order
        return self.api.call(method="get-transactions", params=params)

    def get_balance(self, address, chain_id=None, token_id=None, issuer_id=None):
        params = Rpc.check_id_params(chain_id, token_id, issuer_id)
        params["address"] = address
        return self.api.call(method="get-balance", params=params)

    def get_nf_balance(self, address, chain_id=None, token_id=None, issuer_id=None):
        params = Rpc.check_id_params(chain_id, token_id, issuer_id)
        params["address"] = address
        return self.api.call(method="get-nf-balance", params=params)

    def get_nf_token(self, nf_token_id, chain_id=None, token_id=None, issuer_id=None):
        params = Rpc.check_id_params(chain_id, token_id, issuer_id)
        params["nftokenid"] = nf_token_id
        return self.api.call(method="get-nf-token", params=params)

    def get_nf_tokens(self, page=None, limit=None, order=None, chain_id=None,
                      token_id=None, issuer_id=None):
        params = Rpc.check_id_params(chain_id, token_id, issuer_id)
        if page:
            params["page"] = page
        if limit:
            params["limit"] = limit
        if order:
            params["order"] = order
        print(params)
        return self.api.call(method="get-nf-tokens", params=params)

    def get_stats(self, chain_id=None, token_id=None, issuer_id=None):
        params = Rpc.check_id_params(chain_id, token_id, issuer_id)
        return self.api.call(method="get-stats", params=params)

    def send_transaction(self, extids, content, chain_id=None, token_id=None, issuer_id=None):
        params = Rpc.check_id_params(chain_id, token_id, issuer_id)
        params["extids"] = extids
        params["content"] = content
        return self.api.call(method="send-transaction", params=params)


class Daemon:
    def __init__(self, api: BaseApi):
        self.api = api

    def get_tokens(self):
        return self.api.call(method="get-daemon-tokens")

    def get_properties(self):
        return self.api.call(method="get-daemon-properties")

    def get_sync_status(self):
        return self.api.call(method="get-sync-status")
