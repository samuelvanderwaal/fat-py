import vcr
from pytest import fixture
from fat.client import Fat


class TestFat:
    def setup(self):
        self.chain_id = (
            "b54c4310530dc4dd361101644fa55cb10aec561e7874a7b786ea3b66f2c6fdfb")
        self.token_id = "test"
        self.issuer_id = (
            "88888807e4f3bbb9a2b229645ab6d2f184224190f83e78761674c2362aca4425")
        self.entry_hash = (
            "3b2c34b26365f01d432df762479da91eb995e6791248c98be7f8c202f1c1a28a")

    @fixture
    def fat_instance(self):
        return Fat("http://localhost:8078/v1")

    @fixture
    def get_issuance_subkeys(self):
        return ["chainid", "tokenid", "issuerid", "entryhash", "timestamp",
                "issuance"]

    @fixture
    def get_transaction_subkeys(self):
        return ["entryhash", "timestamp", "data"]

    @vcr.use_cassette("tests/vcr_cassettes/get_issuance.yaml")
    def test_get_issuance_by_chain(self, fat_instance, get_issuance_subkeys):
        """Tests an API call to get a token's issuance."""

        response = fat_instance.get_issuance(self.chain_id)

        assert isinstance(response, dict)
        assert isinstance(response["result"], dict)
        assert response["result"]["chainid"] == self.chain_id
        assert set(get_issuance_subkeys).issubset(response["result"])

    @vcr.use_cassette("tests/vcr_cassettes/get_issuance.yaml")
    def test_get_issuance_by_token(self, fat_instance, get_issuance_subkeys):
        """Tests an API call to get a token's issuance."""

        response = fat_instance.get_issuance(token_id=self.token_id,
                                             issuer_id=self.issuer_id)

        assert isinstance(response, dict)
        assert isinstance(response["result"], dict)
        assert response["result"]["tokenid"] == self.token_id
        assert response["result"]["issuerid"] == self.issuer_id
        assert set(get_issuance_subkeys).issubset(response["result"])

    @vcr.use_cassette("tests/vcr_cassettes/get_transaction.yaml")
    def test_get_transaction(self, fat_instance, get_transaction_subkeys):

        response = fat_instance.get_transaction(self.entry_hash, self.chain_id)

        assert isinstance(response, dict)
        assert isinstance(response["result"], dict)
        assert response["result"]["entryhash"] == self.entry_hash
        assert set(get_transaction_subkeys).issubset(response["result"])
