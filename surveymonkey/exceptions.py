class BaseError(Exception):
    pass


class UnknownError(BaseError):
    pass


class BadRequestError(BaseError):
    pass


class AuthorizationError(BaseError):
    pass


class PermissionError(BaseError):
    pass


class ResourceNotFoundError(BaseError):
    pass


class ResourceConflictError(BaseError):
    pass


class RequestEntityTooLargeError(BaseError):
    pass


class RateLimitReachedError(BaseError):
    pass


class InternalServerError(BaseError):
    pass


class UserSoftDeletedError(BaseError):
    pass


class UserDeletedError(BaseError):
    pass

