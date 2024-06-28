from abc import ABC


class BaseContextException(Exception, ABC):
    """
    A base exception for all specification context-related exception.
    """
    pass


class ContextNotAvailableError(Exception):
    pass


class ContextualisationNotAllowed(Exception):
    pass


# WORKAROUND - traditional inhertiance syntax is not working in context of abstract Exceptions
BaseContextException.register(ContextNotAvailableError)
BaseContextException.register(ContextualisationNotAllowed)
