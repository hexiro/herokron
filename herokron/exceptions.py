class HerokronError(Exception):
    pass


class AppError(HerokronError):
    pass


class DatabaseError(HerokronError):
    pass
