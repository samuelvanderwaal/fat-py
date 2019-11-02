import sys
import re
import math
import time
import json
from hashlib import sha256, sha512
from dataclasses import dataclass, field
from typing import List, Tuple
from datetime import timezone
from datetime import datetime as dt
from .errors import InvalidParamError, InvalidTransactionError, MissingRequiredParameter
sys.path.insert(0, '/home/samuel/Coding/factom-keys/')
sys.path.insert(0, '/home/samuel/Coding/factom-core')
from factom_keys.serverid import ServerIDPrivateKey
from factom_keys.ec import ECAddress, ECPrivateKey
from factom_core.block_elements import ChainCommit, Entry, EntryCommit


@dataclass
class Issuance:
    _token_id: str = ""
    _issuer_id: str = ""
    _supply: int = 0
    _symbol: str = ""
    _metadata: dict = field(default_factory=dict)
    _ec_address: ECAddress = field(default_factory=str)
    _ec_priv_key: ECPrivateKey = field(default_factory=str)
    _server_priv_key: ServerIDPrivateKey = field(default_factory=str)
    _timestamp: float = dt.now(timezone.utc).timestamp()

    @property
    def token_id(self):
        return self._token_id

    @token_id.setter
    def token_id(self, token_id):
        if not isinstance(token_id, str):
            raise InvalidParamError("Token ID must be a string!")
        self._token_id = token_id

    @property
    def issuer_id(self):
        return self._issuer_id

    @issuer_id.setter
    def issuer_id(self, issuer_id):
        if not isinstance(issuer_id, str):
            raise InvalidParamError("Issuer ID must be a string!")
        # Validate issuer id format
        if not (len(issuer_id) == 64 and issuer_id[0:6] == "888888"):
            raise InvalidParamError("Not a valid issuer ID!")
        self._issuer_id = issuer_id

    @property
    def supply(self):
        return self._supply

    @supply.setter
    def supply(self, supply):
        if not isinstance(supply, int):
            raise InvalidParamError("Supply must be type int!")
        if not (supply > 0 or supply == -1):
            raise InvalidParamError("Supply must be greater than 0 or equal to -1!")
        self._supply = supply
        return True

    @property
    def symbol(self):
        return self._symbol

    @symbol.setter
    def symbol(self, symbol: str) -> bool:
        if not isinstance(symbol, str):
            raise InvalidParamError("Symbol must be type str!")
        # Regex check for characters A-Z and 1-4 in length.
        if not re.fullmatch(r"[A-Z]{1,4}", symbol.upper()):
            raise InvalidParamError("Symbol must be 1-4 characters of the set [A-Z].")
        self._symbol = symbol
        return True

    @property
    def metadata(self):
        return self._metadata

    @metadata.setter
    def metadata(self, metadata):
        if not isinstance(metadata, dict):
            raise InvalidParamError
        self._metadata = metadata
        return True

    @property
    def ec_address(self):
        return self._ec_address

    @ec_address.setter
    def ec_address(self, ec_address):
        if not isinstance(ec_address, ECAddress):
            raise InvalidParamError
        self._ec_address = ec_address

    @property
    def server_priv_key(self):
        return self._server_priv_key

    @server_priv_key.setter
    def server_priv_key(self, server_priv_key):
        if not isinstance(server_priv_key, ServerIDPrivateKey):
            raise InvalidParamError
        self._server_priv_key = server_priv_key
        return True

    @property
    def ec_priv_key(self):
        return self._ec_priv_key

    @ec_priv_key.setter
    def ec_priv_key(self, ec_priv_key):
        if not isinstance(ec_priv_key, ECPrivateKey):
            raise InvalidParamError
        self._ec_priv_key = ec_priv_key
        return True

    def is_valid(self) -> bool:

        # Check that we have all required parameters
        if not (self._token_id and self._issuer_id and self._supply and self._ec_priv_key and self._server_priv_key):
            return False
        return True

    def build_init_content(self) -> bytes:
        content = {}
        content["type"] = "FAT-0"
        content["supply"] = self.supply

        if self.symbol:
            content["symbol"] = self.symbol
        if self.metadata:
            content["metadata"] = self.metadata

        return json.dumps(content, separators=(",", ":")).encode()

    def create_chain_id(self) -> bytes:
        if not (self.token_id and self.issuer_id):
            raise MissingRequiredParameter("Missing token_id and/or issuer_id!")

        ext_ids = [b"token", self.token_id.encode(), b"issuer", bytes.fromhex(self.issuer_id)]
        ext_ids_hash = [sha256(x).digest() for x in ext_ids]
        chain_id = sha256(b''.join([x for x in ext_ids_hash])).digest()
        self.chain_id = chain_id

    def calculate_num_ec(self, content, ext_ids) -> int:
        # 10 EC for the chain + 1 for each kb of data in the entry
        # round up to nearest entry credit
        content_kb = len(content)/1024
        ext_ids_kb = len(b"".join(ext_ids))/1024
        ecs = math.ceil(content_kb + ext_ids_kb)
        return ecs

    def create_chain(self, factomd, ext_ids, content, sleep):
        self.create_chain_id()
        chain_id_hash = sha256(sha256(self.chain_id).digest()).digest()

        entry = Entry(self.chain_id, ext_ids, content)
        entry_hash = entry.entry_hash
        entry_bytes = entry.marshal()

        commit_weld = sha256(sha256(entry_hash + self.chain_id).digest()).digest()

        # Creating a chain is 10 + the amount needed for the entry
        ec_spent = 10 + self.calculate_num_ec(content, ext_ids)
        ec_public_key = self.ec_address.key_bytes

        # Convert timestamp to milliseconds and represent by six bytes, MSB to the left.
        self.milli_timestamp = int(self._timestamp * 1000).to_bytes(6, "big")

        chain_commit = ChainCommit(
            self.milli_timestamp,
            chain_id_hash,
            commit_weld,
            entry_hash,
            ec_spent,
            ec_public_key
        )

        chain_commit.signature = self.ec_priv_key.sign(chain_commit.marshal_for_signature())
        message = chain_commit.marshal()
        factomd.commit_chain(message)
        time.sleep(sleep)
        return factomd.reveal_chain(entry_bytes)

    def initialize_token(self, factomd, ext_ids, content, sleep):
        entry = Entry(self.chain_id, ext_ids, content)
        ec_spent = self.calculate_num_ec(content, ext_ids)

        entry_commit = EntryCommit(
            self.milli_timestamp,
            entry.entry_hash,
            ec_spent,
            self.ec_address.key_bytes
        )

        entry_commit.signature = self.ec_priv_key.sign(entry_commit.marshal_for_signature())
        message = entry_commit.marshal()
        factomd.commit_entry(message)
        time.sleep(sleep)
        return factomd.reveal_entry(entry.marshal())

    def issue_token(self, factomd, sleep: float = 2.0):
        if not self.is_valid():
            raise InvalidTransactionError

        ext_ids = [b"token", self.token_id.encode(), b"issuer", bytes.fromhex(self.issuer_id)]
        # content = self.build_init_content()
        content = "".encode()

        self.create_chain(factomd, ext_ids, content, sleep)

        time.sleep(3)

        # Initialization
        content = self.build_init_content()

        # Create message hash
        message = bytearray()
        message.extend("0".encode())
        message.extend(str(int(self._timestamp)).encode())
        message.extend(self.chain_id)
        message.extend(content)
        message_hash = sha512(message).digest()

        ext_ids = [str(int(self._timestamp)).encode()]
        # Get and append rcd and signature
        ext_ids.append(b"\x01" + self._server_priv_key.get_public_key().key_bytes)
        ext_ids.append(self._server_priv_key.sign(message_hash))

        return self.initialize_token(factomd, ext_ids, content, sleep)