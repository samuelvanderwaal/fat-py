import random
import string
from typing import Union
from urllib.parse import urljoin
from .fat0.transactions import Transaction
from .errors import handle_error_response, InvalidParam, MissingRequiredParameter
from .session import APISession
from factom_keys.fct import FactoidAddress


class BaseAPI(object):
    def __init__(self, ec_address=None, fct_address=None, host=None, username=None, password=None, certfile=None):
        """
        Instantiate a new API client.
        Args:
            ec_address (str): A default entry credit address to use for
                transactions. Credits will be spent from this address.
            fct_address (str): A default factoid address to use for
                transactions.
            host (str): Hostname, including http(s)://, of the node
            username (str): RPC username for protected APIs.
            password (str): RPC password for protected APIs.
            certfile (str): Path to certificate file to verify for TLS
                connections (mostly untested).
        """
        self.ec_address = ec_address
        self.fct_address = fct_address
        self.version = "v1"

        if host:
            self.host = host

        self.session = APISession()

        if username and password:
            self.session.init_basic_auth(username, password)

        if certfile:
            self.session.init_tls(certfile)

    @property
    def url(self):
        return urljoin(self.host, self.version)

    @staticmethod
    def _xact_name():
        return "TX_{}".format("".join(random.choices(string.ascii_uppercase + string.digits, k=6)))

    def _request(self, method, params=None, request_id: int = 0):
        data = {"jsonrpc": "2.0", "id": request_id, "method": method}
        if params:
            data["params"] = params

        resp = self.session.request("POST", self.url, json=data)
        print(f"Resp status code: {resp.status_code}")
        print(f"Response: {resp.json()}")
        if resp.status_code >= 400:
            handle_error_response(resp)

        return resp.json()


class FATd(BaseAPI):
    def __init__(self, ec_address=None, fct_address=None, host=None, username=None, password=None, certfile=None):
        tmp_host = host if host is not None else "http://localhost:8078"
        super().__init__(ec_address, fct_address, tmp_host, username, password, certfile)

    # RPC methods
    def get_issuance(self, chain_id=None, token_id=None, issuer_id=None):
        """Get the issuance entry for a token."""
        params = FATd.check_id_params(chain_id, token_id, issuer_id)
        return self._request("get-issuance", params)

    def get_transaction(self, entry_hash, chain_id=None, token_id=None, issuer_id=None):
        """Get a valid FAT transaction for a token."""
        params = FATd.check_id_params(chain_id, token_id, issuer_id)
        params["entryhash"] = entry_hash
        return self._request("get-transaction", params)

    def get_transactions(self, chain_id=None, token_id=None, issuer_id=None, nf_token_id=None, addresses=None,
                         to_from=None, entry_hash=None, page=None, limit=None, order=None):
        """
        Get time ordered valid FAT transactions for a token, or token address, non-fungible token ID,
        or a combination.
        """
        params = FATd.check_id_params(chain_id, token_id, issuer_id)
        param_list = {"nf_token_id": "nftokenid", "addresses": "addresses", "to_from": "tofrom",
                      "entry_hash": "entryhash", "page": "page", "limit": "limit",
                      "order": "order"
                      }

        # Check all params provided to the function against the param_list and if present,
        # add them to the params dict.
        for arg, value in locals().copy().items():
            if arg in param_list and value is not None:
                param = param_list[arg]
                params[param] = value

        return self._request("get-transactions", params)

    def get_balance(self, address, chain_id=None, token_id=None, issuer_id=None):
        """Get the balance of an address for a token."""
        params = FATd.check_id_params(chain_id, token_id, issuer_id)
        params["address"] = address
        return self._request("get-balance", params)

    def get_nf_balance(self, address, chain_id=None, token_id=None, issuer_id=None):
        """Get the tokens belonging to an address on a non-fungible token."""
        params = FATd.check_id_params(chain_id, token_id, issuer_id)
        params["address"] = address
        return self._request("get-nf-balance", params)

    def get_stats(self, chain_id=None, token_id=None, issuer_id=None):
        """Get overall statistics for a token."""
        params = FATd.check_id_params(chain_id, token_id, issuer_id)
        return self._request("get-stats", params)

    def get_nf_token(self, nf_token_id, chain_id=None, token_id=None, issuer_id=None):
        """Get a non fungible token by ID. The token belong to non fungible token class."""
        params = FATd.check_id_params(chain_id, token_id, issuer_id)
        params["nftokenid"] = nf_token_id
        return self._request("get-nf-token", params)

    def get_nf_tokens(self, chain_id=None, token_id=None, issuer_id=None, page=None, limit=None, order=None):
        """List all issued non fungible tokens in circulation"""
        params = FATd.check_id_params(chain_id, token_id, issuer_id)
        param_list = ["page", "limit", "order"]

        # Check all params provided to the function against the param_list and if present,
        # add them to the params dict.
        for arg, value in locals().copy().items():
            if arg in param_list and value is not None:
                params[arg] = value
        print(f"params: {params}")
        return self._request("get-nf-tokens", params)

    def send_transaction(self, ext_ids, content, chain_id=None, token_id=None, issuer_id=None):
        """Send A FAT transaction to a token."""
        params = FATd.check_id_params(chain_id, token_id, issuer_id)
        params["extids"] = ext_ids
        params["content"] = content
        return self._request("send-transaction", params)

    # Daemon methods
    def get_daemon_tokens(self):
        """Get the list of FAT tokens the daemon is currently tracking."""
        return self._request("get-daemon-tokens")

    def get_daemon_properties(self):
        return self._request("get-daemon-properties")

    def get_sync_status(self):
        """Retrieve the current sync status of the node."""
        return self._request("get-sync-status")

    def get_balances(self, address: Union[FactoidAddress, str]):
        """
        Get all balances for all tracked tokens of a public Factoid address.

        :param address: a public Factoid Address of type factom-keys.FactoidAddress
        :return: JSON response from fatd request "get-balances"
        """
        address = FATd.validate_address(address)
        return self._request("get-balances", {"address": address})

    def submit_transaction(self, tx: Transaction):
        """Convenience function that sends a Transaction object through the "send-transaction" RPC call."""
        return self._request(
            "send-transaction",
            {
                "chainid": bytes.fromhex(tx.chain_id).hex(),
                "extids": [x.hex() for x in tx._ext_ids],
                "content": tx._content.hex(),
            },
        )

    @staticmethod
    def validate_address(address: Union[FactoidAddress, str]) -> str:
        """
        Validate a Factoid address and convert to a str.

        :param address: a Factoid address as a str or a FactoidAddress object
        """

        if isinstance(address, FactoidAddress):
            address = address.to_string()
        elif isinstance(address, str):
            address = FactoidAddress(address_string=address).to_string()
        else:
            raise InvalidParam("Invalid address!")
        return address

    @staticmethod
    def check_id_params(chain_id, token_id, issuer_id):
        if chain_id:
            return {"chainid": chain_id}
        elif token_id and issuer_id:
            return {"tokenid": token_id, "issuerid": issuer_id}
        else:
            raise MissingRequiredParameter("Requires either chain_id or token_id AND issuer_id.")
