"""Project Exceptions."""


class EsXportError(Exception):
    """Project Base Exception."""


class IndexNotFoundError(EsXportError):
    """Index provided does not exist."""


class FieldNotFoundError(EsXportError):
    """Field provided does not exist."""


class MetaFieldNotFoundError(FieldNotFoundError):
    """Meta Field provided does not exist."""


class ESConnectionError(EsXportError):
    """Elasticsearch connection error."""


class ScrollExpiredError(EsXportError):
    """When scroll expires."""


class HealthCheckError(EsXportError):
    """Health check error."""


class InvalidEsQueryError(EsXportError):
    """Invalid query param."""


class NoDataFoundError(EsXportError):
    """No data found in the index."""
