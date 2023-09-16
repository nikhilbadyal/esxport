"""Project Exceptions."""


class EsXportError(Exception):
    """Project Base Exception."""


class IndexNotFoundError(EsXportError):
    """Index provided does not exist."""
