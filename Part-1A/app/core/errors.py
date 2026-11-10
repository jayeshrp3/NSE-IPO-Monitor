"""Domain and persistence errors with safe HTTP representations."""


class IPOError(Exception):
    """Base class for expected IPO domain failures."""


class ValidationError(IPOError):
    """Raised when an IPO payload does not satisfy domain rules."""


class DuplicateIPOError(IPOError):
    """Raised when a new or updated record duplicates another IPO."""


class IPODataError(IPOError):
    """Raised when stored IPO data cannot safely be interpreted."""


class IPOStorageError(IPOError):
    """Raised when persistence fails without exposing internal details."""
