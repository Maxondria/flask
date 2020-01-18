from marshmallow import schema, fields
from werkzeug.datastructures import FileStorage


class FileStorageField(fields.Field):
    default_error_messages = {
        'invalid': 'Not a valid image.'
    }

    def _deserialize(self, value, attr, data) -> FileStorage:
        if value is None:
            return None
        return value if isinstance(value, FileStorage) else self.fail('invalid')


class ImageSchema(schema):
    image = FileStorageField(required=True)
