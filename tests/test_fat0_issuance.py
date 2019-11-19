import sys
from base64 import b64decode
from pytest import fixture, raises
from fat.fat0.issuance import Issuance
from fat.errors import InvalidParam
from factom_keys.ec import ECAddress, ECPrivateKey
sys.path.insert(0, '/home/samuel/Coding/factom-keys')
from factom_keys.serverid import ServerIDPrivateKey, BadKeyStringError as BadKeyID
from factom_keys.ec import BadKeyStringError as BadKeyEC


class TestIssuance:
    @classmethod
    def setup(cls):
        # These are throwaway private keys.
        cls.chain_id = "145d5207a1ca2978e2a1cb43c97d538cd516d65cd5d14579549664bfecd80296"
        cls.issuer_id = "8888883beff463483a56398545cd02832c74bcdd9c468d61a79d6928f6208291"
        cls.issuer_signer = ServerIDPrivateKey(key_string="sk12hDMpMzcm9XEdvcy77XwxYU57hpLoCMY1kHtKnyjdGWUpsAvXD")
        cls.ec_address = ECAddress(key_string="EC3cQ1QnsE5rKWR1B5mzVHdTkAReK5kJwaQn5meXzU9wANyk7Aej")
        cls.ec_priv_key = ECPrivateKey(key_string="Es3w7m5KkGs97595YEiYouyjaJcsouHQr7cCLUrqKt6Y8LvWurAP")

    @fixture
    def issuance(self) -> Issuance:
        issuance = Issuance()
        issuance.token_id = "test"
        issuance.issuer_id = "888888a37cbf303c0bfc8d0cc7e77885c42000b757bd4d9e659de994477a0904"
        issuance.supply = -1
        issuance.symbol = "test"
        issuance.ec_priv_key = ECPrivateKey(key_string="Es3w7m5KkGs97595YEiYouyjaJcsouHQr7cCLUrqKt6Y8LvWurAP")
        issuance.server_priv_key = ServerIDPrivateKey(
            key_string="sk12hDMpMzcm9XEdvcy77XwxYU57hpLoCMY1kHtKnyjdGWUpsAvXD")
        return issuance

    @fixture
    def issuance_chain_ext_ids(self) -> list:
        """
        Ext IDs for chain creation
        """
        return [b"token", b"test", b"issuer",
                bytes.fromhex("888888a37cbf303c0bfc8d0cc7e77885c42000b757bd4d9e659de994477a0904")]

    @fixture
    def issuance_init_ext_ids(self) -> list:
        """
        Ext_IDs for intialization entry
        """
        rcd0 = b64decode("AUCUKWQqyS7HtHiLGRN2iEiWP1sE7zSMAuHxvvzA5XD6")
        signature0 = b64decode(
            "Lqbjm0YRj/Xb9/WhBLjKtrzRFqmbIZsm06nCvuXjKTnAcpvoy0/3GWs25co7mYLlC9GWncjAf2erTIb5czpHCQ=="
        )
        return ["1557643031", rcd0, signature0]

    def test_issuance_set_token_id(self):
        """
        Validate setting token id.
        """
        issuance = Issuance()

        # Not a str
        with raises(InvalidParam):
            issuance.token_id = 100

        with raises(InvalidParam):
            issuance.token_id = {"not": "a token id"}

        issuance.token_id = "BestToken"
        assert issuance.token_id == "BestToken"

    def test_issuance_set_issuer_id(self):
        """
        Validate issuer id values.
        """
        issuance = Issuance()

        # Not a string
        with raises(InvalidParam):
            issuance.symbol = 100

        # Not a valid ID
        with raises(InvalidParam):
            issuance.symbol = "188888412343124123412341234"

        issuance.issuer_id = "888888a37cbf303c0bfc8d0cc7e77885c42000b757bd4d9e659de994477a0904"
        assert issuance.issuer_id == "888888a37cbf303c0bfc8d0cc7e77885c42000b757bd4d9e659de994477a0904"

    def test_issuance_set_supply(self):
        """
        Validate issuance supply limits and values.
        """
        issuance = Issuance()

        # Type str is invalid.
        with raises(InvalidParam):
            issuance.supply = "100"

        # Negative integers other than -1 are invalid.
        with raises(InvalidParam):
            issuance.supply = -2

        # Zero is invalid
        with raises(InvalidParam):
            issuance.supply = 0

        # Check some valid values.
        issuance.supply = 100
        assert issuance.supply == 100
        issuance.supply = -1
        assert issuance.supply == -1
        issuance.supply = 9876543210
        assert issuance.supply == 9876543210

    def test_issuance_set_symbol(self):
        """
        Validate issuance symbol values.
        """
        issuance = Issuance()

        # Not a string
        with raises(InvalidParam):
            issuance.symbol = 100

        # Too long
        with raises(InvalidParam):
            issuance.symbol = "too long"

        # Too short
        with raises(InvalidParam):
            issuance.symbol = ""

        # Just right
        issuance.symbol = "EXT"
        assert issuance.symbol == "EXT"
        issuance.symbol = "ilpt"
        assert issuance.symbol == "ilpt"
        issuance.symbol = "TI"
        assert issuance.symbol == "TI"
        issuance.symbol = "a"
        assert issuance.symbol == "a"

    def test_issuance_set_metadata(self):
        """
        Validate values for metadata parameter.
        """
        issuance = Issuance()

        # Not a dict
        with raises(InvalidParam):
            issuance.metadata = 0

        with raises(InvalidParam):
            issuance.metadata = "not a dict"

        issuance.metadata = {}
        assert issuance.metadata == {}

        metadata = {"item1": "value1", "item2": "value2"}
        issuance.metadata = metadata
        assert issuance.metadata == metadata

    def test_issuance_set_server_priv_key(self):
        issuance = Issuance()

        # Not a ServerIDPrivateKey or str
        with raises(InvalidParam):
            issuance.server_priv_key = 1110

        with raises(InvalidParam):
            issuance.server_priv_key = b"1010101"

        with raises(BadKeyID):
            issuance.server_priv_key = "not a ServerID key"

        server_priv_key = "sk11pz4AG9XgB1eNVkbppYAWsgyg7sftDXqBASsagKJqvVRKYodCU"
        issuance.server_priv_key = server_priv_key
        assert isinstance(issuance.server_priv_key, ServerIDPrivateKey)
        assert issuance.server_priv_key.to_string() == "sk11pz4AG9XgB1eNVkbppYAWsgyg7sftDXqBASsagKJqvVRKYodCU"

        server_priv_key = ServerIDPrivateKey(key_string="sk11pz4AG9XgB1eNVkbppYAWsgyg7sftDXqBASsagKJqvVRKYodCU")
        issuance.server_priv_key = server_priv_key
        assert issuance.server_priv_key == server_priv_key

    def test_issuance_set_ec_priv_key(self):
        issuance = Issuance()

        # Not a ECPrivateKey
        with raises(InvalidParam):
            issuance.ec_priv_key = 1110

        with raises(InvalidParam):
            issuance.ec_priv_key = b"1010101"

        with raises(BadKeyEC):
            issuance.ec_priv_key = "not a ServerID key"

        ec_priv_key = ECPrivateKey(key_string="Es3w7m5KkGs97595YEiYouyjaJcsouHQr7cCLUrqKt6Y8LvWurAP")
        issuance.ec_priv_key = ec_priv_key
        assert issuance.ec_priv_key == ec_priv_key

    def test_issuance_is_valid(self, issuance):
        assert issuance.is_valid()

    def test_create_chain_id(self, issuance):
        issuance.create_chain_id()
        assert issuance.chain_id == bytes.fromhex("145d5207a1ca2978e2a1cb43c97d538cd516d65cd5d14579549664bfecd80296")

    def test_calculate_num_ec(self):
        content = b"short"
        ext_ids = [b"one", b"two", b"three"]
        assert Issuance.calculate_num_ec(content, ext_ids) == 1

        content = b"0"*1021
        ext_ids = [b"four"]
        assert Issuance.calculate_num_ec(content, ext_ids) == 2

        content = b"f"*1024*10
        ext_ids = b""
        assert Issuance.calculate_num_ec(content, ext_ids) == 10

    def test_issuance_constructor_init(self):
        issuance = Issuance(
            token_id="token",
            issuer_id=self.issuer_id,
            supply=-1,
            symbol="TKN",
            metadata={"note": "have some metadata"},
            ec_address=self.ec_address,
            ec_priv_key=self.ec_priv_key,
            server_priv_key=self.issuer_signer
        )

        assert issuance.token_id == "token"
        assert issuance.issuer_id == self.issuer_id
        assert issuance.supply == -1
        assert issuance.symbol == "TKN"
        assert issuance.metadata == {"note": "have some metadata"}
        assert issuance.ec_address == self.ec_address
        assert issuance.ec_priv_key == self.ec_priv_key
        assert issuance.server_priv_key == self.issuer_signer
