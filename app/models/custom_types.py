import ulid
from sqlalchemy.types import CHAR, TypeDecorator

class ULIDType(TypeDecorator):
    impl = CHAR

    def __init__(self):
        super().__init__(26)

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        if isinstance(value, ulid.ULID):
            return str(value)
        raise ValueError("value %s is not a valid ulid.ULID" % value)

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        return ulid.from_str(value)
    
    @staticmethod
    def create_ulid():
        return ulid.new()
