# src/domain/exceptions/validation_exceptions.py
import sys
import inspect

class ValidationException(Exception):
    def __init__(self, message: str):
        tb = sys.exc_info()[2]
        if tb:
            frame = tb.tb_frame
            self.module = frame.f_globals.get('__name__', '')
            self.class_name = frame.f_locals.get('self', None).__class__.__name__ if 'self' in frame.f_locals else ''
            self.method = tb.tb_frame.f_code.co_name
        else:
            frame = inspect.currentframe().f_back
            self.module = frame.f_globals.get('__name__', '')
            self.class_name = frame.f_locals.get('self', None).__class__.__name__ if 'self' in frame.f_locals else ''
            self.method = frame.f_code.co_name
        super().__init__(message)

    def __str__(self):
        return f"[{self.module}.{self.class_name}.{self.method}] {super().__str__()}"

class DocumentNotFoundError(ValidationException):
    pass

class InvalidDocumentStatusError(ValidationException):
    pass

class RejectCommentRequiredError(ValidationException):
    pass