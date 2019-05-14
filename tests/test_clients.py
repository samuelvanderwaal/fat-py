import vcr
from pytest import fixture
from fat.client import Fat


class TestRpc:
    def setup(self):
        self.chain_id = (
            "145d5207a1ca2978e2a1cb43c97d538cd516d65cd5d14579549664bfecd80296")
        self.token_id = "test"
        self.issuer_id = (
            "888888a37cbf303c0bfc8d0cc7e77885c42000b757bd4d9e659de994477a0904")
        self.entry_hash = (
            "506278a53f299bc9941e7d576e61d6d216864703ef02310434182eb1481030c3")
        self.address = "FA2gCmih3PaSYRVMt1jLkdG4Xpo2koebUpQ6FpRRnqw5FfTSN2vW"

    @fixture
    def fat(self):
        return Fat("http://localhost:8078/v1")

    @fixture
    def get_issuance_subkeys(self):
        return ["chainid", "tokenid", "issuerid", "entryhash", "timestamp",
                "issuance"]

    @fixture
    def get_transaction_subkeys(self):
        return ["entryhash", "timestamp", "data"]

    @vcr.use_cassette("tests/vcr_cassettes/get_issuance.yaml")
    def test_get_issuance_by_chain(self, fat, get_issuance_subkeys):
        """Tests an API call to get a token's issuance."""

        response = fat.rpc.get_issuance(self.chain_id)

        assert isinstance(response, dict)
        assert isinstance(response["result"], dict)
        assert response["result"]["chainid"] == self.chain_id
        assert set(get_issuance_subkeys).issubset(response["result"])

    @vcr.use_cassette("tests/vcr_cassettes/get_issuance.yaml")
    def test_get_issuance_by_token(self, fat, get_issuance_subkeys):
        """Tests an API call to get a token's issuance."""

        response = fat.rpc.get_issuance(token_id=self.token_id,
                                        issuer_id=self.issuer_id)

        assert isinstance(response, dict)
        assert isinstance(response["result"], dict)
        assert response["result"]["tokenid"] == self.token_id
        assert response["result"]["issuerid"] == self.issuer_id
        assert set(get_issuance_subkeys).issubset(response["result"])

    @vcr.use_cassette("tests/vcr_cassettes/get_transaction.yaml")
    def test_get_transaction(self, fat, get_transaction_subkeys):

        response = fat.rpc.get_transaction(self.entry_hash, self.chain_id)

        result = response["result"]
        data = result["data"]

        assert isinstance(response, dict)
        assert isinstance(response["result"], dict)
        assert result["entryhash"] == self.entry_hash
        assert set(get_transaction_subkeys).issubset(response["result"])
        assert data["inputs"] == {"FA1zT4aFpEvcnPqPCigB3fvGu4Q4mTXY22iiuV69DqE1pNhdF2MC": 100}
        assert data["outputs"] == {"FA2gCmih3PaSYRVMt1jLkdG4Xpo2koebUpQ6FpRRnqw5FfTSN2vW": 100}

    @vcr.use_cassette("tests/vcr_cassettes/get_transactions.yaml")
    def test_get_transactions(self, fat, get_transaction_subkeys):

        response = fat.rpc.get_transactions(
            ["FA2gCmih3PaSYRVMt1jLkdG4Xpo2koebUpQ6FpRRnqw5FfTSN2vW",
             "FA3j68XNwKwvHXV2TKndxPpyCK3KrWTDyyfxzi8LwuM5XRuEmhy6"], self.chain_id)

        result = response["result"]
        tx1 = result[0]
        tx2 = result[1]
        data1 = tx1["data"]
        data2 = tx2["data"]

        assert len(result) == 2
        assert data1["inputs"] == {"FA1zT4aFpEvcnPqPCigB3fvGu4Q4mTXY22iiuV69DqE1pNhdF2MC": 100}
        assert data1["outputs"] == {"FA2gCmih3PaSYRVMt1jLkdG4Xpo2koebUpQ6FpRRnqw5FfTSN2vW": 100}
        assert data2["inputs"] == {"FA2gCmih3PaSYRVMt1jLkdG4Xpo2koebUpQ6FpRRnqw5FfTSN2vW": 50}
        assert data2["outputs"] == {"FA3j68XNwKwvHXV2TKndxPpyCK3KrWTDyyfxzi8LwuM5XRuEmhy6": 50}

    @vcr.use_cassette("tests/vcr_cassettes/get_balance.yaml")
    def test_get_balance(self, fat):

        response = fat.rpc.get_balance(self.address, self.chain_id)

        assert isinstance(response, dict)
        assert response["result"] == 50

    def test_get_nf_balance(self, fat):
        pass

    def test_get_stats(self, fat):
        pass

    def test_get_nf_token(self, fat):
        pass

    def test_get_nf_tokens(self, fat):
        pass

    def test_send_transaction(self, fat):
        pass


class TestDaemon:
    @fixture
    def fat(self):
        return Fat("http://localhost:8078/v1")

    @vcr.use_cassette("tests/vcr_cassettes/daemon/get_tokens.yaml")
    def test_get_tokens(self, fat):
        response = fat.daemon.get_tokens()
        assert isinstance(response["result"], list)
        assert isinstance(response["result"][0]["chainid"], str)
        assert isinstance(response["result"][0]["tokenid"], str)
        assert isinstance(response["result"][0]["issuerid"], str)

    @vcr.use_cassette("tests/vcr_cassettes/daemon/get_properties.yaml")
    def test_get_properties(self, fat):
        response = fat.daemon.get_properties()
        assert isinstance(response["result"], dict)
        assert isinstance(response["result"]["fatdversion"], str)
        assert isinstance(response["result"]["apiversion"], str)

    @vcr.use_cassette("tests/vcr_cassettes/daemon/get_sync_status.yaml")
    def test_get_sync_status(self, fat):
        response = fat.daemon.get_sync_status()
        assert isinstance(response["result"], dict)
        assert isinstance(response["result"]["syncheight"], int)
        assert isinstance(response["result"]["factomheight"], int)
