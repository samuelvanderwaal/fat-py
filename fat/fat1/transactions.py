import json
import hashlib
from datetime import datetime as dt, timezone as tz
from typing import List, Tuple, Union
from fat.errors import InvalidParam, InvalidChainID, InvalidTransaction
from factom_keys.fct import FactoidPrivateKey, FactoidAddress
from factom_keys.serverid import ServerIDPrivateKey


class Transaction:
    def __init__(self, inputs=None, outputs=None, metadata=None, chain_id=None, signers=None):
        self._timestamp = str(int(dt.now(tz.utc).timestamp()))

        self.inputs = {}
        self.outputs = {}
        self.signers = []
        self.metadata = metadata
        self.chain_id = chain_id

        if inputs:
            for address, amount in inputs.items():
                self.add_input(address, amount)

        if outputs:
            for address, amount in outputs.items():
                self.add_output(address, amount)

        if chain_id:
            self.set_chain_id(chain_id)

        if signers:
            for s in signers:
                self.add_signer(s)

    def add_input(self, address: Union[FactoidAddress, str], amount: list) -> None:
        """
        Create an input entry from an address and amount.

        :param address: the factoid input address as a str or FactoidAddress object
        :param amount: the factoid input amount as a n int
        """

        address = Transaction.validate_address(address)
        self.validate_amount(amount)
        self.inputs[address] = amount
        return self

    def add_output(self, address: Union[FactoidAddress, str], amount: list) -> None:
        """
        Create an output entry from an address and amount.

        :param address: the factoid output address as a str or FactoidAddress object
        :param amount: the factoid output amount as a n int
        """

        address = Transaction.validate_address(address)
        self.validate_amount(amount)
        self.outputs[address] = amount
        return self

    def add_signer(self, signer: Union[FactoidPrivateKey, ServerIDPrivateKey, str]) -> None:
        """
        Add a signing key to the transaction.

        :param signer: the private key for an input Factoid address or the private key for the issuing ID
        """

        self.signers.append(self.validate_signer(signer))
        return self

    def set_metadata(self, data: dict) -> None:
        """
        Set a metadata value for the transaction.

        :param data: the metadata value as a Python dict
        """

        self.metadata = data
        return self

    def set_chain_id(self, chain_id: str) -> None:
        """
        Set the chain id for the transaction.

        :param chain_id: the chain id to submit the transaction entry on as a str
        """

        if not isinstance(chain_id, str):
            raise InvalidChainID
        self.chain_id = chain_id
        return self

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
    def validate_amount(amount: list):
        if not isinstance(amount, list):
            raise InvalidParam("Invalid amount!")

        for entry in amount:
            if not (isinstance(entry, dict) or isinstance(entry, int)):
                raise InvalidParam("Invalid amount!")

    def validate_signer(
        self, signer: Union[FactoidPrivateKey, ServerIDPrivateKey, str]
    ) -> Union[FactoidPrivateKey, ServerIDPrivateKey]:
        """
        Validate a privatekey and convert it to a str.

        :param signer: a signing key as a FactoidPrivateKey, ServerIDPrivateKey or a str
        """

        if self.is_mint():
            if isinstance(signer, str):
                signer = ServerIDPrivateKey(signer)
            elif isinstance(signer, ServerIDPrivateKey):
                pass
            else:
                raise InvalidParam("Invalid signer key for transaction type!")
        else:
            if isinstance(signer, str):
                signer = FactoidPrivateKey(signer)
            elif isinstance(signer, FactoidPrivateKey):
                pass
            else:
                raise InvalidParam("Invalid signer key for transaction type!")
        return signer

    def is_valid(self) -> bool:
        """
        Check transaction for various error conditions.

        :return: a bool representing whether the transaction is valid or not.
        """

        # Check that we have a private key for every input.
        if not (len(self.inputs) == len(self.signers)):
            return False

        # Check that inputs and outputs are not empty.
        if not (self.inputs and self.outputs):
            return False

        if not self.chain_id:
            return False

        return True

    def is_mint(self) -> bool:
        """
        Check if transaction mints new coins from coinbase.
        :return: a bool representing whether the transaction is a mint type or not.
        """

        # If only one input and it is the coinbase address
        return len(self.inputs) == 1 and "FA1zT4aFpEvcnPqPCigB3fvGu4Q4mTXY22iiuV69DqE1pNhdF2MC" in self.inputs

    def build_content(self) -> dict:
        """
        Build entry content.

        :return: entry content as bytes.
        """

        content = {}

        content["inputs"] = self.inputs
        content["outputs"] = self.outputs

        if self.metadata:
            content["metadata"] = self.metadata

        # Including separators removes whitespace.
        return json.dumps(content, separators=(",", ":")).encode()

    def sign(self) -> Tuple[List[bytes], bytes]:
        """
        Sign transaction and create ext_ids and content.

        :return: a tuple of the extids and the content: ([extids], content)
        """

        if not self.is_valid():
            raise InvalidTransaction

        ext_ids = [self._timestamp.encode()]
        content = self.build_content()
        chain_id = bytes.fromhex(self.chain_id)

        for i, signer in enumerate(self.signers):
            # Create message hash
            message = bytearray()
            message.extend(str(i).encode())
            message.extend(self._timestamp.encode())
            message.extend(chain_id)
            message.extend(content)
            message_hash = hashlib.sha512(message).digest()

            # Get and append rcd and signature
            if self.is_mint():
                ext_ids.append(b"\x01" + signer.get_public_key().key_bytes)
            else:
                ext_ids.append(b"\x01" + signer.get_factoid_address().key_bytes)
            ext_ids.append(signer.sign(message_hash))

        self._ext_ids = ext_ids
        self._content = content
