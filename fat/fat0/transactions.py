import sys
import json
import hashlib
from datetime import datetime as dt, timezone as tz
from typing import List, Tuple, Union
from .errors import InvalidParamError, InvalidChainIDError, InvalidTransactionError

sys.path.insert(0, "/home/samuel/Coding/factom-keys/")
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

    def add_input(self, address: Union[FactoidAddress, str], amount: int) -> None:
        address = Transaction.validate_address(address)

        if not isinstance(amount, int):
            raise InvalidParamError("Incorrect address or amount!")

        self.inputs[address] = amount
        return self

    def add_output(self, address: Union[FactoidAddress, str], amount: int) -> None:
        address = Transaction.validate_address(address)

        if not isinstance(amount, int):
            raise InvalidParamError("Incorrect address or amount!")

        self.outputs[address] = amount
        return self

    def add_signer(self, signer: Union[FactoidPrivateKey, ServerIDPrivateKey, str]) -> None:
        self.signers.append(self.validate_signer(signer))
        return self

    def set_metadata(self, data: dict) -> None:
        self.metadata = data
        return self

    def set_chain_id(self, chain_id: str) -> None:
        if not isinstance(chain_id, str):
            raise InvalidChainIDError
        self.chain_id = chain_id
        return self

    @staticmethod
    def validate_address(address: Union[FactoidAddress, str]) -> str:
        if isinstance(address, FactoidAddress):
            address = address.to_string()
        elif isinstance(address, str):
            address = FactoidAddress(address_string=address).to_string()
        else:
            raise InvalidParamError("Invalid address!")
        return address

    def validate_signer(
        self, signer: Union[FactoidPrivateKey, ServerIDPrivateKey, str]
    ) -> Union[FactoidPrivateKey, ServerIDPrivateKey]:
        if self.is_mint():
            if isinstance(signer, str):
                signer = ServerIDPrivateKey(signer)
            elif isinstance(signer, ServerIDPrivateKey):
                pass
            else:
                raise InvalidParamError("Invalid signer key for transaction type!")
        else:
            if isinstance(signer, str):
                signer = FactoidPrivateKey(signer)
            elif isinstance(signer, FactoidPrivateKey):
                pass
            else:
                raise InvalidParamError("Invalid signer key for transaction type!")
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

        # Check that sum of inputs == sum of outputs
        inputs_sum = 0
        outputs_sum = 0

        for _, value in self.inputs.items():
            inputs_sum += value

        for _, value in self.outputs.items():
            outputs_sum += value

        if not inputs_sum == outputs_sum:
            return False

        return True

    def is_mint(self) -> bool:
        # If only one input and it is the coinbase address
        return len(self.inputs) == 1 and "FA1zT4aFpEvcnPqPCigB3fvGu4Q4mTXY22iiuV69DqE1pNhdF2MC" in self.inputs

    def build_content(self) -> dict:
        content = {}

        content["inputs"] = self.inputs
        content["outputs"] = self.outputs

        if self.metadata:
            content["metadata"] = self.metadata

        # Including separators removes whitespace.
        return json.dumps(content, separators=(",", ":")).encode()

    def sign(self) -> Tuple[List[bytes], bytes]:
        """
        Sign all transaction.

        :return: a tuple of the extids and the content: ([extids], content)
        """
        if not self.is_valid():
            raise InvalidTransactionError

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
