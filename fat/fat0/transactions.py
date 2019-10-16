import json
import hashlib
from datetime import datetime as dt
from dataclasses import dataclass
from dataclasses import field as data_field
from typing import List, Tuple
from factom_keys.fct import FactoidPrivateKey, FactoidAddress


class InvalidTransactionError(Exception):
    pass


class MissingRequiredParameter(Exception):
    def __init__(self):
        super.__init__(self, "Requires either chain_id or token_id AND issuer_id.")


class InvalidChainIDError(ValueError):
    pass


class InvalidParamError(ValueError):
    pass


class InvalidFactoidKey(ValueError):
    pass


@dataclass
class Transaction:
    inputs: dict = data_field(default_factory=dict)
    outputs: dict = data_field(default_factory=dict)
    metadata: dict = data_field(default_factory=dict)
    chainid: str = data_field(default_factory=str)
    timestamp: str = str(int(dt.utcnow().timestamp()))
    _signer_keys: List[FactoidPrivateKey] = data_field(init=False, default_factory=list)

    def add_input(self, address: FactoidAddress, amount: int) -> None:
        if not (isinstance(address, FactoidAddress) and isinstance(amount, int)):
            raise InvalidParamError("Incorrect address or amount!")
        self.inputs[address.to_string()] = amount

    def add_output(self, address: FactoidAddress, amount: int) -> None:
        if not (isinstance(address, FactoidAddress) and isinstance(amount, int)):
            raise InvalidParamError("Incorrect address or amount!")
        self.outputs[address.to_string()] = amount

    def add_signer(self, signer: FactoidPrivateKey) -> None:
        if not isinstance(signer, FactoidPrivateKey):
            raise InvalidParamError("Not a factoid private key!")

        self._signer_keys.append(signer)

    def set_metadata(self, data: dict) -> None:
        self.metadata = data

    def set_chainid(self, chainid: str) -> None:
        if not isinstance(chainid, str):
            raise InvalidChainIDError
        self.chainid = chainid

    def is_valid(self) -> bool:
        """
        Check transaction for various error conditions.

        :return: a bool representing whether the transaction is valid or not.
        """
        # Check that we have a private key for every input.
        if len(self.inputs) > len(self._signer_keys):
            return False
        elif len(self.inputs) < len(self._signer_keys):
            return False

        # Check that inputs and outputs are not empty.
        if not self.inputs and self.outputs:
            return False

        if not self.chainid:
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

    def build_content(self) -> bytes:
        content = {}

        content["inputs"] = self.inputs
        content["outputs"] = self.outputs

        if self.metadata:
            content["metadata"] = self.metadata

        # Including separators removes whitespace.
        return json.dumps(content, separators=(",", ":"))

    def sign(self) -> Tuple[List[bytes], bytes]:
        """
        Sign all transaction.

        :return: a tuple of the extids and the content: ([extids], content)
        """
        if not self.is_valid():
            raise InvalidTransactionError

        extids = [self.timestamp.encode()]

        content = self.build_content()
        # print(content.encode().hex())

        chainid = bytes.fromhex(self.chainid)
        # print(content.encode().hex())

        for i, signer in enumerate(self._signer_keys):
            # Create message hash
            message = bytearray()
            message.extend(str(i).encode())
            message.extend(self.timestamp.encode())
            message.extend(chainid)
            message.extend(content.encode())
            message_hash = hashlib.sha512(message).digest()

            # Get and append rcd and signature
            extids.append(b"\x01" + signer.get_factoid_address().key_bytes)
            print(b"\x01" + signer.get_factoid_address().key_bytes)
            extids.append(signer.sign(message_hash))

        return (extids, content)
