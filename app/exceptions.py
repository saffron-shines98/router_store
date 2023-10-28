class AuthMissing(Exception):
    def __init__(self, message, error_code=403):
        self.http_code = error_code
        self.message = message
        super(AuthMissing, self).__init__()


class InvalidAuth(Exception):
    def __init__(self, message, error_code=401):
        self.http_code = error_code
        self.message = message
        super(InvalidAuth, self).__init__()

class CustomrAlreadyExist(Exception):
    def __init__(self, message, error_code= 400):
        self.http_code = error_code
        self.message = message
        super(CustomrAlreadyExist, self).__init__()

class AlreadyExists(Exception):
    def __init__(self, message, error_code=200):
        self.http_code = error_code
        self.message = message
        super(AlreadyExists, self).__init__()

class InvalidDateFormat(Exception):
    def __init__(self, message, error_code=400):
        self.http_code = error_code
        self.message = message
        super(InvalidDateFormat, self).__init__()

