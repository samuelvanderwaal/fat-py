from . import session


class MissingRequiredParameter(Exception):
    pass


class FAT:
    def __init__(self, url):
        self.url = url

    @staticmethod
    def check_id_params(chain_id, token_id, issuer_id):
        if chain_id:
            return {"chainid": chain_id}
        elif token_id and issuer_id:
            return {"tokenid": token_id, "issuerid": issuer_id}
        else:
            raise MissingRequiredParameter(
                "Requires either chain_id or token_id AND issuer_id.")

    def get_issuance(self, chain_id=None, token_id=None, issuer_id=None):
        params = FAT.check_id_params(chain_id, token_id, issuer_id)

        payload = {"jsonrpc": "2.0", "method": "get-issuance",
                   "params": params, "id": 1}

        response = session.post(self.url, json=payload)
        return response.json()

    def get_transaction(self, entry_hash, chain_id=None, token_id=None,
                        issuer_id=None):
        params = FAT.check_id_params(chain_id, token_id, issuer_id)
        params["entryhash"] = entry_hash

        payload = {"jsonrpc": "2.0", "method": "get-transaction",
                   "params": params, "id": 1}

        response = session.post(self.url, json=payload)
        return response.json()
