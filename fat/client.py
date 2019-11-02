import sys
import random
import string
from urllib.parse import urljoin
from .fat0.transactions import Transaction
from .errors import handle_error_response
from .session import APISession
sys.path.insert(0, "/home/samuel/Coding/factom_keys")
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

    def get_sync_status(self):
        """Retrieve the current sync status of the node."""
        return self._request("get-sync-status")

    def get_daemon_properties(self):
        return self._request("get-daemon-properties")

    def get_balances(self, address: FactoidAddress):
        """
        Get all balances for all tracked tokens of a public Factoid address.

        :param address: a public Factoid Address of type factom-keys.FactoidAddress
        :return: JSON response from fatd request "get-balances"
        """
        return self._request("get-balances", {"address": address.to_string()})

    def send_transaction(self, tx: Transaction):
        return self._request(
            "send-transaction",
            {"chainid": bytes.fromhex(tx.chain_id).hex(), "extids": [x.hex() for x in tx._ext_ids], "content": tx._content.hex()},
        )
