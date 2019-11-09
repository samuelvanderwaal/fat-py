import sys
from base64 import b64decode
from pytest import fixture
from fat.fat1.transactions import Transaction
from factom_keys.fct import FactoidPrivateKey, FactoidAddress
sys.path.insert(0, '/home/samuel/Coding/factom-keys')
from factom_keys.serverid import ServerIDPrivateKey


class TestTransaction:
    @classmethod
    def setup(cls):
        # These are throwaway private keys.
        cls.chain_id = "1e5037be95e108c34220d724763444098528e88d08ec30bc15204c98525c3f7d"
        cls.coinbase_address = "FA1zT4aFpEvcnPqPCigB3fvGu4Q4mTXY22iiuV69DqE1pNhdF2MC"
        cls.address1 = FactoidAddress(address_string="FA2gCmih3PaSYRVMt1jLkdG4Xpo2koebUpQ6FpRRnqw5FfTSN2vW")
        cls._private_fct_key1 = FactoidPrivateKey(key_string="Fs1fR4dMNdyp1a6qYfkLFPJZUyRg1uFW3b6NEK9VaRELD4qALstq")
        cls.address2 = FactoidAddress(address_string="FA3j68XNwKwvHXV2TKndxPpyCK3KrWTDyyfxzi8LwuM5XRuEmhy6")
        cls._private_fct_key2 = FactoidPrivateKey(key_string="Fs2jSmXgaysrqiADPmAvvb71NfAa9MqvXvRemozTE8LRc64hLqtf")
        cls.address3 = FactoidAddress(address_string="FA3rsxWx4WSN5Egj2ZxPoju1mzwfjBivTDMcEvoC1JSsqkddZPCB")
        cls._private_fct_key3 = FactoidPrivateKey(key_string="Fs2EDKpBA4QQgarTUhJnZeZ4HeymT5U6RSWGsoTtkt1ezGCmNdSo")
        cls._issuer_signer = ServerIDPrivateKey(key_string="sk12hDMpMzcm9XEdvcy77XwxYU57hpLoCMY1kHtKnyjdGWUpsAvXD")

    @fixture
    def tx1(self) -> Transaction:
        tx = Transaction()
        tx.set_chain_id(self.chain_id)
        tx.add_input(self.coinbase_address, [10])
        tx.add_output(self.address1, [10])
        tx.add_signer(self._issuer_signer)
        return tx

    @fixture
    def tx1_extids(self) -> list:
        # Values pulled from explorer:
        # https://explorer.factoid.org/entry?hash=4cbd9ea30064ea772d74bae008720be74c9f60d5dddb1c3eae9647a0f9f154e6
        timestamp = "1557879692".encode()
        rcd0 = b64decode("AUCUKWQqyS7HtHiLGRN2iEiWP1sE7zSMAuHxvvzA5XD6")
        signature0 = b64decode(
            "u7SWjhTiE9CldCRWqeYk+BECKpCgYaO7S0IXyEIltzB/MDDeQAFvvChyx6sj1OLLFF6k8afGTiRws14XUx75AQ=="
        )
        return [timestamp, rcd0, signature0]

    # @fixture
    # def tx2(self) -> Transaction:
    #     tx = Transaction()
    #     tx.add_input(self.address1, 50)
    #     tx.add_input(self.address2, 100)
    #     tx.add_output(self.address3, 150)
    #     tx.add_signer(self._private_fct_key2)
    #     tx.add_signer(self._private_fct_key1)
    #     tx.set_chain_id(self.chain_id)
    #     return tx

    # @fixture
    # def tx2_extids(self) -> list:
    #     # Values pulled from explorer:
    #     # https://explorer.factoid.org/entry?hash=8279a10c9c26ce55ef29f382df4e8d4c31ce556f1c3efe4fbbd75ed396a56ef9
    #     timestamp = "1571166720".encode()
    #     rcd0 = b64decode("AXLmQ8mDpKyNC9xhrDe18NhwiG2pG3zdoKtejylwKIg6")
    #     signature0 = b64decode(
    #         "2ttzm02Vwn/hLv3wEUY1TipWbBRMJQ7BWkgM+0Zu+Ipe7hAiwAuk+ber3+vKylWWusYhpohPeHrLBOSt38ReDA=="
    #     )
    #     rcd1 = b64decode("AdCUH3BmZa2VGFRzcr8IzB8fUq4rQiPNoy8jw0zqIf6q")
    #     signature1 = b64decode(
    #         "lzSoUouLbw17i1pWgWToG96yl8t3WXCyiU4lYrzr42Uz2TMyZOEr4t+HaUezMJ2h7ZDdkDNuV7qKU/7v2w25Dw=="
    #     )
    #     return [timestamp, rcd0, signature0, rcd1, signature1]

    def test_transaction_values(self):
        tx = Transaction()
        tx.add_input(self.address1, [1])
        tx.add_input(self.address2, [10])
        assert len(tx.inputs) == 2

        tx.add_output(self.address3, [1, 10])
        assert len(tx.outputs) == 1

        tx.set_metadata({"note": "Goodbye and thanks for all the fish!"})
        assert len(tx.metadata) == 1

        tx.add_signer(self._private_fct_key1)
        tx.add_signer(self._private_fct_key2)
        assert len(tx.signers) == 2

        # Missing chain_id
        assert not tx.is_valid()

        tx.set_chain_id(self.chain_id)
        assert tx.is_valid()

    def test_transaction_signing_single_input(self, tx1, tx1_extids):
        # Override timestamp to match historical transactions
        tx1._timestamp = "1557879692"

        tx1.sign()

        actual_tx1_extids = tx1._ext_ids

        # add = FactoidPrivateKey(key_string="Fs1KWJrpLdfucvmYwN2nWrwepLn8ercpMbzXshd1g8zyhKXLVLWj")
        # a = FactoidPrivateKey(key_string="Fs2jSmXgaysrqiADPmAvvb71NfAa9MqvXvRemozTE8LRc64hLqtf")

        assert tx1_extids == actual_tx1_extids

    # def test_transaction_signing_multiple_input(self, tx2, tx2_extids):
    #     # Override timestamp to match historical transactions
    #     tx2._timestamp = "1571166720"

    #     tx2.sign()

    #     actual_tx2_extids = tx2._ext_ids

    #     # Skip comparing timestamps
    #     assert tx2_extids == actual_tx2_extids