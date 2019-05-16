from pytest import fixture
from fat.client import Fat


class TestRpc:
    def setup(self):
        self.chain_id = "145d5207a1ca2978e2a1cb43c97d538cd516d65cd5d14579549664bfecd80296"
        self.nft_chaind_id = "1e5037be95e108c34220d724763444098528e88d08ec30bc15204c98525c3f7d"
        self.token_id = "test"
        self.issuer_id = "888888a37cbf303c0bfc8d0cc7e77885c42000b757bd4d9e659de994477a0904"
        self.entry_hash = "506278a53f299bc9941e7d576e61d6d216864703ef02310434182eb1481030c3"
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

    def test_get_issuance_by_chain(self, fat, get_issuance_subkeys):
        """Tests an API call to get a token's issuance."""
        response = fat.rpc.get_issuance(chain_id=self.chain_id)
        assert isinstance(response, dict)
        assert isinstance(response["result"], dict)
        assert response["result"]["chainid"] == self.chain_id
        assert set(get_issuance_subkeys).issubset(response["result"])

    def test_get_issuance_by_token(self, fat, get_issuance_subkeys):
        """Tests an API call to get a token's issuance."""
        response = fat.rpc.get_issuance(token_id=self.token_id,
                                        issuer_id=self.issuer_id)
        assert isinstance(response, dict)
        assert isinstance(response["result"], dict)
        assert response["result"]["tokenid"] == self.token_id
        assert response["result"]["issuerid"] == self.issuer_id
        assert set(get_issuance_subkeys).issubset(response["result"])

    def test_get_transaction(self, fat, get_transaction_subkeys):
        response = fat.rpc.get_transaction(self.entry_hash, chain_id=self.chain_id)
        result = response["result"]
        data = result["data"]
        assert isinstance(response, dict)
        assert isinstance(response["result"], dict)
        assert result["entryhash"] == self.entry_hash
        assert set(get_transaction_subkeys).issubset(response["result"])
        assert data["inputs"] == {"FA1zT4aFpEvcnPqPCigB3fvGu4Q4mTXY22iiuV69DqE1pNhdF2MC": 100}
        assert data["outputs"] == {"FA2gCmih3PaSYRVMt1jLkdG4Xpo2koebUpQ6FpRRnqw5FfTSN2vW": 100}

    def test_get_transactions(self, fat, get_transaction_subkeys):
        response = fat.rpc.get_transactions(
            addresses=["FA2gCmih3PaSYRVMt1jLkdG4Xpo2koebUpQ6FpRRnqw5FfTSN2vW",
                       "FA3j68XNwKwvHXV2TKndxPpyCK3KrWTDyyfxzi8LwuM5XRuEmhy6"],
            chain_id=self.chain_id)
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

    def test_get_balance(self, fat):
        response = fat.rpc.get_balance(self.address, self.chain_id)
        assert isinstance(response, dict)
        assert response["result"] == 50

    def test_get_nf_balance(self, fat):
        response = fat.rpc.get_nf_balance(self.address, chain_id=self.nft_chaind_id)
        assert isinstance(response, dict)
        assert response["result"] == [10]

    def test_get_nf_token(self, fat):
        response = fat.rpc.get_nf_token(10, chain_id=self.nft_chaind_id)
        print(response)
        assert response["result"]["id"] == 10

    def test_get_nf_tokens_default(self, fat):
        response = fat.rpc.get_nf_tokens(0, 25, "asc", chain_id=self.nft_chaind_id)
        result = response["result"]
        assert isinstance(result, list)
        for r in result:
            assert [*r] == ["id", "owner"]
            assert isinstance(r["id"], int)
            assert isinstance(r["owner"], str)

    def test_get_nf_tokens(self, fat):
        response = fat.rpc.get_nf_tokens(order="desc", chain_id=self.nft_chaind_id)
        result = response["result"]
        assert isinstance(result, list)
        for r in result:
            assert [*r] == ["id", "owner"]
            assert isinstance(r["id"], int)
            assert isinstance(r["owner"], str)

    def test_get_stats(self, fat):
        response = fat.rpc.get_stats(chain_id=self.nft_chaind_id)
        result = response["result"]
        chain_id = "1e5037be95e108c34220d724763444098528e88d08ec30bc15204c98525c3f7d"
        assert isinstance(result, dict)
        assert result["chainid"] == chain_id
        assert result["Issuance"]["type"] == "FAT-1"
        assert result["Issuance"]["supply"] == -1

    def test_send_transaction(self, fat):
        pass


class TestDaemon:
    @fixture
    def fat(self):
        return Fat("http://localhost:8078/v1")

    def test_get_tokens(self, fat):
        response = fat.daemon.get_tokens()
        assert isinstance(response["result"], list)
        assert isinstance(response["result"][0]["chainid"], str)
        assert isinstance(response["result"][0]["tokenid"], str)
        assert isinstance(response["result"][0]["issuerid"], str)

    def test_get_properties(self, fat):
        response = fat.daemon.get_properties()
        assert isinstance(response["result"], dict)
        assert isinstance(response["result"]["fatdversion"], str)
        assert isinstance(response["result"]["apiversion"], str)

    def test_get_sync_status(self, fat):
        response = fat.daemon.get_sync_status()
        assert isinstance(response["result"], dict)
        assert isinstance(response["result"]["syncheight"], int)
        assert isinstance(response["result"]["factomheight"], int)
