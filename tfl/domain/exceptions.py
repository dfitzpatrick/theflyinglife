
class EntityExistsError(Exception):
    ...


class EntityNotFoundError(Exception):
    ...


class MemberExists(Exception):
    ...


class NoMember(Exception):
    ...


class AuthenticationError(Exception):
    ...