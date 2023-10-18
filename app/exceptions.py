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