class InvalidTransactionError(Exception):
    pass


class MissingRequiredParameter(Exception):
    pass


class InvalidChainIDError(ValueError):
    pass


class InvalidParamError(ValueError):
    pass


class InvalidFactoidKey(ValueError):
    pass
