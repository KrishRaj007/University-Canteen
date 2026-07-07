from bson.errors import InvalidId
from bson.objectid import ObjectId


def id_filter(value):
    try:
        return {'_id': ObjectId(value)}
    except (InvalidId, TypeError):
        return {'_id': str(value)}
