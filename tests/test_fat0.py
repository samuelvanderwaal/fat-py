from pytest import fixture
from fat.fat0.transactions import Transaction
from factom_keys.fct import FactoidPrivateKey, FactoidAddress


class TestTransactions:
    @classmethod
    def setup(cls):
        # These are throwaway private keys.
        cls.chainid = "145d5207a1ca2978e2a1cb43c97d538cd516d65cd5d14579549664bfecd80296"
        cls.address1 = FactoidAddress(address_string="FA2gCmih3PaSYRVMt1jLkdG4Xpo2koebUpQ6FpRRnqw5FfTSN2vW")
        cls._private_fct_key1 = FactoidPrivateKey(key_string="Fs1fR4dMNdyp1a6qYfkLFPJZUyRg1uFW3b6NEK9VaRELD4qALstq")
        cls.address2 = FactoidAddress(address_string="FA3j68XNwKwvHXV2TKndxPpyCK3KrWTDyyfxzi8LwuM5XRuEmhy6")
        cls._private_fct_key2 = FactoidPrivateKey(key_string="Fs2jSmXgaysrqiADPmAvvb71NfAa9MqvXvRemozTE8LRc64hLqtf")
        cls.address3 = FactoidAddress(address_string="FA3rsxWx4WSN5Egj2ZxPoju1mzwfjBivTDMcEvoC1JSsqkddZPCB")
        cls._private_fct_key3 = FactoidPrivateKey(key_string="Fs2EDKpBA4QQgarTUhJnZeZ4HeymT5U6RSWGsoTtkt1ezGCmNdSo")

    @fixture
    def tx1(self) -> Transaction:
        tx = Transaction()
        tx.set_chainid(self.chainid)
        tx.add_input(self.address3, 50)
        tx.add_output(self.address1, 50)
        tx.add_signer(self._private_fct_key3)
        return tx

    @fixture
    def tx1_extids(self) -> list:
        # Values pulled from explorer:
        # https://explorer.factoid.org/entry?hash=506278a53f299bc9941e7d576e61d6d216864703ef02310434182eb1481030c3
        timestamp = "1571180727".encode()
        rcd0 = bytes.fromhex("01670ef9d6ac00dd6ff74f826d8c33ca915fb7e569539728cade7b5f325c049c09")
        signature0 = bytes.fromhex(
            "774f789f612e80252ceb6f61624e0b0ccdd25cb115b33dc51a3fb9d667375834fb6eea7414e1f91d50a175d58f25d95797726b24e6f12edda2f0177abd0a800e"
        )
        return [timestamp, rcd0, signature0]

    @fixture
    def tx2(self) -> Transaction:
        tx = Transaction()
        tx.add_input(self.address1, 50)
        tx.add_input(self.address2, 100)
        tx.add_output(self.address3, 150)
        tx.add_signer(self._private_fct_key2)
        tx.add_signer(self._private_fct_key1)
        tx.set_chainid(self.chainid)
        return tx

    @fixture
    def tx2_extids(self) -> list:
        # Values pulled from explorer:
        # https://explorer.factoid.org/entry?hash=8279a10c9c26ce55ef29f382df4e8d4c31ce556f1c3efe4fbbd75ed396a56ef9
        timestamp = "1571166720".encode()
        rcd0 = bytes.fromhex("0172e643c983a4ac8d0bdc61ac37b5f0d870886da91b7cdda0ab5e8f297028883a")
        signature0 = bytes.fromhex(
            "dadb739b4d95c27fe12efdf01146354e2a566c144c250ec15a480cfb466ef88a5eee1022c00ba4f9b7abdfebcaca5596bac621a6884f787acb04e4addfc45e0c"
        )
        rcd1 = bytes.fromhex("01d0941f706665ad9518547372bf08cc1f1f52ae2b4223cda32f23c34cea21feaa")
        signature1 = bytes.fromhex(
            "9734a8528b8b6f0d7b8b5a568164e81bdeb297cb775970b2894e2562bcebe36533d9333264e12be2df876947b3309da1ed90dd90336e57ba8a53feefdb0db90f"
        )
        return [timestamp, rcd0, signature0, rcd1, signature1]

    def test_transaction_values(self):
        tx = Transaction()
        tx.add_input(self.address1, 50)
        tx.add_input(self.address2, 100)
        assert len(tx.inputs) == 2

        tx.add_output(self.address3, 150)
        assert len(tx.outputs) == 1

        tx.set_metadata({"note": "Goodbye and thanks for all the fish!"})
        assert len(tx.metadata) == 1

        tx.add_signer(self._private_fct_key1)
        tx.add_signer(self._private_fct_key2)
        assert len(tx._signer_keys) == 2

        # Missing chainid
        assert not tx.is_valid()

        tx.set_chainid(self.chainid)
        assert tx.is_valid()

    def test_transaction_signing_single_input(self, tx1, tx1_extids):
        # Override timestamp to match historical transactions
        tx1.timestamp = "1571180727"

        signed_tx = tx1.sign()

        actual_tx1_extids = signed_tx[0]

        # add = FactoidPrivateKey(key_string="Fs1KWJrpLdfucvmYwN2nWrwepLn8ercpMbzXshd1g8zyhKXLVLWj")
        # a = FactoidPrivateKey(key_string="Fs2jSmXgaysrqiADPmAvvb71NfAa9MqvXvRemozTE8LRc64hLqtf")

        # Skip comparing timestamps
        assert tx1_extids[1:] == actual_tx1_extids[1:]

    def test_transaction_signing_multiple_input(self, tx2, tx2_extids):
        # Override timestamp to match historical transactions
        tx2.timestamp = "1571166720"

        signed_tx = tx2.sign()

        actual_tx2_extids = signed_tx[0]

        # Skip comparing timestamps
        assert tx2_extids[1:] == actual_tx2_extids[1:]
