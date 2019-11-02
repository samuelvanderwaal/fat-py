import sys
import json
import hashlib
from datetime import datetime as dt
from dataclasses import dataclass, field
from typing import List, Tuple, Union
from .errors import InvalidParamError, InvalidChainIDError, InvalidTransactionError
sys.path.insert(0, '/home/samuel/Coding/factom-keys/')
from factom_keys.fct import FactoidPrivateKey, FactoidAddress
from factom_keys.serverid import ServerIDPrivateKey


@dataclass
class Transaction:
    inputs: dict = field(default_factory=dict)
    outputs: dict = field(default_factory=dict)
    metadata: dict = field(default_factory=dict)
    chain_id: str = field(default_factory=str)
    timestamp: str = str(int(dt.utcnow().timestamp()))
    _signer_keys: List[FactoidPrivateKey] = field(init=False, default_factory=list)
    _ext_ids: list = None
    _content: bytes = None

    def add_input(self, address: FactoidAddress, amount: int) -> None:
        if not (isinstance(address, FactoidAddress) and isinstance(amount, int)):
            raise InvalidParamError("Incorrect address or amount!")
        self.inputs[address.to_string()] = amount

    def add_output(self, address: FactoidAddress, amount: int) -> None:
        if not (isinstance(address, FactoidAddress) and isinstance(amount, int)):
            raise InvalidParamError("Incorrect address or amount!")
        self.outputs[address.to_string()] = amount

    def add_signer(self, signer: Union[FactoidPrivateKey, ServerIDPrivateKey]) -> None:
        if not (isinstance(signer, FactoidPrivateKey) or isinstance(signer, ServerIDPrivateKey)):
            raise InvalidParamError("Not a factoid private key!")

        self._signer_keys.append(signer)

    def set_metadata(self, data: dict) -> None:
        self.metadata = data

    def set_chain_id(self, chain_id: str) -> None:
        if not isinstance(chain_id, str):
            raise InvalidChainIDError
        self.chain_id = chain_id

    def is_valid(self) -> bool:
        """
        Check transaction for various error conditions.

        :return: a bool representing whether the transaction is valid or not.
        """
        # Check that we have a private key for every input.
        if not (len(self.inputs) == len(self._signer_keys)):
            return False

        # Check that inputs and outputs are not empty.
        if not self.inputs and self.outputs:
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
        # If only one input and it's the coinbase address
        return (len(self.inputs) == 1 and
                "FA1zT4aFpEvcnPqPCigB3fvGu4Q4mTXY22iiuV69DqE1pNhdF2MC" in self.inputs)

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

        ext_ids = [self.timestamp.encode()]
        content = self.build_content()
        chain_id = bytes.fromhex(self.chain_id)

        for i, signer in enumerate(self._signer_keys):
            # Create message hash
            message = bytearray()
            message.extend(str(i).encode())
            message.extend(self.timestamp.encode())
            message.extend(chain_id)
            message.extend(content)
            message_hash = hashlib.sha512(message).digest()

            # Get and append rcd and signature
            if self.is_mint():
                print("here")
                ext_ids.append(b"\x01" + signer.get_public_key().key_bytes)
            else:
                ext_ids.append(b"\x01" + signer.get_factoid_address().key_bytes)
            ext_ids.append(signer.sign(message_hash))

        self._ext_ids = ext_ids
        self._content = content
