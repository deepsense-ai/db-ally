from abc import ABC


class BaseContextException(Exception, ABC):
    """
    A base (abstract) exception for all specification context-related exception.
    """


class ContextNotAvailableError(Exception):
    """
    An exception inheriting from BaseContextException pointining that no sufficient context information
    was provided by the user while calling view.ask().
    """


class ContextualisationNotAllowed(Exception):
    """
    An exception inheriting from BaseContextException pointining that the filter method signature
    does not allow to provide an additional context.
    """


# WORKAROUND - traditional inhertiance syntax is not working in context of abstract Exceptions
BaseContextException.register(ContextNotAvailableError)
BaseContextException.register(ContextualisationNotAllowed)
