class PasswordStretcherError(Exception):
    pass

class InputListError(PasswordStretcherError):
    pass

class PasswordAnalyzerError(PasswordStretcherError):
    pass