"""Project Exceptions."""


class EsXportError(Exception):
    """Project Base Exception."""


class IndexNotFoundError(EsXportError):
    """Index provided does not exist."""


class FieldNotFoundError(EsXportError):
    """Field provided does not exist."""


class ESConnectionError(EsXportError):
    """Elasticsearch connection error."""
